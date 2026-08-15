"""
Absolute Doctor Octopus — Otto Octavius, khung công nghiệp sống.

Bản sắc riêng, khác cả ba dạng Absolute trước:
    · bộ da `forge` — nền sắt ám khói, gang chảy và đồng thau. Ba bộ kia đều
      lấy nền lạnh; đây là bộ ấm duy nhất, liếc một cái là biết ngay.
    · `evolve_fx="crush"` — giấy không nứt, không bị xé, cũng không bị ăn:
      bốn càng bấu vào, nén cho oằn rồi bẻ thành sáu tảng nặng. Tấm mới đóng
      lại như hai cánh cửa thép trượt vào nhau.
    · chân dung là dạng duy nhất mà nhân vật *tự cử động*: tám xúc tu uốn
      theo sóng, từng đốt một, mỗi khung hình dựng lại đường cong. Ba dạng
      kia đều có bóng người đứng yên và chỉ chi tiết nhỏ động đậy.

Vì xúc tu không đứng yên nên chỉ phần người mới được dựng sẵn vào ảnh nền.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QLinearGradient, QPainter,
                           QPainterPath, QPen, QRadialGradient)

from theme import FORGE

from .art import H, W, Rolls, design, glow, marks, ribbon
from .profile import Profile, Section, Tier

MOLTEN = FORGE.red               # gang chảy
BRASS = FORGE.blue               # đồng thau
ARC = FORGE.yellow               # hồ quang lạnh
SHELL = QColor("#080605")        # bóng máy, đen ám nâu
HUB = QPointF(50, 47)            # chỗ bộ càng cắm vào lưng
FLOOR = 104.0

# (góc gốc, độ dài, biên độ uốn, pha) — bốn càng trên vươn cao, bốn càng dưới
# chống xuống đất. Góc tính theo độ, 0 là hướng phải, âm là hướng lên.
LIMBS = ((-166, 52, 13, 0.0), (-134, 46, 11, 1.7), (-46, 46, 11, 3.1),
         (-14, 52, 13, 4.4), (150, 44, 9, 2.2), (118, 38, 8, 5.0),
         (62, 38, 8, 0.9), (30, 44, 9, 3.7))


def _tone(color, alpha):
    out = QColor(color)
    out.setAlpha(max(0, min(255, int(alpha))))
    return out


# ═══════════════════════════════════════════════════════════ hình khối
def _head():
    """Đầu, cộng mái tóc bát úp — thứ khiến người ta nhận ra Otto ngay."""
    head = QPainterPath()
    head.addEllipse(QPointF(50, 27.5), 7.2, 8.0)
    bowl = QPainterPath()
    bowl.moveTo(41.4, 24.5)
    bowl.cubicTo(41.0, 16.5, 45.0, 13.5, 50.0, 13.5)
    bowl.cubicTo(55.0, 13.5, 59.0, 16.5, 58.6, 24.5)
    bowl.lineTo(56.0, 22.4)
    bowl.lineTo(44.0, 22.4)
    bowl.closeSubpath()
    return head.united(bowl)


def _torso():
    body = QPainterPath()
    body.moveTo(41, 36)
    body.cubicTo(37, 44, 37.5, 54, 40, 62)
    body.lineTo(60, 62)
    body.cubicTo(62.5, 54, 63, 44, 59, 36)
    body.closeSubpath()
    return body


def _harness():
    """Bộ đai lưng mang lò phản ứng — chỗ tám càng mọc ra."""
    rig = QPainterPath()
    rig.moveTo(36, 40)
    rig.lineTo(64, 40)
    rig.lineTo(67, 50)
    rig.lineTo(62, 58)
    rig.lineTo(38, 58)
    rig.lineTo(33, 50)
    rig.closeSubpath()
    return rig


_HEAD = _head()
_TORSO = _torso()
_HARNESS = _harness()
_MAN = _TORSO.united(_HEAD).united(_HARNESS)


def _limb_curve(angle, length, sway, phase, t):
    """Ba điểm của một càng: gốc, chỗ gập, và đầu càng — đều trôi theo giờ."""
    a = math.radians(angle + sway * math.sin(t * 0.6 + phase))
    bend = math.radians(angle + sway * 2.4 * math.sin(t * 0.45 + phase * 1.3))
    mid = QPointF(HUB.x() + math.cos(bend) * length * 0.52,
                  HUB.y() + math.sin(bend) * length * 0.52)
    tip = QPointF(HUB.x() + math.cos(a) * length,
                  HUB.y() + math.sin(a) * length
                  + 3.0 * math.sin(t * 0.9 + phase))
    return HUB, mid, tip


def _claw(p, tip, mid, t, phase):
    """Ba ngạnh ở đầu càng, mở ra khép vào theo nhịp riêng của từng càng."""
    grip = 0.5 + 0.5 * math.sin(t * 1.1 + phase)
    a = math.atan2(tip.y() - mid.y(), tip.x() - mid.x())
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(BRASS, 120), 0.7))
    for k in (-1, 1):
        spread = math.radians(16 + 20 * grip) * k
        p.drawLine(tip, QPointF(tip.x() + math.cos(a + spread) * 2.7,
                                tip.y() + math.sin(a + spread) * 2.7))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_tone(MOLTEN, int(120 + 90 * grip)))
    p.drawEllipse(tip, 0.8, 0.8)


# ═══════════════════════════════════════════════════════════════ các lớp
def _hall(p, t):
    """Gian xưởng tối: khói ám, sàn bê tông, vệt sáng hắt từ lò trên lưng."""
    p.setPen(Qt.PenStyle.NoPen)
    wash = QLinearGradient(0, -6, 0, 126)
    wash.setColorAt(0.0, QColor("#0A0706"))
    wash.setColorAt(0.40, QColor("#1A100C"))
    wash.setColorAt(0.72, QColor("#2A1509"))
    wash.setColorAt(0.88, QColor("#120B08"))
    wash.setColorAt(1.0, QColor("#070505"))
    p.setBrush(wash)
    p.drawRect(QRectF(-6, -6, 112, 132))

    # sàn xưởng: mép sàn bắt sáng từ lò, mặt sàn thì nứt và loang dầu
    p.setBrush(QColor("#0B0807"))
    p.drawRect(QRectF(-6, FLOOR, 112, 132 - FLOOR))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(MOLTEN, 120), 0.7))
    p.drawLine(QPointF(-6, FLOOR), QPointF(106, FLOOR))
    r = Rolls(7071963)
    for _ in range(9):
        y = r(FLOOR + 2, 125)
        p.setPen(QPen(_tone(MOLTEN, r(16, 40)), 0.4))
        p.drawLine(QPointF(r(-6, 40), y), QPointF(r(60, 106), y))
    # vũng sáng dưới chân, chỗ càng chống xuống
    p.setPen(Qt.PenStyle.NoPen)
    for x in (26, 50, 74):
        pool = QRadialGradient(QPointF(x, FLOOR), 20)
        pool.setColorAt(0.0, _tone(MOLTEN, 46))
        pool.setColorAt(1.0, _tone(MOLTEN, 0))
        p.setBrush(pool)
        p.drawRect(QRectF(x - 22, FLOOR - 6, 44, 26))


def _reactor(p, t):
    """Lò nhiệt hạch trên lưng: nguồn sáng duy nhất của cả khung hình."""
    beat = 0.6 + 0.4 * math.sin(t * 2.2)
    core = QPointF(50, 45)
    bloom = QRadialGradient(core, 54 * (0.85 + 0.15 * beat))
    bloom.setColorAt(0.0, _tone(MOLTEN, int(120 * beat)))
    bloom.setColorAt(0.35, _tone(MOLTEN, int(38 * beat)))
    bloom.setColorAt(1.0, _tone(MOLTEN, 0))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(bloom)
    p.drawRect(QRectF(-6, -6, 112, 132))
    return beat


def _limbs(p, t):
    """Tám càng: mỗi khung hình dựng lại đường cong, nên chúng thật sự uốn."""
    for angle, length, sway, phase in LIMBS:
        root, mid, tip = _limb_curve(angle, length, sway, phase, t)
        arm = ribbon(root, mid, tip, 3.4, 1.5)
        p.setPen(Qt.PenStyle.NoPen)
        for color, dx, dy in ((MOLTEN, 0.9, 0.7), (BRASS, -0.9, -0.7)):
            p.setBrush(_tone(color, 80))
            p.drawPath(arm.translated(dx, dy))
        p.setBrush(SHELL)
        p.drawPath(arm)

        # đốt càng: vạch cắt ngang thân, vuông góc với hướng đi. Vẽ bằng vòng
        # tròn thì cả cánh tay hoá ra chuỗi hạt cườm.
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(_tone(BRASS, 70), 0.45))
        p.save()
        p.setClipPath(arm)
        for i in range(1, 10):
            u = i / 10.0
            v = 1 - u
            c = QPointF(v * v * root.x() + 2 * v * u * mid.x()
                        + u * u * tip.x(),
                        v * v * root.y() + 2 * v * u * mid.y()
                        + u * u * tip.y())
            dx = 2 * v * (mid.x() - root.x()) + 2 * u * (tip.x() - mid.x())
            dy = 2 * v * (mid.y() - root.y()) + 2 * u * (tip.y() - mid.y())
            n = math.hypot(dx, dy) or 1.0
            half = (3.4 + (1.5 - 3.4) * u) * 0.72
            p.drawLine(QPointF(c.x() - dy / n * half, c.y() + dx / n * half),
                       QPointF(c.x() + dy / n * half, c.y() - dx / n * half))
        p.restore()

        _claw(p, tip, mid, t, phase)


def _man(p):
    """Phần người: nhỏ, gọn, và đứng yên. Chỉ khối này được dựng sẵn."""
    p.setPen(Qt.PenStyle.NoPen)
    for color, dx, dy in ((MOLTEN, 1.0, 0.8), (BRASS, -1.0, -0.8)):
        p.setBrush(_tone(color, 85))
        p.drawPath(_MAN.translated(dx, dy))
    p.setBrush(SHELL)
    p.drawPath(_MAN)

    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(BRASS, 130), 0.6))
    p.drawPath(_HARNESS)
    p.setPen(QPen(_tone(MOLTEN, 120), 0.6))
    p.drawPath(_TORSO)
    p.drawPath(_HEAD)


def _face(p, t, beat):
    """Kính bảo hộ và cái lò — hai thứ duy nhất tự phát sáng trên người hắn."""
    glow(p, QPointF(50, 27), 6.4 * (0.85 + 0.15 * beat),
         _tone(MOLTEN, int(120 * beat)))
    # kính bảo hộ tròn — dấu hiệu nhận dạng của Otto — nhưng nhỏ, nằm sâu
    # dưới một hàng lông mày nặng, để nó ra kính chứ không ra hai con mắt tròn
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_tone(SHELL, 255))
    p.drawRect(QRectF(43.6, 23.4, 12.8, 1.7))
    for sx in (-1, 1):
        c = QPointF(50 + sx * 3.5, 27.0)
        p.setBrush(_tone(MOLTEN, int(170 * beat)))
        p.drawEllipse(c, 2.4, 2.0)
        p.setBrush(QColor("#FFE9C4"))
        p.drawEllipse(c, 0.8, 0.7)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(_tone(BRASS, 170), 0.5))
        p.drawEllipse(c, 2.4, 2.0)
        p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_tone(SHELL, 235))
    p.drawRect(QRectF(48.7, 25.4, 2.6, 3.0))

    core = QPointF(50, 49)
    glow(p, core, 8.0 * beat, _tone(MOLTEN, int(170 * beat)))
    p.setBrush(_tone(ARC, int(150 + 100 * beat)))
    p.drawEllipse(core, 1.8, 1.8)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(BRASS, 190), 0.6))
    p.drawEllipse(core, 4.2, 4.2)
    p.setPen(QPen(_tone(MOLTEN, 110), 0.4))
    p.drawEllipse(core, 6.4, 6.4)


def _mites(p, t):
    """Octo-Mites: bầy drone quẩn quanh, thỉnh thoảng dồn thành tấm chắn."""
    shield = max(0.0, math.sin(t * 0.42) - 0.55) / 0.45   # từng chặp mới dồn
    r = Rolls(3071963)
    p.setPen(Qt.PenStyle.NoPen)
    for i in range(90):
        base = r(0, 360)
        speed = r(6, 20)
        radius = 16 + r(0, 6) ** 2
        a = math.radians(base + t * speed)
        fx = 50 + math.cos(a) * radius * 1.15
        fy = 46 + math.sin(a) * radius * 0.9
        # khi dồn: xếp thành lưới phẳng ngay trước ngực
        gx = 30 + (i % 15) * 2.9
        gy = 60 + (i // 15) * 2.6
        x = fx + (gx - fx) * shield
        y = fy + (gy - fy) * shield
        tone = QColor(BRASS if i % 4 else MOLTEN)
        tone.setAlpha(int(70 + 120 * max(shield,
                                         abs(math.sin(t * 2 + i * 0.7)))))
        p.setBrush(tone)
        p.drawRect(QRectF(x, y, 0.75, 0.75))


def _lidar(p, t):
    """Quét LIDAR 360°: một nan sáng quay đều quanh trục lò."""
    a = (t * 66) % 360
    p.setPen(Qt.PenStyle.NoPen)
    sweep = QRadialGradient(QPointF(50, 46), 58)
    sweep.setColorAt(0.0, _tone(ARC, 40))
    sweep.setColorAt(1.0, _tone(ARC, 0))
    p.setBrush(sweep)
    p.save()
    p.translate(50, 46)
    p.rotate(a)
    wedge = QPainterPath()
    wedge.moveTo(0, 0)
    wedge.lineTo(58, -7)
    wedge.lineTo(58, 7)
    wedge.closeSubpath()
    p.drawPath(wedge)
    p.restore()


def _gauges(p, t):
    """Đồng hồ áp suất thuỷ lực ở lề — kim rung quanh vạch 12.000 psi."""
    needle = 0.62 + 0.06 * math.sin(t * 3.1) + 0.03 * math.sin(t * 7.7)
    for cx, cy in ((7, 12), (93, 12)):
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(_tone(BRASS, 90), 0.5))
        p.drawEllipse(QPointF(cx, cy), 4.4, 4.4)
        for k in range(7):
            a = math.radians(140 + k * 43)
            p.drawLine(QPointF(cx + math.cos(a) * 3.2,
                               cy + math.sin(a) * 3.2),
                       QPointF(cx + math.cos(a) * 4.2,
                               cy + math.sin(a) * 4.2))
        a = math.radians(140 + needle * 258)
        p.setPen(QPen(_tone(MOLTEN, 210), 0.7))
        p.drawLine(QPointF(cx, cy), QPointF(cx + math.cos(a) * 3.6,
                                            cy + math.sin(a) * 3.6))


# ═════════════════════════════════════════════ ảnh nền dựng sẵn cho lớp tĩnh
_STILL = {}


def _still(scale):
    """Chỉ mỗi phần người là tĩnh; tám càng thì khung nào cũng phải vẽ lại."""
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
        _man(q)
        q.end()
        _STILL[key] = ready
    return ready


def draw_absolute_octopus(p, rect, t=0.0):
    """Chân dung sống: nhận thêm `t` (giây) nên khung hồ sơ tự vẽ lại."""
    scale = min(rect.width() / W, rect.height() / H)
    still = _still(scale)
    with design(p, rect):
        _hall(p, t)
        beat = _reactor(p, t)
        _lidar(p, t)
        _limbs(p, t)
        p.drawImage(QRectF(-6, -6, still.width() / scale,
                           still.height() / scale), still)
        _face(p, t, beat)
        _mites(p, t)
        _gauges(p, t)
        marks(p, QColor("#6E5346"))


# ═══════════════════════════════════════════════════════════════ hồ sơ
ABSOLUTE = Profile(
    name="Absolute Doctor Octopus",
    vi_name="Bác Sĩ Bạch Tuộc Tuyệt Đối",
    real_name="Otto Gunther Octavius",
    keys=("Doctor Octopus Absolute",),

    kicker="Hồ sơ tuyệt đối",
    stamp="PHÂN LOẠI  ·  MỐI ĐE DOẠ CẤP QUỐC GIA",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="forge",
    evolve_fx="crush",       # bốn càng bấu vào, nén cho oằn rồi bẻ thành tảng

    tagline="Không còn là gã béo bám sau bốn cánh tay máy. Là một hệ thống vũ "
            "khí quốc gia có ý thức, vận hành bằng bộ não Otto Octavius.",

    summary=(
        "Ở bản Absolute, Otto trở thành một khung công nghiệp sống — sinh vật "
        "nửa người nửa máy được tối ưu hoá để điều khiển chiến trường. Cột "
        "sống sinh học bị bỏ đi, thay bằng chuỗi đốt titan-beryllium bọc ống "
        "nano carbon; tim thay bằng tim nhân tạo kép bơm dung dịch thuỷ lực "
        "12.000 psi; phổi thay bằng bộ trao đổi khí màng lọc.",

        "Bốn càng thành tám. Mỗi càng dài 9 mét, nặng 1,2 tấn, nâng được 80 "
        "tấn và đập ra 3 MJ — đủ xuyên bê tông cốt thép dày hai mét. Nhưng "
        "thứ khiến hắn thành mối đe doạ cấp quốc gia không phải sức mạnh ấy, "
        "mà là bộ não được cấy 12.000 vi điện cực nối thẳng vào một AI chỉ "
        "huy.",

        "Hắn không cần chiếm đất. Hắn biến một quốc gia thành nhà tù công "
        "nghiệp đang sụp đổ.",
    ),

    sections=(
        Section(
            title="Khuyếch đại năng lực vật lý & sinh học",
            intro="Gần như không còn bộ phận sinh học nào nguyên vẹn — mỗi thứ "
                  "bị thay đều để phục vụ việc vận hành tám chi cùng lúc.",
            items=(
                ("Khung xương và nội tạng thay thế",
                 "Đốt sống nhân tạo titan-beryllium bọc ống nano carbon, tuỷ "
                 "sống nằm trong vỏ giáp chống phản hồi lực. Tim nhân tạo kép "
                 "bơm thuỷ lực 12.000 psi nuôi toàn bộ chi máy. Phổi màng lọc "
                 "cho phép hoạt động trong chân không, dưới nước sâu 2.000 m "
                 "hoặc giữa khí độc công nghiệp."),
                ("Cơ tiêm sợi polymer",
                 "Chịu được gia tốc 40G và một cú đâm trực diện tương đương xe "
                 "tải 10 tấn ở 80 km/h."),
                ("12.000 vi điện cực xuyên vỏ não",
                 "Nối thẳng não vào AI. Phản xạ 0,07 giây, đủ để vận hành tám "
                 "xúc tu như tám chi thể thật chứ không phải tám cái máy."),
                ("Xúc tu bốn lớp",
                 "Lõi truyền động thuỷ lực và cơ điện hoá; giữa là cáp sợi "
                 "carbon xoắn chịu kéo 1.200 tấn; ngoài là giáp composite "
                 "chống đạn 20 mm; ngoài cùng là cảm biến áp điện phủ polymer "
                 "chống dính. Mỗi càng nâng 80 tấn, đầu càng đi 200 m/s, một "
                 "cú đập ra 3 MJ."),
                ("Module đầu càng, đổi trong 0,3 giây",
                 "Mũi khoan kim cương 30.000 vòng/phút · đèn plasma 3.000°C · "
                 "laser cắt 50 kW · súng bắn đinh điện từ Mach 4 · vòi phun "
                 "nitơ lỏng."),
                ("Lò nhiệt hạch 40 MW",
                 "Gắn trên lưng, nuôi toàn hệ thống. Bị phá thì cho một vụ nổ "
                 "sạch cỡ 50 kiloton — nhưng Otto không dùng nó làm bom tự sát "
                 "trừ khi bị dồn tới đường cùng."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="Bộ càng không phải vũ khí. Nó là một sở chỉ huy quân sự di "
                  "động.",
            items=(
                ("AI ORACLE-8",
                 "Octal Rational Adaptive Combat & Logistics Engine: tự học từ "
                 "2 triệu giờ mô phỏng cộng dữ liệu camera chiến trường thật. "
                 "Dự đoán chuyển động đối thủ trước 0,8 giây với độ chính xác "
                 "94%, xử lý đồng thời 50.000 nguồn — vệ tinh quang học, radar "
                 "xuyên tường, camera giao thông, micro định hướng, cảm biến "
                 "địa chấn — và xâm nhập được mạng quân sự cấp quốc gia để giả "
                 "lệnh điều động hoặc chiếm quyền drone."),
                ("Bầy Octo-Mites",
                 "10.000 drone cỡ 3 cm, bay 50 km/h, sạc bằng cách đậu lên "
                 "lưng Otto. Mỗi con mang tụ 50 kV hoặc 0,5 g chất nổ nano — "
                 "đủ cắt cáp quang, làm mù cảm biến, hoặc tiêm độc thần kinh. "
                 "Khi hắn đứng yên, cả bầy phủ lên người thành lớp giáp phản "
                 "ứng chặn đạn đạo."),
                ("Xúc tu tự hành",
                 "Mỗi càng tách rời khỏi khung chính và sống độc lập 120 phút "
                 "bằng pin dự phòng, làm việc như một con rắn máy: cắt cáp "
                 "ngầm, đặt mìn, khoan đường hầm."),
                ("Máy in nano trong thân càng",
                 "Chế vật liệu ngay tại chỗ: mìn dẻo bám bề mặt, dung môi phá "
                 "kim loại, bọt polymer nở 50 lần thể tích trong 2 giây để bịt "
                 "hầm hoặc giam mục tiêu, và chất bôi trơn siêu trơn xoá sạch "
                 "ma sát cả một khu vực."),
                ("Cảm biến diện rộng",
                 "LIDAR 360°, radar xuyên tường 200 m, sonar chủ động dưới "
                 "nước, từ kế dò kim loại và mìn, máy dò hoá chất cùng rung "
                 "động mặt đất tới 0,1 micron."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Mọi lợi thế của Spider-Man đều bị bẻ ngược thành điểm chết.",
            items=(
                ("Spider-Sense Flooder",
                 "Phát cùng lúc 40 tín hiệu đe doạ giả: loa siêu âm 18–40 kHz, "
                 "laser chớp 60 Hz, rung nền 0,5 mm, drone cắt ngang tầm nhìn. "
                 "Giác quan nhện buộc phải xử lý tất cả một lượt, gây co giật "
                 "nhẹ, buồn nôn, phản xạ chậm 0,4–0,6 giây. Mọi đòn của Otto "
                 "trở thành đòn chí mạng bị bỏ lỡ."),
                ("Web-Breaker 4.0",
                 "Dung môi enzyme serine protease trộn axit hữu cơ và chất "
                 "hoạt động bề mặt, phun sương 5 micron ở 280°C: tơ bị thuỷ "
                 "phân, mất 92% độ bền kéo trong 0,2 giây. Mặt càng phủ polymer "
                 "chống dính cộng rung siêu âm 40 kHz nên tơ không bám nổi."),
                ("Oracle Prediction",
                 "AI ghi 500 cú bắn tơ đầu tiên rồi tính ra chu kỳ tay, trọng "
                 "tâm, lực kéo, góc vung. Sau đó drone đã chờ sẵn ở điểm neo "
                 "để cắt dây hoặc đặt mìn, còn càng thì đánh vào đúng góc chết "
                 "của chu kỳ — chỗ không đổi hướng kịp."),
                ("Vibration Cage",
                 "Sóng âm 7 Hz cộng hưởng với dịch trong ống bán khuyên gây "
                 "chóng mặt và mất phương hướng; tám càng vây quanh thành một "
                 "lồng rung cộng hưởng, đứng còn không vững."),
                ("Magnetic Webbing Interference",
                 "Xung điện từ hẹp 10 kW làm hỏng van điện từ trong bộ bắn tơ: "
                 "tơ tắc hoặc bắn ngược, cơ động coi như hết."),
                ("Myosin Inhibitor",
                 "Sương nano chứa chất ức chế ATP thẩm thấu qua da, giảm 50% "
                 "lực co cơ trong 30 giây — mất luôn khả năng nâng đỡ, nắm bám "
                 "và phản công."),
            ),
        ),
    ),

    tiers=(
        Tier("Tier 1", "Đô thị",
             "Drone cắt trạm biến áp, xúc tu khoan ống dẫn khí đốt và cáp "
             "quang, AI mở van xả khí gây cháy lan. Ba tới năm triệu dân mất "
             "điện; cầu, toà nhà và hầm ngầm đổ sập.",
             "0 – 6 giờ"),
        Tier("Tier 2", "Vùng kinh tế",
             "Đục thủng tàu chở dầu, kích nổ kho xăng, giả mạo hệ thống hậu "
             "cần, phát tán hoá chất công nghiệp vào sông. Cảng biển, sân bay "
             "và nhà máy lọc dầu tê liệt, nguồn nước nhiễm độc.",
             "6 – 24 giờ"),
        Tier("Tier 3", "Quốc gia",
             "Đánh đồng bộ 50 trạm biến áp bằng drone kèm EMP bán kính 20 km; "
             "AI xâm nhập hệ thống IFF khiến tiêm kích bắn nhầm nhau; khoan "
             "thủng tàu khu trục từ dưới nước. Lưới điện quốc gia sụp, hải "
             "quân và không quân mất khả năng phản ứng.",
             "24 – 72 giờ"),
    ),

    facts=(
        ("Tên thật", "Otto Gunther Octavius"),
        ("Cấp đe doạ", "Quốc gia — dưới hành tinh/vũ trụ một bậc"),
        ("Số càng", "8  ·  mỗi càng 9 m, 1,2 tấn, nâng 80 tấn"),
        ("Lực một cú đập", "3 MJ  ·  đầu càng đi 200 m/s"),
        ("Thuỷ lực", "12.000 psi  ·  phản xạ 0,07 giây"),
        ("Nguồn", "Lò nhiệt hạch 40 MW trên lưng"),
        ("AI", "ORACLE-8  ·  dự đoán trước 0,8 giây, 94%"),
        ("Bầy drone", "10.000 Octo-Mites cỡ 3 cm"),
    ),

    blurb="Một tiểu đoàn thiết giáp 30 xe: vô hiệu trong 10 phút. Một tàu khu "
          "trục lớp Arleigh Burke: thủng vỏ dưới mực nước trong 3 phút. Một "
          "sân bay quân sự: tê liệt trong 5 phút. Và trong 48 giờ, một quốc "
          "gia nhỏ mất 60–70% hạ tầng thiết yếu — Otto không cần chiếm lấy nó, "
          "hắn chỉ cần tắt nó đi.",

    art=draw_absolute_octopus,
    caption="Dựng lại từ dữ liệu cảm biến  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Doctor_Octopus"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Otto_Octavius_(Earth-616)"),
    ),
)
