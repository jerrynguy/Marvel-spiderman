"""
Absolute Mysterio — Quentin Beck, và cả thế giới là sân khấu của hắn.

Bản sắc riêng, khác cả tám dạng Absolute trước:
    · bộ da `stage` — bộ duy nhất lấy nền là **đỏ**: nhung rượu, mực giấy
      chương trình, đèn hồng limelight và viền vàng kim. Hai lớp mực lệch
      trục trượt xa nhất cả dàn, vì đó không phải bản in sai mà là hai diễn
      viên đóng thế đứng sau lưng tờ giấy.
    · `evolve_fx="mirage"` — tờ giấy cũ không bị phá gì hết. Nó nhân thành
      sáu bản y hệt, tráo chỗ cho nhau tới lúc không ai biết cái nào là cái
      thật, rồi lần lượt tắt; cái còn lại **lật mặt** sang tấm mới như lật
      một quân bài. Hướng dựng thứ chín, và là hướng duy nhất không cắt
      xén gì cả mà bóp cả tờ giấy quanh trục dọc.
    · chân dung đi tiếp đúng ý của hồ sơ gốc rồi lật ngược nó. Ở ASM #13,
      quả cầu thuỷ tinh **rỗng** — không có mặt để mà giấu. Ở đây quả cầu
      chứa nguyên một thế giới đang được dàn dựng, còn cái rỗng thì chuyển
      sang thân hắn: đó chỉ là một tấm phông cắt, có nẹp gỗ chống phía sau
      và không có gì đằng sau tấm phông cả.

Ngôn ngữ chuyển động cũng là kiểu chưa ai dùng: **chuyển cảnh**. Tám dạng
kia đều động theo lối vật lý — thở, uốn, trôi, lở, nháy. Hình này thì cứ vài
giây lại *hoà tan* sang một cảnh khác trong quả cầu, và thỉnh thoảng đứng
hình đúng hai khung: cả bức tranh rơi mất lớp sơn, trơ ra khung dây.
"""

import math
from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QLinearGradient, QPainter,
                           QPainterPath, QPen, QPolygonF)

from theme import STAGE

from .art import H, W, Rolls, design, glow, marks
from .profile import Profile, Section, Tier

ROSE = STAGE.red                 # đèn hồng limelight
GOLD = STAGE.blue                # viền vàng, đèn chân sân khấu
COLD = STAGE.yellow              # ánh lạnh trong quả cầu
PARCH = STAGE.ink                # mực giấy chương trình
BOARD = QColor("#3A1622")        # mặt trước tấm phông, sơn phẳng
EDGE = QColor("#5C3A22")         # cạnh ván bắt đèn chân — chỗ lộ ra là đồ giả
FLOOR = 100.0                    # mặt sàn sân khấu
DOME = QPointF(50, 31)
DOME_R = 17.5
SCENES = 4
HOLD = 2.4                       # số giây mỗi cảnh trong quả cầu


def _tone(color, alpha):
    out = QColor(color)
    out.setAlpha(max(0, min(255, int(alpha))))
    return out


# ═══════════════════════════════════════════════════════════════ hình khối
@lru_cache(maxsize=1)
def _collar():
    """Cổ áo dựng cao sau gáy — dấu hiệu nhận ra Beck ngang với quả cầu.

    Phải là một mảng riêng vẽ đè lên áo choàng chứ không hợp chung: hợp vào
    thì mất đường nối, và cả người rút lại thành một cái chụp đèn.
    """
    collar = QPainterPath()
    collar.moveTo(31, 52)
    collar.cubicTo(24, 36, 30, 20, 39, 14)
    collar.lineTo(45, 22)
    collar.lineTo(55, 22)
    collar.lineTo(61, 14)
    collar.cubicTo(70, 20, 76, 36, 69, 52)
    collar.closeSubpath()
    return collar


@lru_cache(maxsize=1)
def _flat():
    """Tấm phông cắt: áo choàng xoè từ vai xuống sàn, và cái đầu tròn."""
    cape = QPainterPath()
    cape.moveTo(36, 44)
    cape.lineTo(64, 44)
    cape.cubicTo(74, 62, 79, 82, 81, FLOOR)
    cape.lineTo(19, FLOOR)
    cape.cubicTo(21, 82, 26, 62, 36, 44)
    cape.closeSubpath()

    head = QPainterPath()
    head.addEllipse(DOME, DOME_R, DOME_R)
    return cape.united(_collar()).united(head)


