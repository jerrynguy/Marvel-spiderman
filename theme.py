"""
Bảng màu, mặt chữ và chất liệu giấy dùng chung cho toàn ứng dụng.

Tách riêng để `spiderman.py`, `characters/` và `ui/` cùng dùng một nguồn màu
mà không import vòng lẫn nhau.

Một tấm hồ sơ chọn màu qua `Skin`: `PULP` là giấy in Silver Age quen thuộc,
`VOID` dành cho các dạng Absolute — nền đen, mực huỳnh quang, lệch trục theo
kiểu tín hiệu số hỏng thay vì bản in chồng màu sai.
"""

from dataclasses import dataclass
from typing import Dict, Tuple

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (QBrush, QColor, QFont, QFontDatabase, QPainter,
                           QPixmap, QRadialGradient)
from PySide6.QtWidgets import QWidget

# ═══════════════════════════════════════════════════════════════ bảng màu
# Bốn màu của máy in Silver Age, cộng giấy pulp và mực đen ám nâu.
PAPER = QColor("#E6DCC6")
PAPER_HI = QColor("#F0E8D6")
INK = QColor("#1A1613")
INK_SOFT = QColor("#6E6355")
RED = QColor("#D6323C")
BLUE = QColor("#2B4F9E")
YELLOW = QColor("#E3B22B")

ACCENT = {"edge": (BLUE, QColor("#D8DEEE")),
          "new": (RED, QColor("#F2D8D6")),
          "fix": (YELLOW, QColor("#F2E4C2"))}


def blend(a, b, t):
    """Pha hai màu theo tỉ lệ t — 0 là `a`, 1 là `b`, kể cả kênh alpha."""
    t = max(0.0, min(1.0, t))
    return QColor(int(a.red() + (b.red() - a.red()) * t),
                  int(a.green() + (b.green() - a.green()) * t),
                  int(a.blue() + (b.blue() - a.blue()) * t),
                  int(a.alpha() + (b.alpha() - a.alpha()) * t))


# ═══════════════════════════════════════════════════════ da của tấm hồ sơ
@dataclass(frozen=True)
class Skin:
    """Toàn bộ màu của một tấm hồ sơ, để mọi widget hỏi chung một chỗ.

    `ghosts` là các lớp mực lệch trục vẽ dưới tờ giấy — giấy pulp thì đó là
    bóng đổ và bản in đỏ trượt, nền void thì đó là quầng sáng đỏ/lam.
    """

    name: str
    paper: QColor
    paper_hi: QColor
    ink: QColor
    ink_soft: QColor
    red: QColor
    blue: QColor
    yellow: QColor
    dot: QColor        # chấm halftone rải trên mặt giấy
    frame: QColor      # nét kẻ quanh tờ giấy
    scrim: QColor      # màn phủ sau lưng tờ giấy, alpha là độ đậm tối đa
    grid: QColor       # chấm halftone rắc lên màn phủ
    ghosts: Tuple[Tuple[QColor, float, float, int], ...]
    accents: Dict[str, Tuple[QColor, QColor]]
    dark: bool = False

    def accent(self, kind):
        """Cặp (màu viền, màu nền) cho một loại nhãn."""
        return self.accents.get(kind, (self.ink_soft, self.paper_hi))


PULP = Skin(
    name="pulp",
    paper=PAPER, paper_hi=PAPER_HI, ink=INK, ink_soft=INK_SOFT,
    red=RED, blue=BLUE, yellow=YELLOW,
    dot=QColor(26, 22, 19, 26),
    frame=INK,
    scrim=QColor(26, 22, 19, 176),
    grid=QColor(240, 232, 214, 34),
    ghosts=((INK, 11, 11, 105), (RED, 5, 5, 160)),
    accents=ACCENT,
)

VOID = Skin(
    name="void",
    paper=QColor("#0A0810"), paper_hi=QColor("#100D18"),
    ink=QColor("#EDE7DE"), ink_soft=QColor("#8B84A0"),
    red=QColor("#FF2E4C"), blue=QColor("#2BE6D8"), yellow=QColor("#B4F03C"),
    dot=QColor(150, 240, 255, 15),
    frame=QColor("#4A4360"),
    scrim=QColor(4, 3, 10, 224),
    grid=QColor(120, 240, 230, 24),
    ghosts=((QColor("#2BE6D8"), -7, -7, 70), (QColor("#FF2E4C"), 7, 7, 92)),
    accents={"edge": (QColor("#2BE6D8"), QColor("#0C2028")),
             "new": (QColor("#FF2E4C"), QColor("#26101A")),
             "fix": (QColor("#B4F03C"), QColor("#1A2410"))},
    dark=True,
)


def pick_font(candidates, fallback="DejaVu Sans"):
    have = set(QFontDatabase.families())
    for name in candidates:
        if name in have:
            return name
    return fallback


class Type:
    """Chọn font một lần sau khi QApplication đã tồn tại."""
    display = body = None

    @classmethod
    def load(cls):
        # Mặt chữ đậm nén cho masthead — logo bìa truyện tranh.
        cls.display = pick_font(["Haettenschweiler", "Impact",
                                 "Franklin Gothic Heavy", "Arial Narrow Bold",
                                 "Arial Narrow", "DejaVu Sans Condensed"])
        cls.body = pick_font(["Segoe UI", "Helvetica Neue", "Inter",
                              "Noto Sans", "DejaVu Sans"])

    @classmethod
    def head(cls, size, letter=2.0):
        f = QFont(cls.display, size)
        f.setBold(True)
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, letter)
        return f

    @classmethod
    def text(cls, size, bold=False, letter=0.0, caps=False, italic=False):
        f = QFont(cls.body, size)
        f.setBold(bold)
        f.setItalic(italic)
        if letter:
            f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, letter)
        if caps:
            f.setCapitalization(QFont.Capitalization.AllUppercase)
        return f


# ═══════════════════════════════════════════════════════ lưới halftone
def halftone_tile(dot=1.5, step=5, color=QColor(26, 22, 19, 34)):
    """Ô lát 45° — hai chấm lệch nửa bước tạo lưới nghiêng liền mạch."""
    size = step * 2
    tile = QPixmap(size, size)
    tile.fill(Qt.GlobalColor.transparent)
    p = QPainter(tile)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(color)
    for cx, cy in ((step * 0.5, step * 0.5), (step * 1.5, step * 1.5)):
        p.drawEllipse(QPointF(cx, cy), dot / 2, dot / 2)
    p.end()
    return tile


class Paper(QWidget):
    """Nền giấy: màu pulp + lưới halftone + vệt ố ở rìa."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tile = None

    def paintEvent(self, _):
        if self._tile is None:
            self._tile = halftone_tile()
        p = QPainter(self)
        r = self.rect()
        p.fillRect(r, PAPER)
        glow = QRadialGradient(r.center(), max(r.width(), r.height()) * 0.72)
        glow.setColorAt(0.0, PAPER_HI)
        glow.setColorAt(1.0, QColor(198, 184, 158))
        p.fillRect(r, QBrush(glow))
        p.fillRect(r, QBrush(self._tile))
        p.end()
