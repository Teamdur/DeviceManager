import io
from typing import Iterable, Type

import pymupdf
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
        # Font size is 20% of the box size
        font_size = self.config.unit_converter.cm_to_px(self.box_size / 5)
        font = ImageFont.load_default(size=font_size)

        text_lines = title.split("\n")
        text_width = max(font.getbbox(line)[2] for line in text_lines)
        text_height = sum(font.getbbox(line)[3] for line in text_lines)

        expanded_width = max(im_width, text_width)
        padding_bottom = self.config.unit_converter.cm_to_px(
            self.border * 0.3
        )  # Around 3 times the unit gives similar padding
        expanded_height = im_height + text_height
        expanded_img = Image.new("RGB", (expanded_width, expanded_height + padding_bottom), self.back_color)

        qr_position = ((expanded_width - im_width) // 2, 0)
        expanded_img.paste(img, qr_position)

        draw = ImageDraw.Draw(expanded_img)
        y_offset = im_height

        line_offsets = [(expanded_width - font.getbbox(line)[2]) // 2 for line in text_lines]
        x_offset = min(line_offsets)

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
        tile_width = max(qr.width for qr in qr_codes)
        tile_height = max(qr.height for qr in qr_codes)

        num_horizontal_tiles = self.page_width_px // tile_width
        num_vertical_tiles = self.page_height_px // tile_height

        tiles_per_page = num_horizontal_tiles * num_vertical_tiles
        num_pages = max(len(self.devices) // tiles_per_page, 1)

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
                (x_offset, y_offset, tile_width + x_offset, tile_height + y_offset), stream=stream, keep_proportion=True
            )

        output = io.BytesIO()
        self.pdf.save(output)
        output.seek(0)
        return output