@lru_cache(maxsize=1)
def _side():
    """Cạnh bên của tấm phông — bề dày một tấm ván, nhìn hơi chếch.

    Đây là chi tiết cả bức tranh xoay quanh: có cạnh nghĩa là có mặt sau, mà
    mặt sau thì rỗng.
    """
    side = QPainterPath()
    side.moveTo(64, 44)
    side.cubicTo(74, 62, 79, 82, 81, FLOOR)
    side.lineTo(85, FLOOR)
    side.cubicTo(83, 81, 78, 61, 67, 43)
    side.closeSubpath()
    return side


def _dome_clip():
    path = QPainterPath()
    path.addEllipse(DOME, DOME_R - 1.2, DOME_R - 1.2)
    return path


_DOME_CLIP = _dome_clip()


# ═══════════════════════════════════════════════════ cảnh diễn trong quả cầu
def _skyline(p, seed, tint, height=1.0):
    """Đường chân trời thành phố — cùng một dãy nhà cho cả bốn cảnh."""
    r = Rolls(seed)
    p.setPen(Qt.PenStyle.NoPen)
    x = DOME.x() - DOME_R
    while x < DOME.x() + DOME_R:
        w = r(2.2, 5.0)
        h = r(3, 11) * height
        p.setBrush(_tone(tint, r(150, 230)))
        p.drawRect(QRectF(x, DOME.y() + 8 - h, w, h + 8))
        x += w + r(0.5, 1.6)


def _scene(p, index, t):
    """Một cảnh trong quả cầu. Bốn cảnh, và cảnh nào cũng là đồ dàn dựng."""
    if index == 0:                                    # thành phố lúc chạng vạng
        sky = QLinearGradient(0, DOME.y() - 16, 0, DOME.y() + 14)
        sky.setColorAt(0.0, QColor("#2A1030"))
        sky.setColorAt(1.0, QColor("#7A2E44"))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(sky)
        p.drawRect(QRectF(30, 10, 40, 40))
        p.setBrush(_tone(GOLD, 220))
        p.drawEllipse(QPointF(58, DOME.y() - 3), 4.2, 4.2)
        _skyline(p, 1361964, QColor("#1B0A12"))

    elif index == 1:                                  # cũng thành phố ấy, cháy
        sky = QLinearGradient(0, DOME.y() - 16, 0, DOME.y() + 14)
        sky.setColorAt(0.0, QColor("#3A0A18"))
        sky.setColorAt(1.0, QColor("#C4453E"))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(sky)
        p.drawRect(QRectF(30, 10, 40, 40))
        r = Rolls(int(t * 6) + 77)
        for _ in range(9):                            # lưỡi lửa liếm lên
            x = r(34, 66)
            h = r(4, 11)
            flame = QPolygonF([QPointF(x - 1.6, DOME.y() + 8),
                               QPointF(x, DOME.y() + 8 - h),
                               QPointF(x + 1.6, DOME.y() + 8)])
            p.setBrush(_tone(GOLD, r(120, 220)))
            p.drawPolygon(flame)
        _skyline(p, 1361964, QColor("#170810"))

    elif index == 2:                                  # hạm đội ngoài hành tinh
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#0E1826"))
        p.drawRect(QRectF(30, 10, 40, 40))
        _skyline(p, 1361964, QColor("#050A10"))
        for k, (x, y, w) in enumerate(((40, 22, 7), (54, 18, 9), (62, 26, 6))):
            bob = math.sin(t * 1.3 + k * 2.0) * 0.8
            p.setBrush(_tone(COLD, 60))                # chùm sáng chiếu xuống
            p.drawPolygon(QPolygonF([
                QPointF(x - w * 0.4, y + bob), QPointF(x + w * 0.4, y + bob),
                QPointF(x + w * 1.1, DOME.y() + 9),
                QPointF(x - w * 1.1, DOME.y() + 9)]))
            p.setBrush(_tone(PARCH, 210))
            p.drawEllipse(QPointF(x, y + bob), w * 0.5, w * 0.18)

    else:                                             # quái vật khổng lồ
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#20122E"))
        p.drawRect(QRectF(30, 10, 40, 40))
        beast = QPainterPath()
        beast.moveTo(38, DOME.y() + 9)
        beast.cubicTo(40, 24, 46, 16, 50, 15)
        beast.cubicTo(56, 15, 60, 22, 62, DOME.y() + 9)
        beast.closeSubpath()
        p.setBrush(QColor("#0A0410"))
        p.drawPath(beast)
        p.setBrush(_tone(ROSE, 230))                   # hai con mắt
        for sign in (-1, 1):
            p.drawEllipse(QPointF(50 + sign * 2.6, 21), 0.9, 1.2)
        _skyline(p, 1361964, QColor("#060310"), height=0.55)


