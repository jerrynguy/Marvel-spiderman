"""
Prowler — Hobie Brown.

Mười chín chân dung trước đều cho người xem đứng ngoài nhìn thẳng vào nhân
vật, không có gì chắn giữa. Bức này dựng một thứ chắn ngang và để nó ở lớp
gần nhất: **cả tờ giấy là một ô cửa kính**, còn hắn thì ở phía bên kia. Nẹp
cửa và hai thanh chia ô vẽ sau cùng, đè lên cả người hắn; một vệt loang
phản sáng vắt chéo mặt kính cũng đè lên nốt. Chỉ hai lớp ấy thôi là mắt
hiểu ngay đang có một tấm kính ở giữa.

Phải là cửa kính vì Hobie Brown làm nghề lau kính thuê. Nên trên mặt kính
có đủ ba dấu vết của một ca làm: mảng bụi mờ ở chỗ chưa lau, một vệt gạt
sạch bong hình vòng cung, và mấy dòng nước chảy dài xuống từ mép vệt ấy.
Bàn tay hắn áp lên kính để lấy thăng bằng cũng để lại một vết.

Chi tiết cuối cùng là chỗ hắn đứng: bệ cửa, bên ngoài, trên cao. Cậu thanh
niên này chế ra bộ vuốt và ống phun ấy để làm sạch cửa sổ cho người khác,
rồi một hôm quyết định dùng chúng để trèo vào. Cả tiểu sử nằm ở phía bên
kia tấm kính — và tấm kính thì hắn tự tay lau.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QLinearGradient, QPainter,
                           QPainterPath, QPen)

from theme import INK, INK_SOFT, PAPER_HI, RED

from .art import Rolls, curve_at, curve_normal, design, marks, ribbon
from .profile import Profile

GLASS = QRectF(9, 11, 82, 100)   # phần kính, tính cả nẹp
MID_X = 50.0                     # thanh chia dọc
MID_Y = 59.0                     # thanh chia ngang
PALM = QPointF(31, 79)           # vết tay, lệch khỏi bàn tay hiện tại


# ═══════════════════════════════════════════════════ mặt kính
def _panes():
    """Vùng kính, đã trừ nẹp và hai thanh chia — nơi mọi vết bẩn được cắt vào."""
    panes = QPainterPath()
    panes.addRect(GLASS.adjusted(3.4, 3.4, -3.4, -3.4))
    return panes


SWIPE = (QPointF(6, 52), QPointF(48, 26), QPointF(94, 44))   # đường gạt


def _swipe():
    """Vệt gạt: một vòng cung rộng, chỗ duy nhất mặt kính đã sạch."""
    return ribbon(SWIPE[0], SWIPE[1], SWIPE[2], 11.0, 8.0)


def _grime(p, panes):
    """Bụi phủ mặt kính, chừa lại đúng chỗ vừa gạt qua.

    Bụi tô rất nhạt. Đậm lên một chút là mặt kính hoá thành bức tường, và
    cái người đứng sau nó biến mất.
    """
    p.save()
    p.setClipPath(panes.subtracted(_swipe()), Qt.ClipOperation.IntersectClip)
    dust = QColor(INK_SOFT)
    dust.setAlpha(26)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(dust)
    p.drawRect(GLASS)

    r = Rolls(78111969)                       # ASM #78, 11/1969
    speck = QColor(INK_SOFT)
    speck.setAlpha(34)
    p.setBrush(speck)
    for _ in range(140):
        p.drawEllipse(QPointF(r(8, 92), r(10, 112)), r(0.4, 1.1), r(0.4, 1.0))
    p.restore()


def _drips(p, panes):
    """Nước chảy xuống từ mép dưới vệt gạt — thứ cho biết vệt ấy vừa mới xong."""
    p.save()
    p.setClipPath(panes, Qt.ClipOperation.IntersectClip)
    p.setBrush(Qt.BrushStyle.NoBrush)
    r = Rolls(19691178)
    p0, p1, p2 = SWIPE
    for _ in range(9):
        # bám đúng mép dưới vệt gạt: lấy điểm trên đường cong rồi đẩy ra theo
        # pháp tuyến. Ước lượng bằng hàm sin thì mấy dòng nước rơi lửng lơ
        # giữa ô kính, không dính vào vệt nào cả.
        t = r(0.08, 0.92)
        c = curve_at(p0, p1, p2, t)
        nx, ny = curve_normal(p0, p1, p2, t)
        half = 11.0 + (8.0 - 11.0) * t
        start = QPointF(c.x() + nx * half * 0.92, c.y() + ny * half * 0.92)
        run = r(6, 18)
        tone = QColor(INK_SOFT)
        tone.setAlpha(int(r(30, 66)))
        p.setPen(QPen(tone, r(0.5, 1.1)))
        drip = QPainterPath(start)
        drip.lineTo(start.x() + r(-1.2, 1.2), start.y() + run)
        p.drawPath(drip)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(tone)
        p.drawEllipse(QPointF(start.x() + r(-1.0, 1.0), start.y() + run),
                      0.7, 1.0)
    p.restore()


def _handprint(p, panes):
    """Vết bàn tay áp lên kính: lòng bàn tay, bốn ngón, một ngón cái tách ra."""
    p.save()
    p.setClipPath(panes, Qt.ClipOperation.IntersectClip)
    smear = QColor(INK_SOFT)
    smear.setAlpha(58)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(smear)
    palm = QPainterPath()
    palm.addEllipse(PALM, 3.8, 4.2)
    p.drawPath(palm)
    for ang, length in ((108, 7.0), (89, 7.8), (70, 7.4), (51, 6.2)):
        a = math.radians(ang)
        finger = ribbon(PALM,
                        QPointF(PALM.x() + math.cos(a) * length * 0.6,
                                PALM.y() - math.sin(a) * length * 0.6),
                        QPointF(PALM.x() + math.cos(a) * length,
                                PALM.y() - math.sin(a) * length), 1.4, 1.0)
        p.drawPath(finger)
    p.drawEllipse(QPointF(PALM.x() - 4.4, PALM.y() + 2.4), 1.7, 1.3)
    p.restore()


def _sheen(p, panes):
    """Vệt phản sáng vắt chéo mặt kính, vẽ đè lên cả người phía sau."""
    p.save()
    p.setClipPath(panes, Qt.ClipOperation.IntersectClip)
    band = QPainterPath()
    band.moveTo(9, 104)
    band.lineTo(44, 11)
    band.lineTo(62, 11)
    band.lineTo(27, 111)
    band.closeSubpath()

    grad = QLinearGradient(QPointF(20, 90), QPointF(56, 30))
    edge = QColor(PAPER_HI)
    edge.setAlpha(0)
    core = QColor(PAPER_HI)
    core.setAlpha(120)
    grad.setColorAt(0.0, edge)
    grad.setColorAt(0.5, core)
    grad.setColorAt(1.0, edge)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(grad)
    p.drawPath(band)
    p.restore()


def _frame(p):
    """Nẹp cửa và hai thanh chia ô — lớp gần người xem nhất, nên vẽ sau cùng."""
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(INK)
    outer = QPainterPath()
    outer.addRect(GLASS)
    inner = QPainterPath()
    inner.addRect(GLASS.adjusted(3.4, 3.4, -3.4, -3.4))
    p.drawPath(outer.subtracted(inner))
    p.drawRect(QRectF(MID_X - 1.6, GLASS.top(), 3.2, GLASS.height()))
    p.drawRect(QRectF(GLASS.left(), MID_Y - 1.6, GLASS.width(), 3.2))

    light = QColor(PAPER_HI)                  # cạnh trên nẹp bắt sáng
    light.setAlpha(90)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(light, 0.9))
    p.drawLine(QPointF(GLASS.left() + 1.2, GLASS.top() + 1.0),
               QPointF(GLASS.right() - 1.2, GLASS.top() + 1.0))
    p.drawLine(QPointF(MID_X - 0.6, GLASS.top() + 3.4),
               QPointF(MID_X - 0.6, GLASS.bottom() - 3.4))


# ═══════════════════════════════════════════════════ người ở phía bên kia
def _figure():
    """Ngồi xổm trên bệ cửa, một tay áp kính, một tay giơ vuốt lên."""
    head = QPainterPath()                     # mũ trùm: đỉnh tròn, gáy vát ra sau
    head.moveTo(57.4, 40)
    head.cubicTo(57.4, 30, 71.4, 29, 71.6, 39)
    head.cubicTo(72.6, 44, 70, 48, 66, 49)
    head.lineTo(60, 48)
    head.cubicTo(58, 45.4, 57.2, 42.6, 57.4, 40)
    head.closeSubpath()

    torso = QPainterPath()
    torso.moveTo(57, 50)
    torso.cubicTo(52, 56, 51, 66, 54, 76)
    torso.cubicTo(58, 86, 66, 90, 74, 88)
    torso.cubicTo(80, 84, 80, 68, 76, 56)
    torso.cubicTo(72, 50, 62, 48, 57, 50)
    torso.closeSubpath()

    thigh = ribbon(QPointF(63, 84), QPointF(55, 90), QPointF(51, 95), 8.0, 6.2)
    shin = ribbon(QPointF(51, 94), QPointF(51, 101), QPointF(55, 105), 6.2, 5.2)
    knee = ribbon(QPointF(75, 84), QPointF(80, 93), QPointF(77, 104), 7.4, 5.6)

    reach = ribbon(QPointF(56, 58), QPointF(46, 66), QPointF(38, 73), 5.0, 3.8)
    hand = QPainterPath()
    hand.addEllipse(QPointF(36.6, 74), 3.6, 3.2)

    claw = ribbon(QPointF(74, 58), QPointF(82, 50), QPointF(84, 40), 5.2, 4.0)
    fist = QPainterPath()
    fist.addEllipse(QPointF(84.5, 38.5), 3.8, 3.4)

    figure = head.united(torso).united(thigh).united(shin).united(knee)
    return figure.united(reach).united(hand).united(claw).united(fist)


def _cape():
    """Áo choàng hắt ngược lên sau lưng — mảng lớn duy nhất còn động đậy."""
    cape = QPainterPath()
    cape.moveTo(69, 47)
    cape.cubicTo(84, 44, 94, 54, 95, 70)
    cape.cubicTo(96, 84, 91, 96, 84, 103)
    cape.cubicTo(85, 88, 82, 72, 75, 60)
    cape.closeSubpath()
    return cape


def _limbs(p, figure):
    """Nét chia tay, chân và áo choàng.

    Hợp hết vào một bóng thì cả người thành một cục mực; mấy đường này vẽ đè
    lên để trả lại chỗ nối, cắt theo bóng người nên không tràn ra kính.
    """
    p.save()
    p.setClipPath(figure, Qt.ClipOperation.IntersectClip)
    seam = QColor(PAPER_HI)
    seam.setAlpha(96)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(seam, 1.2))
    for a, b, c in (((57, 55), (52, 62), (45, 68)),      # rìa trên tay với
                    ((60, 82), (56, 87), (52, 92)),      # mép đùi gần
                    ((72, 82), (76, 88), (76, 96)),      # mép đùi xa
                    ((74, 56), (79, 50), (82, 44))):     # rìa trong tay giơ
        line = QPainterPath()
        line.moveTo(*a)
        line.quadTo(QPointF(*b), QPointF(*c))
        p.drawPath(line)

    belt = QPainterPath()                     # thắt lưng, mốc chia thân với chân
    belt.moveTo(53, 78)
    belt.cubicTo(60, 83, 70, 83, 78, 77)
    p.drawPath(belt)
    p.restore()


def _talons(p):
    """Ba cái vuốt trên găng: đồ nghề lau kính, đem dùng vào việc khác."""
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(INK, 1.5))
    for ang in (58, 76, 96):
        a = math.radians(ang)
        tip = QPointF(84.5 + math.cos(a) * 8.6, 38.5 - math.sin(a) * 8.6)
        claw = QPainterPath(QPointF(84.5, 38.5))
        claw.quadTo(QPointF(84.5 + math.cos(a) * 5.6 + 1.6,
                            38.5 - math.sin(a) * 5.6), tip)
        p.drawPath(claw)


def _mask(p):
    """Hai mắt kính hẹp trên mũ trùm.

    Đã thử hai lối hỏng trước khi tới đây: một dải sáng vắt ngang cả mặt thì
    đọc ra cái miệng đang cười, còn hai vòng tròn có con ngươi thì ra mắt
    nhân vật hoạt hình. Thêm một nét cong dưới hai mắt nữa là thành mặt cười
    hẳn. Hai vệt hẹp, xếch, và không có gì bên dưới — thế là đủ.
    """
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(PAPER_HI))
    for cx, cy, ang in ((61.6, 39.6, -16), (67.6, 38.4, -12)):
        p.save()
        p.translate(cx, cy)
        p.rotate(ang)
        lens = QPainterPath()
        lens.moveTo(-2.6, 0)
        lens.quadTo(0, -1.9, 2.6, -0.2)
        lens.quadTo(0, 1.3, -2.6, 0)
        lens.closeSubpath()
        p.drawPath(lens)
        p.restore()


def _sill(p):
    """Bệ cửa ngoài: cái vạch cho biết hắn đang đứng trên một mỏm rộng hai gang."""
    ledge = QColor(INK)
    ledge.setAlpha(150)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(ledge)
    p.drawRect(QRectF(12, 104, 76, 4.4))


# ═══════════════════════════════════════════════════ dựng cả bức
def _paint(p, rect):
    with design(p, rect):
        panes = _panes()

        p.save()                              # mọi thứ bên kia kính, cắt trong ô
        p.setClipPath(panes, Qt.ClipOperation.IntersectClip)
        _sill(p)
        p.setPen(Qt.PenStyle.NoPen)
        cape = QColor(INK)
        cape.setAlpha(210)
        p.setBrush(cape)
        p.drawPath(_cape())
        p.setBrush(INK)
        figure = _figure()
        p.drawPath(figure)
        _limbs(p, figure)
        _talons(p)
        _mask(p)
        p.restore()

        _grime(p, panes)
        _drips(p, panes)
        _handprint(p, panes)
        _sheen(p, panes)
        _frame(p)

        tag = QColor(RED)                     # cái nhãn dán góc kính, đỏ một chấm
        tag.setAlpha(110)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(tag)
        p.drawRect(QRectF(15.0, 101, 4.6, 3.2))

        marks(p)


_STILL = {}


def draw_prowler(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước.

    Bụi, nước chảy, vết tay, vệt phản sáng: bốn lớp đều phải cắt theo ô kính.
    Dựng sẵn vào ảnh đúng cỡ điểm ảnh thật rồi dán, như `electro.py`.
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
    name="Prowler",
    vi_name="Kẻ Rình Mò",
    real_name="Hobie Brown",

    tagline="Một cậu kỹ sư giỏi phải đi lau kính thuê. Bộ đồ nghề hắn tự chế "
            "để làm cho xong việc ấy chính là thứ biến hắn thành ác nhân.",

    summary=(
        "Hobie Brown là thanh niên da đen, đầu óc phát minh, và đang lau kính "
        "cho những toà nhà cao tầng ở New York để nuôi mình và bạn gái. Việc "
        "thì nặng, lương thì thấp, và cấp trên coi thường hắn ra mặt. Để đỡ "
        "cực, hắn tự chế đồ nghề: bộ vuốt bám tường và mấy ống phun gắn ở "
        "găng tay. Cả hai đều là dụng cụ lau kính.",

        "Rồi hắn nhận ra đám đồ nghề ấy dùng vào việc khác thì tốt hơn nhiều. "
        "The Amazing Spider-Man #78 (11/1969) của Stan Lee và John Buscema "
        "cho ra đời Prowler: bộ đồ tự may, đôi găng phun và bám, và một cậu "
        "thanh niên trèo vào cửa sổ những căn hộ mà hôm trước cậu ta còn lau "
        "kính bên ngoài.",

        "Đây là hồ sơ hiếm hoi mà cái kết không phải nhà tù. Spider-Man bắt "
        "được hắn, nghe hắn nói, và nhận ra hai người giống nhau đến mức khó "
        "chịu: cùng trẻ, cùng túng, cùng thông minh hơn chỗ đứng của mình. "
        "Peter thả hắn đi kèm một lời khuyên, và Hobie nghe theo thật. Từ đó "
        "Prowler đứng về phía Spider-Man nhiều hơn là đứng đối diện — và "
        "trong ASM #87, hắn là người đầu tiên ngoài Peter Parker mặc bộ đồ "
        "Người Nhện, để gỡ tiếng oan cho chính Peter.",

        "Ba mươi năm sau, Brian Bendis lấy nhân vật này chẻ ra làm ba khi "
        "dựng thế giới của Miles Morales: người cha đã hoàn lương, ông chú "
        "Aaron Davis không hoàn lương và vẫn mang tên Prowler, và một đứa "
        "trẻ mặc bộ đồ Người Nhện. Cả ba mảnh ấy vốn nằm trong đúng một "
        "người: cậu lau kính ở số báo 78.",
    ),

    powers=(
        "Không có siêu năng lực nào — toàn bộ là đồ nghề hắn tự chế",
        "Vuốt thép ở găng và ủng: bám tường, phá khoá, cắt kính",
        "Ống phun nén khí bắn hơi cay, khí mê và đạn thép cỡ nhỏ",
        "Áo choàng căng gió cho hắn lượn giữa các toà nhà, không phải bay",
        "Thuộc mặt ngoài những toà nhà mà người khác chỉ biết mặt trong",
        "Đầu óc kỹ sư — mọi lần thua đều dẫn tới một bản nâng cấp",
    ),

    facts=(
        ("Tên thật", "Hobie Brown"),
        ("Xuất hiện đầu", "ASM #78  ·  11/1969"),
        ("Tác giả", "Stan Lee & John Buscema"),
        ("Nghề cũ", "Lau kính nhà cao tầng"),
        ("Cột mốc", "ASM #87 — mặc đồ Người Nhện"),
        ("Về sau", "Đồng minh; Aaron Davis mượn tên"),
    ),

    blurb="Chín mươi cái tên còn lại trong danh sách này đi tới cùng con "
          "đường đã chọn. Hobie Brown quay lại được, vì có đúng một người "
          "chịu nghe hết câu chuyện của cậu ta trước khi gọi cảnh sát.",

    art=draw_prowler,
    caption="Nhìn qua ô kính hắn vừa lau  ·  dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Prowler_(Marvel_Comics)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Hobart_Brown_(Earth-616)"),
    ),
)
