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
    dot_size: float = 1.4      # cỡ chấm halftone — nới ra thì mặt giấy nhám hơn
    dot_step: int = 5

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

# Tầng bình lưu lúc rạng đông: thép lạnh và đèn natri. Dành cho những kẻ
# Absolute sống trên không, để chúng không đội chung một bộ da với Chameleon.
SKY = Skin(
    name="sky",
    paper=QColor("#070A11"), paper_hi=QColor("#0D111B"),
    ink=QColor("#EFEBE1"), ink_soft=QColor("#7C879C"),
    red=QColor("#FF9A1F"), blue=QColor("#5FC8FF"), yellow=QColor("#E8C24A"),
    dot=QColor(170, 210, 255, 14),
    frame=QColor("#3E4A5E"),
    scrim=QColor(3, 5, 11, 224),
    grid=QColor(150, 200, 255, 22),
    ghosts=((QColor("#5FC8FF"), -7, -7, 66), (QColor("#FF9A1F"), 7, 7, 88)),
    accents={"edge": (QColor("#5FC8FF"), QColor("#0B1C2A")),
             "new": (QColor("#FF9A1F"), QColor("#2A1A08")),
             "fix": (QColor("#E8C24A"), QColor("#241D0A"))},
    dark=True,
)

# Vật chất lập trình: graphite lạnh, mực đỏ tía và xanh axit. Dành cho những
# kẻ Absolute mà thân thể lẫn chiến trường đều là thứ có thể lập trình được.
MESH = Skin(
    name="mesh",
    paper=QColor("#06100D"), paper_hi=QColor("#0B1714"),
    ink=QColor("#E9F3ED"), ink_soft=QColor("#7B9289"),
    red=QColor("#FF2FB2"), blue=QColor("#6BFF2E"), yellow=QColor("#E8FF4A"),
    dot=QColor(120, 255, 190, 15),
    frame=QColor("#3A5349"),
    scrim=QColor(3, 9, 7, 226),
    grid=QColor(110, 255, 180, 22),
    ghosts=((QColor("#6BFF2E"), -7, -7, 62), (QColor("#FF2FB2"), 7, 7, 92)),
    accents={"edge": (QColor("#6BFF2E"), QColor("#0A2011")),
             "new": (QColor("#FF2FB2"), QColor("#26091C")),
             "fix": (QColor("#E8FF4A"), QColor("#1F2409"))},
    dark=True,
)

# Lò rèn: sắt ám khói, gang chảy và đồng thau. Đây là bộ da ấm duy nhất —
# ba bộ kia đều lấy nền lạnh, nên chỉ cần liếc là biết đang xem hồ sơ nào.
FORGE = Skin(
    name="forge",
    paper=QColor("#0E0908"), paper_hi=QColor("#171010"),
    ink=QColor("#F3EADF"), ink_soft=QColor("#9C8579"),
    red=QColor("#FF5A1F"), blue=QColor("#FFC94A"), yellow=QColor("#BFE3FF"),
    dot=QColor(255, 180, 120, 14),
    frame=QColor("#4A342A"),
    scrim=QColor(10, 5, 3, 224),
    grid=QColor(255, 170, 110, 22),
    ghosts=((QColor("#FFC94A"), -7, -7, 62), (QColor("#FF5A1F"), 7, 7, 96)),
    accents={"edge": (QColor("#FFC94A"), QColor("#241704")),
             "new": (QColor("#FF5A1F"), QColor("#2A1108")),
             "fix": (QColor("#BFE3FF"), QColor("#0E1B24"))},
    dark=True,
)

# Bão cát: bộ da sáng duy nhất. Bốn bộ kia đều tối dần đi khi mở ra, còn bộ
# này thì loà lên — màn phủ là một trận cát trắng xoá chứ không phải bóng đêm.
# Mặt giấy cũng nhám hơn hẳn: chấm halftone to và dày, sờ vào là ra hạt.
DUST = Skin(
    name="dust",
    paper=QColor("#C6BBA0"), paper_hi=QColor("#D6CCB4"),
    ink=QColor("#241D14"), ink_soft=QColor("#6B5F4B"),
    red=QColor("#A63D14"), blue=QColor("#2E3A52"), yellow=QColor("#8A6B18"),
    dot=QColor(62, 50, 33, 34),
    frame=QColor("#463628"),
    scrim=QColor(198, 186, 160, 232),
    grid=QColor(92, 76, 52, 30),
    ghosts=((QColor("#2E3A52"), -7, -7, 58), (QColor("#A63D14"), 7, 7, 84)),
    accents={"edge": (QColor("#2E3A52"), QColor("#BFC6D2")),
             "new": (QColor("#A63D14"), QColor("#E2C7B4")),
             "fix": (QColor("#8A6B18"), QColor("#E0D3A8"))},
    dot_size=2.0,
    dot_step=4,
)

# Đầm lầy: bộ da duy nhất có nền là một *màu* chứ không phải sắc trung tính.
# Năm bộ kia đều gần đen hoặc gần trắng; bộ này xanh rêu đậm, mực vàng lưu
# huỳnh và tím nọc — cặp màu không xuất hiện ở bất kỳ bộ nào khác.
SWAMP = Skin(
    name="swamp",
    paper=QColor("#0E2A1C"), paper_hi=QColor("#143824"),
    ink=QColor("#EAF3E2"), ink_soft=QColor("#82A38B"),
    red=QColor("#D4E33A"), blue=QColor("#B072FF"), yellow=QColor("#6FE3B4"),
    dot=QColor(190, 255, 200, 16),
    frame=QColor("#3E6B4C"),
    scrim=QColor(6, 18, 12, 226),
    grid=QColor(150, 255, 190, 24),
    ghosts=((QColor("#B072FF"), -7, -7, 70), (QColor("#D4E33A"), 7, 7, 84)),
    accents={"edge": (QColor("#B072FF"), QColor("#231539")),
             "new": (QColor("#D4E33A"), QColor("#2A2E08")),
             "fix": (QColor("#6FE3B4"), QColor("#0D2A22"))},
    dark=True,
)