def _production(p, t):
    """Quả cầu: cảnh này hoà tan sang cảnh kia, không cắt phựt.

    Đây là chỗ duy nhất trong cả bộ có chuyển cảnh kiểu phim — bảy chân dung
    động kia đều động bằng chuyển động vật lý.
    """
    p.save()
    p.setClipPath(_DOME_CLIP)
    p.setBrush(QColor("#0B0410"))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(QRectF(30, 10, 40, 44))

    step = t / HOLD
    index = int(step) % SCENES
    frac = step - int(step)
    _scene(p, index, t)
    if frac > 0.78:                       # hoà tan sang cảnh kế
        p.setOpacity((frac - 0.78) / 0.22)
        _scene(p, (index + 1) % SCENES, t)
        p.setOpacity(1.0)

    # sương của Beck, vẫn còn đó nhưng nay nằm dưới chân cái thế giới của hắn
    r = Rolls(1361964)
    for k in range(7):
        drift = (t * 0.06 + r(0, 1)) % 1.0
        x = 30 + drift * 40
        y = DOME.y() + 8 + r(-2, 5)
        p.setBrush(_tone(PARCH, 26))
        p.drawEllipse(QPointF(x, y), r(5, 11), r(2, 4))
    p.restore()

    # mặt kính: vành sáng, hai vệt phản chiếu, và một vòng viền vàng
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(GOLD, 210), 1.3))
    p.drawEllipse(DOME, DOME_R, DOME_R)
    p.setPen(QPen(_tone(PARCH, 120), 1.6))
    p.drawArc(QRectF(DOME.x() - DOME_R + 2.5, DOME.y() - DOME_R + 2.5,
                     (DOME_R - 2.5) * 2, (DOME_R - 2.5) * 2), 108 * 16, 54 * 16)
    p.setPen(QPen(_tone(PARCH, 70), 1.0))
    p.drawArc(QRectF(DOME.x() - DOME_R + 5, DOME.y() - DOME_R + 5,
                     (DOME_R - 5) * 2, (DOME_R - 5) * 2), 96 * 16, 30 * 16)


