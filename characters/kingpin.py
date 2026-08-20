"""
Kingpin — Wilson Fisk.

Mười tám chân dung trước đều vẽ đúng một thứ: nhân vật. Cái này vẽ hai thứ
chồng lên nhau trong cùng một đường bao, và cả hai đều đúng — **một người
mặc vest trắng, và một toà cao ốc**. Hai bờ vai chính là tầng giật cấp trên
cùng; hàng khuy áo là một cột cửa sổ; mấy dãy ô sáng chạy ngang thân vừa là
cửa sổ đêm vừa là sọc của bộ vest; cây gậy chống dựng bên sườn cũng là cái
cột thu lôi. Mắt đọc ra cái nào trước là tuỳ, và đó là chủ ý.

Vì Wilson Fisk là kẻ duy nhất trong danh sách này không mặc đồ hoá trang.
Mười tám người kia đánh nhau bằng càng máy, bằng sét, bằng đuôi bọ cạp; hắn
đánh nhau bằng giấy tờ, bằng tiền, và bằng người khác. Vẽ hắn thành một bóng
người đứng trên nền giấy là vẽ hụt: thứ hắn thật sự sở hữu không nằm trong
bộ đồ mà nằm ở cái thành phố dưới chân.

Nên bức này còn có hai chi tiết nữa. Dưới đáy là đường chân trời của những
toà nhà khác, thấp hơn hẳn và tô mực đen — hắn là cái duy nhất sáng. Và ở
mép dưới có ba cái bóng người bé xíu: chúng đứng đó để ta biết cái khối kia
cao bao nhiêu, và để nhớ rằng Kingpin chưa bao giờ tự tay làm gì.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QPainter, QPainterPath, QPen)

from theme import INK, INK_SOFT, PAPER_HI, YELLOW

from .art import H, W, Rolls, design, marks
from .profile import Profile

TIERS = ((40.0, 56.0, 30.0, 70.0),        # (đỉnh, đáy, mép trái, mép phải)
         (56.0, 82.0, 24.0, 76.0),
         (82.0, 122.0, 18.0, 82.0))
LIT = QColor(YELLOW)                      # ô cửa còn sáng đèn


# ═══════════════════════════════════════════════════ cái khối
def _tower():
    """Thân người, cũng là toà nhà: ba tầng giật cấp, vai là tầng trên cùng."""
    tower = QPainterPath()
    tower.moveTo(30, 40)
    for _, bottom, left, right in TIERS:
        tower.lineTo(right, tower.currentPosition().y())
        tower.lineTo(right, bottom)
    tower.lineTo(18, 122)
    for top, _, left, right in reversed(TIERS):
        tower.lineTo(left, tower.currentPosition().y())
        tower.lineTo(left, top)
    tower.closeSubpath()
    return tower


def _head():
    """Đầu hói, hàm bạnh, cổ dày — khối duy nhất trong bức không vuông góc."""
    head = QPainterPath()
    head.moveTo(38, 26)
    head.cubicTo(38, 14, 62, 14, 62, 26)      # vòm sọ
    head.cubicTo(62, 34, 59, 40, 55, 42)      # thái dương xuống góc hàm
    head.lineTo(45, 42)
    head.cubicTo(41, 40, 38, 34, 38, 26)
    head.closeSubpath()
    neck = QPainterPath()
    neck.addRect(QRectF(44, 38, 12, 6))
    for side in (-1, 1):                      # hai vành tai nhỏ, ép sát sọ:
        ear = QPainterPath()                  # thiếu chúng thì đầu ra mặt nạ
        ear.addEllipse(QPointF(50 + side * 12.4, 28.5), 1.9, 3.0)
        head = head.united(ear)
    return head.united(neck)


def _cane():
    """Gậy chống dựng bên sườn phải — cũng là cái cột trên nóc một toà nhà."""
    cane = QPainterPath()
    cane.addRect(QRectF(83.4, 56, 2.0, 64))
    knob = QPainterPath()
    knob.addEllipse(QPointF(84.4, 54.8), 2.0, 2.0)
    return cane.united(knob)


def _hand():
    """Bàn tay nắm đầu gậy: mảng đen duy nhất nhô ra khỏi cạnh phải khối."""
    hand = QPainterPath()
    hand.addRoundedRect(QRectF(77.5, 60.0, 8.0, 6.4), 2.2, 2.2)
    return hand


# ═══════════════════════════════════════════════════ thành phố quanh hắn
def _skyline(p):
    """Những toà nhà khác: thấp hơn hẳn, tô mực đen, chạy ngang đáy khung."""
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(INK)
    for x, w, top in ((-4, 14, 96), (10, 10, 88), (74, 12, 92),
                      (86, 12, 84), (96, 10, 98)):
        p.drawRect(QRectF(x, top, w, 122 - top))

    lit = QColor(LIT)                         # vài ô đèn còn sáng bên kia đường
    lit.setAlpha(190)
    p.setBrush(lit)
    r = Rolls(50071967)                       # ASM #50, 07/1967
    for _ in range(16):
        x, y = r(-2, 100), r(88, 116)
        if 16 < x < 84:
            continue
        p.drawRect(QRectF(x, y, 1.6, 1.2))


def _bystanders(p):
    """Ba cái bóng người bé xíu ở mép dưới: thước đo chiều cao của cái khối."""
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(INK)
    for cx, h in ((28, 6.0), (46, 5.4), (63, 6.4)):
        body = QPainterPath()
        body.addRoundedRect(QRectF(cx - h * 0.22, 122 - h, h * 0.44, h),
                            h * 0.2, h * 0.2)
        head = QPainterPath()
        head.addEllipse(QPointF(cx, 122 - h - h * 0.16), h * 0.17, h * 0.17)
        p.drawPath(body.united(head))


# ═══════════════════════════════════════════════════ mặt tiền: cửa sổ = sọc vest
def _windows(p, tower):
    """Ô cửa sổ, cũng là hàng sọc trên bộ vest.

    Hàng chạy ngang theo tầng, cột chừa một khoảng giữa để cà vạt và hàng
    khuy đi xuống — chính khoảng chừa ấy giữ cho mặt tiền còn đọc ra một bộ
    vest chứ không thành cái bảng ô ly.
    """
    p.save()
    p.setClipPath(tower, Qt.ClipOperation.IntersectClip)
    p.setPen(Qt.PenStyle.NoPen)
    r = Rolls(19670701)
    for top, bottom, left, right in TIERS:
        y = top + 4.0
        while y < bottom - 2.0:
            x = left + 3.0
            while x < right - 3.4:
                if abs(x + 1.7 - 50) > 5.0:   # chừa cột giữa cho khuy áo
                    if r(0, 1) < 0.17:
                        p.setBrush(LIT)
                    else:
                        p.setBrush(INK)
                    p.drawRect(QRectF(x, y, 3.4, 2.2))
                x += 6.0
            y += 6.0
    p.restore()


def _suit(p, tower):
    """Cổ áo, ve áo và hàng khuy — ba nét kéo cái mặt tiền về phía bộ vest."""
    p.save()
    p.setClipPath(tower, Qt.ClipOperation.IntersectClip)

    collar = QPainterPath()                   # cổ sơ mi trắng, hình chữ V
    collar.moveTo(41, 40)
    collar.lineTo(50, 56)
    collar.lineTo(59, 40)
    collar.lineTo(56, 40)
    collar.lineTo(50, 50)
    collar.lineTo(44, 40)
    collar.closeSubpath()
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(INK)
    p.drawPath(collar)

    tie = QPainterPath()                      # cà vạt: cũng là khe thang máy
    tie.moveTo(47.6, 48)
    tie.lineTo(52.4, 48)
    tie.lineTo(53.4, 76)
    tie.lineTo(50, 82)
    tie.lineTo(46.6, 76)
    tie.closeSubpath()
    p.drawPath(tie)

    p.setBrush(Qt.BrushStyle.NoBrush)         # ve áo, chạy dài xuống như cạnh nhà
    p.setPen(QPen(INK, 2.0))
    for side in (-1, 1):
        lapel = QPainterPath()
        lapel.moveTo(50 + side * 9, 41)
        lapel.lineTo(50 + side * 18, 72)
        p.drawPath(lapel)

    p.setBrush(INK)                           # hàng khuy áo, cột cửa sổ giữa
    p.setPen(Qt.PenStyle.NoPen)
    for y in (88, 98, 108):
        p.drawEllipse(QPointF(50, y), 1.5, 1.5)
    p.restore()


def _face(p):
    """Mắt, mày, mép — ba nét sáng trên khối đầu, không hơn.

    Bản trước có thêm hai nếp nọng vòng từ cánh mũi xuống hàm, cộng một cái
    mép hơi cong. Ba nét ấy chụm lại thành một cái mặt nạ đang cười toe.
    Chỗ này không cần diễn cảm: mép kẻ thẳng đúng một vạch, mày kẻ thẳng và
    chúc vào giữa, thế là ra cái nhìn của người không việc gì phải vội.
    """
    light = QColor(PAPER_HI)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(light)
    for cx in (44.2, 55.8):                   # hai mắt nhỏ, hẹp, đặt sâu
        eye = QPainterPath()
        eye.moveTo(cx - 3.0, 25.8)
        eye.cubicTo(cx - 1.0, 24.4, cx + 1.4, 24.4, cx + 3.0, 25.6)
        eye.cubicTo(cx + 1.2, 27.0, cx - 1.2, 27.0, cx - 3.0, 25.8)
        eye.closeSubpath()
        p.drawPath(eye)

    ridge = QColor(PAPER_HI)
    ridge.setAlpha(120)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(ridge, 1.4))
    for side in (-1, 1):                      # mày thẳng, đầu trong chúc xuống
        line = QPainterPath()
        line.moveTo(50 + side * 8.4, 21.0)
        line.lineTo(50 + side * 2.2, 22.6)
        p.drawPath(line)

    p.setPen(QPen(ridge, 1.6))                # mép: một vạch ngang, hết
    p.drawLine(QPointF(45.0, 34.4), QPointF(55.0, 34.4))


# ═══════════════════════════════════════════════════ dựng cả bức
def _paint(p, rect):
    with design(p, rect):
        _skyline(p)

        tower = _tower()
        p.setBrush(QColor(PAPER_HI))          # bộ vest trắng: mảng sáng duy nhất
        p.setPen(QPen(INK, 1.6))
        p.drawPath(tower)
        _windows(p, tower)
        _suit(p, tower)

        p.setBrush(INK)                       # gậy chống, tay nắm, rồi cái đầu
        p.setPen(QPen(INK, 1.2))
        p.drawPath(_cane())
        p.drawPath(_hand())
        p.setPen(QPen(INK, 1.6))
        p.drawPath(_head())

        knuckle = QColor(PAPER_HI)            # hai khía ngón, cho ra nắm tay
        knuckle.setAlpha(110)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(knuckle, 0.9))
        for x in (79.8, 82.2):
            p.drawLine(QPointF(x, 61.2), QPointF(x, 65.8))

        _face(p)
        _bystanders(p)

        haze = QColor(INK_SOFT)               # sương đèn đường hắt lên chân khối
        haze.setAlpha(40)
        p.setBrush(haze)
        p.drawRect(QRectF(0, 112, 100, 10))

        marks(p)


_STILL = {}


def draw_kingpin(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước.

    Vài trăm ô cửa sổ cộng mấy lớp cắt theo khối: dựng sẵn vào ảnh đúng cỡ
    điểm ảnh thật rồi dán, như `electro.py`.
    """
    scale = p.transform().m11() or 1.0
    key = (round(rect.width(), 1), round(rect.height(), 1), round(scale, 2))
    ready = _STILL.get(key)
    if ready is None:
        if len(_STILL) > 6:
            _STILL.clear()
        ready = QImage(max(1, math.ceil(rect.width() * scale)),
                       max(1, math.ceil(rect.height() * scale)),
                       QImage.Format.Format_ARGB32_Premultiplied)
        ready.fill(Qt.GlobalColor.transparent)
        q = QPainter(ready)
        q.setRenderHint(QPainter.RenderHint.Antialiasing)
        q.scale(scale, scale)
        _paint(q, QRectF(0, 0, rect.width(), rect.height()))
        q.end()
        _STILL[key] = ready
    p.drawImage(rect, ready)


