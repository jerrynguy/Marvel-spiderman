"""
Absolute Vulture — Adrian Toomes, The Apex Predator.

Cũng như `chameleon_absolute.py`, file này không khai `PROFILE` nên sổ tra bỏ
qua nó; nó treo dưới hồ sơ gốc qua `evolution=ABSOLUTE` trong `vulture.py`.

Điều quan trọng: mỗi dạng Absolute phải khác hẳn nhau, không chỉ khác nội
dung. Chameleon là kẻ nấp trong đám đông — nền tím than, mực đỏ/lam, mặt nạ
vỡ thành dải trượt, và tờ giấy cũ thì nổ tung. Vulture sống trên tầng bình
lưu — nên bộ da là `sky` (thép lạnh và đèn natri), tờ giấy cũ bị vuốt xé rồi
cuốn đi trong gió (`evolve_fx="shred"`), còn chân dung thì chuyển động theo
ngôn ngữ của buồng lái: đường chân trời nghiêng theo cú lượn, bầy lông vũ
tách khỏi cánh, vòng nổ siêu thanh, và khung ngắm nhảy từ mục tiêu này sang
mục tiêu khác.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QLinearGradient, QPainter,
                           QPainterPath, QPen, QRadialGradient)

from theme import SKY

from .art import (H, W, Rolls, design, fan, glow, marks, mirrored, ribbon)
from .profile import Profile, Section, Tier

AMBER = SKY.red                  # đèn natri phía chân trời
STEEL = SKY.blue                 # ánh trời lạnh trên lưng
GOLD = SKY.yellow
SHELL = QColor("#05070C")        # bóng con chim, đen hơn cả nền trời
HORIZON = 106.0                  # đường chân trời khi máy bay thăng bằng
LIFT = 12.0                      # nâng cả con chim lên khỏi mặt đất

WING_ROOT = QPointF(43, 46)
# (góc, dài, nửa bề ngang) — cánh trái dựng ngược lên thành chữ V
WING = ((183, 41, 5.6), (198, 45, 5.9), (213, 44, 5.5),
        (228, 40, 4.9), (243, 34, 4.2), (256, 28, 3.4))


# ═══════════════════════════════════════════════════════════ hình khối
def _wings():
    left = fan(WING_ROOT, WING)
    return left.united(mirrored(left))


def _torso():
    body = QPainterPath()
    body.moveTo(41, 44)
    body.cubicTo(38.5, 54, 39.5, 66, 44, 77)
    body.lineTo(56, 77)
    body.cubicTo(60.5, 66, 61.5, 54, 59, 44)
    body.closeSubpath()
    return body


def _head():
    """Mũ giáp bó sát, hai bên hõm vào, mỏ chúc thẳng xuống thành một mũi nhọn."""
    head = QPainterPath()
    head.moveTo(50, 20.5)
    head.cubicTo(57.5, 20.5, 60, 26, 58.5, 32.5)
    head.cubicTo(57.5, 36, 55, 38.5, 52.5, 39.5)
    head.lineTo(50, 47.5)
    head.lineTo(47.5, 39.5)
    head.cubicTo(45, 38.5, 42.5, 36, 41.5, 32.5)
    head.cubicTo(40, 26, 42.5, 20.5, 50, 20.5)
    head.closeSubpath()
    return head


def _claws():
    """Chân nặng và ba móng quặp mỗi bên, chìa thẳng về phía người xem."""
    one = QPainterPath()
    one.addPath(ribbon(QPointF(46, 70), QPointF(42.5, 82), QPointF(39.5, 93),
                       5.0, 2.6))
    for tip, bend in (((23.5, 104), (31, 97)), ((36, 114), (37.5, 101)),
                      ((49.5, 105), (45, 98))):
        one.addPath(ribbon(QPointF(39.5, 92), QPointF(*bend), QPointF(*tip),
                           2.3, 0.16))
    return one


_WINGS = _wings()
_TORSO = _torso()
_HEAD = _head()
_CLAW = _claws()
_CLAWS = QPainterPath(_CLAW)
_CLAWS.addPath(mirrored(_CLAW))


def _tone(color, alpha):
    out = QColor(color)
    out.setAlpha(max(0, min(255, int(alpha))))
    return out


# ═══════════════════════════════════════════════════════════════ các lớp
def _sky(p):
    """Trời tầng bình lưu: đen kịt trên đỉnh, cháy dần xuống chân trời."""
    p.setPen(Qt.PenStyle.NoPen)
    wash = QLinearGradient(0, -6, 0, 126)
    wash.setColorAt(0.0, QColor("#05070F"))
    wash.setColorAt(0.34, QColor("#101B33"))
    wash.setColorAt(0.58, QColor("#3B2C4A"))
    wash.setColorAt(0.74, QColor("#8A4622"))
    wash.setColorAt(0.86, QColor("#C4661F"))
    wash.setColorAt(0.94, QColor("#1B1119"))
    wash.setColorAt(1.0, QColor("#06060C"))
    p.setBrush(wash)
    p.drawRect(QRectF(-6, -6, 112, 132))


def _world(p, t):
    """Mặt trời mọc sau lưng hắn, và cả chân trời nghiêng theo cú lượn.

    Con chim đứng yên, thế giới thì nghiêng — đó là cách buồng lái nói cho ta
    biết ai mới là kẻ đang bẻ lái. Đĩa mặt trời nằm ngay sau thân, để bóng
    hắn cắt ra khỏi nền trời thành một mảng đen tuyệt đối.
    """
    roll = 7.0 * math.sin(t * 0.34) + 2.2 * math.sin(t * 0.83 + 1.1)
    p.save()
    p.setClipRect(QRectF(-6, -6, 112, 132))
    p.translate(50, HORIZON)
    p.rotate(roll)
    p.setPen(Qt.PenStyle.NoPen)

    # quầng sáng khổng lồ, rồi mới tới đĩa mặt trời
    halo = QRadialGradient(QPointF(0, -14), 52)
    halo.setColorAt(0.0, _tone(QColor("#FFD79A"), 210))
    halo.setColorAt(0.24, _tone(AMBER, 130))
    halo.setColorAt(0.55, _tone(AMBER, 44))
    halo.setColorAt(1.0, _tone(AMBER, 0))
    p.setBrush(halo)
    p.drawRect(QRectF(-70, -70, 140, 76))

    disc = QRadialGradient(QPointF(0, -14), 15)
    disc.setColorAt(0.0, QColor("#FFF6E2"))
    disc.setColorAt(0.72, QColor("#FFD98C"))
    disc.setColorAt(1.0, _tone(QColor("#FFB347"), 210))
    p.setBrush(disc)
    p.drawEllipse(QPointF(0, -14), 14.5, 14.5)

    # mặt đất bên dưới nuốt hết ánh sáng
    p.setBrush(QColor("#08080F"))
    p.drawRect(QRectF(-90, 0.6, 180, 60))

    # mây: dải tối vắt ngang đĩa mặt trời, mép trên bắt lửa
    r = Rolls(5021963)
    for _ in range(10):
        cx = r(-70, 70)
        cy = r(-24, 24)
        cw = r(14, 38)
        p.setBrush(_tone(QColor("#150F1A"), 225))
        p.drawEllipse(QPointF(cx, cy), cw, r(1.2, 2.6))
        p.setBrush(_tone(QColor("#FFC978"), 90))
        p.drawEllipse(QPointF(cx, cy - 0.8), cw * 0.8, 0.5)

    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(QColor("#FFD79A"), 190), 0.8))
    p.drawLine(QPointF(-90, 0), QPointF(90, 0))

    # thang chúc ngóc: vạch ngắn trên và dưới, chừa khoảng giữa cho mục tiêu
    p.setPen(QPen(_tone(STEEL, 85), 0.5))
    for i in (-3, -2, -1, 1, 2, 3):
        y = i * 9.0
        half = 13 if abs(i) % 2 else 8
        p.drawLine(QPointF(-half, y), QPointF(-4, y))
        p.drawLine(QPointF(4, y), QPointF(half, y))
    p.restore()


def _shock(p, t):
    """Vòng nổ siêu thanh, cứ vài giây lại bung ra một cái rồi tan."""
    for lag in (0.0, 0.5):
        phase = ((t / 3.4) + lag) % 1.0
        if phase > 0.30:
            continue
        s = phase / 0.30
        radius = 10 + 74 * (s ** 0.6)
        ring = _tone(AMBER if lag else STEEL, int(95 * (1 - s) ** 1.9))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(ring, 0.3 + 1.5 * (1 - s)))
        p.drawEllipse(QPointF(50, 52), radius * 1.25, radius * 0.82)


def _storm(p, t):
    """Bão Lông Vũ: phiến lông tách khỏi mép cánh rồi bay thẳng ra xa.

    Mỗi hạt là một lưỡi mảnh xoay đúng theo hướng bay của nó, không phải
    chấm tròn — nhìn là biết dao bay chứ không phải bụi. Chúng đi thẳng và
    không đổi ý giữa đường: đây là đạn, không phải drone.
    """
    r = Rolls(2051963)
    p.setPen(Qt.PenStyle.NoPen)
    for i in range(120):
        u = r(0, 1)
        span = r(0.5, 1.0)
        speed = r(0.22, 0.62)
        phase = r(0, 1)
        drift = r(-16, 16)
        side = 1 if i % 2 else -1

        a_src = math.radians(183 + u * 73)
        reach = (41 - u * 12) * span
        sx = WING_ROOT.x() + math.cos(a_src) * reach
        sy = WING_ROOT.y() + math.sin(a_src) * reach
        if side > 0:
            sx = W - sx

        travel = (t * speed + phase) % 1.0
        a_fly = math.radians((0 if side > 0 else 180) - 34 + drift)
        dist = 34 * travel
        x = sx + math.cos(a_fly) * dist * side * (1 if side > 0 else -1)
        y = sy + math.sin(a_fly) * dist
        if not (-8 < x < 108 and -8 < y < 128):
            continue

        fade = math.sin(math.pi * travel)
        blade = QColor(STEEL if i % 5 else AMBER)
        blade.setAlpha(int(190 * fade))
        p.setBrush(blade)
        p.save()
        p.translate(x, y)
        p.rotate(math.degrees(a_fly) * (1 if side > 0 else -1))
        p.drawRect(QRectF(-1.3, -0.22, 2.6, 0.44))
        p.restore()


def _figure(p):
    """Bóng con chim: mảng đen tuyệt đối, chỉ viền là bắt sáng.

    Ngược sáng nên không dùng mực lệch trục như các chân dung khác — cái làm
    nên hình khối ở đây là hai đường viền: lửa mặt trời hắt từ dưới lên, ánh
    trời lạnh phủ từ trên xuống.
    """
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(SHELL)
    for path in (_WINGS, _TORSO, _HEAD):
        p.drawPath(path)

    # khe hở giữa các lông: vạch tối cắt mảng cánh cho khỏi bết thành một khối
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(QColor("#FFC066"), 60), 0.45))
    p.setClipPath(_WINGS)
    mirror_root = QPointF(W - WING_ROOT.x(), WING_ROOT.y())
    for angle, length, _ in WING:
        a = math.radians(angle)
        for root, sign in ((WING_ROOT, 1), (mirror_root, -1)):
            p.drawLine(
                QPointF(root.x() + sign * math.cos(a) * 7,
                        root.y() + math.sin(a) * 7),
                QPointF(root.x() + sign * math.cos(a) * (length - 3),
                        root.y() + math.sin(a) * (length - 3)))
    p.setClipping(False)

    # viền dưới: lửa. Viền trên: thép. Hai nét này gánh toàn bộ khối.
    p.save()
    p.setClipRect(QRectF(-8, 46, W + 16, 90))
    p.setPen(QPen(_tone(QColor("#FFCE86"), 205), 0.9))
    for path in (_WINGS, _TORSO, _HEAD):
        p.drawPath(path)
    p.restore()
    p.save()
    p.setClipRect(QRectF(-8, -8, W + 16, 54))
    p.setPen(QPen(_tone(STEEL, 120), 0.6))
    for path in (_WINGS, _HEAD, _TORSO):
        p.drawPath(path)
    p.restore()

    # đai giáp ngực, chỉ đủ thấy để biết đó là giáp chứ không phải da
    p.setPen(QPen(_tone(QColor("#FFB55E"), 60), 0.55))
    p.setClipPath(_TORSO)
    for y0, y1 in ((52, 56), (61, 65)):
        p.drawLine(QPointF(38, y0), QPointF(62, y1))
    p.setClipping(False)


def _talons(p, t):
    """Móng vuốt dao động tần số cao: bóng kép rung nhanh quanh lưỡi thật."""
    buzz = math.sin(t * 47.0)
    for color, off in ((AMBER, 0.42), (STEEL, -0.42)):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(_tone(color, 110))
        p.drawPath(_CLAWS.translated(off * buzz, off * buzz * 0.6))
    p.setBrush(SHELL)
    p.drawPath(_CLAWS)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(STEEL, 90), 0.5))
    p.drawPath(_CLAWS)

    # một chấm loé rất nhỏ ở đầu mỗi móng — chỗ liên kết vật chất sắp đứt
    for x, y in ((23.5, 104), (36, 114), (49.5, 105)):
        for sx in (x, W - x):
            glow(p, QPointF(sx, y), 1.3 + 0.4 * abs(buzz),
                 _tone(QColor("#DCEBFF"), int(70 + 60 * abs(buzz))))


def _face(p, t):
    """Hai thấu kính mắt và lò ăn xác thối giữa ngực — thứ duy nhất tự sáng.

    Lò không đốt nhiên liệu, nó rút điện của thứ khác; nên nhịp đập của nó là
    nhịp của một cái bụng đang no dần, không phải của một động cơ chạy đều.
    """
    beat = 0.55 + 0.45 * math.sin(t * 2.0)
    for side in (-1, 1):
        eye = QPointF(50 + side * 4.4, 30)
        glow(p, eye, 4.4 * (0.85 + 0.15 * beat), _tone(AMBER, int(150 * beat)))
        lens = QPainterPath()
        lens.moveTo(eye.x() - side * 0.6, eye.y() + 1.5)
        lens.lineTo(eye.x() + side * 4.6, eye.y() - 1.4)
        lens.lineTo(eye.x() + side * 4.6, eye.y() - 0.2)
        lens.lineTo(eye.x() - side * 0.6, eye.y() + 2.4)
        lens.closeSubpath()
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#FFE9C8"))
        p.drawPath(lens)

    core = QPointF(50, 57)
    glow(p, core, 7.0 * beat, _tone(AMBER, int(140 * beat)))
    p.setBrush(_tone(GOLD, int(150 + 100 * beat)))
    p.drawEllipse(core, 1.5, 1.5)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(AMBER, 190), 0.5))
    p.drawEllipse(core, 3.4, 3.4)


def _lock(p, t):
    """Khung ngắm nhảy chỗ, kèm sợi chỉ nối về mắt hắn.

    Không có máy nào chọn mục tiêu hộ: cảm biến thụ động chỉ dựng ra bản đồ,
    còn khoá vào ai là do chính Toomes — nên sợi chỉ nối về mắt, không nối về
    một hộp máy tính nào.
    """
    step = int(t / 1.45)
    r = Rolls(step * 7919 + 11)
    tx, ty = r(14, 86), r(58, 108)
    age = (t / 1.45) % 1.0
    grip = min(1.0, age * 5)          # bung rộng rồi siết lại quanh mục tiêu
    pad = 9.0 - 5.0 * grip

    fade = int(190 * min(1.0, (1 - age) * 3))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(AMBER, fade), 0.6))
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = tx + sx * pad, ty + sy * pad
            p.drawLine(QPointF(cx, cy), QPointF(cx - sx * 2.6, cy))
            p.drawLine(QPointF(cx, cy), QPointF(cx, cy - sy * 2.6))
    if grip > 0.9:
        p.setPen(QPen(_tone(AMBER, 55), 0.4))
        p.drawLine(QPointF(50, 33 - LIFT), QPointF(tx, ty))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(_tone(AMBER, fade))
        p.drawRect(QRectF(tx - 0.5, ty - 0.5, 1.0, 1.0))


def _gauges(p, t):
    """Hai cột số liệu ở lề: vạch trôi xuống, vì hắn đang lao xuống."""
    p.setBrush(Qt.BrushStyle.NoBrush)
    for x, sign, color in ((3.5, 1, STEEL), (96.5, -1, AMBER)):
        p.setPen(QPen(_tone(color, 70), 0.45))
        offset = (t * 13 * (1 if sign > 0 else 0.6)) % 8.0
        k = 0
        y = 12 + offset
        while y < 110:
            long_tick = k % 4 == 0
            p.drawLine(QPointF(x, y),
                       QPointF(x + sign * (4.5 if long_tick else 2.2), y))
            y += 8.0
            k += 1
        p.setPen(QPen(_tone(color, 130), 0.6))
        p.drawLine(QPointF(x, 10), QPointF(x, 112))


# ═════════════════════════════════════════════ ảnh nền dựng sẵn cho lớp tĩnh
_STILL = {}


def _still(scale):
    """Bóng con chim không đổi theo thời gian — vẽ một lần rồi dán lại.

    Đôi cánh là kết quả của phép hợp path nên tô rất tốn; để nó vẽ lại 25 lần
    mỗi giây thì phí, trong khi nó đứng yên suốt.
    """
    key = round(scale, 2)
    ready = _STILL.get(key)
    if ready is None:
        if len(_STILL) > 6:
            _STILL.clear()
        w = max(1, math.ceil(112 * scale))
        h = max(1, math.ceil(132 * scale))
        ready = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
        ready.fill(Qt.GlobalColor.transparent)
        q = QPainter(ready)
        q.setRenderHint(QPainter.RenderHint.Antialiasing)
        q.scale(scale, scale)
        q.translate(6, 6)
        _figure(q)
        q.end()
        _STILL[key] = ready
    return ready


def draw_absolute_vulture(p, rect, t=0.0):
    """Chân dung sống: nhận thêm `t` (giây) nên khung hồ sơ tự vẽ lại."""
    scale = min(rect.width() / W, rect.height() / H)
    still = _still(scale)
    with design(p, rect):
        _sky(p)
        _world(p, t)
        # Con chim được nâng lên khỏi đường chân trời: móng vuốt kết thúc ở
        # lưng chừng trời chứ không chạm đất, nếu không hắn trông như đang
        # đứng chứ không phải đang lao xuống.
        p.save()
        p.translate(0, -LIFT)
        _shock(p, t)
        p.drawImage(QRectF(-6, -6, still.width() / scale,
                           still.height() / scale), still)
        _talons(p, t)
        _face(p, t)
        _storm(p, t)
        p.restore()
        _lock(p, t)
        _gauges(p, t)
        marks(p, QColor("#5C6A80"))


# ═══════════════════════════════════════════════════════════════ hồ sơ
ABSOLUTE = Profile(
    name="Absolute Vulture",
    vi_name="Kền Kền Tuyệt Đối",
    real_name="Adrian Toomes",
    keys=("Vulture Absolute", "Apex Predator", "Sky Tyrant"),

    kicker="Hồ sơ tuyệt đối",
    stamp="PHÂN LOẠI  ·  MỐI ĐE DOẠ CẤP HÀNH TINH",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="sky",
    evolve_fx="shred",       # vuốt xé tờ giấy rồi cuốn đi, không nổ

    tagline="The Apex Predator · The Sky Tyrant. Kẻ ăn xác thối không giết "
            "con mồi — hắn bay vòng bên trên, chờ nền văn minh công nghiệp "
            "tự gục xuống, rồi mới đáp.",

    summary=(
        "Adrian Toomes chưa bao giờ có siêu năng lực. Hắn là một kỹ sư cơ khí "
        "thiên tài dựng bộ cánh điện từ từ vật liệu nhặt nhạnh, và hắn đánh "
        "theo đúng lối của loài kền kền: kiên nhẫn, lượn trên cao, không bao "
        "giờ đối đầu trực diện, chỉ lao xuống khi con mồi đã yếu hoặc mất "
        "cảnh giác. Động cơ của hắn là phẫn uất — bị hệ thống chèn ép, muốn "
        "giữ lấy gia đình, và căm ghét giới tinh hoa.",

        "Ba điểm yếu của bản gốc là tuổi tác, sự lệ thuộc vào bộ giáp, và cái "
        "tôi của một kẻ tự coi mình là nạn nhân. Absolute xoá hai điểm đầu: "
        "cơ thể lão hoá được tái cấu trúc thành một sinh vật lai cơ khí — "
        "sinh học, nên tách khỏi cánh hắn vẫn là sát thủ cận chiến. Điểm yếu "
        "thứ ba thì giữ nguyên, vì chính nó là động cơ.",

        "Bộ giáp Aasvogel Mk.VII không có AI tự hành. Nó chỉ có một bộ phản "
        "xạ bay giữ thăng bằng và né chướng ngại khi Toomes bị thương; mọi "
        "quyết định tấn công đều đi qua giao diện thần kinh của chính hắn. "
        "Đây không phải kẻ ngồi thả drone — đây là một con chim săn mồi tự "
        "chọn thời điểm bổ nhào.",
    ),

    sections=(
        Section(
            title="Khuếch đại năng lực vật lý & sinh học",
            intro="Bản gốc là một người đàn ông lão niên, thể chất bình "
                  "thường: mọi sức mạnh đến từ bộ giáp, tách khỏi giáp là gần "
                  "như vô hại. “Sinh lý Kền kền Apex” sửa đúng chỗ đó — cơ thể "
                  "thôi làm gánh nặng và trở thành một nửa của vũ khí.",
            items=(
                ("Hệ xương khí nén titan–hữu cơ",
                 "Xương thay bằng cấu trúc tổ ong từ titan xốp và sợi carbon: "
                 "nhẹ, nhưng chịu được lực nén của cú bổ nhào Mach 5. Các "
                 "khớp bọc trong bao hoạt dịch áp suất cao, cho biên độ "
                 "chuyển động vượt xa người thường — hắn gập người giữa không "
                 "trung theo những góc mà cột sống người không cho phép."),
                ("Hệ tuần hoàn perfluorocarbon",
                 "Máu được thay một phần bằng dung dịch perfluorocarbon tổng "
                 "hợp, hoà tan oxy gấp khoảng 20 lần hemoglobin. Nhờ đó hắn "
                 "bay ở tầng bình lưu 20.000–30.000 m mà không cần mặt nạ "
                 "dưỡng khí, và chịu được cú giảm áp đột ngột khi lao xuống. "
                 "Tim bọc cơ tim nhân tạo polyme dẫn điện, tự chỉnh nhịp theo "
                 "gia tốc."),
                ("Bó cơ Electro-Active Polymer",
                 "Sợi cơ được cấy xen kẽ polymer điện hoạt. Có dòng điện từ "
                 "bộ giáp, chúng co rút mạnh gấp 15 lần cơ người — đủ để nâng "
                 "một xe tải nhỏ mà không cần trợ lực khung ngoài. Quan trọng "
                 "hơn: bẻ gãy đôi cánh không còn là kết thúc trận đấu."),
                ("Giác quan kền kền",
                 "Thuỷ tinh thể đa quang phổ nhìn từ hồng ngoại tới cực tím, "
                 "vỏ não thị giác dựng lại ảnh độ phân giải cao từ 5 km. Tai "
                 "trong có màng rung áp điện, bắt được dao động không khí do "
                 "con mồi tạo ra trong bán kính 300 m. Xoang mũi mang một cơ "
                 "quan cảm từ, đủ để hắn định hướng theo từ trường Trái Đất "
                 "giữa đêm không trăng."),
                ("Tuyến thượng thận “Cơn điên kiếm ăn”",
                 "Căng thẳng cực độ thì tuyến thượng thận cấy ghép bơm ra hỗn "
                 "hợp adrenaline, norepinephrine và enzyme steroid tổng hợp: "
                 "tốc độ phản xạ tăng gấp đôi, ngưỡng chịu đau dâng lên, nỗi "
                 "sợ bị khoá lại. Đây đúng là hành vi của con kền kền lao vào "
                 "xác thối giữa bầy đối thủ — và cũng là lúc hắn nguy hiểm "
                 "nhất vì không còn biết lùi."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="“Bộ giáp Kền kền Aasvogel Mk.VII” là phần nối dài tự nhiên "
                  "của triết lý nhặt nhạnh và đánh từ trên cao. Nó không có AI "
                  "tự hành — chỉ một bộ phản xạ bay giữ thăng bằng và né "
                  "chướng ngại khi Toomes bị thương; mọi phát bắn đều do hắn "
                  "quyết, qua giao diện thần kinh.",
            items=(
                ("Cánh lông vũ hợp kim thông minh — “Bão Lông Vũ”",
                 "Bốn nghìn phiến lông vũ bằng hợp kim nhớ hình và graphene, "
                 "mỗi phiến xoay độc lập dưới điện trường: cánh phẳng thì lượn "
                 "không tiếng động, cánh xoáy thì bổ nhào. Rời khỏi khung, mỗi "
                 "phiến thành một mũi dao đơn phân tử bay theo quỹ đạo đạn đạo "
                 "nạp sẵn bằng tín hiệu điện từ. Phóng cả bầy một lượt là một "
                 "trận mưa dao cắt đứt dây điện, tháp ăng-ten, cầu thép. Đây "
                 "không phải drone: từng phiến chỉ là viên đạn đã nạp sẵn "
                 "đường bay, không có AI — và thu lại được bằng từ trường nếu "
                 "còn nguyên."),
                ("Lò phản ứng ăn xác thối",
                 "Bộ giáp không mang nhiên liệu, nó ăn năng lượng của môi "
                 "trường. Móng vuốt và mép cánh có dải đồng siêu dẫn: cắm vào "
                 "đường dây cao thế hay máy biến áp là rút điện thẳng. Lớp phủ "
                 "áp điện thu thêm nhiệt thải và động năng gió. Hắn “ăn” điện "
                 "của một thành phố theo đúng nghĩa đen, và lưới điện mất ổn "
                 "định là dấu chân hắn để lại."),
                ("Móng vuốt cộng hưởng huỷ kết dính",
                 "Titan pha cacbua vonfram, gắn bộ rung siêu âm áp điện. Chạm "
                 "vào bề mặt, chúng phát rung 40 kHz phá vỡ lực bám Van der "
                 "Waals — thứ giữ Spider-Man trên tường. Trong rãnh vuốt còn "
                 "tiết ra dung môi tơ nhện: hợp chất hydrocarbon thơm bẻ gãy "
                 "liên kết polypeptide, tơ chảy nhão ngay chỗ bị cắt."),
                ("Hệ thống cảm biến thụ động",
                 "Radar chủ động thì phát sóng, mà phát sóng là bị bắt bài — "
                 "nên bộ giáp chỉ dùng cảm biến quang học và từ trường thụ "
                 "động, dựng bản đồ chiến trường từ ánh sáng phản chiếu và "
                 "biến thiên từ trường. Hắn nhìn thấy tất cả mà không để lại "
                 "một tín hiệu nào: vẫn là con kền kền quan sát từ xa."),
                ("Thiết bị phóng “Mưa Xác Thối”",
                 "Khoang bụng giáp mang 200 kg đạn chùm — khối kim loại nặng, "
                 "bi thép, mảnh vỡ công trình. Thả từ độ cao 3.000 m, động "
                 "năng va chạm ngang một loạt pháo kích. Vì toàn là đồ nhặt "
                 "nhạnh nên bắn hết thì quay lại bãi phế liệu nạp thêm; không "
                 "có dây chuyền tiếp đạn nào để cắt đứt."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Cả bộ chiến thuật dựng trên bản chất kền kền: kiên nhẫn, "
                  "lượn trên cao, đánh chớp nhoáng từ trên xuống, và hiểu tâm "
                  "lý con mồi. Không đòn nào trong đây là một cuộc đấu tay đôi "
                  "sòng phẳng — kền kền không đánh sòng phẳng bao giờ.",
            items=(
                ("Bão Lông Vũ bão hoà giác quan nhện",
                 "Toomes không phá giác quan nhện, hắn làm nó quá tải. Bốn "
                 "nghìn phiến lông vũ lao đi ở tốc độ siêu thanh theo quỹ đạo "
                 "hỗn loạn, mỗi phiến mang một điện tích và hướng xoay khác "
                 "nhau, buộc giác quan nhện xử lý hàng nghìn tín hiệu đe doạ "
                 "cùng lúc. Trường điện từ dao động của chúng biến “cảm giác "
                 "báo động” thành tiếng ồn trắng; độ trễ thần kinh 0,3–0,5 "
                 "giây là vừa đủ cho một mũi dao cắt dây tơ hoặc găm vào vai."),
                ("Dung môi tơ nhện & rung siêu âm huỷ bám",
                 "Móng vuốt rung 40 kHz phá lực Van der Waals ở tay chân "
                 "Peter, cậu trượt khỏi tường như trượt trên kính ướt. Lông vũ "
                 "thì tẩm dung môi hydrocarbon thơm: cắt trúng tơ là tơ rã ra "
                 "thành từng chuỗi polypeptide rời. Mất bám và mất tơ, "
                 "Spider-Man mất luôn hai thứ làm nên mình — di chuyển và "
                 "giăng bẫy."),
                ("Khoá chết trên không",
                 "Vulture tuyệt đối không đánh dưới mặt đất, nơi Peter có "
                 "tường để bám và phố xá để mượn. Cánh xoáy thổi gió giật 200 "
                 "km/h cuốn bay mọi điểm bám, rồi móng vuốt kẹp cổ chân và kéo "
                 "cậu lên 12.000 m. Trên đó không khí loãng, âm 50 độ, tơ bắn "
                 "ra chẳng có gì để neo. Peter vùng thoát thì hắn chỉ việc thả "
                 "rơi tự do rồi bổ nhào đón đầu."),
                ("Phục kích thụ động",
                 "Kền kền không săn con mồi khoẻ mạnh, nó chờ con mồi kiệt "
                 "sức. Cảm biến thụ động cho phép Toomes bám theo Peter từ 3 "
                 "km mà không phát một tín hiệu nào — giác quan nhện không có "
                 "gì để bắt. Hắn đợi đúng lúc Peter đang đánh nhau với kẻ khác "
                 "hoặc đã bị thương mới lao xuống; giác quan đang chia cho "
                 "nhiều mối đe doạ, còn cú bổ nhào Mach 5 chỉ chừa lại 0,2 "
                 "giây để phản ứng."),
                ("Đòn tâm lý gia đình — mạng lưới “kền kền non”",
                 "Toomes vốn đã biết Peter Parker là ai và biết cậu sợ mất "
                 "những gì. Hắn nuôi một mạng lưới dân buôn phế liệu, thợ máy "
                 "và người lao động bất mãn để theo dõi gia đình Peter. Hắn "
                 "không ra tay với dì May — hắn gửi cho Peter ảnh dì May đi "
                 "chợ, ảnh bạn gái ở sân trường, kèm một chiếc lông vũ kim "
                 "loại. Đây là chiến tranh hao mòn: mất ngủ trước, sơ hở sau."),
            ),
        ),
    ),

    # Thang đọc ngược từ Zeta lên Omega, cùng lối với Chameleon: bậc càng cao
    # thì phạm vi càng rộng chứ không phải càng nhanh — kền kền không vội.
    tiers=(
        Tier("Tier Zeta", "Đe doạ đường phố",
             "Chế độ tối thiểu: không phóng lông vũ, chỉ cơ thể cường hoá và "
             "móng vuốt. Hạ gục trọn một đội cảnh sát trong vài phút. Bản gốc "
             "mà mất giáp thì chỉ còn là một lão già; Absolute mất cánh vẫn "
             "là sát thủ cận chiến.",
             "Vài phút"),
        Tier("Tier Epsilon", "Tàn phá một khu phố",
             "Phóng một phần Bão Lông Vũ vào một toà nhà: cắt dây cáp, làm "
             "sập trần, đẩy cả khu vào hoảng loạn. Một đồn cảnh sát bị xoá "
             "trong mười lăm phút.",
             "30 phút"),
        Tier("Tier Delta", "Vô hiệu hoá một căn cứ quân sự",
             "Móng vuốt và Mưa Xác Thối phá radar, kho đạn, bãi đáp trực "
             "thăng; cảm biến thụ động chỉ ra chỗ chôn đường ống nhiên liệu "
             "để một cú bổ nhào cắt đứt. Bộ giáp gốc chỉ trộm được vũ khí rồi "
             "chạy; Absolute biến cả căn cứ thành phế liệu — và phế liệu thì "
             "hắn nhặt được.",
             "1–2 giờ"),
        Tier("Tier Gamma", "Một thành phố bị phong toả",
             "Cắm móng vuốt vào trạm biến áp chính rút cạn điện, thả lông vũ "
             "cắt cáp ngầm làm tê liệt giao thông. Trong nửa ngày, một đô thị "
             "mười triệu dân rơi vào hỗn loạn mà không cần một quả bom nào.",
             "6–12 giờ"),
        Tier("Tier Beta", "Sụp đổ hạ tầng một quốc gia",
             "Bay dọc tuyến cao thế quốc gia, hút năng lượng từ nhiều trạm "
             "biến áp cùng lúc để tạo dao động điện áp đồng bộ — lưới điện cả "
             "nước sụp theo dây chuyền. Sân bay, bệnh viện, nhà máy lọc dầu "
             "dừng lại; một quốc gia công nghiệp bị đẩy về thời chưa có điện.",
             "24–72 giờ"),
        Tier("Tier Alpha", "Khủng hoảng đa quốc gia",
             "Ghép phá hoại năng lượng với phá hoại vận tải: lông vũ đơn phân "
             "tử cắt cáp quang biển ngay tại các điểm nút, cảng trung chuyển "
             "và kho dầu chiến lược bị đánh lần lượt. Chuỗi cung ứng toàn cầu "
             "đứt gãy trong khi chưa ai kịp gọi được cho ai.",
             "Một tuần"),
        Tier("Tier Omega", "“Cuộc săn toàn cầu”",
             "Nhờ hệ tuần hoàn perfluorocarbon và lò phản ứng ăn xác thối, "
             "hắn bay vòng quanh Trái Đất ở tầng bình lưu, lần lượt nhằm vào "
             "các nút sống còn: trạm biến áp siêu cao thế, cáp quang liên lục "
             "địa, trung tâm dữ liệu, sân bay và cảng biển chiến lược. Trong "
             "72 giờ, lưới điện Bắc Mỹ, châu Âu rồi Đông Á sụp theo nhau; "
             "ngân hàng, truyền thông và hậu cần quốc tế tê liệt. Trong 120 "
             "giờ, không còn chuyến bay thương mại hay tàu container nào an "
             "toàn. Hắn không cho nổ hành tinh — hắn làm nền văn minh công "
             "nghiệp gục xuống rồi ăn xác nó, đúng chất kền kền.",
             "72–120 giờ"),
    ),

    # Nhãn giữ dưới 94 px, giá trị dưới 188 px — xem chú thích cùng chỗ trong
    # `chameleon_absolute.py`: bảng lý lịch cao quá thì nó bị dồn xuống cuối
    # cột đọc và khung chân dung phình ra chiếm chỗ trống.
    facts=(
        ("Danh hiệu", "The Apex Predator · Sky Tyrant"),
        ("Cấp đe doạ", "Hành tinh · hạ tầng công nghiệp"),
        ("Bộ giáp", "Aasvogel Mk.VII · 4.000 phiến"),
        ("Nhiên liệu", "Rút từ lưới điện và gió"),
        ("Trần bay", "20.000–30.000 m"),
        ("Không dùng", "Chỉ phản xạ giữ thăng bằng"),
        ("Cuộc săn", "72–120 giờ  ·  Omega"),
    ),

    blurb="Absolute Vulture không phải kẻ huỷ diệt hành tinh theo nghĩa cho "
          "nó nổ tung. Hắn là một mối đe doạ hệ thống: biến nền văn minh công "
          "nghiệp thành xác thối rồi bay lượn bên trên nó. Mọi nâng cấp đều "
          "phục vụ đúng một triết lý — không giết ngay, mà chờ con mồi gục "
          "xuống.",

    art=draw_absolute_vulture,
    caption="Dựng lại từ dữ liệu bay  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Vulture_(Marvel_Comics)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Adrian_Toomes_(Earth-616)"),
    ),
)