# ═══════════════════════════════════════════════════════════ lớp dựng sẵn
def _stage(p):
    """Sàn diễn, đèn chân, nẹp chống, tấm phông — những lớp không đổi.

    Thứ tự vẽ chính là câu chuyện: chùm đèn hắt lên **trước**, rồi mới tới
    tấm phông đè lên. Vẽ ngược lại thì chùm sáng phủ lên mặt phông và cả
    người hoá ra trong suốt.
    """
    p.setPen(Qt.PenStyle.NoPen)
    dark = QLinearGradient(0, -6, 0, 126)
    dark.setColorAt(0.0, QColor("#0B0308"))
    dark.setColorAt(0.55, QColor("#1B0A12"))
    dark.setColorAt(1.0, QColor("#2A0F18"))
    p.setBrush(dark)
    p.drawRect(QRectF(-6, -6, 112, 132))

    # sàn: ván chạy về phía người xem
    p.setBrush(QColor("#210C15"))
    p.drawRect(QRectF(-6, FLOOR, 112, 132 - FLOOR))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(GOLD, 40), 0.5))
    for k in range(9):
        x = -6 + k * 14
        p.drawLine(QPointF(x, FLOOR), QPointF(x - 14, 126))
    p.setPen(QPen(_tone(GOLD, 90), 0.8))
    p.drawLine(QPointF(-6, FLOOR), QPointF(106, FLOOR))

    # chùm đèn chân hắt ngược lên, nằm sau tấm phông
    p.setPen(Qt.PenStyle.NoPen)
    for k in range(5):
        x = 14 + k * 18
        cone = QLinearGradient(0, 112, 0, 46)
        cone.setColorAt(0.0, _tone(GOLD, 64))
        cone.setColorAt(1.0, _tone(GOLD, 0))
        p.setBrush(cone)
        p.drawPolygon(QPolygonF([QPointF(x - 2, 112), QPointF(x + 2, 112),
                                 QPointF(x + 15, 46), QPointF(x - 15, 46)]))

    # hai nẹp gỗ chống sau lưng, thò hẳn ra ngoài mép phông
    for (x0, y0, x1, y1) in ((78, 98, 96, 62), (74, 100, 88, 56)):
        p.setBrush(QColor("#6A4A2A"))
        p.drawPolygon(QPolygonF([QPointF(x0, y0), QPointF(x0 + 2.4, y0),
                                 QPointF(x1 + 1.8, y1), QPointF(x1, y1)]))

    # bóng đổ của tấm phông trên sàn
    p.setBrush(_tone(QColor("#050106"), 190))
    p.drawEllipse(QPointF(50, FLOOR + 2.2), 36, 3.2)

    # cạnh bên bắt đèn chân rồi mới tới mặt trước — có thế mới ra bề dày ván
    p.setBrush(EDGE)
    p.drawPath(_side())
    p.setBrush(BOARD)
    p.drawPath(_flat())

    # nét sơn giả nếp áo: vẽ trên ván chứ không phải nếp vải thật
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(QColor("#5A2436"), 220), 1.0))
    for x0, x1 in ((42, 27), (48, 42), (53, 60), (58, 73)):
        fold = QPainterPath(QPointF(x0, 50))
        fold.cubicTo(QPointF(x0 + (x1 - x0) * 0.4, 70),
                     QPointF(x1, 84), QPointF(x1, FLOOR - 1))
        p.drawPath(fold)

    # mép dưới bắt đèn chân
    hem = QLinearGradient(0, FLOOR - 22, 0, FLOOR)
    hem.setColorAt(0.0, _tone(GOLD, 0))
    hem.setColorAt(1.0, _tone(GOLD, 60))
    p.save()
    p.setClipPath(_flat())
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(hem)
    p.drawRect(QRectF(14, FLOOR - 22, 72, 22))
    p.restore()

    # cổ áo dựng: mảng riêng, tông sáng hơn, viền vàng — không hợp vào áo
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#4A1C2C"))
    p.drawPath(_collar())
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(GOLD, 190), 1.0))
    p.drawPath(_collar())
    p.setPen(QPen(_tone(GOLD, 150), 0.9))
    p.drawPath(_flat())


_STILL = {}


def _still(scale):
    key = round(scale, 2)
    ready = _STILL.get(key)
    if ready is None:
        if len(_STILL) > 6:
            _STILL.clear()
        ready = QImage(max(1, math.ceil(112 * scale)),
                       max(1, math.ceil(132 * scale)),
                       QImage.Format.Format_ARGB32_Premultiplied)
        ready.fill(Qt.GlobalColor.transparent)
        q = QPainter(ready)
        q.setRenderHint(QPainter.RenderHint.Antialiasing)
        q.scale(scale, scale)
        q.translate(6, 6)
        _stage(q)
        q.end()
        _STILL[key] = ready
    return ready


# ═══════════════════════════════════════════════════════════ lớp tự chạy
def _lamps(p, t):
    """Đèn chân: bóng đèn thật thì nhấp nháy, không sáng đều như ảnh dựng sẵn."""
    p.setPen(Qt.PenStyle.NoPen)
    for k in range(5):
        x = 14 + k * 18
        beat = 0.72 + 0.28 * math.sin(t * (3.1 + k * 0.7) + k)
        glow(p, QPointF(x, 111), 6.5 * beat, _tone(GOLD, 120))
        p.setBrush(_tone(PARCH, 200 + beat * 55))
        p.drawEllipse(QPointF(x, 111), 1.7, 1.2)


def _haze(p, t):
    """Sương sân khấu bò dưới chân tấm phông, trôi ngang rất chậm."""
    r = Rolls(1361965)
    p.setPen(Qt.PenStyle.NoPen)
    for k in range(9):
        speed = r(0.02, 0.06)
        x = ((t * speed + r(0, 1)) % 1.2 - 0.1) * 112 - 6
        y = 88 + r(0, 14)
        p.setBrush(_tone(ROSE if k % 4 == 0 else PARCH, r(10, 26)))
        p.drawEllipse(QPointF(x, y), r(12, 26), r(3, 7))


