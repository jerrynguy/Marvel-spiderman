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
    """Feather Storm: lông vũ cơ khí tách khỏi mép cánh rồi trôi ra xa.

    Mỗi hạt là một lưỡi mảnh xoay đúng theo hướng bay của nó, không phải
    chấm tròn — nhìn là biết bầy drone chứ không phải bụi.
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
    """Hai thấu kính mắt và lò nhiệt hạch giữa ngực — thứ duy nhất tự phát sáng."""
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
    """Sagittarius khoá mục tiêu: khung ngắm nhảy chỗ, kèm sợi chỉ nối về mắt."""
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
    stamp="PHÂN LOẠI  ·  MỐI ĐE DOẠ CẤP QUỐC GIA",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="sky",
    evolve_fx="shred",       # vuốt xé tờ giấy rồi cuốn đi, không nổ

    tagline="The Apex Predator · The Sky Tyrant. Làm chủ bầu trời, phá huỷ "
            "mặt đất — một ông già trong bộ cánh đã thành thứ không quân "
            "nào bắn tới.",

    summary=(
        "Bản gốc chỉ là một ông già mặc bộ cánh bay lượn. Để thành thế lực "
        "cấp quốc gia, chính cơ thể sinh học của Adrian Toomes và bộ cánh của "
        "hắn được tái cấu trúc toàn bộ theo nguyên lý của loài chim săn mồi "
        "đã tuyệt chủng — Argentavis magnificens — kết hợp với vật liệu siêu "
        "nhẹ.",

        "Bộ cánh từ trường ngày xưa nay là một Hệ thống Săn mồi Trên không "
        "Tích hợp: động cơ nhiệt hạch, mười nghìn lông vũ biết bay tách rời, "
        "và một AI đọc trước ba giây mọi chuyển động của con mồi. Toomes "
        "không còn đi cướp nữa — hắn đóng cửa cả một vùng trời.",
    ),

    sections=(
        Section(
            title="Khuếch đại năng lực vật lý & sinh học",
            intro="Toomes không còn là ông già yếu ớt: từ bộ xương trở đi, "
                  "mọi thứ trong người hắn đều được thay để chịu được tốc độ.",
            items=(
                ("Bộ xương khí động học",
                 "Xương được thay bằng mạng hợp kim cấu trúc rỗng tổ ong, nhẹ "
                 "hơn xương người 80% nhưng cứng hơn titan. Hắn chịu được lực "
                 "G cực lớn khi bổ nhào ở Mach 3 mà nội tạng không vỡ."),
                ("Mắt chim săn mồi & gia tốc thần kinh",
                 "Võng mạc thay bằng thấu kính sinh học tổng hợp: phóng đại "
                 "quang học 50 lần, nhìn được cả tử ngoại lẫn hồng ngoại. Dây "
                 "thần kinh thị giác khuếch đại bằng sợi nano truyền tín hiệu "
                 "nhanh gấp 10 lần não thường — đủ để thấy viên đạn đang bay."),
                ("Nội tạng chống áp suất",
                 "Phổi và hệ tuần hoàn bọc trong lớp mô tổng hợp đàn hồi. Bổ "
                 "nhào từ 15.000 mét ở tốc độ siêu thanh, cơ thể tự điều chỉnh "
                 "áp suất nội môi thay vì vỡ phổi."),
                ("Móng vuốt đầu vibranium",
                 "Vuốt tay và chân dao động ở tần số cao. Chạm vào bất cứ vật "
                 "rắn nào — bê tông cốt thép hay vỏ xe tăng — rung động phân "
                 "tử phá vỡ liên kết cấu trúc, hắn xé mọi thứ như xé giấy."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="Bộ cánh không còn là một khối liền. Nó là một hệ vũ khí "
                  "biết tự tháo rời.",
            items=(
                ("Lõi phản lực Aerospike Ramjet",
                 "Động cơ dòng thẳng ghép lò nhiệt hạch mini: tối đa Mach 5, "
                 "đồng thời treo lơ lửng hoàn hảo ở chế độ tàng hình âm thanh "
                 "— không một tiếng động."),
                ("Lưới drone “Feather Storm”",
                 "Mười nghìn lông vũ cơ khí tách khỏi khung cánh và bay tự do. "
                 "Ba việc: quét cảm biến 360 độ, đâm xuyên bằng động năng, và "
                 "kết thành lưới điện từ cắt đứt mọi thứ bay qua không phận."),
                ("AI “Sagittarius”",
                 "Dự đoán trước ba giây chuyển động của mục tiêu từ dữ liệu "
                 "sinh trắc, chuyển động cơ bắp và hướng gió. Với Spider-Man, "
                 "nó dựng bản đồ tư thế nhện rồi tính ra điểm mù duy nhất mà "
                 "Peter không né được dù giác quan có báo."),
                ("Sonic Boom Cascade",
                 "Bay siêu thanh thì bộ cánh sinh ra sóng xung kích; hệ vũ khí "
                 "gom chúng lại thành một lưỡi dao áp suất hẹp, san phẳng cả "
                 "dãy nhà mà không tốn một quả bom."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Mọi lợi thế của Peter đều bị bẻ thành điểm yếu chí mạng.",
            items=(
                ("Noise-Cancelling Mirage",
                 "Giác quan nhện báo nguy hiểm nhưng không phân biệt được mức "
                 "độ hay nguồn gốc nếu xung quanh cái gì cũng nguy hiểm. Mười "
                 "nghìn drone phát hạ âm và dao động điện từ mô phỏng đúng "
                 "“tần số của một cú đấm”, khiến giác quan réo liên tục ở mọi "
                 "hướng. Phản xạ của Peter chậm đi 1,5 giây — trong một trận "
                 "đánh tốc độ, 1,5 giây là cái chết."),
                ("“Moth's Dust” — bụi bướm đêm",
                 "Tơ nhện bền kéo cực cao, dao thường không cắt nổi. Nên khi "
                 "Peter bắn tơ, bầy Feather Storm phun ra đám mây hoá chất ở "
                 "đúng nhiệt độ nóng chảy của polyme, phá liên kết hydro và "
                 "liên kết chéo. Tơ tan thành tro sau 0,5 giây."),
                ("Khoá tứ chi bằng trường áp suất",
                 "Peter thoát được mọi loại còng, nên vũ khí này không dùng "
                 "xích. Bay ngang qua, hắn thả bốn con quay hồi chuyển bám vào "
                 "cổ tay cổ chân, tạo bong bóng chân không ép ngược hai tấn "
                 "trên mỗi centimet vuông. Mọi cú vung tay thành vô dụng — anh "
                 "ta bị chính không khí quanh mình đóng băng tại chỗ."),
            ),
        ),
    ),

    tiers=(
        Tier("Tier Alpha", "Phá hạ tầng giao thông & viễn thông",
             "Mười nghìn drone phủ kín một thành phố lớn, cắt đứt lưới điện "
             "ngầm, cáp quang và mọi cột sóng trên 100 km². Sân bay quốc tế "
             "đóng cửa vĩnh viễn vì drone xuyên thủng được động cơ máy bay dân "
             "dụng giữa không trung.",
             "30 phút cho một thành phố"),
        Tier("Tier Beta", "Đánh sập mạng lưới kinh tế & công nghiệp",
             "Dàn tên lửa hành trình siêu nhỏ trên lưng, Sagittarius quét ra "
             "điểm yếu nhất của nền kinh tế: nhà máy lọc dầu, trạm biến áp cao "
             "thế, kho dự trữ lương thực. Một phi vụ là 40% sản lượng điện tê "
             "liệt, hậu cần vỡ trận, chứng khoán sụp.",
             "45 phút bay qua một quốc gia nhỏ"),
        Tier("Tier Gamma", "Tiêu diệt lực lượng phản ứng nhanh",
             "Mach 5 cộng khả năng bẻ quỹ đạo gấp khúc: không tên lửa đất đối "
             "không hay tiêm kích thế hệ 5 nào bám kịp. Hắn bổ nhào từ tầng "
             "bình lưu, dùng vuốt tần số cao rạch đôi boong-ke chỉ huy và "
             "boong tàu sân bay trước khi phòng không kịp nhả đạn.",
             "4 phút cho trọn một phi đội 12 chiếc"),
    ),

    facts=(
        ("Danh hiệu", "The Apex Predator  ·  The Sky Tyrant"),
        ("Cấp đe doạ", "Quốc gia — làm chủ bầu trời, phá huỷ mặt đất"),
        ("Tốc độ tối đa", "Mach 5, treo lơ lửng không tiếng động"),
        ("Bầy drone", "10.000 lông vũ cơ khí tách rời"),
        ("Nguyên mẫu", "Argentavis magnificens"),
        ("Trần bay", "Tầng bình lưu, bổ nhào từ 15.000 m"),
    ),

    blurb="Chạm trán Spider-Man, hắn bay lên độ cao Peter không nhảy tới, bật "
          "False Positive Overload để phá hệ thần kinh, thả Moth's Dust để "
          "vô hiệu hoá tơ, rồi bổ nhào Mach 5 xuyên qua nạn nhân bằng móng "
          "vuốt. Nếu Peter sống sót, cậu ta sẽ không bao giờ dám bắn tơ hay né "
          "đòn trong bán kính 500 mét quanh Vulture nữa.",

    art=draw_absolute_vulture,
    caption="Dựng lại từ dữ liệu bay  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Vulture_(Marvel_Comics)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Adrian_Toomes_(Earth-616)"),
    ),
)
