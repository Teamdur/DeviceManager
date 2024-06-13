import io
from math import ceil
from typing import Iterable, Type

import pymupdf
from django.conf import settings
from django.db.models import QuerySet
from PIL import Image, ImageDraw, ImageFont
from qrcode.main import QRCode
from rest_framework import serializers

from devicemanager.inventory.models import Device, QRCodeGenerationConfig


class QRCodeGenerator:
    def __init__(self, embedded_data: bytes, config: QRCodeGenerationConfig | None = None) -> None:
        self.embedded_data = embedded_data
        self.config = config or QRCodeGenerationConfig.get_active_configuration()
        self.box_size = self.config.qr_code_size_cm
        self.border = self.config.qr_code_margin_mm
        self.fill_color = self.config.fill_color
        self.back_color = self.config.back_color

    def make_qr_code(self) -> QRCode:
        qr = QRCode(box_size=self.box_size, border=self.border)
        qr.add_data(self.embedded_data)
        qr.make(fit=True)
        return qr

    def qr_code_image(self, title: str | None = None) -> Image:
        qr = self.make_qr_code()
        img = qr.make_image(fill_color=self.fill_color, back_color=self.back_color)

        if title:
            img = self._draw_title(img, title)

        return img

    def qr_code_png_file(self, title: str | None = None) -> io.BytesIO:
        bytes_io = io.BytesIO()
        image = self.qr_code_image(title=title)
        image.save(bytes_io, format="PNG")
        bytes_io.seek(0)
        return bytes_io

    def _draw_title(self, img: Image, title: str) -> Image:
        im_width, im_height = img.size
        # Font size is 20% of the box size]
        font_size = self.config.unit_converter.cm_to_px(self.box_size / 4)
        font = ImageFont.truetype(f"{settings.BASE_DIR}/devicemanager/fonts/roboto.ttf", font_size)

        text_lines = title.split("\n")
        text_width = max(font.getbbox(line)[2] for line in text_lines)
        text_height = sum(font.getbbox(line)[3] for line in text_lines)

        # The width of expanded image needs to accommodate both the image and the text.
        # The height of expanded image should be as high as the taller one between the image and the text.
        expanded_width = im_width + text_width
        expanded_height = max(im_height, text_height)

        # The text will be located beside the QR code, so we do not need the bottom padding.
        expanded_img = Image.new("RGB", (expanded_width, expanded_height), self.back_color)

        qr_position = (0, (expanded_height - im_height) // 2)  # Center the QR code vertically
        expanded_img.paste(img, qr_position)

        draw = ImageDraw.Draw(expanded_img)

        # The offset for text should be beside the image, so the y_offset keeps the same.
        x_offset = im_width

        # Initialize y_offset considering vertical centering of text
        y_offset = (im_height - text_height) // 2

        # Print the text
        for line in text_lines:
            _, _, line_width, line_height = font.getbbox(line)
            draw.text((x_offset, y_offset), line, fill=self.fill_color, font=font)
            y_offset += line_height

        return expanded_img


class QRCodePDFGenerator:
    def __init__(
        self,
        devices: Iterable[Device] | QuerySet,
        serializer_cls: Type[serializers.Serializer],
        config: QRCodeGenerationConfig | None = None,
    ) -> None:
        self.config = config or QRCodeGenerationConfig.get_active_configuration()
        self.devices = devices
        self.serializer_cls = serializer_cls
        self.pdf = pymupdf.open()
        self.page_width_px = self.config.unit_converter.mm_to_px(self.config.pdf_page_width_mm)
        self.page_height_px = self.config.unit_converter.mm_to_px(self.config.pdf_page_height_mm)

    def add_page(self):
        self.pdf.new_page(-1, width=self.page_width_px, height=self.page_height_px)

    def gen_qr_image(self, device: Device) -> Image:
        embedded_data = self.serializer_cls(device).data
        labels = device.get_print_label(config=self.config)

        qr_gen = QRCodeGenerator(embedded_data=embedded_data, config=self.config)
        return qr_gen.qr_code_image(title=labels)

    def run(self):
        qr_codes = [self.gen_qr_image(device) for device in self.devices]
        tile_width = max(qr.size[0] for qr in qr_codes)
        tile_height = max(qr.size[1] for qr in qr_codes)

        num_horizontal_tiles = max(self.page_width_px // tile_width, 1)
        num_vertical_tiles = max(self.page_height_px // tile_height, 1)

        tiles_per_page = max(num_horizontal_tiles * num_vertical_tiles, 1)

        num_pages = ceil(max(len(self.devices) / tiles_per_page, 1))

        for _ in range(num_pages):
            self.add_page()

        for i, qr in enumerate(qr_codes):
            page_index = i // tiles_per_page
            x_index = (i % tiles_per_page) % num_horizontal_tiles
            y_index = (i % tiles_per_page) // num_horizontal_tiles

            x_offset = x_index * tile_width
            y_offset = y_index * tile_height

            stream = io.BytesIO()
            qr.save(stream, format="PNG")
            stream.seek(0)

            self.pdf[page_index].insert_image(
                (x_offset, y_offset, x_offset + qr.size[0], y_offset + qr.size[1]), stream=stream, keep_proportion=True
            )

        output = io.BytesIO()
        self.pdf.save(output)
        output.seek(0)
        return output