# Tín hiệu: bộ da duy nhất gần như không có màu. Nền đen trung tính tuyệt đối
# — sáu bộ kia đều ám một sắc (tím, lam, lục, nâu, cát, rêu) — mực trắng sạch
# nhất dàn, và chỗ lệch trục không còn là bản in chồng sai mà là ba kênh cộng
# màu R · G · B của một màn hình bị xé. Đây cũng là bộ duy nhất có ba lớp
# `ghosts` thay vì hai: mực in chỉ có hai bản lệch, còn màn hình thì ba.
SIGNAL = Skin(
    name="signal",
    paper=QColor("#08090B"), paper_hi=QColor("#101217"),
    ink=QColor("#F8FAFC"), ink_soft=QColor("#78808C"),
    red=QColor("#FF2D2D"), blue=QColor("#2D6BFF"), yellow=QColor("#DCE6F5"),
    dot=QColor(210, 226, 255, 13),
    frame=QColor("#39404A"),
    scrim=QColor(2, 2, 3, 232),
    grid=QColor(200, 220, 255, 20),
    ghosts=((QColor("#FF2D2D"), -9, -4, 74), (QColor("#25E06A"), 0, 7, 46),
            (QColor("#2D6BFF"), 9, 4, 80)),
    accents={"edge": (QColor("#2D6BFF"), QColor("#0A1428")),
             "new": (QColor("#FF2D2D"), QColor("#260C0C")),
             "fix": (QColor("#DCE6F5"), QColor("#171A20"))},
    dark=True,
    dot_size=1.0,
    dot_step=4,
)

# Hồ quang: bộ da duy nhất ghép một tờ giấy **sáng loà** với một màn phủ
# **đen kịt**. `dust` cũng sáng, nhưng sáng kiểu cát bụi ấm và màn phủ cũng
# trắng theo; bộ này thì ngược — trang giấy cháy sáng như một cú phóng hồ
# quang giữa đêm, nền sau lưng tối nhất cả dàn. Mực tím và lam điện, chấm
# halftone mịn và dày nhất để mặt giấy trông như đang tích điện.
ARC = Skin(
    name="arc",
    paper=QColor("#E7ECFA"), paper_hi=QColor("#F7F9FF"),
    ink=QColor("#0E1220"), ink_soft=QColor("#59617D"),
    red=QColor("#6D2BD9"), blue=QColor("#1E5BD6"), yellow=QColor("#29A8E0"),
    dot=QColor(70, 96, 200, 24),
    frame=QColor("#2A3350"),
    scrim=QColor(4, 5, 12, 236),
    grid=QColor(150, 190, 255, 26),
    # lệch trục sát và gắt: đây là quầng sáng rung quanh vật, không phải hai
    # bản in trượt khỏi nhau
    ghosts=((QColor("#7B2BE0"), -3, -3, 118), (QColor("#24D8F0"), 3, 3, 104)),
    accents={"edge": (QColor("#1E5BD6"), QColor("#D8E2FA")),
             "new": (QColor("#6D2BD9"), QColor("#E4D8FA")),
             "fix": (QColor("#29A8E0"), QColor("#D6ECFA"))},
    dot_size=0.9,
    dot_step=3,
)

# Sân khấu: nền nhung rượu, mực giấy tờ chương trình, đèn hồng limelight và
# viền vàng kim. Tám bộ kia đều lấy nền trung tính hoặc lạnh; đây là bộ duy
# nhất lấy nền **đỏ**. Và hai lớp mực lệch trục thì trượt xa nhất cả dàn —
# không phải in sai, mà là hai diễn viên đóng thế đứng sau lưng tờ giấy.
STAGE = Skin(
    name="stage",
    paper=QColor("#1B0A12"), paper_hi=QColor("#27101B"),
    ink=QColor("#F7EADB"), ink_soft=QColor("#B08E93"),
    red=QColor("#FF5470"), blue=QColor("#E9B44C"), yellow=QColor("#6FD0E8"),
    dot=QColor(255, 170, 190, 18),
    frame=QColor("#6B3348"),
    scrim=QColor(12, 3, 8, 228),
    grid=QColor(255, 180, 200, 22),
    ghosts=((QColor("#FF5470"), -16, 6, 60), (QColor("#E9B44C"), 16, -6, 56)),
    accents={"edge": (QColor("#E9B44C"), QColor("#2E1A0C")),
             "new": (QColor("#FF5470"), QColor("#33101A")),
             "fix": (QColor("#6FD0E8"), QColor("#0E2630"))},
    dark=True,
    dot_size=1.6,
    dot_step=6,
)

# Tra theo tên để hồ sơ chỉ cần ghi `skin="sky"`.
SKINS = {skin.name: skin
         for skin in (PULP, VOID, SKY, MESH, FORGE, DUST, SWAMP, SIGNAL, ARC,
                      STAGE)}


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
