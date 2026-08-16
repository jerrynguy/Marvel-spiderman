"""
Absolute Chameleon — dạng tiến hoá của Dmitri Smerdyakov.

File này không khai báo `PROFILE` nên sổ tra ở `__init__.py` bỏ qua nó: dạng
Absolute không đứng riêng trong dòng thời gian, nó treo dưới hồ sơ gốc qua
`evolution=ABSOLUTE` trong `chameleon.py`, mở ra bằng nút tiến hoá.

Chân dung vẽ bằng code và có tham số thời gian (`t`) nên nó sống: bầy gương
mặt đã lấy quay quanh, mắt thở, mặt nạ vỡ rung theo từng chặp nhiễu. Bảng màu
lấy từ `VOID` chứ không phải giấy pulp — cả tấm hồ sơ đổi da khi tiến hoá.

Hắn không dùng máy móc tự hành, nên trong tranh không có gì là drone hay vệ
tinh: những chấm sáng trên trời là bản sắc bị đánh cắp, các sợi chạy ra mép
khung là người của Hội Gương, và bộ khung ngắm quanh đầu là của phía đang cố
nhận dạng hắn — không phải của hắn.
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
    """Dãy lưỡi gương mảnh dựng sau lưng, xoè dần ra hai bên.

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


def _shards(p, t):
    """Bầy bản sắc đã đánh cắp: mảnh gương dày trên trời, hai vành gãy khúc."""
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


def _gland(p, t):
    """Tuyến pheromone xã hội: hạch phát giữa ngực, hai ống dẫn chạy lên vai."""
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
    """Khung ngắm của phía đang truy tìm hắn: bốn ngoặc quanh đầu, vạch đo ở lề.

    Khoá được cái đầu nhưng không đọc nổi cái mặt — đó là toàn bộ vấn đề.
    """
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


def _threads(p, t):
    """Hội Gương: các mối liên lạc bò ra hai góc dưới, mỗi đốm sáng một người."""
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
        _shards(p, t)
        _echoes(p, t)
        p.drawImage(QRectF(-6, -6, still.width() / scale,
                           still.height() / scale), still)
        _city_lights(p, t)
        _mask(p, t)
        _gland(p, t)
        _hud(p, t)
        _threads(p, t)
        _glitch(p, t)
        marks(p, QColor("#6E6A86"))


