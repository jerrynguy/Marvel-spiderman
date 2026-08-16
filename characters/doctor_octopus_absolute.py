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


def _filaments(p, t):
    """Vi sợi tách khỏi càng, quẩn quanh, thỉnh thoảng dồn lại thành tấm chắn.

    Chúng không bay lấy: mỗi sợi vẫn là một mẩu xúc tu, vẫn nằm trong tay
    Otto. Cái quẩn quanh đó là chuyển động của hắn, không phải của chúng.
    """
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


def _seismic(p, t):
    """Vòng nghe địa chấn: một nan sáng quay đều quanh trục lò.

    Không phải radar hay LIDAR — hắn không phát gì ra cả. Nan quay chỉ là
    nhịp mà bản đồ rung động trong bán kính 50 km được dựng lại.
    """
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
        _seismic(p, t)
        _limbs(p, t)
        p.drawImage(QRectF(-6, -6, still.width() / scale,
                           still.height() / scale), still)
        _face(p, t, beat)
        _filaments(p, t)
        _gauges(p, t)
        marks(p, QColor("#6E5346"))


# ═══════════════════════════════════════════════════════════════ hồ sơ
ABSOLUTE = Profile(
    name="Absolute Doctor Octopus",
    vi_name="Bác Sĩ Bạch Tuộc Tuyệt Đối",
    real_name="Otto Gunther Octavius",
    keys=("Doctor Octopus Absolute",),

    kicker="Hồ sơ tuyệt đối",
    stamp="PHÂN LOẠI  ·  MỐI ĐE DOẠ CẤP HÀNH TINH",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="forge",
    evolve_fx="crush",       # bốn càng bấu vào, nén cho oằn rồi bẻ thành tảng

    tagline="Bạch tuộc Địa chấn Hạt nhân. Không huỷ diệt hành tinh — chỉ trở "
            "thành hệ thần kinh của nó, và mỗi nhịp đập là một trận động đất.",

    summary=(
        "Otto Octavius vốn là một thiên tài vật lý hạt nhân với bốn xúc tu cơ "
        "khí nối thẳng vào cột sống, quen đánh bằng kế hoạch nhiều lớp hơn là "
        "bằng sức. Toàn bộ sức mạnh của hắn đến từ trí tuệ và công nghệ; "
        "điểm yếu cốt tử cũng chỉ có hai — một cơ thể người thường, và một "
        "cái tôi khiêu khích là nổ.",

        "Bản Absolute vá cái thứ nhất và giữ nguyên cái thứ hai. Cột sống "
        "thành một lò tokamak, khung xương thành ống nano carbon pha sắt, "
        "não được cấy các nút giao thoa photon vướng víu để điều khiển tám "
        "xúc tu với độ trễ picosecond. Bốn càng thành tám cộng một càng trục, "
        "mỗi càng vươn được ba cây số và tự lắp thêm đốt bằng quặng nó nhặt "
        "dọc đường.",

        "Nhưng bước nhảy thật nằm ở chỗ khác: cắm xuống đất, tám xúc tu ấy "
        "thành một mạng thần kinh địa chấn. Otto nghe được mọi rung động "
        "trong bán kính 50 km, và biết cách trả lời chúng bằng những rung "
        "động của riêng mình — đúng tần số, đúng đứt gãy.",

        "Trong toàn hệ thống không có một dòng AI hay một chiếc drone nào. "
        "Otto tin tự động hoá là chỗ hở để người khác chọc vào, nên mọi thứ "
        "đều phải là phần nối dài của chính thân thể và thần kinh hắn — kể cả "
        "khi thứ phải điều khiển là một cơn động đất.",
    ),

    sections=(
        Section(
            title="Khuyếch đại năng lực vật lý & sinh học",
            intro="Bản gốc là người thường về mặt sinh học: xúc tu quật đổ "
                  "tường được, nhưng cái thân mang chúng thì vẫn bị thương như "
                  "mọi cái thân khác. Absolute vá đúng khoảng hở đó, không thêm "
                  "một siêu năng lực nào — chỉ thêm kỹ thuật.",
            items=(
                ("Cột sống Tokamak cá nhân",
                 "Cả cột sống bị thay bằng một lò nhiệt hạch dạng cột: plasma "
                 "deuterium–tritium giam trong từ trường siêu dẫn, công suất "
                 "đỉnh 5 terawatt nuôi trọn hệ thống. Hợp hạch không rải chất "
                 "thải phóng xạ ra xung quanh, nên hắn mang nó trong người "
                 "được — và nhờ nó, hắn sống nhiều ngày không cần ăn, không "
                 "cần oxy, chịu được cả nhiệt độ lõi lò."),
                ("Hệ xương carbon pha sắt",
                 "Khung xương tái cấu trúc bằng ống nano carbon pha sắt từ, "
                 "hấp thụ lực nén tới 500 tấn. Da phủ boron carbide và "
                 "graphene: chống đạn, chống bức xạ, chống cả xung điện từ — "
                 "thứ vũ khí đầu tiên người ta nghĩ tới khi đối đầu một kẻ "
                 "chạy bằng điện."),
                ("Thần kinh lượng tử điều khiển",
                 "Não được cấy các nút giao thoa photon vướng víu, truyền lệnh "
                 "xuống xúc tu với độ trễ tính bằng picosecond. Đây mới là "
                 "bước nhảy về chất: Otto thôi phản xạ như một con người, hắn "
                 "xử lý song song hàng nghìn luồng tín hiệu từ tám xúc tu và "
                 "từ cả mạng lưới ngoài kia cùng một lúc."),
                ("Hệ xúc tu bạch tuộc 8+1",
                 "Tám xúc tu chính — hai lưng, hai bên, bốn bụng — cộng một "
                 "càng trục mọc từ xương cụt. Lõi vẫn là truyền động thuỷ lực "
                 "áp suất cao, nhưng chiều dài thì không còn cố định: mỗi càng "
                 "vươn 3 km trong không khí, 10 km dưới nước bằng cách tự lắp "
                 "thêm đốt từ quặng sắt, silicon và carbon nhặt dọc đường. Mỗi "
                 "càng nâng 20.000 tấn, cả bộ là 160.000 tấn. Đầu càng đổi "
                 "được thành mỏ cắt plasma, súng điện từ, hoặc lưới vi sợi."),
                ("Mạng thần kinh địa chấn",
                 "Xúc tu tự vá lại bằng kim loại hút từ môi trường, nên đánh "
                 "gãy một càng chỉ là làm chậm hắn. Nhưng công dụng đáng sợ "
                 "nhất lại là lúc chúng cắm xuống đất: cả bộ thành một mạng "
                 "thần kinh địa chấn khổng lồ, nghe được mọi rung động trong "
                 "bán kính 50 km và dựng bản đồ thời gian thực của mọi vật "
                 "nặng trên 100 kg. Hắn trở thành hệ thần kinh của nền địa "
                 "chất đô thị — không cần nhìn cũng biết ai đang đứng ở đâu."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="Không một dòng AI, không một chiếc drone. Otto tin tự động "
                  "hoá là chỗ hở để người khác chọc vào — thứ gì tự quyết được "
                  "thì cũng bị chiếm quyền được — nên mọi hệ thống ở đây đều "
                  "chỉ là phần nối dài của thân thể và thần kinh hắn.",
            items=(
                ("Cụm lò nhiệt hạch nén quán tính",
                 "Tám lõi nhỏ gắn ở gốc mỗi xúc tu, mỗi lõi 1,5 GW, cộng lại "
                 "12 GW. Viên nhiên liệu deuterium–lithium được laser nén "
                 "quán tính kích nổ, và toàn bộ nhịp bắn ấy do thần kinh lượng "
                 "tử của Otto điều khiển trực tiếp — không có máy tính phụ trợ "
                 "nào đứng giữa để mà tấn công."),
                ("Mũi khoan plasma địa nhiệt",
                 "Đầu xúc tu phun plasma 10.000°C, khoan xuyên lớp vỏ Trái Đất "
                 "ở tốc độ 50 km/h. Hắn dùng chúng để đặt những “Bom Hài hoà” "
                 "vào đúng các đứt gãy kiến tạo: không phá bằng sức nổ, mà "
                 "bằng cách thúc cho vỏ Trái Đất làm nốt phần việc còn lại."),
                ("Bộ cộng hưởng thuỷ âm đại dương",
                 "Dưới nước, xúc tu phát hạ âm 7 Hz ở cường độ cực lớn, đúng "
                 "tần số dao động tự nhiên của tầng nước sâu. Cộng hưởng "
                 "khuếch đại năng lượng lên hàng nghìn lần và sinh ra sóng "
                 "thần — thứ vũ khí không cần mang theo một gam thuốc nổ nào."),
                ("Mạng lưới cáp bạch tuộc",
                 "Những “sâu cáp” — phân đoạn xúc tu dạng mảnh — bò theo tuyến "
                 "cáp ngầm dưới biển và cáp điện trong lòng đô thị, nối vật lý "
                 "vào lưới điện, cáp quang và đường ống dẫn khí. Chúng không "
                 "tự hành: từng sợi một đều do chính não Otto điều khiển, đúng "
                 "kiểu kiểm soát tuyệt đối của hắn. Không có gì để hack, vì "
                 "không có gì tự nghĩ."),
                ("Tháp cộng hưởng địa chấn lưu động",
                 "Tám tháp phát dựng quanh một thành phố, tạo sóng đứng trong "
                 "nền đất cho tới khi móng công trình hoá lỏng. Tháp không "
                 "chạy một mình được — phải có xúc tu của Otto cắm vào để "
                 "chỉnh tần số theo thời gian thực, nghĩa là muốn dừng chúng "
                 "thì phải tới chỗ hắn."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Bản gốc đã biết đánh nhiều hướng cùng lúc để giác quan nhện "
                  "không kịp chọn, và biết bẫy Peter bằng tâm lý thay vì bằng "
                  "sức. Absolute giữ nguyên lối đánh ấy, chỉ đẩy từng mảnh của "
                  "nó tới giới hạn vật lý.",
            items=(
                ("Tấn công đa vector bất định",
                 "Tám xúc tu tách thành 128 vi sợi, mỗi sợi chuyển động theo "
                 "quỹ đạo Brown hỗn loạn do một bộ tạo số ngẫu nhiên lượng tử "
                 "cầm nhịp. Giác quan nhện vốn báo được vì mối nguy có tính "
                 "xác định — có hướng, có ý đồ. Khi mọi vector đều nguy hiểm "
                 "và đều ngẫu nhiên thật, nó tụt xuống thành nhiễu trắng: vẫn "
                 "kêu, nhưng thôi chỉ được đường nào mà né."),
                ("Bẫy cộng hưởng tơ nhện",
                 "Tơ Spider-Man là chất lỏng đặc dần theo lực cắt, nên Otto "
                 "không đi phá sợi tơ đã bắn ra — hắn phá nó khi còn trong "
                 "ống. Một xung vi ba 2,4 GHz nhắm đúng bộ phóng, nhiệt vi "
                 "sóng làm chuỗi polymer đông đặc sớm; tơ bắn ra giòn và đứt "
                 "ngay tại chỗ. Mất đu dây, mất luôn trói."),
                ("Chặn trước giác quan nhện",
                 "Đầu xúc tu gắn cảm biến điện não siêu nhạy, đọc được xung "
                 "thần kinh tiền vận động trong não Peter ngay khi giác quan "
                 "nhện vừa kích hoạt — tức là biết cậu sắp né về đâu trước khi "
                 "chính cậu kịp cử động. Một mũi tên tungsten đã đợi sẵn ở "
                 "điểm đó. Giác quan nhện càng nhanh thì càng phản chủ, vì nó "
                 "là thứ báo trước cho Otto."),
                ("Kìm toả tiền đình",
                 "Hạ âm 7 Hz cộng hưởng với ống bán khuyên trong tai trong. "
                 "Sức mạnh và độ bám không cứu được ai khỏi mất thăng bằng: "
                 "Peter thôi chạy được trên vách, thôi lộn được giữa không "
                 "trung, chỉ còn chóng mặt và buồn nôn."),
                ("Chuỗi thảm hoạ bắt cóc tinh thần",
                 "Otto biết Peter sẽ không bao giờ tha thứ cho mình nếu bỏ mặc "
                 "người vô tội. Nên hắn cho sập ba toà nhà ở ba quận khác "
                 "nhau, rò rỉ hoá chất cạnh trường Mary Jane, và một trận rung "
                 "nhỏ ngay gần nhà dì May — tất cả cùng một lúc. Peter buộc "
                 "phải chọn một chỗ, và cái giá của bốn chỗ còn lại đánh gục "
                 "cậu trước khi trận đánh kịp bắt đầu."),
                ("Đòn kết liễu",
                 "Khi đối thủ đã mất thăng bằng, mất tơ và quá tải giác quan, "
                 "càng trục bọc cậu trong một kén ferrofluid rồi hoá rắn. Kén "
                 "siết lại từ từ; giãy thì nó dẫn điện, hoặc chiếu xạ. Không "
                 "phải một cú đấm kết thúc trận đấu — là một cái ôm."),
            ),
        ),
    ),

    # Thang chữ cái Hy Lạp, đọc từ Zeta lên Omega như ba dạng Absolute kia.
    # Bậc Delta có ghi mốc so với bản gốc: đó là trần của Otto ngày xưa.
    tiers=(
        Tier("Tier Zeta", "Một toà nhà, một tiểu đội",
             "Một xúc tu là đủ: quật đổ toà nhà, xoá sổ một tiểu đội vũ trang. "
             "Không cần chuẩn bị, không cần vũ khí địa chấn.",
             "Vài giây"),
        Tier("Tier Epsilon", "San phẳng một khu phố",
             "Đánh gãy cột chống của cả dãy nhà rồi để cháy nổ lan theo dây "
             "chuyền — hắn chỉ cần chọn đúng vài điểm chịu lực, phần còn lại "
             "do trọng lực làm.",
             "5 phút"),
        Tier("Tier Delta", "Một quận của siêu đô thị",
             "Cắt điện, cắt nước, sập cầu đường, xoá trọn một quận. Đây chính "
             "là trần của bản gốc — mối đe doạ cấp thành phố mà Otto ngày xưa "
             "phải chuẩn bị hàng tuần mới với tới. Absolute làm y như vậy chỉ "
             "bằng một xúc tu, chưa đụng tới vũ khí địa chấn.",
             "10–30 phút"),
        Tier("Tier Gamma", "Sụp đổ một siêu đô thị",
             "Cắm xúc tu xuống nền đất và kích hoạt hoá lỏng toàn diện: móng "
             "công trình mất sức chịu, điện nước giao thông viễn thông đứt "
             "cùng lúc. Thành phố không bị đánh sập — nó bị rút nền ra từ bên "
             "dưới.",
             "2 giờ"),
        Tier("Tier Beta", "Tê liệt một quốc gia",
             "Đánh đồng thời lưới điện quốc gia và các tuyến cáp ngầm: mất "
             "điện toàn quốc, hệ thống tài chính đứng, liên lạc quân sự đứt. "
             "Không có mặt trận nào để dàn quân, vì thứ tấn công đang nằm "
             "trong chính đường dây của họ.",
             "24 giờ"),
        Tier("Tier Alpha", "Thảm hoạ cấp châu lục",
             "Kích hoạt ba tới bốn đứt gãy lớn cùng lúc: động đất và sóng thần "
             "xoá hàng loạt thành phố ven biển, sản xuất lương thực của cả một "
             "châu lục vỡ trận.",
             "72 giờ"),
        Tier("Tier Omega", "“Chuỗi Bạch tuộc Địa chấn”",
             "Tám điểm nóng kiến tạo trên toàn cầu — Vành đai lửa Thái Bình "
             "Dương, Địa Trung Hải, đứt gãy San Andreas — được đánh thức cùng "
             "lúc. Sóng thần đập vào cả bờ đông lẫn bờ tây các lục địa, tro "
             "núi lửa che mờ ánh sáng, mùa màng mất trắng, chuỗi cung ứng và "
             "cùng với nó là kinh tế lẫn chính trị toàn cầu sụp theo. Hành "
             "tinh không bị huỷ diệt: chỉ có nền văn minh công nghiệp trên đó "
             "bị xoá sổ. Một sự kiện tuyệt chủng công nghiệp.",
             "30 ngày"),
    ),

    # Nhãn giữ dưới 94 px, giá trị dưới 188 px — xem chú thích cùng chỗ trong
    # `chameleon_absolute.py`: bảng cao quá thì nó bị dồn xuống cuối cột đọc.
    facts=(
        ("Cấp đe doạ", "Hành tinh · văn minh công nghiệp"),
        ("Nguồn", "Cột sống tokamak · 5 TW đỉnh"),
        ("Số càng", "8 + 1 càng trục"),
        ("Tầm với", "3 km trên cạn · 10 km dưới nước"),
        ("Sức nâng", "20.000 tấn mỗi càng"),
        ("Tai địa chấn", "Nghe rung động trong 50 km"),
        ("Không dùng", "AI · drone · máy tự hành"),
        ("Chuỗi Omega", "8 điểm kiến tạo  ·  30 ngày"),
    ),

    blurb="Hắn không phải kẻ huỷ diệt vũ trụ, và cũng chẳng buồn chiếm lấy "
          "thứ gì. Tám xúc tu cắm xuống đất biến hắn thành hệ thần kinh của "
          "chính nền địa chất mà loài người xây nhà lên trên — và một hệ thần "
          "kinh thì không cần phá cái gì cả, nó chỉ cần quyết định co lại.",

    art=draw_absolute_octopus,
    caption="Dựng lại từ dữ liệu cảm biến  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Doctor_Octopus"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Otto_Octavius_(Earth-616)"),
    ),
)