def _wire(p):
    """Hai khung hình trơ khung dây: lớp sơn rơi mất, lộ ra đồ dựng.

    Không phải hiệu ứng trang trí — đây là câu của cả bức chân dung. Cứ vài
    giây, cái đang nhìn lại tự khai ra nó là đồ giả, rồi lập tức khoác lại
    lớp sơn như chưa có gì.
    """
    p.setBrush(_tone(QColor("#07020A"), 232))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(QRectF(-6, -6, 112, 132))

    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(COLD, 200), 0.7))
    p.drawPath(_flat())
    p.drawPath(_side())
    p.drawEllipse(DOME, DOME_R, DOME_R)
    p.setPen(QPen(_tone(COLD, 90), 0.4))
    for x in range(0, 101, 10):          # lưới dựng hình
        p.drawLine(QPointF(x, -6), QPointF(x, 126))
    for y in range(0, 121, 10):
        p.drawLine(QPointF(-6, y), QPointF(106, y))
    p.setPen(QPen(_tone(ROSE, 190), 0.6))
    p.drawLine(QPointF(-6, FLOOR), QPointF(106, FLOOR))


def draw_absolute_mysterio(p, rect, t=0.0):
    """Chân dung sống: nhận thêm `t` (giây) nên khung hồ sơ tự vẽ lại."""
    dpr = p.device().devicePixelRatio() if p.device() else 1.0
    grow = (p.transform().m11() or 1.0) * (dpr or 1.0)
    scale = min(rect.width() / W, rect.height() / H) * grow
    still = _still(scale)

    with design(p, rect):
        p.drawImage(QRectF(-6, -6, still.width() / scale,
                           still.height() / scale), still)
        _lamps(p, t)
        _production(p, t)
        _haze(p, t)

        # cứ 3,4 giây thì lộ đúng hai khung hình
        if (t % 3.4) < 0.08:
            _wire(p)

        marks(p, STAGE.ink_soft)


