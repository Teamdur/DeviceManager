import io

from PIL import Image, ImageDraw, ImageFont
from qrcode.main import QRCode

from devicemanager.inventory.models import QRCodeGenerationConfig


class UnitConverter:
    inch_to_cm = 2.54
    dpi = 96  # 96 pixels per inch

    @classmethod
    def cm_to_px(cls, cm: float) -> int:
        cm_to_px = cls.dpi / cls.inch_to_cm
        return int(cm * cm_to_px)


class QRCodeGenerator:
    def __init__(self, embedded_data: bytes, config: QRCodeGenerationConfig | None = None) -> None:
        self.embedded_data = embedded_data
        self.config = config or QRCodeGenerationConfig.get_active_configuration()
        self.box_size = self.config.qr_code_size_cm
        self.border = self.config.qr_code_margin_mm
        self.fill_color = self.config.fill_color
        self.back_color = self.config.back_color

    def make_qr_code(self) -> QRCode:
        qr = QRCode(self.box_size, self.border)
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
        # Font size is 25% of the box size
        font_size = UnitConverter.cm_to_px(self.box_size / 4)
        font = ImageFont.load_default(size=font_size)

        text_lines = title.split("\n")
        text_width = max(font.getbbox(line)[2] for line in text_lines)
        text_height = sum(font.getbbox(line)[3] for line in text_lines)

        expanded_width = max(im_width, text_width)
        padding_bottom = UnitConverter.cm_to_px(self.border * 0.3)  # Around 3 times the unit gives similar padding
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
            draw.text((x_offset, y_offset), line, fill="black", font=font)
            y_offset += line_height

        return expanded_img
