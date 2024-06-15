import io
import json
from functools import cache

import PIL
import qrcode
from django.conf import settings
from PIL.Image import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import (
    getFont,
    getRegisteredFontNames,
    registerFont,
    stringWidth,
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from devicemanager.inventory.models import Device
from devicemanager.utils.units import UnitConverter


class DeviceQRCodeGenerator:
    def __init__(
        self,
        pdf_width_mm: int,
        pdf_height_mm: int,
        pdf_padding_mm: int,
        gap_x_mm: int,
        gap_y_mm: int,
        title_gap_mm: int,
        inv_prefix: str,
        sn_prefix: str,
        dpi: int = 72,
        font_size: int = 12,
        font_size_large: int = 16,
        font_size_small: int = 10,
        fill_color: str = "#000000",
        background_color: str = "#FFFFFF",
    ) -> None:
        self._buffer = io.BytesIO()

        self.unit_converter = UnitConverter(dpi)
        self.dpi = dpi
        self.font_size = font_size
        self.font_size_large = font_size_large
        self.font_size_small = font_size_small
        self.fill_color = fill_color
        self.background_color = background_color
        self.inv_prefix = inv_prefix
        self.sn_prefix = sn_prefix

        self.pdf_width = self.unit_converter.mm_to_px(pdf_width_mm)
        self.pdf_height = self.unit_converter.mm_to_px(pdf_height_mm)
        self.pdf_padding = self.unit_converter.mm_to_px(pdf_padding_mm)
        self.gap_x = self.unit_converter.mm_to_px(gap_x_mm)
        self.gap_y = self.unit_converter.mm_to_px(gap_y_mm)
        self.title_gap = self.unit_converter.mm_to_px(title_gap_mm)

        self._canvas = canvas.Canvas(self._buffer, pagesize=(self.pdf_width, self.pdf_height))
        self._canvas.setFillColor(self.fill_color)
        self._canvas.setStrokeColor(self.fill_color)

        self.standard_font = "Roboto"
        if "Roboto" not in getRegisteredFontNames():
            registerFont(TTFont("Roboto", settings.BASE_DIR / "devicemanager/fonts/Roboto.ttf"))

        self.bold_font = "Roboto-Bold"
        if "Roboto-Bold" not in getRegisteredFontNames():
            registerFont(
                TTFont(
                    "Roboto-Bold",
                    settings.BASE_DIR / "devicemanager/fonts/Roboto-Bold.ttf",
                )
            )

    def _generate_qr_code(self, data: bytes) -> tuple[io.BytesIO, tuple[int, int]]:
        qr_size = self.pdf_height - self.pdf_padding * 2
        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=qr_size,
            border=0,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img: Image = qr.make_image(fill_color=self.fill_color, back_color=self.background_color)
        img = img.resize((qr_size, qr_size), PIL.Image.Resampling.NEAREST)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer, img.size

    def _draw_text_line(self, text: str, x: int, y: int, font_size: int | None = None, font_name=None) -> None:
        font_name = font_name or self.standard_font
        font_size = font_size or self.font_size

        self._canvas.saveState()

        self._canvas.setFont(font_name, font_size)
        width = stringWidth(text, fontName=font_name, fontSize=font_size)
        self._canvas.drawString(x, y, text)

        self._canvas.restoreState()
        return width

    @cache
    def get_line_height(self, font_size: int | None = None, font_name=None) -> int:
        font_size = font_size or self.font_size
        font_name = font_name or self.standard_font
        face = getFont(font_name).face
        string_height = (face.ascent - face.descent) / 1000 * font_size * 0.9
        return int(string_height)

    def add_device(
        self,
        device: Device,
    ) -> None:
        device_id = device.id
        building = device.room.building
        room = device.room.room_number
        owner = device.owner.get_full_name()
        inventory_number = device.inventory_number
        serial_number = device.serial_number
        manufacturer = device.device_model.manufacturer
        model = device.device_model.name

        qrcode_data = json.dumps(
            {
                "id": f"{device_id:04}",
                "room": f"{building}-{room}",
                "own": owner,
                "inv": inventory_number,
                "s/n": serial_number,
            }
        ).encode("utf-8")
        qr_img, (qr_img_width, qr_img_height) = self._generate_qr_code(qrcode_data)

        self._canvas.drawImage(
            image=ImageReader(qr_img),
            x=self.pdf_padding,
            y=self.pdf_height - qr_img_height - self.pdf_padding,
            width=qr_img_width,
            height=qr_img_height,
        )

        label_x = self.pdf_padding + qr_img_width + self.gap_x
        label_y = (
            self.pdf_height - self.get_line_height(self.font_size_large, font_name=self.bold_font) - self.pdf_padding
        )

        self._draw_text_line(
            f"{building} - {room}",
            label_x,
            label_y,
            font_size=self.font_size_large,
            font_name=self.bold_font,
        )
        label_y -= self.get_line_height(self.font_size_large, font_name=self.bold_font) + self.title_gap

        self._draw_text_line(owner, label_x, label_y, self.font_size)
        label_y -= self.get_line_height(self.font_size) + self.gap_y

        w = self._draw_text_line(f"{self.inv_prefix} ", label_x, label_y, font_size=self.font_size_small)
        self._draw_text_line(f"{inventory_number}", label_x + w, label_y, self.font_size)
        label_y -= self.get_line_height(self.font_size) + self.gap_y

        w = self._draw_text_line(
            f"{manufacturer}",
            label_x,
            label_y,
            font_size=self.font_size,
            font_name=self.bold_font,
        )
        self._draw_text_line(f" - {model}", label_x + w, label_y)
        label_y -= self.get_line_height(self.font_size) + self.gap_y

        w = self._draw_text_line(f"{self.sn_prefix} ", label_x, label_y, font_size=self.font_size_small)
        self._draw_text_line(f"{serial_number}", label_x + w, label_y, self.font_size)
        self._canvas.showPage()

    def build_pdf(self) -> io.BytesIO:
        self._canvas.save()
        return io.BytesIO(self._buffer.getvalue())