# ═══════════════════════════════════════════════════════════════ hồ sơ
PROFILE = Profile(
    name="Kingpin",
    vi_name="Ông Trùm",
    real_name="Wilson Fisk",

    tagline="Kẻ duy nhất trong danh sách này không mặc đồ hoá trang. Hắn "
            "không cần: thứ hắn có là cả thành phố.",

    summary=(
        "The Amazing Spider-Man #50 (07/1967) là số báo nổi tiếng nhất của cả "
        "thập kỷ, và nổi tiếng vì chuyện khác: Peter Parker bỏ nghề. Bìa của "
        "John Romita Sr. — cậu thanh niên bước đi, bộ đồ Người Nhện vứt trong "
        "thùng rác — là một trong những hình ảnh được chép lại nhiều nhất "
        "lịch sử truyện tranh. Nhưng chính trong số đó, Stan Lee và Romita "
        "cho ra mắt một nhân vật mới, và cái khoảng trống Peter để lại là thứ "
        "hắn bước vào.",

        "Wilson Fisk không có siêu năng lực, không có vũ khí ngoài hành tinh, "
        "và trong hồ sơ cảnh sát thì là một doanh nhân đáng kính. Hắn cao gần "
        "hai mét, nặng hơn hai trăm ký, và gần như toàn bộ chỗ đó là cơ: "
        "phần mỡ thật sự chỉ chừng bốn ký. Hắn đấu vật kiểu sumo thắng cả "
        "những nhà vô địch, và đủ nhanh để hạ một người bình thường trước "
        "khi người ấy kịp nhận ra. Món duy nhất hắn mang theo là cây gậy "
        "chống — bên trong là một chùm tia đủ mạnh để làm bốc hơi khẩu súng "
        "trong tay đối phương.",

        "Nhưng sức mạnh ấy gần như không bao giờ được dùng, và đó mới là "
        "điểm khiến hắn khác cả danh sách. Mọi kẻ khác đích thân đi cướp; "
        "Kingpin thuê người đi cướp, rồi thuê luật sư, rồi mua nốt cảnh sát "
        "và toà. Cách hạ hắn không phải là đấm mạnh hơn, mà là tìm ra một "
        "chữ ký. Hắn có vợ là Vanessa và một người con trai, Richard — và "
        "trong nhiều truyện, gia đình mới là chỗ duy nhất chạm được vào hắn.",

        "Về sau hắn rời khỏi vùng trời của Spider-Man để thành kẻ thù lớn "
        "nhất đời Daredevil, nhất là ở Born Again — mạch truyện hắn không hạ "
        "đối thủ bằng nắm đấm mà tháo dỡ từng mảnh cuộc đời người ấy: nhà "
        "băng, chỗ ở, bạn bè, danh tiếng. Và rồi hắn làm đúng cái việc lẽ ra "
        "phải đoán được từ đầu: ra tranh cử, thắng, và thành thị trưởng New "
        "York. Không phải leo lên nóc toà nhà — mà mua nó.",
    ),

    powers=(
        "Không có siêu năng lực: hơn hai trăm ký, và gần như toàn bộ là cơ",
        "Đấu vật sumo và cận chiến ở trình độ vô địch, nhanh hơn vẻ ngoài rất nhiều",
        "Gậy chống giấu chùm tia ba trăm oát, đủ làm bốc hơi một khẩu súng",
        "Cả một đế chế tội phạm: người làm thuê, luật sư, cảnh sát và quan toà",
        "Vỏ bọc doanh nhân hợp pháp — thứ khiến bắt hắn khó hơn là đánh hắn",
        "Điểm yếu duy nhất là những người hắn thật sự yêu quý",
    ),

    facts=(
        ("Tên thật", "Wilson Fisk"),
        ("Xuất hiện đầu", "ASM #50  ·  07/1967"),
        ("Tác giả", "Stan Lee & John Romita Sr."),
        ("Số báo ấy", "'Spider-Man No More!'"),
        ("Thể hình", "≈2 m, hơn 200 kg, gần hết là cơ"),
        ("Về sau", "Kẻ thù của Daredevil, thị trưởng NY"),
    ),

    blurb="Chín mươi cái tên còn lại trong danh sách này trèo lên nóc các toà "
          "nhà. Wilson Fisk thì mua chúng, rồi mua luôn cái thành phố có "
          "chúng trong đó.",

    art=draw_kingpin,
    caption="Người, cũng là toà nhà  ·  dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Kingpin_(character)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Wilson_Fisk_(Earth-616)"),
    ),
)