# ═══════════════════════════════════════════════════════════════ hồ sơ
ABSOLUTE = Profile(
    name="Absolute Chameleon",
    vi_name="Tắc Kè Hoa Tuyệt Đối",
    real_name="Dmitri Nikolayevich Smerdyakov",
    keys=("Chameleon Absolute",),

    kicker="Hồ sơ tuyệt đối",
    stamp="PHÂN LOẠI  ·  MỐI ĐE DOẠ CẤP HÀNH TINH",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="void",
    evolve_fx="shatter",     # kẻ giả dạng thì vỡ vụn ra rồi được quét lại

    tagline="Không cơ bắp, không tia laser, không AI. Một kẻ đánh cắp bản "
            "sắc — và một nền văn minh không còn cách nào xác minh ai là ai.",

    summary=(
        "Chameleon chưa bao giờ là kẻ huỷ diệt bằng sức mạnh. Bản chất của "
        "hắn là đánh cắp bản sắc, thao túng tâm lý xã hội và tiến hành chiến "
        "tranh thông tin. Nên phiên bản Absolute không lớn lên theo hướng "
        "năng lượng vũ trụ hay máy móc tự hành, mà theo đúng hướng của chính "
        "hắn: một mối đe doạ hành tinh dựng hoàn toàn trên lòng tin bị thao "
        "túng.",

        "Bản gốc là người thường — mặt nạ, phấn, keo dán, và nhiều tuần rình "
        "một mục tiêu; đứng gần là lộ, quét vân tay là hỏng. Absolute biến "
        "chính cơ thể thành một cỗ máy đánh cắp bản sắc sống: mô mềm nắn lại "
        "được, sinh trắc học mượn được, giọng nói và mùi cơ thể sao chép "
        "được. Giới hạn duy nhất còn giữ là hình thái người.",

        "Và hắn tuyệt đối không dùng AI, drone hay máy tự động. Chameleon "
        "tin rằng chỉ bộ não người mới đủ linh hoạt để lừa người khác — nên "
        "quanh hắn chỉ có công cụ thủ công và một mạng lưới người thật. "
        "Chính vì thế không có hệ thống mạng nào để tấn công ngược, không có "
        "máy chủ nào để đánh sập.",
    ),

    sections=(
        Section(
            title="Khuyếch đại năng lực vật lý & sinh học",
            intro="Bản gốc không có siêu năng lực nào: hắn quan sát, bắt "
                  "chước, hoá trang và kiên nhẫn. Absolute giữ nguyên con "
                  "người đó rồi biến cơ thể thành công cụ của nó — cơ thể "
                  "không còn là chỗ để đeo mặt nạ, nó chính là mặt nạ.",
            items=(
                ("Da bản sắc biến đổi — Epidermal Mimicry Matrix",
                 "Lớp hạ bì được cấy tế bào sắc tố nhân tạo và các túi "
                 "collagen–sụn dẻo. Dưới tín hiệu thần kinh, tế bào gốc trung "
                 "mô phản ứng với cortisol và noradrenaline, tái hấp thu canxi "
                 "cục bộ để làm mềm sụn: gò má, đường hàm, sống mũi, trán, độ "
                 "dày môi và mí mắt được nắn lại trong 5–10 phút. Giới hạn: "
                 "chỉ trong phạm vi hình thái người — không mọc thêm chi, "
                 "không đổi hẳn chiều cao — nhưng thừa sức đánh lừa mọi hệ "
                 "nhận diện khuôn mặt."),
                ("Retrovirus đánh cắp sinh trắc — Biometric Hijack",
                 "Một mẩu da, một giọt nước bọt hay một sợi tóc của mục tiêu "
                 "là đủ. Retrovirus đặc chế gắn vào tế bào gốc biểu mô của "
                 "Chameleon và chèn đoạn gen tổng hợp mã hoá protein bề mặt "
                 "của mục tiêu: vân tay, protein mồ hôi, hệ vi sinh trên da, "
                 "cả kháng nguyên nhóm máu bề mặt trở nên giống hệt trong "
                 "48–72 giờ — qua được máy quét sinh trắc, xét nghiệm DNA "
                 "nhanh và khoá vân tay. Hết hạn, tế bào tự chết theo chu kỳ "
                 "và cơ thể trở lại nguyên bản, không để lại bằng chứng."),
                ("Thanh quản đa âm sắc — Polyphonic Vocal Cords",
                 "Hai cặp dây thanh phụ cho phép phát nhiều tần số cùng lúc: "
                 "nghe vài phút là nhại lại chính xác giọng nói, ngữ điệu, "
                 "tiếng thở và tiếng cười của bất kỳ ai. Cùng bộ máy đó phát "
                 "được hạ âm 15–20 Hz — thứ âm thanh không ai nghe thấy nhưng "
                 "khiến người trong phòng thấy bất an và dễ bị dẫn dắt."),
                ("Tuyến pheromone xã hội — Social Pheromone Gland",
                 "Tuyến dưới da tổng hợp hỗn hợp oxytocin, vasopressin và "
                 "androstenone, pha theo đúng hồ sơ MHC của người đối diện. "
                 "Mục tiêu không nhận ra mình đang bị tác động; họ chỉ thấy kẻ "
                 "trước mặt quen thuộc và đáng tin một cách khó giải thích. "
                 "Khi cần gây rối, hắn đổi công thức sang pheromone adrenaline "
                 "để đẩy cả một đám đông vào kích động."),
                ("Hệ thần kinh gương cường hoá — Mirror Neuron Hyperplasia",
                 "Mật độ neuron gương gấp mười lần người thường. Hắn không "
                 "còn cần nhiều tuần nghiên cứu: quan sát 5–10 phút là hấp thụ "
                 "trọn ngôn ngữ cơ thể, biểu cảm vi mô, thói quen và cách phản "
                 "ứng xã hội của mục tiêu. Đây là thay đổi về chất — từ "
                 "“chuẩn bị kỹ lưỡng” thành “bắt chước tức thời”."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="Đây là chỗ hắn đi ngược mọi ác nhân Absolute khác: không "
                  "một dòng AI, không một con drone, không một cỗ máy tự "
                  "hành. Chameleon tin chỉ bộ não người mới đủ linh hoạt để "
                  "thao túng người — nên hạ tầng của hắn là công cụ thủ công "
                  "và người thật, thứ không hệ thống mạng nào rà ra được.",
            items=(
                ("Xưởng mặt nạ sinh học “Nhà máy Gương”",
                 "Một phòng thí nghiệm bí mật do các nhà khoa học bị khống chế "
                 "hoặc cuồng tín vận hành: nuôi cấy da nhân tạo, in sinh học "
                 "3D khuôn mặt, kính áp tròng mống mắt giả, găng silicon vân "
                 "tay, răng giả, miếng dán vi sinh da. Không có dây chuyền tự "
                 "động — từng món làm thủ công như đồ may đo, nên không để lại "
                 "dấu vết nào cho hệ thống giám sát công nghệ bắt được."),
                ("Kho lưu trữ bản sắc “Mật thất Nhân dạng”",
                 "Mạng lưới kho phân tán khắp thế giới, chứa DNA, mẫu giọng, "
                 "hồ sơ hành vi và thói quen của hàng chục nghìn nhân vật quan "
                 "trọng: chính trị gia, giám đốc ngân hàng, tướng lĩnh, người "
                 "nổi tiếng. Việc tra cứu và đối chiếu do con người làm, phần "
                 "lớn dữ liệu nằm trong trí nhớ của chính Chameleon — không có "
                 "cơ sở dữ liệu nào để hack, không có máy chủ nào để đánh sập."),
                ("Mạng lưới điệp viên “Hội Gương”",
                 "Một tổ chức gồm kẻ trung thành, người bị tống tiền, điệp "
                 "viên hai mang và những “bản sao” được đào tạo bài bản. Họ lo "
                 "chỗ ở, chứng cứ ngoại phạm, tin tình báo — và quan trọng "
                 "nhất là đóng thế để hắn có mặt ở nhiều nơi cùng lúc. Trong "
                 "lúc Chameleon đang là một tổng thống, một thành viên Hội "
                 "Gương khác đang là Chameleon ở đầu kia địa cầu."),
                ("Bộ công cụ sinh trắc giả “Bộ Mặt Thứ Hai”",
                 "Kính áp tròng in mống mắt, găng silicone vân tay, miếng dán "
                 "màng nhĩ đổi giọng, răng giả chỉnh khớp cắn. Tự thân là đồ "
                 "tĩnh, không mạch điện; ghép với phần nâng cấp sinh học thì "
                 "đủ vượt qua mọi vòng kiểm tra thông thường."),
                ("Máy phát nhiễu nhận thức “Khói Gương”",
                 "Thiết bị đeo nhỏ phát xung ánh sáng 30 Hz và âm thanh cận "
                 "ngưỡng, đồng bộ với sóng alpha của não người quan sát. Nó "
                 "khuếch đại hiện tượng pareidolia: bộ não vốn hay điền vào "
                 "chỗ trống theo kỳ vọng, nay điền hẳn ra đúng khuôn mặt mà "
                 "người đó đang mong được thấy, chứ không phải khuôn mặt "
                 "đang đứng trước họ. Không phải thôi miên — chỉ là bắt não "
                 "bỏ qua những sai lệch nhỏ."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Spider-Man mạnh về thể chất, nhanh, và có giác quan nhện. "
                  "Nhưng điểm yếu lớn nhất của Peter Parker không nằm ở phần "
                  "cứng: đó là trách nhiệm, lòng tin và những người anh "
                  "thương. Chameleon đánh đúng vào đó.",
            items=(
                ("Mây pheromone đồng minh",
                 "Miếng dán giải phóng hỗn hợp oxytocin và peptide MHC đặc "
                 "trưng của những người Peter yêu quý nhất — dì May, Mary "
                 "Jane, Harry Osborn. Giác quan nhện không toàn năng: nó là "
                 "một hệ đánh giá mối đe doạ dựa trên dữ liệu giác quan, nên "
                 "khi mọi tín hiệu hoá sinh đều báo “người thân, an toàn”, não "
                 "Peter đọc cái tín hiệu nguy hiểm yếu ớt kia thành lo âu "
                 "thường ngày. Anh do dự đúng một tích tắc — vừa đủ cho một "
                 "nhát dao từ phía sau."),
                ("Độc tố hoảng loạn nhện — Arachnid Panic Toxin",
                 "Độc tố thần kinh dạng khí, bắt chước cortisol và adrenaline "
                 "ngay trong thân não, kéo tụt ngưỡng kích hoạt của giác quan "
                 "nhện. Từ đó mọi thứ đều báo động: tiếng bước chân, giọt "
                 "nước, ánh đèn. Hệ cảnh báo không bị phá, nó bị làm cho vô "
                 "dụng — sau vài giờ Peter kiệt sức và không còn phân biệt "
                 "nổi nguy hiểm thật với nhiễu."),
                ("Nghịch lý bản sắc — Identity Paradox Protocol",
                 "Hắn không đối đầu trực diện. Hắn giả dạng lần lượt nhiều "
                 "người trong đời Peter và thả ra những thông tin đá nhau: dì "
                 "May gọi “đừng ra ngoài tối nay, dì cần con”, một giờ sau "
                 "Mary Jane nói “dì May bị Chameleon bắt rồi, đừng tin ai "
                 "cả”. Kèm theo là một chất gây rối loạn tái củng cố trí nhớ, "
                 "khiến Peter không xác minh nổi ký ức của chính mình. Giác "
                 "quan nhện phải qua não bộ mới thành hành động; một cái não "
                 "đã nghi ngờ tất cả sẽ bỏ qua cả tín hiệu thật."),
                ("Bầy người hoảng loạn",
                 "Hạ âm 19 Hz dựng lên nỗi sợ không có nguồn gốc, pheromone "
                 "đẩy nó thành bạo lực: cả một đám đông lao vào tấn công bất "
                 "cứ thứ gì chuyển động, kể cả Spider-Man. Peter không thể "
                 "đánh trả người vô tội nên chỉ còn cách chịu đòn và sơ tán, "
                 "trong khi giác quan nhện réo từ mọi hướng cho tới lúc quá "
                 "tải. Hắn bị vô hiệu hoá bằng chính những người anh đang bảo "
                 "vệ — Chameleon không cần ra mặt lấy một lần."),
            ),
        ),
    ),

    # Thang bậc đặt tên theo chữ cái Hy Lạp, đọc ngược từ Zeta lên Omega:
    # bậc càng cao thì phạm vi càng rộng, nhưng thời gian càng dài — hắn
    # không phá nhanh hơn, hắn phá xa hơn.
    tiers=(
        Tier("Tier Zeta", "Giả dạng tức thời",
             "Đổi mặt trong vài phút rồi bước qua các máy quét sinh trắc "
             "thông thường: phá hoại một công ty, lấy trọn tài liệu mật. Bản "
             "gốc cần hàng tuần chuẩn bị cho đúng một lần vào cửa; Absolute "
             "cần một buổi chiều.",
             "Vài giờ"),
        Tier("Tier Epsilon", "Một thành phố mất kiểm soát",
             "Thay giám đốc ngân hàng hoặc sĩ quan chỉ huy cảnh sát trong một "
             "ngày: rút cạn quỹ, bẻ hướng điều tra, châm ngòi bạo loạn cục "
             "bộ. Bản gốc chỉ gây rối được một tổ chức; Absolute làm cả thành "
             "phố tuột khỏi tay chính quyền của nó.",
             "6–12 giờ"),
        Tier("Tier Delta", "Tập đoàn & cơ quan tình báo",
             "Chiếm quyền điều hành một tập đoàn đa quốc gia hoặc một cơ quan "
             "tình báo: làm rò rỉ danh tính điệp viên, thao túng chứng khoán. "
             "Bản gốc không chạm nổi tới cấp nhà nước; Absolute làm sụp niềm "
             "tin của dân chúng vào chính phủ của họ.",
             "3–5 ngày"),
        Tier("Tier Gamma", "Lật đổ một chính phủ",
             "Thay bộ trưởng quốc phòng hoặc thống đốc ngân hàng trung ương: "
             "ra lệnh điều quân, phá giá tiền tệ, dựng một cuộc đảo chính ở "
             "nước nhỏ. Bước nhảy từ thành phố lên quốc gia — và không ai bắt "
             "được kẻ đã ký lệnh, vì kẻ đó vẫn đang ngồi ở bàn làm việc.",
             "Một tuần"),
        Tier("Tier Beta", "Xung đột giữa hai cường quốc",
             "Hội Gương đồng thời thay nhiều quan chức ở hai cường quốc, dựng "
             "bằng chứng giả về một vụ tấn công hạt nhân, đẩy cả hai quân đội "
             "vào trạng thái báo động. Bản gốc không thể gây ra một cuộc "
             "chiến; Absolute kích hoạt xung đột ở tầm lục địa.",
             "2–3 tuần"),
        Tier("Tier Alpha", "Tê liệt ngoại giao toàn cầu",
             "Giả mạo nhiều nguyên thủ cùng lúc, cắt đứt mọi kênh xác minh "
             "giữa các thủ đô, kích hoạt khủng hoảng tên lửa trên nhiều châu "
             "lục. Bản gốc là kẻ đóng vai người khác; Absolute là kẻ giật dây "
             "toàn bộ trật tự thế giới.",
             "Một tháng"),
        Tier("Tier Omega", "Sự sụp đổ bản sắc toàn cầu",
             "Đồng loạt thay thế và tống tiền giới lãnh đạo, phát tán bằng "
             "chứng sinh trắc giả mạo, phủ pheromone và Khói Gương lên đám "
             "đông cho tới khi hoang tưởng trở thành trạng thái đại chúng. Hệ "
             "thống tài chính đứng lại vì không xác minh nổi danh tính, các "
             "hiệp ước phòng thủ tan rã, chiến tranh hạt nhân có thể nổ ra "
             "chỉ vì một nhầm lẫn. Bản gốc là mối đe doạ cấp thành phố; "
             "Absolute khiến nền văn minh tự huỷ diệt chỉ bằng lòng tin bị "
             "đánh cắp.",
             "30 ngày"),
    ),

    # Nhãn giữ dưới 94 px, giá trị dưới 188 px: quá cỡ thì nhãn bị cắt, còn
    # giá trị bị đẩy xuống dòng riêng — mỗi dòng thừa làm bảng cao thêm ~14 px,
    # và bảng cao quá thì cả khối lý lịch bị dồn xuống cuối cột đọc
    # (`Card.fit`), để lại một khung chân dung phình to trống trơn.
    facts=(
        ("Cấp đe doạ", "Hành tinh — bằng lòng tin"),
        ("Nền tảng", "Sinh học · thủ công · người thật"),
        ("Không dùng", "AI · drone · máy tự động"),
        ("Sao chép", "Vân tay, mống mắt, vi sinh da"),
        ("Hạn bản sao", "48–72 giờ mỗi lần"),
        ("Rình mục tiêu", "5–10 phút quan sát"),
        ("Bậc Omega", "30 ngày  ·  toàn cầu"),
    ),

    blurb="Absolute Chameleon là mối đe doạ hành tinh không cần bắn một viên "
          "đạn. Hắn không phá thành phố bằng sức mạnh, hắn phá nền văn minh "
          "bằng cách đánh cắp lòng tin, bản sắc và mọi mối quan hệ giữa người "
          "với người. Với Spider-Man, hắn không cần thắng bằng cơ bắp — chỉ "
          "cần khiến Peter Parker thôi tin vào chính mình.",

    art=draw_absolute_chameleon,
    caption="Ảnh ghép từ Mật thất Nhân dạng  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Chameleon_(character)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Dmitri_Smerdyakov_(Earth-616)"),
    ),
)
