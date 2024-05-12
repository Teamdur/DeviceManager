class UnitConverter:
    inch_to_cm = 2.54

    def __init__(self, dpi: int = 72) -> None:
        self.dpi = dpi

    def cm_to_px(self, cm: float) -> int:
        cm_to_px = self.dpi / self.inch_to_cm
        return int(cm * cm_to_px)

    def mm_to_px(self, mm: float) -> int:
        mm_to_px = (self.dpi / self.inch_to_cm) / 10
        return int(mm * mm_to_px)
