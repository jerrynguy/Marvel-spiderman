"""
Absolute Chameleon — dạng tiến hoá của Dmitri Smerdyakov.

File này không khai báo `PROFILE` nên sổ tra ở `__init__.py` bỏ qua nó: dạng
Absolute không đứng riêng trong dòng thời gian, nó treo dưới hồ sơ gốc qua
`evolution=ABSOLUTE` trong `chameleon.py`, mở ra bằng nút tiến hoá.

Chân dung vẽ bằng code và có tham số thời gian (`t`) nên nó sống: bầy nano
quay, mắt thở, mặt nạ vỡ rung theo từng chặp nhiễu. Bảng màu lấy từ `VOID`
chứ không phải giấy pulp — cả tấm hồ sơ đổi da khi tiến hoá.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QLinearGradient, QPainter,
                           QPainterPath, QPen, QRadialGradient)

from theme import VOID

from .art import H, W, Rolls, design, glow, marks, mirrored, scanlines
from .profile import Profile, Section, Tier

CYAN = VOID.blue
CRIMSON = VOID.red
LIME = VOID.yellow
SHELL = QColor("#06050B")        # bóng người: đen hơn cả nền
BONE = QColor("#D6CFC0")         # phía mặt nạ ăn ánh lửa
BONE_DARK = QColor("#1C1726")    # phía mặt nạ chìm hẳn vào tối

FX, FY = 50.0, 36.0              # tâm mặt nạ
HORIZON = 93.0                   # đường chân trời của thành phố phía sau
BANDS = 13                       # số dải cắt ngang mặt nạ


# ═══════════════════════════════════════════════════════════ bóng người
def _head():
    """Sọ: vòm trên bè ra, hai gò má gãy, hàm thon lại thành cằm nhọn."""
    path = QPainterPath()
    path.moveTo(50, 13.6)
    path.cubicTo(65.0, 13.6, 69.6, 24.0, 68.6, 36.0)
    path.cubicTo(68.0, 46.5, 62.0, 54.8, 50.0, 58.4)
    path.cubicTo(38.0, 54.8, 32.0, 46.5, 31.4, 36.0)
    path.cubicTo(30.4, 24.0, 35.0, 13.6, 50.0, 13.6)
    path.closeSubpath()
    return path


def _body():
    """Vai đổ rộng ra khỏi khung, áo choàng dài, cổ áo dựng ngang hàm."""
    path = QPainterPath()
    path.moveTo(-14, 122)
    path.cubicTo(-6, 104, 12, 88, 30, 80)
    path.lineTo(50, 93)
    path.lineTo(70, 80)
    path.cubicTo(88, 88, 106, 104, 114, 122)
    path.closeSubpath()

    neck = QPainterPath()
    neck.addRect(44, 48, 12, 48)
    path = path.united(neck)

    collar = QPainterPath()
    for side in (-1, 1):
        wing = QPainterPath()
        wing.moveTo(50 + side * 4, 95)
        wing.lineTo(50 + side * 7, 63)
        wing.lineTo(50 + side * 23, 46)      # đỉnh vạt dừng ngang hàm
        wing.lineTo(50 + side * 28, 57)
        wing.lineTo(50 + side * 21, 79)
        wing.lineTo(50 + side * 16, 97)
        wing.closeSubpath()
        collar = collar.united(wing)
    return path.united(collar)


def _spines():
    """Dãy ăng-ten mảnh dựng sau lưng, xoè dần ra hai bên.

    Các lưỡi không chạm nhau nên ghép thẳng thành nhiều nhánh của một
    đường dẫn, khỏi phải hợp path — hợp xong tô chậm gấp bốn lần.
    """
    one = QPainterPath()
    for root, tip, top, half in ((15, 21, 50, 0.55), (23, 34, 37, 0.7),
                                 (31, 45, 47, 0.55), (38, 54, 62, 0.45)):
        one.moveTo(50 + root - half, 99)
        one.lineTo(50 + root + half, 99)
        one.lineTo(50 + tip + half * 0.8, top)
        one.lineTo(50 + tip - half * 0.8, top)
        one.closeSubpath()
    both = QPainterPath(one)
    both.addPath(mirrored(one))
    return both


_HEAD = _head()
_HEAD_BOX = _HEAD.boundingRect()
_BODY = _body()
_SPINE = _spines()


def _fade_to(color, alpha):
    """Bản sao của một màu với alpha đặt thẳng."""
    tone = QColor(color)
    tone.setAlpha(alpha)
    return tone


def _figure(p):
    """Bóng đen, rồi hai đường viền sáng: lạnh bên trái, lửa bên phải."""
    p.setPen(Qt.PenStyle.NoPen)
    for path, alpha in ((_SPINE, 0.75), (_BODY, 1.0)):
        for color, dx, dy in ((CRIMSON, 1.1, 0.9), (CYAN, -1.1, -0.9)):
            tint = QColor(color)
            tint.setAlpha(int(95 * alpha))
            p.setBrush(tint)
            p.drawPath(path.translated(dx, dy))
        p.setBrush(SHELL)
        p.drawPath(path)

    p.setBrush(Qt.BrushStyle.NoBrush)
    rim = QColor(CYAN)
    rim.setAlpha(90)
    p.setPen(QPen(rim, 0.6))
    p.drawPath(_BODY)
    p.save()                       # nửa phải bắt ánh lửa dưới chân trời
    p.setClipRect(QRectF(50, 0, 70, 122))
    fire = QColor(CRIMSON)
    fire.setAlpha(130)
    p.setPen(QPen(fire, 0.7))
    p.drawPath(_BODY)
    p.restore()


# ═══════════════════════════════════════════════════════════════ các lớp
def _void(p, t):
    """Bầu trời rỗng phía trên, ánh cháy phía dưới, vạch quét trôi ngang."""
    p.setPen(Qt.PenStyle.NoPen)
    sky = QLinearGradient(0, -6, 0, 126)
    sky.setColorAt(0.0, QColor("#0A0714"))
    sky.setColorAt(0.55, QColor("#120C20"))
    sky.setColorAt(0.78, QColor("#2A1024"))
    sky.setColorAt(1.0, QColor("#07050C"))
    p.setBrush(sky)
    p.drawRect(QRectF(-6, -6, 112, 132))

    haze = QRadialGradient(QPointF(50, HORIZON + 4), 62)
    for stop, weight in ((0.0, 0.42), (0.45, 0.16), (1.0, 0.0)):
        tone = QColor(CRIMSON)
        tone.setAlpha(int(255 * weight))
        haze.setColorAt(stop, tone)
    p.setBrush(haze)
    p.drawRect(QRectF(-6, 62, 112, 64))

    scanlines(p, QRectF(-6, -6, 112, 132), 2.7,
              QColor(120, 240, 255, 12), offset=(t * 3.1) % 2.7)


def _city_plan():
    """Thành phố dưới chân, dựng một lần: (x, rộng, cao, các ô cửa còn sáng)."""
    r = Rolls(3061963)
    plan, x = [], -8.0
    while x < 108:
        w = r(4, 11)
        h = r(5, 23)
        lights = tuple((x + r(0.8, max(1.0, w - 1.6)),
                        HORIZON - h + r(1.5, max(2.0, h - 1.5)),
                        r(0, 1) > 0.72)
                       for _ in range(int(r(0, 4))))
        plan.append((x, w, h, lights))
        x += w + r(1.2, 3.4)
    return tuple(plan)


_CITY = _city_plan()
BODY_ZONE = (26.0, 74.0)     # bề ngang bóng người che mất phần thành phố


def _city_blocks(p):
    """Khối nhà: đứng yên, nằm chung trong ảnh nền dựng sẵn."""
    p.setPen(Qt.PenStyle.NoPen)
    for x, w, h, _ in _CITY:
        p.setBrush(QColor("#0A0812"))
        p.drawRect(QRectF(x, HORIZON - h, w, h + 30))
        edge = QColor(CRIMSON)
        edge.setAlpha(60)
        p.setBrush(edge)
        p.drawRect(QRectF(x, HORIZON - h, w, 0.45))


def _city_lights(p, t):
    """Cửa sổ còn điện, nhấp nháy lệch nhau. Bỏ qua chỗ bóng người che."""
    p.setPen(Qt.PenStyle.NoPen)
    for _, _, _, lights in _CITY:
        for wx, wy, cool in lights:
            if BODY_ZONE[0] < wx < BODY_ZONE[1]:
                continue
            lit = QColor(LIME if cool else CRIMSON)
            lit.setAlpha(int(90 + 90 * abs(math.sin(t * 0.8 + wx))))
            p.setBrush(lit)
            p.drawRect(QRectF(wx, wy, 0.55, 0.8))


def _swarm(p, t):
    """Ghost Swarm: bầy nano dày trên trời, hai vành vệ tinh gãy khúc."""
    r = Rolls(20260815)
    p.setPen(Qt.PenStyle.NoPen)
    for i in range(120):
        base = r(0, 360)
        speed = r(3, 12)
        radius = 24 + r(0, 5.4) ** 2.05
        a = math.radians(base + t * speed)
        wob = math.sin(t * 1.4 + i * 0.9) * 0.8
        x = 50 + math.cos(a) * (radius + wob) * 1.18
        y = 40 + math.sin(a) * (radius + wob) * 0.86
        if y > HORIZON - 2:
            continue
        tone = QColor(CRIMSON if i % 5 == 0 else CYAN)
        tone.setAlpha(int(30 + 105 * abs(math.sin(t * 2.1 + i * 0.7))))
        p.setBrush(tone)
        p.drawEllipse(QPointF(x, y), 0.38, 0.38)

    p.setBrush(Qt.BrushStyle.NoBrush)
    for radius, speed, color, alpha in ((34, 13, CYAN, 46),
                                        (45, -9, CRIMSON, 34)):
        tone = QColor(color)
        tone.setAlpha(alpha)
        p.setPen(QPen(tone, 0.45))
        box = QRectF(50 - radius * 1.16, 40 - radius * 0.84,
                     radius * 2.32, radius * 1.68)
        start = int((t * speed) % 360)
        p.drawArc(box, start * 16, 96 * 16)
        p.drawArc(box, (start + 172) * 16, 54 * 16)


def _echoes(p, t):
    """Hai gương mặt vừa bị bỏ lại, còn kịp bám hai bên như ảnh dư."""
    for dx, color, phase in ((-12, CYAN, 0.0), (12, CRIMSON, 1.9)):
        tone = QColor(color)
        tone.setAlpha(int(44 * (0.5 + 0.5 * math.sin(t * 1.1 + phase))))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(tone, 0.55))
        p.drawPath(_HEAD.translated(dx, 1))
        for ex in (-6.4, 6.4):
            p.drawLine(QPointF(FX + dx + ex - 2.0, FY - 2),
                       QPointF(FX + dx + ex + 2.0, FY - 2))


def _band_shift(i, t):
    """Dải thứ i trượt ngang bao nhiêu — phần lớn đứng yên, vài dải trôi."""
    wave = math.sin(t * 0.7 + i * 1.9) + math.sin(t * 1.31 + i * 0.7)
    if wave < 0.95:
        return 0.0
    return (wave - 0.95) * 4.6 * (1 if i % 2 else -1)


def _slit(ex, ey):
    """Khe mắt: đầu phía sống mũi chúi xuống, đuôi hất lên — dáng của cơn giận."""
    side = 1 if ex > FX else -1
    inner = QPointF(FX + side * 3.3, ey + 1.6)
    outer = QPointF(FX + side * 11.6, ey - 1.4)
    half = 0.9
    path = QPainterPath()
    path.moveTo(inner.x(), inner.y() - half * 0.4)
    path.lineTo(outer.x(), outer.y() - half)
    path.lineTo(outer.x() + side * 0.8, outer.y() + half * 0.2)
    path.lineTo(inner.x(), inner.y() + half * 0.8)
    path.closeSubpath()
    return path


def _mask(p, t):
    """Mặt nạ trắng ngày xưa: nay cắt thành dải, dải nào cũng trượt được.

    Ánh sáng chỉ đến từ đám cháy phía dưới bên trái, nên hơn nửa gương mặt
    chìm hẳn vào tối — thứ sáng rõ nhất trên đó là hai khe mắt tự phát sáng.
    """
    pulse = 0.6 + 0.4 * math.sin(t * 2.4)
    top, bottom = _HEAD_BOX.top(), _HEAD_BOX.bottom()
    height = (bottom - top) / BANDS
    eyes = ((FX - 7.6, FY - 2.4), (FX + 7.6, FY - 2.4))

    wash = QRadialGradient(QPointF(FX - 12, FY + 16), 26)
    wash.setColorAt(0.0, BONE)
    wash.setColorAt(0.18, QColor("#B6AC9B"))
    wash.setColorAt(0.38, QColor("#7A7080"))
    wash.setColorAt(0.58, QColor("#40374F"))
    wash.setColorAt(0.78, QColor("#241E31"))
    wash.setColorAt(1.0, BONE_DARK)

    p.save()
    p.setClipPath(_HEAD)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#120810"))          # khoảng trống giữa các dải
    p.drawPath(_HEAD)
    # trong khe hở giữa các dải có thứ gì đó đang cháy âm ỉ
    ember = QColor(CRIMSON)
    ember.setAlpha(int(70 * pulse))
    glow(p, QPointF(FX + 1, FY + 2), 17, ember)

    for i in range(BANDS):
        y0 = top + i * height
        dx = _band_shift(i, t)
        p.save()
        # cắt thêm chứ không thay: dải trượt vẫn phải nằm trong bóng cái đầu
        p.setClipRect(QRectF(FX - 24, y0, 48, height * 0.94),
                      Qt.ClipOperation.IntersectClip)
        p.translate(dx, 0)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(wash)
        p.drawPath(_HEAD)

        # khe mắt nằm trong dải nào thì trượt theo đúng dải đó
        for ex, ey in eyes:
            if not y0 - 2.4 < ey < y0 + height + 2.4:
                continue
            p.setBrush(QColor("#FFF2EA"))
            p.drawPath(_slit(ex, ey))
        p.restore()

        if abs(dx) > 0.2:      # mép dải trượt thì rớm sáng, dài bằng chỗ hở
            leak = QColor(CRIMSON if dx > 0 else CYAN)
            leak.setAlpha(70)
            p.setPen(QPen(leak, 0.45))
            span = min(16.0, 2.5 + abs(dx) * 2.2)
            p.drawLine(QPointF(FX + dx - span, y0), QPointF(FX + dx + span, y0))

    # dải mã vạch chỗ đáng lẽ là miệng, đang đọc dở một danh tính
    r = Rolls(9152026)
    x = FX - 7.5
    while x < FX + 7.5:
        w = r(0.3, 1.1)
        bar = QColor(BONE if r(0, 1) > 0.45 else CYAN)
        bar.setAlpha(int(40 + 45 * r(0, 1)))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bar)
        p.drawRect(QRectF(x, FY + 11.4, w, 2.3))
        x += w + r(0.4, 1.0)
    cursor = QColor(LIME)
    cursor.setAlpha(150)
    p.setBrush(cursor)
    p.drawRect(QRectF(FX - 7.5 + ((t * 6) % 15), FY + 11.0, 0.5, 3.1))

    mesh = QColor(CYAN)
    mesh.setAlpha(22)
    p.setPen(QPen(mesh, 0.3))
    p.setBrush(Qt.BrushStyle.NoBrush)
    for k in range(-2, 3):
        arc = QPainterPath()
        arc.moveTo(FX + k * 5.5, top)
        arc.quadTo(FX + k * 7.6, FY, FX + k * 5.5, bottom)
        p.drawPath(arc)
    p.restore()

    # quầng sáng của hai khe mắt, vẽ ngoài lớp cắt nên nó loang ra cả mặt nạ
    for ex, ey in eyes:
        halo = QColor(CRIMSON)
        halo.setAlpha(int(150 * pulse))
        glow(p, QPointF(FX + (6.8 if ex > FX else -6.8), ey),
             4.6 * (0.82 + 0.18 * pulse), halo)

    # mép dưới bên trái hứng ánh lửa, tách cái đầu khỏi nền
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.save()
    p.setClipRect(QRectF(FX - 24, FY, 24, 40))
    p.setPen(QPen(_fade_to(BONE, 150), 0.7))
    p.drawPath(_HEAD)
    p.restore()
    p.setPen(QPen(_fade_to(CYAN, 60), 0.6))
    p.drawPath(_HEAD)


def _core(p, t):
    """Cổng phát của mạng lượng tử, gắn giữa ngực, kéo hai sợi cáp lên vai."""
    beat = 0.55 + 0.45 * math.sin(t * 1.7 + 0.6)
    hub = QPointF(50, 104)

    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_fade_to(CYAN, 60), 0.5))
    for side in (-1, 1):
        cable = QPainterPath(QPointF(50 + side * 1.6, 103))
        cable.quadTo(QPointF(50 + side * 13, 100),
                     QPointF(50 + side * 19, 88))
        p.drawPath(cable)
    seam = QPainterPath(QPointF(24, 116))
    seam.quadTo(QPointF(50, 108), QPointF(76, 116))
    p.setPen(QPen(_fade_to(CYAN, 34), 0.45))
    p.drawPath(seam)

    glow(p, hub, 7.5 * beat, _fade_to(CRIMSON, int(150 * beat)))
    gem = QPainterPath()
    gem.moveTo(hub.x(), hub.y() - 3.4)
    gem.lineTo(hub.x() + 2.3, hub.y())
    gem.lineTo(hub.x(), hub.y() + 3.4)
    gem.lineTo(hub.x() - 2.3, hub.y())
    gem.closeSubpath()
    p.setPen(QPen(_fade_to(CRIMSON, 220), 0.5))
    p.setBrush(QColor("#1A0A12"))
    p.drawPath(gem)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_fade_to(QColor("#FFE9E4"), int(90 + 140 * beat)))
    p.drawEllipse(hub, 0.85, 0.85)


def _hud(p, t):
    """Bốn ngoặc khoá mục tiêu quanh đầu, cộng vạch đo ở lề khung."""
    tone = QColor(CYAN)
    tone.setAlpha(110)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(tone, 0.6))
    pad = 5.5 + 0.7 * math.sin(t * 1.6)
    left, right = _HEAD_BOX.left() - pad, _HEAD_BOX.right() + pad
    high, low = _HEAD_BOX.top() - pad, _HEAD_BOX.bottom() + pad
    arm = 4.5
    for x, sx in ((left, 1), (right, -1)):
        for y, sy in ((high, 1), (low, -1)):
            p.drawLine(QPointF(x, y), QPointF(x + sx * arm, y))
            p.drawLine(QPointF(x, y), QPointF(x, y + sy * arm))

    faint = QColor(CYAN)
    faint.setAlpha(60)
    p.setPen(QPen(faint, 0.45))
    for i in range(11):
        y = 14 + i * 8
        long_tick = i % 5 == 0
        p.drawLine(QPointF(3, y), QPointF(3 + (4 if long_tick else 2), y))
        p.drawLine(QPointF(97, y), QPointF(97 - (4 if long_tick else 2), y))

    live = QColor(CRIMSON)
    live.setAlpha(int(120 + 90 * abs(math.sin(t * 2.6))))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(live)
    p.drawRect(QRectF(3, 8, 3.4, 1.2))


def _nerves(p, t):
    """Bào tử đồng hoá: mạng thần kinh bò ra hai góc dưới, có tín hiệu chạy."""
    lines = (((30, 100), (18, 108), (4, 119)), ((70, 100), (82, 108), (96, 119)),
             ((50, 108), (38, 115), (24, 121)), ((50, 108), (62, 115), (76, 121)))
    for i, pts in enumerate(lines):
        vein = QColor(CYAN if i % 2 else LIME)
        vein.setAlpha(52)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(vein, 0.5))
        path = QPainterPath(QPointF(*pts[0]))
        path.quadTo(QPointF(*pts[1]), QPointF(*pts[2]))
        p.drawPath(path)

        spark = path.pointAtPercent((t * 0.33 + i * 0.25) % 1.0)
        hot = QColor(vein)
        hot.setAlpha(200)
        glow(p, spark, 2.2, hot)


def _glitch(p, t):
    """Nhiễu: cứ vài giây lại có một chặp dải ngang trượt khỏi trục."""
    cycle = (t * 0.47) % 1.0
    if cycle > 0.11:
        return
    k = 1.0 - cycle / 0.11
    r = Rolls(int(t * 9) * 977 + 41)
    p.setPen(Qt.PenStyle.NoPen)
    for _ in range(4):
        y = r(2, 116)
        h = r(0.8, 3.4)
        dx = r(-9, 9) * k
        tone = QColor(CYAN if r(0, 1) > 0.5 else CRIMSON)
        tone.setAlpha(int(46 * k))
        p.setBrush(tone)
        p.drawRect(QRectF(dx, y, 100, h))
    p.setBrush(QColor(4, 3, 10, int(110 * k)))
    p.drawRect(QRectF(0, r(2, 116), 100, r(0.6, 1.6)))


# ═════════════════════════════════════════════ ảnh nền dựng sẵn cho lớp tĩnh
_STILL = {}


def _still(scale):
    """Thành phố và bóng người không đổi theo thời gian — vẽ một lần rồi dán.

    Đây là hai lớp tốn công nhất; để chúng vẽ lại 25 lần mỗi giây thì phí.
    Ảnh được dựng đúng bằng số điểm ảnh thật nên dán vào không bị nhoè.
    """
    key = round(scale, 2)
    ready = _STILL.get(key)
    if ready is None:
        if len(_STILL) > 6:           # đổi cỡ cửa sổ liên tục thì đừng giữ hết
            _STILL.clear()
        w = max(1, math.ceil(112 * scale))
        h = max(1, math.ceil(132 * scale))
        ready = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
        ready.fill(Qt.GlobalColor.transparent)
        q = QPainter(ready)
        q.setRenderHint(QPainter.RenderHint.Antialiasing)
        q.scale(scale, scale)
        q.translate(6, 6)             # gốc ảnh ứng với điểm (-6, -6) khung vẽ
        _city_blocks(q)
        _figure(q)
        q.end()
        _STILL[key] = ready
    return ready


def draw_absolute_chameleon(p, rect, t=0.0):
    """Chân dung sống: nhận thêm `t` (giây) nên khung hồ sơ tự vẽ lại."""
    scale = min(rect.width() / W, rect.height() / H)
    still = _still(scale)
    with design(p, rect):
        _void(p, t)
        _swarm(p, t)
        _echoes(p, t)
        p.drawImage(QRectF(-6, -6, still.width() / scale,
                           still.height() / scale), still)
        _city_lights(p, t)
        _mask(p, t)
        _core(p, t)
        _hud(p, t)
        _nerves(p, t)
        _glitch(p, t)
        marks(p, QColor("#6E6A86"))


# ═══════════════════════════════════════════════════════════════ hồ sơ
ABSOLUTE = Profile(
    name="Absolute Chameleon",
    vi_name="Tắc Kè Hoa Tuyệt Đối",
    real_name="Dmitri Nikolayevich Smerdyakov",
    keys=("Chameleon Absolute",),

    kicker="Hồ sơ tuyệt đối",
    stamp="PHÂN LOẠI  ·  MỐI ĐE DOẠ CẤP QUỐC GIA",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="void",
    evolve_fx="shatter",     # kẻ giả dạng thì vỡ vụn ra rồi được quét lại

    tagline="Không phép thuật vũ trụ, không thao túng thực tại. Chỉ vật lý "
            "cường hoá, sinh học đột biến và công nghệ huỷ diệt — đủ để một "
            "quốc gia tự sụp đổ trong 72 giờ.",

    summary=(
        "Chameleon gốc chỉ là kẻ giả dạng bằng mặt nạ và hoá chất. Ở phiên "
        "bản Absolute, cơ thể hắn được tái cấu trúc thành một cỗ máy nguỵ "
        "trang sinh học hoàn hảo, vượt xa mọi giới hạn vật lý thông thường — "
        "và quanh cỗ máy đó là một hạ tầng thông tin đủ sức thao túng cả một "
        "quốc gia.",

        "Giới hạn sức mạnh được giữ nguyên ở cấp quốc gia: hắn không bẻ cong "
        "thực tại, không mượn phép thuật. Mọi thứ hắn làm đều có thể truy ra "
        "một chuỗi nhân quả vật lý — và chính điều đó khiến hắn không thể bị "
        "phủ nhận, cũng không thể bị đánh bại bằng cách đấm mạnh hơn.",
    ),

    sections=(
        Section(
            title="Khuyếch đại năng lực vật lý & sinh học",
            intro="Cơ thể không còn là chỗ để đeo mặt nạ, nó chính là mặt nạ.",
            items=(
                ("Biến hình tế bào toàn phần",
                 "Tái lập trình toàn bộ cấu trúc sinh học ở cấp độ tế bào: "
                 "dáng người, giọng nói, mùi cơ thể, nhiệt độ bề mặt, cả DNA, "
                 "dấu vân tay, mống mắt và hệ vi sinh vật trên da — chỉ cần "
                 "một mẫu tế bào nhỏ. Mọi hệ nhận dạng sinh trắc học trên thế "
                 "giới trở nên vô dụng."),
                ("Tăng cường thể chất thích ứng",
                 "Cơ, xương và mô liên kết tái cấu trúc để mô phỏng sức mạnh, "
                 "tốc độ và độ bền của mục tiêu: tăng mật độ cơ gấp nhiều lần, "
                 "biến cánh tay thành lưỡi dao xương, tạo lớp da sừng chống "
                 "đạn, tự lành vết thương trong vài giây bằng cách tăng tốc "
                 "nguyên phân."),
                ("Tuyến pheromone điều khiển hành vi",
                 "Pheromone tổng hợp tác động thẳng vào hệ thần kinh người và "
                 "động vật: sợ hãi tột độ, tuân phục vô thức, hoặc thịnh nộ "
                 "tập thể. Trong vài km, hắn biến một đám đông thành công cụ "
                 "bạo loạn mà không cần lộ diện."),
                ("Bào tử đồng hoá sinh quyển",
                 "Bào tử biến đổi gen lây vào cây cối, côn trùng, thú vật, "
                 "biến chúng thành cảm biến sinh học. Ở chế độ cực đoan, các "
                 "sinh vật nhiễm bệnh phát triển thành mạng thần kinh cộng "
                 "sinh — cả một vùng rộng lớn trở thành hệ thần kinh mở rộng "
                 "của hắn."),
                ("Tàng hình đa phổ",
                 "Da đổi màu, kết cấu và độ phản xạ để biến mất trước mắt "
                 "thường, camera, radar lẫn cảm biến hồng ngoại; thân nhiệt "
                 "chỉnh được để qua mặt thiết bị tầm nhiệt."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="Một sinh vật đột biến thì giết được vài người. Một sinh vật "
                  "đột biến có hạ tầng thì giết được một thể chế.",
            items=(
                ("Mạng vệ tinh nano “Ghost Swarm”",
                 "Hàng nghìn vệ tinh siêu nhỏ lơ lửng ở tầng khí quyển thấp, "
                 "quét quang học, nhiệt và tín hiệu điện từ trên phạm vi toàn "
                 "quốc, dựng bản đồ sinh trắc học 3D của mọi công dân — đủ để "
                 "tạo bản sao chính xác đến từng milimet."),
                ("Android thay người thật",
                 "Hàng trăm “Doppelganger Drones” phủ da sinh học tổng hợp "
                 "đổi được màu và nhiệt, mang AI tự học để nhại giọng, ngôn "
                 "ngữ cơ thể và thói quen. Chúng ngồi được vào ghế trong chính "
                 "phủ, quân đội, ngân hàng và cơ quan an ninh mà không ai nghi."),
                ("AI “Mirror Mind”",
                 "Nuốt toàn bộ dữ liệu từ vệ tinh nano, camera công cộng, mạng "
                 "xã hội, giao dịch tài chính và sinh trắc học; dự đoán phản "
                 "ứng đám đông, quyết định của chính trị gia và cả đường di "
                 "chuyển của siêu anh hùng với độ chính xác trên 95%."),
                ("Nanite “Spoof Cloud”",
                 "Hạt nano tự sao chép phát tán trong không khí, chui vào mọi "
                 "thiết bị điện tử: làm lệch GPS, chặn và giả mạo liên lạc, "
                 "phát tin giả, kích hoạt lệnh sai trong hệ thống ngân hàng và "
                 "quân sự, dựng cả “bóng ma điện tử” cho radar nhìn thấy thứ "
                 "không tồn tại."),
                ("Puppet Master Protocol",
                 "Điều khiển đồng thời hàng trăm android và thiết bị tự hành "
                 "qua mạng lượng tử — trong giới hạn một quốc gia. Đủ để dựng "
                 "một cuộc tấn công giả, làm rối loạn hạ tầng, hoặc quay hệ "
                 "thống vũ khí tự động của một nước vào chính phủ nước đó."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Hắn hiểu điểm mạnh lớn nhất của Spider-Man là giác quan "
                  "báo động và hệ thần kinh siêu nhạy — nên hắn không đánh vào "
                  "cơ bắp, hắn đánh vào cảm biến.",
            items=(
                ("Spider-Sense Jamming Array",
                 "Xung điện từ tần số cao cộng sóng âm hạ tần, hiệu chỉnh để "
                 "làm quá tải các hạch thần kinh cảm nhận nguy hiểm. Giác quan "
                 "nhện reo báo động giả từ mọi hướng cho đến khi hệ thần kinh "
                 "suy nhược, không còn phân biệt nổi mối đe doạ thật."),
                ("Nanite Webbing Dissolver",
                 "Đám mây nano chui vào cấu trúc polymer của tơ nhện, cắt liên "
                 "kết hoá học ngay khi chạm: tơ tan thành chất lỏng vô hại "
                 "trong chưa đầy 0,2 giây, mất cả khả năng di chuyển lẫn khống "
                 "chế đối thủ."),
                ("Sensory Overload Protocol",
                 "Ánh sáng nhấp nháy đa tần, âm thanh cường độ cao trải nhiều "
                 "dải, mùi hoá chất kích thích thần kinh — bộ ba nhắm thẳng "
                 "vào giác quan siêu nhạy, gây chóng mặt, mất phương hướng và "
                 "co giật."),
                ("Ghost Pattern Algorithm",
                 "Mirror Mind đọc chuyển động của Spider-Man theo thời gian "
                 "thực rồi thả ra tín hiệu giả, ảo ảnh nhiệt và android giả "
                 "dạng chính anh ta. Anh ta đấm vào những mục tiêu không tồn "
                 "tại cho tới lúc kiệt sức và hở sườn."),
                ("Chiến tranh tâm lý",
                 "Giả dạng Mary Jane, dì May hoặc chính Peter Parker; dựng "
                 "cảnh người thân bị thương, đồng đội phản bội. Cộng thêm bào "
                 "tử pheromone gây sợ hãi là đủ đẩy anh ta vào hoảng loạn."),
                ("Độc thần kinh “Arachnotoxin”",
                 "Đặc chế cho hệ thần kinh tăng cường của Spider-Man: tê liệt "
                 "dây thần kinh vận động, cơ bắp co cứng ngoài tầm kiểm soát. "
                 "Phát tán dạng khí dung hoặc qua mảnh vỡ nano."),
            ),
        ),
    ),

    tiers=(
        Tier("Tier 1", "Gián điệp & ám sát chính xác",
             "Giả dạng bất kỳ ai để vào cơ sở tuyệt mật, lấy dữ liệu nhà nước "
             "hoặc thay thế nhân vật chủ chốt. Ám sát bằng khuôn mặt người "
             "thân cận, hiện trường không để lại dấu vết.",
             "Vài giờ  ·  không thương vong ngoài mục tiêu"),
        Tier("Tier 2", "Phá hoại hạ tầng & khủng hoảng tài chính",
             "Tê liệt lưới điện, giao thông, nhà máy nước, mạng viễn thông. "
             "Thao túng thị trường chứng khoán và niềm tin vào ngân hàng, dẫn "
             "tới rút tiền ồ ạt và sụp đổ kinh tế.",
             "Hỗn loạn trong 24 giờ"),
        Tier("Tier 3", "Chiến tranh thông tin & thao túng chính phủ",
             "Giả dạng tổng thống, bộ trưởng quốc phòng hay tướng lĩnh để phát "
             "lệnh tấn công sai mục tiêu; tung video giả chân thực tuyệt đối "
             "để kích động bạo loạn và lật đổ chính quyền.",
             "Một tuần để đẩy vào nội chiến"),
        Tier("Tier 4", "Sụp đổ quốc gia",
             "Chiếm quyền các hệ thống vũ khí tự động, làm sai lệch mọi liên "
             "lạc, thay toàn bộ giới lãnh đạo bằng android. Một quốc gia tự "
             "huỷ diệt mà không cần bắn một viên đạn nào.",
             "72 giờ tới vô chính phủ hoàn toàn"),
    ),

    facts=(
        ("Cấp đe doạ", "Quốc gia — không vũ trụ, không thao túng thực tại"),
        ("Nền tảng", "Vật lý cường hoá · sinh học đột biến · công nghệ huỷ diệt"),
        ("Sao chép", "DNA, vân tay, mống mắt, hệ vi sinh vật trên da"),
        ("Tầm điều khiển", "Trọn một quốc gia, qua mạng lượng tử"),
        ("Dự đoán hành vi", "Mirror Mind  ·  chính xác trên 95%"),
        ("Thời gian sụp đổ", "72 giờ"),
    ),

    blurb="Bản gốc mở màn danh sách này bằng cách không có gương mặt nào. Bản "
          "Absolute kết thúc nó bằng cách có tất cả các gương mặt — kể cả "
          "gương mặt của người vừa ra lệnh truy lùng hắn.",

    art=draw_absolute_chameleon,
    caption="Dựng lại từ dữ liệu quét  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Chameleon_(character)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Dmitri_Smerdyakov_(Earth-616)"),
    ),
)