# ═══════════════════════════════════════════════════════════════ hồ sơ
ABSOLUTE = Profile(
    name="Absolute Mysterio",
    vi_name="Ảo Thuật Gia Tuyệt Đối",
    real_name="Quentin Beck  ·  đạo diễn duy nhất",
    keys=("Mysterio Absolute",),

    kicker="Hồ sơ tuyệt đối",
    stamp="PHÂN LOẠI  ·  SỤP ĐỔ NHẬN THỨC TOÀN CẦU",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="stage",
    evolve_fx="mirage",      # giấy không bị phá, chỉ hoá ra chưa từng có thật

    tagline="Không phá huỷ hành tinh. Chỉ phá huỷ khả năng phân biệt thật giả "
            "của toàn bộ loài người, rồi ngồi xem họ tự làm nốt phần còn lại.",

    summary=(
        "Beck bản gốc không có siêu năng lực nào cả: một chuyên gia hiệu ứng "
        "đặc biệt, một tay đóng thế, một nhà thôi miên. Toàn bộ sức mạnh nằm "
        "ở hologram, khí gây ảo giác và tài dàn dựng. Nên điểm yếu cũng nằm "
        "đúng ở đó — vạch trần được màn kịch thì hắn chỉ còn là một người "
        "thường trong bộ đồ lố lăng.",

        "Bản Absolute không cho hắn thêm cơ bắp. Nó cho hắn một bộ não: vỏ "
        "não Đạo diễn, một mạng xử lý sinh học cấy thẳng vào hệ thần kinh, "
        "cho phép hắn cầm nhịp hàng triệu thông số ảo giác cùng lúc mà không "
        "cần một cái máy tính ngoài nào. Kèm theo là mắt nhìn được hồng "
        "ngoại tới terahertz và tai nghe từ hạ âm tới siêu âm — nghĩa là "
        "hắn nhìn xuyên được ảo giác của chính mình, thứ mà bản gốc nhiều "
        "lần suýt chết vì không làm được.",

        "Sân khấu thì phóng ra cỡ hành tinh: một chòm vệ tinh ion hoá tầng "
        "cao khí quyển để chiếu hình lên bầu trời nhiều châu lục, và hàng tỷ "
        "hạt bụi ảo ảnh mang máy chiếu tí hon lơ lửng hàng tuần trên một "
        "thành phố. Không một món nào trong đó có AI tự chủ. Chúng là con "
        "rối, và hắn là người duy nhất giật dây — đúng cái tôi của một kẻ "
        "cả đời chỉ muốn được công nhận là tác giả.",

        "Vì thế bậc cao nhất của hồ sơ này không có một quả bom nào. Loài "
        "người bấm nút, loài người bắn nhau, loài người tự cắt lấy chuỗi "
        "cung ứng của mình — tất cả vì những thứ họ nhìn thấy rất rõ mà "
        "không thứ nào có thật.",
    ),

    sections=(
        Section(
            title="Khuyếch đại năng lực vật lý & sinh học",
            intro="Chỗ này cố tình không cho hắn sức mạnh. Beck mà đấm được "
                  "thủng tường thì hỏng nhân vật: mọi nâng cấp ở đây đều để "
                  "phục vụ việc dựng và cầm nhịp ảo giác, chứ không phải để "
                  "thắng một trận đánh tay đôi.",
            items=(
                ("Vỏ não Đạo diễn",
                 "Một mạng xử lý sinh học phân tán cấy vào hệ thần kinh, cho "
                 "hắn cầm nhịp hàng triệu thông số ảo giác cùng lúc mà không "
                 "cần máy tính ngoài. Dữ liệu từ hàng nghìn mắt chiếu và cảm "
                 "biến được gộp lại trong vài mili giây. Đây không phải tăng "
                 "cơ bắp mà tăng năng lực chỉ huy nhận thức — thứ mà chưa "
                 "phản diện nào trong danh sách này có."),
                ("Tuyến ảo giác nội sinh",
                 "Tuyến mồ hôi và nước bọt được sửa để tự tổng hợp một hợp "
                 "chất kích thích thần kinh cực mạnh. Đứng gần hắn trong "
                 "vòng năm mét là bắt đầu rối loạn tri giác, hoang tưởng, sợ "
                 "hãi vô cớ. Lớp phòng thủ này hoàn toàn thụ động: hắn không "
                 "phải làm gì cả, chỉ cần có mặt."),
                ("Giác quan đa phổ",
                 "Mắt sinh học nhìn được hồng ngoại, tử ngoại và terahertz; "
                 "tai trong nghe từ hạ âm 1 Hz tới siêu âm 200 kHz; da cấy "
                 "thụ thể cảm được trường điện từ. Nhờ đó hắn nhìn xuyên "
                 "chính màn kịch của mình, thấy kẻ đang nấp, và không bao "
                 "giờ mắc kẹt trong cái bẫy do mình dựng ra — đúng chỗ bản "
                 "gốc từng trả giá."),
                ("Thể chất nghệ sĩ",
                 "Dây chằng và cơ được gia cố bằng vật liệu sinh học dẻo: "
                 "thăng bằng, mềm và phản xạ né của một nghệ sĩ xiếc hạng "
                 "nhất. Hắn vẫn không đấm mạnh, nhưng luồn được qua làn đạn "
                 "trong lúc tay vẫn đang điều phối cả một màn diễn."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="Nguyên tắc của cả mục này: không có AI tự chủ, không một "
                  "món nào tự quyết. Mysterio là đạo diễn duy nhất, mọi thứ "
                  "còn lại là đạo cụ — vì một kẻ khao khát được công nhận thì "
                  "không bao giờ chịu chia công cho cái máy.",
            items=(
                ("Chòm vệ tinh phân chiếu",
                 "Vệ tinh tàng hình mang máy phát plasma khí quyển và laser "
                 "đa phổ, ion hoá tầng cao để dựng ảnh ba chiều khổng lồ "
                 "trên bầu trời nhiều châu lục cùng lúc: hạm đội ngoài hành "
                 "tinh, ma quỷ, hay một vị thần đang giận. Chúng không có "
                 "AI — chúng nhận xung thần kinh thẳng từ vỏ não Đạo diễn."),
                ("Bụi ảo ảnh tự lắp ráp",
                 "Hàng tỷ hạt siêu nhỏ rải xuống bằng tên lửa hành trình, "
                 "mỗi hạt là một máy chiếu laser tí hon kèm loa, bộ tổng hợp "
                 "mùi và bộ phát vi sóng. Ghép lại, chúng dựng ra những khối "
                 "ảo giác **sờ được** nhờ sóng siêu âm, và lơ lửng nhiều "
                 "tuần liền. Cả một thành phố thành sân khấu riêng, còn "
                 "người trong đó thì không biết mình đang ở trong cảnh nào."),
                ("Động cơ Sợ hãi",
                 "Mạng nhà máy hoá chất bí mật cùng các đơn vị phun tán, "
                 "pha riêng cho từng khu vực: pheromone gây hoảng loạn tập "
                 "thể, chất ức chế lòng tin làm rạn vỡ quan hệ xã hội, khí "
                 "tuân phục biến đám đông thành con rối. Đây là bình khí gây "
                 "ảo giác cũ của hắn, nâng lên quy mô hạ tầng công nghiệp."),
                ("Bộ giáp Bản dựng cuối",
                 "Máy chiếu lượng tử cầm tay, bộ triệt âm, lớp nguỵ trang "
                 "quang học và mũ giao diện thần kinh. Nó dựng quanh hắn một "
                 "bong bóng thực tại 360 độ: hắn xuất hiện ở nhiều chỗ cùng "
                 "lúc, tàng hình, hoặc để lại bản sao đứng chịu đòn. Kèm "
                 "vòi phun phá tơ nhện và một xung điện từ để dọn dẹp."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Không đòn nào ở đây nhằm áp đảo Peter bằng sức. Tất cả đều "
                  "nhằm biến đúng những lợi thế lớn nhất của cậu — giác quan "
                  "báo nguy, mạng tơ, và cái lương tâm — thành thứ quay lại "
                  "cắn chính cậu.",
            items=(
                ("Làm nghẹt giác quan nhện",
                 "Một trường nhiễu gồm hạ âm 7–19 Hz cộng hưởng với hệ tiền "
                 "đình, kèm xung laser hồng ngoại giả tín hiệu nhiệt của mối "
                 "đe doạ. Giác quan nhện kêu liên tục từ mọi hướng cho tới "
                 "khi Peter kiệt sức thần kinh. Mysterio không cần ra đòn "
                 "nào: chính năng lực của Người Nhện thành hình phạt."),
                ("Nhà hát Vô hiểm",
                 "Ngược lại hoàn toàn: hắn dựng một khoảng *an toàn giả* — "
                 "một con phố vắng, một sân thượng yên tĩnh. Giác quan nhện "
                 "chỉ báo khi có nguy hiểm thật, nên khi nó im, Peter tin. "
                 "Đòn thật được giấu trong lớp ảo giác nền và tới từ đúng "
                 "góc mà cậu không kịp quay lại. Đây là chỗ tàn nhẫn nhất: "
                 "không phá giác quan ấy, mà mượn chính nó."),
                ("Sol khí phá tơ",
                 "Enzyme protease cùng dung môi xúc tác cắt liên kết "
                 "beta-sheet trong polymer tơ nhện, làm độ bền kéo rụng 90% "
                 "trong vài giây. Bão hoà cả chiến trường thì mạng tơ hoá "
                 "giòn, và Peter buộc phải đánh tay đôi — đúng cự ly Mysterio "
                 "chọn, vì ở đó hắn chỉ cần né và tiếp tục dựng cảnh."),
                ("Bóng ma tội lỗi",
                 "Từ dữ liệu đánh cắp được về đời tư Peter, hắn dựng hologram "
                 "thể tích cực thật của chú Ben, Gwen Stacy, dì May, Mary "
                 "Jane — đang gặp nguy, hoặc đang bị chính Người Nhện làm "
                 "hại. Không phải điều khiển tâm trí, mà là nhằm thẳng vào "
                 "chỗ Peter tự cắn rứt nhất. Cậu chỉ cần do dự nửa giây."),
                ("Cắt đường rung",
                 "Peter đọc trận đánh qua rung động truyền trên tơ. Máy phát "
                 "nhiễu trắng cùng bộ giảm chấn địa chấn cắt sạch kênh ấy: "
                 "cậu mù thông tin ngay giữa cái mạng do chính mình giăng, "
                 "và mọi thứ còn lại để tin thì đều do Mysterio viết ra."),
            ),
        ),
    ),

    # Thang chữ cái Hy Lạp, đọc từ Zeta lên Omega. Cả thang này đo bằng mức
    # sụp đổ nhận thức, không phải bằng sức phá vật lý.
    tiers=(
        Tier("Tier Zeta", "Đóng lại chính mình ngày xưa",
             "Ảo ảnh gói trong một nhà kho hay một trung tâm thương mại: "
             "cướp ngân hàng, gây rối, doạ dẫm. Đây đúng bằng trần của bản "
             "gốc — và hắn giữ bậc này chỉ để người ta tưởng vẫn đang đối "
             "phó với gã Mysterio cũ.",
             "Vài phút tới vài giờ"),
        Tier("Tier Epsilon", "Một quận tin vào một vụ khủng bố không có",
             "Bộ giáp cơ bản cộng một đám bụi ảo ảnh hạn chế là đủ phủ ảo "
             "giác khắp một quận: bạo loạn, một vụ tấn công khủng bố dàn "
             "dựng, cảnh sát địa phương tê liệt. Bản gốc phải chuẩn bị nhiều "
             "ngày cho một màn nhỏ hơn thế.",
             "1–6 giờ"),
        Tier("Tier Delta", "Lừa được cả một quân đội",
             "Bụi ảo ảnh trải quy mô thành phố, dựng quái vật khổng lồ hoặc "
             "một đạo quân xâm lược. Quân đội buộc phải nổ súng, và thiệt "
             "hại hạ tầng là do chính đạn của họ bắn vào thành phố của "
             "mình.",
             "12–24 giờ"),
        Tier("Tier Gamma", "Xung đột khu vực",
             "Vệ tinh phân chiếu cộng Động cơ Sợ hãi phủ nhiều thành phố: "
             "dựng các vụ tấn công giả giữa các quốc gia, kích xung đột khu "
             "vực, đánh sập thị trường chứng khoán, đẩy hàng triệu người vào "
             "cuộc sơ tán. Bản gốc chưa từng với tới chính trị quốc tế.",
             "1–3 ngày"),
        Tier("Tier Beta", "Cuộc chiến ma toàn cầu",
             "Chiếm sóng truyền thông toàn thế giới và phát ảo ảnh đồng "
             "loạt, dựng một cuộc chiến giữa các siêu cường mà không bên nào "
             "thật sự nổ súng trước. Tài chính tê liệt, lương thực khủng "
             "hoảng, hoảng loạn lan khắp nơi.",
             "1–2 tuần"),
        Tier("Tier Alpha", "Sự thật bị thay hẳn",
             "Ở nhiều khu vực, cái gọi là thực tại đã hoàn toàn là bản dựng "
             "của Mysterio. Chính phủ và quân đội phát động chiến tranh nhắm "
             "vào những mối đe doạ không tồn tại, còn dân chúng thì rơi vào "
             "loạn thần tập thể. Không ai còn cách nào để kiểm chứng bất cứ "
             "điều gì.",
             "2–4 tuần"),
        Tier("Tier Omega", "Tận thế nhận thức",
             "Nền văn minh sụp không phải vì bị đánh mà vì mất khả năng phân "
             "biệt thật giả: kho hạt nhân được phóng vì báo động giả, chuỗi "
             "cung ứng đứt vì bạo loạn do ảo giác tập thể, các chính phủ "
             "đánh lẫn nhau. Hàng tỷ người chết vì khủng hoảng tâm lý hàng "
             "loạt, vì đói, vì bạo lực. Bản gốc là mối đe doạ cấp khu phố; "
             "bậc này xoá sổ nền văn minh toàn cầu trong chưa đầy một tháng "
             "mà không cần một quả bom nào có thật.",
             "Dưới 30 ngày"),
    ),

    # Nhãn giữ dưới 94 px, giá trị dưới 188 px — xem chú thích cùng chỗ trong
    # `chameleon_absolute.py`.
    facts=(
        ("Cấp đe doạ", "Hành tinh  ·  sụp đổ nhận thức"),
        ("Nền tảng", "Ảo giác, sân khấu, hoá học"),
        ("Không dùng", "AI tự chủ  ·  hắn là đạo diễn"),
        ("Cấy ghép", "Vỏ não Đạo diễn, mắt đa phổ"),
        ("Sân khấu", "Vệ tinh ion hoá tầng bình lưu"),
        ("Bụi ảo ảnh", "Hàng tỷ hạt, lơ lửng hàng tuần"),
        ("Khắc tơ nhện", "Sol khí, mất 90% độ bền kéo"),
        ("Bậc Omega", "Dưới 30 ngày"),
    ),

    blurb="Tám hồ sơ kia đều cần một thứ có thật để phá: một thành phố, một "
          "lưới điện, một sinh quyển. Hồ sơ này thì không phá gì cả — hắn chỉ "
          "làm cho không ai còn kiểm chứng được điều gì nữa, rồi đứng sang "
          "một bên. Phần huỷ diệt để loài người tự làm, và họ làm rất nhanh.",

    art=draw_absolute_mysterio,
    caption="Trích từ bản dựng của hắn  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Mysterio"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Quentin_Beck_(Earth-616)"),
    ),
)
