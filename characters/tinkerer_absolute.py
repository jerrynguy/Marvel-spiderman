"""
Absolute Tinkerer — Phin Mason, hệ sinh thái công nghệ sống.

Một lưu ý về nhân vật: hồ sơ gốc trong `tinkerer.py` là Phineas Mason, ông
già sửa radio ở ASM #2 (Earth-616). Dạng Absolute ở đây là Phin Mason —
Tinkerer của Earth-1048, và kẻ cô săn là Miles Morales chứ không phải Peter
Parker. Đó không phải nhầm lẫn mà là chính cái ý: "Tinkerer" vốn là một cái
nghề chứ không phải một con người, và cái nghề ấy đã sang tay.

Bản sắc riêng của dạng này, khác hẳn hai dạng Absolute trước:
    · bộ da `mesh` — graphite lạnh, mực đỏ tía và xanh axit
    · `evolve_fx="dissolve"` — tờ giấy cũ không nổ cũng không bị xé, nó bị ăn
      dần từ mép vào rồi xoắn thành một cơn lốc ô vuông
    · chân dung không lấy bối cảnh trời hay phố, mà lấy chính mạng lưới của
      cô làm nền: một lưới phối cảnh chạy về điểm tụ, sóng sáng lan trên đó,
      còn nửa dưới thân cô thì rã ra thành ô và trôi lên.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QLinearGradient, QPainter,
                           QPainterPath, QPen, QRadialGradient)

from theme import MESH

from .art import H, W, Rolls, design, glow, marks, ribbon
from .profile import Profile, Section, Tier

ACID = MESH.blue                 # xanh axit — màu của mạng lưới
FUCHSIA = MESH.red               # đỏ tía — màu của thứ đang bị chuyển hoá
LIME = MESH.yellow
SHELL = QColor("#04090A")        # bóng người, đen hơn cả nền
VP = QPointF(50, 50)             # điểm tụ của lưới phối cảnh
DEREZ_TOP = 78.0                 # từ đây trở xuống, thân cô bắt đầu rã


# ═══════════════════════════════════════════════════════════ hình khối
def _head():
    """Mũ trùm có chóp, mặt nạ thợ hàn với một khe kính ngang."""
    hood = QPainterPath()
    hood.moveTo(50, 10.5)
    hood.lineTo(56.5, 14.5)
    hood.lineTo(57, 22)
    hood.lineTo(54.5, 26.5)
    hood.lineTo(45.5, 26.5)
    hood.lineTo(43, 22)
    hood.lineTo(43.5, 14.5)
    hood.closeSubpath()
    collar = QPainterPath()
    collar.moveTo(44.5, 24)
    collar.lineTo(41, 30)
    collar.lineTo(45, 33)
    collar.lineTo(55, 33)
    collar.lineTo(59, 30)
    collar.lineTo(55.5, 24)
    collar.closeSubpath()
    return hood.united(collar)


def _torso():
    """Thân mảnh, vai xuôi, áo choàng xoè nhẹ ở hông."""
    body = QPainterPath()
    body.moveTo(37, 31)
    body.cubicTo(34.5, 40, 36, 51, 39.5, 59)
    body.lineTo(38, 71)
    body.lineTo(62, 71)
    body.lineTo(60.5, 59)
    body.cubicTo(64, 51, 65.5, 40, 63, 31)
    body.closeSubpath()
    return body


def _limbs():
    """Tay phải vươn ra cầm kiếm, tay trái buông; hai chân đứng tấn."""
    path = QPainterPath()
    path.addPath(ribbon(QPointF(39, 34), QPointF(31.5, 46), QPointF(26, 58),
                        3.0, 1.7))                      # tay cầm kiếm
    path.addEllipse(QPointF(26, 58), 2.1, 1.9)
    path.addPath(ribbon(QPointF(61, 34), QPointF(66, 47), QPointF(66.5, 61),
                        3.0, 1.7))                      # tay buông
    path.addPath(ribbon(QPointF(44.5, 68), QPointF(42.5, 86), QPointF(41, 105),
                        3.6, 2.2))
    path.addPath(ribbon(QPointF(55.5, 68), QPointF(57.5, 86), QPointF(59, 105),
                        3.6, 2.2))
    return path


_HEAD = _head()
_TORSO = _torso()
_LIMBS = _limbs()

# Hợp lại thành một bóng liền: nếu chỉ chồng path lên nhau thì mỗi chi lại
# được viền riêng, và cô trông như hình que ghép bằng ống neon.
_BODY = _HEAD.united(_TORSO).united(_LIMBS)


def _derez_cells():
    """Những ô nằm trong bóng người ở khúc dưới — chỗ cô rã ra thành lưới."""
    cells = []
    step = 2.4
    y = DEREZ_TOP - 4
    while y < 110:
        x = 30.0
        while x < 70:
            if _BODY.contains(QPointF(x + step / 2, y + step / 2)):
                cells.append((x, y))
            x += step
        y += step
    return tuple(cells)


_CELLS = _derez_cells()


def _tone(color, alpha):
    out = QColor(color)
    out.setAlpha(max(0, min(255, int(alpha))))
    return out


# ═══════════════════════════════════════════════════════════════ các lớp
def _space(p):
    """Nền: hư không lạnh phía trên điểm tụ, tối dần xuống chân."""
    p.setPen(Qt.PenStyle.NoPen)
    wash = QLinearGradient(0, -6, 0, 126)
    wash.setColorAt(0.0, QColor("#040A0B"))
    wash.setColorAt(0.42, QColor("#08161A"))
    wash.setColorAt(0.60, QColor("#0B2320"))
    wash.setColorAt(1.0, QColor("#03080A"))
    p.setBrush(wash)
    p.drawRect(QRectF(-6, -6, 112, 132))

    halo = QRadialGradient(VP, 46)
    halo.setColorAt(0.0, _tone(ACID, 46))
    halo.setColorAt(0.5, _tone(ACID, 14))
    halo.setColorAt(1.0, _tone(ACID, 0))
    p.setBrush(halo)
    p.drawRect(QRectF(-6, -6, 112, 108))


def _ground(p, t):
    """Lưới phối cảnh chạy về điểm tụ, sóng sáng lan ngược về phía người xem.

    Đây là mạng GPMC nhìn từ trên mặt đất: mọi vật chất trong tầm đều đã là
    của cô, và sóng lan trên lưới chính là lệnh đang chạy.
    """
    p.setBrush(Qt.BrushStyle.NoBrush)

    # nan quạt toả từ điểm tụ xuống mép dưới
    for k in range(-11, 12):
        far = QPointF(50 + k * 9, 128)
        tone = _tone(ACID, 34 if k % 2 else 54)
        p.setPen(QPen(tone, 0.4))
        p.drawLine(VP, far)

    # vạch ngang, càng gần người xem càng thưa; sóng chạy dọc theo chúng
    rows = 13
    for i in range(1, rows + 1):
        u = i / rows
        y = VP.y() + 72 * (u ** 2.3)
        if y > 124:
            break
        wave = (u - (t * 0.22) % 1.0) % 1.0
        lit = max(0.0, 1.0 - wave / 0.16)
        tone = _tone(FUCHSIA if lit > 0.35 else ACID,
                     int(30 + 40 * u + 150 * lit))
        p.setPen(QPen(tone, 0.4 + 0.9 * lit + 0.6 * u))
        p.drawLine(QPointF(-10, y), QPointF(110, y))

        # nút mạng sáng lên khi sóng chạy qua
        if lit > 0.1:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(_tone(FUCHSIA, int(190 * lit)))
            spread = 9 * (0.4 + u)
            for k in range(-5, 6):
                p.drawEllipse(QPointF(50 + k * spread, y),
                              0.5 + 0.7 * u, 0.5 + 0.7 * u)
            p.setBrush(Qt.BrushStyle.NoBrush)


def _foundry(p, t):
    """Hai lò phản ứng vật chất đứng trên lưới, nhả drone lên trời."""
    for x, depth in ((16, 0.34), (84, 0.52)):
        y = VP.y() + 72 * (depth ** 2.3)
        w = 3.4 + 7 * depth
        h = 2.2 + 4 * depth
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#050D0E"))
        p.drawRect(QRectF(x - w / 2, y - h, w, h))
        p.setBrush(_tone(ACID, 150))
        p.drawRect(QRectF(x - w / 2, y - h, w, 0.4))

        beat = 0.5 + 0.5 * math.sin(t * 1.6 + x)
        glow(p, QPointF(x, y - h), 3.2 * beat, _tone(ACID, int(90 * beat)))
        p.setBrush(_tone(LIME, 190))
        for k in range(3):
            rise = ((t * 0.5 + k * 0.33 + depth) % 1.0)
            p.drawEllipse(QPointF(x + math.sin(rise * 7 + k) * 2.4,
                                  y - h - rise * 22),
                          0.35, 0.35)


def _figure(p):
    """Bóng cô: mảng đen, viền axit bên trái và đỏ tía bên phải. Tĩnh.

    Chỉ vẽ phần thân còn nguyên. Từ `DEREZ_TOP` trở xuống không vẽ gì cả —
    khúc ấy do lớp ô đảm nhiệm, nên nửa dưới người cô đúng là đang rã chứ
    không phải bị rắc chấm lên trên.
    """
    p.save()
    p.setClipRect(QRectF(-8, -8, 116, DEREZ_TOP + 8))
    p.setPen(Qt.PenStyle.NoPen)
    for color, dx, dy in ((ACID, -1.0, -0.7), (FUCHSIA, 1.0, 0.7)):
        p.setBrush(_tone(color, 70))
        p.drawPath(_BODY.translated(dx, dy))
    p.setBrush(SHELL)
    p.drawPath(_BODY)

    p.setBrush(Qt.BrushStyle.NoBrush)
    p.save()
    p.setClipRect(QRectF(-8, -8, 58, 136))
    p.setPen(QPen(_tone(ACID, 105), 0.45))
    p.drawPath(_BODY)
    p.restore()
    p.save()
    p.setClipRect(QRectF(50, -8, 58, 136))
    p.setPen(QPen(_tone(FUCHSIA, 95), 0.45))
    p.drawPath(_BODY)
    p.restore()

    # mấy đường mạch chạy trên bộ giáp
    p.setPen(QPen(_tone(ACID, 70), 0.5))
    p.setClipPath(_TORSO)
    p.drawLine(QPointF(45, 33), QPointF(45, 68))
    p.drawLine(QPointF(55, 33), QPointF(55, 68))
    p.drawLine(QPointF(40, 55), QPointF(60, 55))
    p.drawLine(QPointF(40, 62), QPointF(60, 62))
    p.setClipping(False)
    p.restore()


def _visor(p, t):
    """Khe kính mặt nạ, và cái lõi năng lượng dự trữ đang vơi dần rồi đầy lại."""
    beat = 0.5 + 0.5 * math.sin(t * 2.6)
    glow(p, QPointF(50, 20), 5.0 * (0.8 + 0.2 * beat),
         _tone(FUCHSIA, int(130 * beat)))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#FFE4F6"))
    p.drawRect(QRectF(44.6, 18.4, 10.8, 1.6))
    p.setBrush(_tone(FUCHSIA, 200))
    p.drawRect(QRectF(44.6, 20.0, 10.8, 0.6))

    core = QPointF(50, 43)
    glow(p, core, 5.0 * beat, _tone(ACID, int(110 * beat)))
    p.setBrush(_tone(LIME, int(140 + 100 * beat)))
    p.drawEllipse(core, 1.3, 1.3)


def _blade(p, t):
    """Kiếm lượng tử: lưỡi thẳng, mép rung ở tần số cao nên nhoè thành hai."""
    hilt = QPointF(26, 58)
    tip = QPointF(10, 90)
    buzz = math.sin(t * 41.0) * 0.5
    for color, off, width in ((FUCHSIA, buzz, 2.2), (ACID, -buzz, 1.4)):
        p.setPen(QPen(_tone(color, 150), width))
        p.drawLine(QPointF(hilt.x() + off, hilt.y()),
                   QPointF(tip.x() + off, tip.y()))
    p.setPen(QPen(QColor("#FFFFFF"), 0.55))
    p.drawLine(hilt, tip)
    glow(p, tip, 3.4 + 0.8 * abs(buzz), _tone(FUCHSIA, 150))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#0A1214"))
    p.drawRect(QRectF(24.5, 55.8, 3.0, 4.2))


def _derez(p, t):
    """Nửa dưới thân cô là một đám ô: gần thắt lưng còn dày, xuống chân thì thưa.

    Mỗi ô có nhịp riêng — nằm yên tại chỗ một lúc rồi mới bứt lên và tan. Ô
    càng thấp thì nằm yên càng ngắn, nên cả khối rã dần từ dưới lên.
    """
    r = Rolls(1120)
    p.setPen(Qt.PenStyle.NoPen)
    for i, (x, y) in enumerate(_CELLS):
        speed = r(0.14, 0.42)
        phase = r(0, 1)
        sway = r(-3.4, 3.4)
        depth = min(1.0, max(0.0, (y - DEREZ_TOP + 4) / 30.0))
        settle = 0.72 - depth * 0.66        # thời gian ô còn bám vào thân
        travel = (t * speed + phase) % 1.0
        size = 1.9

        if travel < settle:                 # còn tại chỗ: vẫn là một phần thân
            hold = 1.0 - depth * 0.55
            p.setBrush(_tone(SHELL, int(255 * hold)))
            p.drawRect(QRectF(x, y, size, size))
            if r(0, 1) < 0.16:              # đôi ô loé lên, chực rời đi
                p.setBrush(_tone(ACID if i % 3 else FUCHSIA, int(150 * hold)))
                p.drawRect(QRectF(x, y, size, size))
            continue

        lift = (travel - settle) / max(0.05, 1.0 - settle)
        alpha = max(0.0, 1.0 - lift)
        if alpha <= 0:
            continue
        p.setBrush(_tone(ACID if i % 3 else FUCHSIA, int(210 * alpha)))
        p.drawRect(QRectF(x + sway * lift, y - lift * 30,
                          size * (1 - 0.45 * lift), size * (1 - 0.45 * lift)))


def _swarm(p, t):
    """Bụi nano lơ lửng phía trước, nhắc rằng không khí ở đây cũng là của cô."""
    r = Rolls(30112020)
    p.setPen(Qt.PenStyle.NoPen)
    for i in range(70):
        x0 = r(-4, 104)
        y0 = r(-4, 124)
        speed = r(0.05, 0.22)
        drift = ((t * speed + r(0, 1)) % 1.0)
        y = y0 - drift * 16
        fade = math.sin(math.pi * drift)
        p.setBrush(_tone(ACID if i % 4 else FUCHSIA, int(120 * fade)))
        size = r(0.35, 0.85)
        p.drawRect(QRectF(x0, y, size, size))


def _budget(p, t):
    """Vạch năng lượng dự trữ ở lề — điểm yếu cố hữu, vơi rồi lại đầy."""
    level = 0.45 + 0.4 * math.sin(t * 0.5)
    box = QRectF(4, 84, 2.6, 30)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(ACID, 90), 0.5))
    p.drawRect(box)
    p.setPen(Qt.PenStyle.NoPen)
    fill = QRectF(box.x() + 0.5, box.bottom() - 0.5 - (box.height() - 1) * level,
                  box.width() - 1, (box.height() - 1) * level)
    p.setBrush(_tone(LIME if level > 0.3 else FUCHSIA, 170))
    p.drawRect(fill)

    # cụm nút mạng ở góc trên phải, nhấp nháy như một bảng trạng thái
    r = Rolls(int(t * 3) * 131 + 7)
    for row in range(4):
        for col in range(4):
            on = r(0, 1) > 0.45
            p.setBrush(_tone(ACID if on else QColor("#12201E"),
                             190 if on else 120))
            p.drawRect(QRectF(88 + col * 2.6, 6 + row * 2.6, 1.7, 1.7))


# ═════════════════════════════════════════════ ảnh nền dựng sẵn cho lớp tĩnh
_STILL = {}


def _still(scale):
    """Bóng người đứng yên suốt — dựng một lần rồi dán, như hai dạng trước."""
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


def draw_absolute_tinkerer(p, rect, t=0.0):
    """Chân dung sống: nhận thêm `t` (giây) nên khung hồ sơ tự vẽ lại."""
    scale = min(rect.width() / W, rect.height() / H)
    still = _still(scale)
    with design(p, rect):
        _space(p)
        _ground(p, t)
        _foundry(p, t)
        p.drawImage(QRectF(-6, -6, still.width() / scale,
                           still.height() / scale), still)
        _derez(p, t)
        _visor(p, t)
        _blade(p, t)
        _swarm(p, t)
        _budget(p, t)
        marks(p, QColor("#4E6B60"))


# ═══════════════════════════════════════════════════════════════ hồ sơ
ABSOLUTE = Profile(
    name="Absolute Tinkerer",
    vi_name="Thợ Vặt Tuyệt Đối",
    real_name="Phin Mason",
    keys=("Tinkerer Absolute",),

    kicker="Hồ sơ tuyệt đối",
    stamp="PHÂN LOẠI  ·  MỐI ĐE DOẠ CẤP QUỐC GIA",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="mesh",
    evolve_fx="dissolve",    # giấy bị ăn dần rồi lắp lại, không nổ không xé

    tagline="Không phải một thiên tài chế đồ nữa. Là một hệ sinh thái công "
            "nghệ sống, nuốt cả một quốc gia từ bên trong.",

    summary=(
        "Cái tên Tinkerer chưa bao giờ là tên một người — nó là tên một nghề. "
        "Phineas Mason mở tiệm sửa radio và bán dịch vụ cho giới tội phạm; "
        "đến lượt mình, Phin Mason nhận lấy cái tên ấy ở một dòng thời gian "
        "khác, và không bán cho ai cả. Cô giữ toàn bộ cho riêng mình.",

        "Ở phiên bản Absolute, cơ thể Phin được tái cấu trúc bằng vật chất "
        "lập trình cấy ghép ở cấp tế bào: cô là thực thể lai giữa người và "
        "máy, tự sửa chữa, tự cường hoá, tự nạp lại. Nhưng thứ đáng sợ không "
        "nằm ở thân thể cô mà ở chỗ cô đã nâng cùng công nghệ đó từ quy mô cá "
        "nhân lên quy mô lãnh thổ.",

        "Mục tiêu của cô cũng không còn là Peter Parker. Người cô hiểu rõ hơn "
        "bất kỳ ai — và cũng là người cô được thiết kế để săn — là Miles "
        "Morales.",
    ),

    sections=(
        Section(
            title="Khuyếch đại năng lực vật lý & sinh học",
            intro="Vật chất lập trình sinh học chạy trong từng tế bào, nên cơ "
                  "thể cô là thứ có thể viết lại giữa trận đánh.",
            items=(
                ("Tế bào tự lập trình",
                 "Hạt nano trong mỗi tế bào tái cấu trúc cơ, xương và thần "
                 "kinh theo thời gian thực: mật độ cơ tăng gấp 10 lần trong "
                 "tích tắc, nâng được khoảng 5 tấn — xé cửa thép, ném ô tô. "
                 "Hệ thần kinh thay bằng sợi quang-lượng tử cho phản xạ 10 "
                 "mili giây."),
                ("Tự phục hồi cấp độ mô",
                 "Hạt nano tuần tra trong máu, phát hiện tổn thương và vá lại "
                 "trong vài giây. Vết đạn hay vết cắt sâu đều kín gần như tức "
                 "thì, miễn là năng lượng dự trữ chưa cạn."),
                ("Da hấp thụ động năng",
                 "Lớp Kinetic-Adaptive Skin nuốt tới 90% động năng của đòn "
                 "đánh, chuyển thành điện nạp vào tụ siêu dẫn trong người. Số "
                 "điện đó quay lại thành một cú đấm điện từ, hoặc thành đạn "
                 "cho vũ khí."),
                ("Miễn nhiễm độc tố & sinh học",
                 "Hệ lọc nano trong máu vô hiệu hầu hết chất độc thần kinh, "
                 "khí độc và vi khuẩn. Cô tự điều chỉnh thân nhiệt, áp suất, "
                 "và sống sót một lúc trong chân không nhờ màng tế bào tự tạo."),
                ("Điểm yếu cố hữu",
                 "Năng lượng dự trữ là hữu hạn. Đánh cường độ cao liên tục quá "
                 "hai giờ thì hạt nano bắt đầu thoái hoá và tốc độ phục hồi "
                 "tụt hẳn — cô buộc phải nạp từ lưới điện hoặc một nguồn công "
                 "nghệ cao nào đó."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="Không có trung tâm nào để đánh sập, vì cô đã bỏ hẳn khái "
                  "niệm trung tâm.",
            items=(
                ("Mạng vật chất lập trình toàn cầu (GPMC)",
                 "Hàng triệu “hạt giống” nano phát tán vào khí quyển, nguồn "
                 "nước và đất, tự nhân bản bằng cách ăn kim loại, silicon, "
                 "carbon quanh chúng. Khi kích hoạt, chúng nối thành mạng thần "
                 "kinh nhân tạo phủ hàng nghìn km² — mọi vật chất trong vùng "
                 "trở thành thứ điều khiển được từ xa."),
                ("Trí tuệ bầy đàn phân tán",
                 "Không có AI trung tâm để vô hiệu hoá. Swarm Intelligence "
                 "Core chạy hàng triệu agent nhỏ trên từng hạt nano, tự học và "
                 "phối hợp theo thời gian thực: quét trọn không gian 3D trong "
                 "bán kính 100 km với độ trễ dưới 5 mili giây, và dự đoán quỹ "
                 "đạo đối phương từ dữ liệu lịch sử lẫn phong cách chiến đấu."),
                ("Lò đúc chiến tranh di động",
                 "Những “lò phản ứng vật chất” cỡ container, thả xuống đâu "
                 "cũng chạy: hút đất đá, nước, kim loại phế thải rồi xuất "
                 "xưởng drone, robot tự hành và vũ khí năng lượng. Một lò cỡ "
                 "trung cho ra 10.000 drone cảm tử mỗi giờ."),
                ("Kho vũ khí cá nhân",
                 "Kiếm lượng tử bằng vật chất lập trình dao động tần số cao, "
                 "cắt đứt liên kết phân tử của thép, bê tông, cả hợp kim "
                 "titan. Pháo ray EMP bắn đạn đạt Mach 7 kèm xung phá huỷ mọi "
                 "thiết bị điện tử trong 50 mét. Khiên năng lượng tự đọc bước "
                 "sóng của đòn đánh rồi chỉnh tần số để chặn."),
                ("Hạ tầng hoá thành vũ khí",
                 "GPMC biến cầu, toà nhà, đường sá thành khí tài: một cây cầu "
                 "gấp lại thành cỗ máy nghiền, một toà nhà phóng ra hàng nghìn "
                 "mảnh kim loại nhọn như tên lửa."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Phin hiểu Miles Morales hơn bất kỳ ai — và bộ biện pháp này "
                  "được thiết kế riêng cho từng năng lực của cậu.",
            items=(
                ("Spider-Sense Overload Protocol",
                 "Giác quan nhện báo trước nguy hiểm, nên cô dựng hàng nghìn "
                 "mối đe doạ giả cùng lúc: drone siêu nhỏ phát sóng điện từ "
                 "trùng tần số tín hiệu thần kinh kích hoạt giác quan ấy, từ "
                 "mọi hướng. Miles ngập trong nhiễu, phản xạ hỗn loạn — né "
                 "nhầm, hoặc đứng yên đúng lúc đòn thật tới — và kiệt quệ chỉ "
                 "sau vài phút."),
                ("Dung môi nano phá tơ",
                 "Chạm vào tơ nhện, dù hữu cơ hay nhân tạo, dung môi phá vỡ "
                 "liên kết polymer tức thì. Phun dạng sương hoặc bắn dạng đạn "
                 "nổ; mọi sợi tơ thành chất lỏng vô hại trong chưa đầy 0,1 "
                 "giây. Không đu dây được, cũng không trói được ai."),
                ("Trường phá tàng hình",
                 "Miles bẻ cong ánh sáng để biến mất. Trường của Phin quét "
                 "toàn phổ điện từ, bắt mọi biến dạng ánh sáng lẫn thân nhiệt, "
                 "rồi bắn laser phát tán để “hiện hình” cậu và phủ lên người "
                 "cậu một lớp bụi nano phát quang."),
                ("Phản đòn Venom Strike",
                 "Tụ điện trên giáp hút trọn luồng điện sinh học Miles phóng "
                 "ra, chuyển thành điện nạp cho vũ khí của cô — rồi trả lại "
                 "một luồng tương tự nhưng mạnh gấp ba. Cậu bị đánh gục bằng "
                 "chính sức mạnh của mình."),
                ("Thuật toán Spider-Bane",
                 "Dựng từ dữ liệu hàng trăm trận cũ của Miles, mô hình dự đoán "
                 "chuyển động đạt 99,3%: bắn đạn vào đúng chỗ cậu sẽ tiếp đất "
                 "sau cú nhảy, đặt bẫy vật chất lập trình ở điểm mù, và tung "
                 "đòn giả để ép cậu vào vị trí đã tính sẵn."),
                ("Bio-Nano Suppressor",
                 "Đám mây nano xuyên qua da, đánh vào hệ thần kinh: không giết "
                 "ngay mà phá lớp lông siêu nhỏ khiến tay chân mất khả năng "
                 "bám dính, làm tê các cơ quan cảm thụ, cướp luôn thăng bằng "
                 "và khả năng phối hợp động tác."),
            ),
        ),
    ),

    tiers=(
        Tier("Pha 1", "Xâm nhập & vô hiệu hoá",
             "GPMC phát tán vào lưới điện quốc gia, biến dây dẫn thành siêu "
             "dẫn nhiệt độ phòng hoặc ngược lại cho tới khi toàn hệ truyền tải "
             "sụp. Thành phố tối đen, viễn thông tê liệt. Hạt nano vào hệ cấp "
             "nước, tạo khối polymer làm nghẽn ống hoặc biến nước thành dung "
             "dịch ăn mòn kim loại.",
             "0 – 6 giờ"),
        Tier("Pha 2", "Đánh hạ tầng trọng yếu",
             "Lò đúc di động xuất xưởng hàng triệu drone tự sát, đánh đồng "
             "loạt sân bay, cảng biển, nhà máy lọc dầu, trạm phát sóng. Drone "
             "tự học để né phòng không và tìm lỗ hổng radar. Cao tốc và cầu "
             "cống bị tái cấu trúc thành bột mịn.",
             "6 – 24 giờ"),
        Tier("Pha 3", "Nghiền nát lực lượng quân sự",
             "Quân đội điều xe tăng, tiêm kích, tên lửa — nhưng GPMC đã ở "
             "trong hệ dẫn đường, tên lửa quay đầu bắn lại phe phòng thủ, xe "
             "tăng bị khối vật chất hoá lỏng nuốt chửng rồi tấn công đồng "
             "minh. Cô dựng được “bão nano”: cột xoáy hàng tỷ hạt cắt nhỏ mọi "
             "thứ trong bán kính 1 km, một cơn lốc làm bằng dao cạo.",
             "24 – 48 giờ"),
        Tier("Pha 4", "Sụp đổ kinh tế & xã hội",
             "Năng lượng, giao thông, viễn thông đã mất; ngân hàng và sàn "
             "chứng khoán bị đánh từ bên trong máy tính. Đất nông nghiệp bị "
             "biến cấu trúc thành chất vô cơ không trồng trọt được, kéo theo "
             "nạn đói diện rộng.",
             "48 – 72 giờ"),
    ),

    facts=(
        ("Tên thật", "Phin Mason"),
        ("Dòng thời gian", "Earth-1048 — cái tên đã sang tay"),
        ("Cấp đe doạ", "Quốc gia — National Threat Tier 3"),
        ("Nền tảng", "Vật chất lập trình sinh học cấy ghép"),
        ("Sức nâng", "≈ 5 tấn  ·  phản xạ 10 mili giây"),
        ("Tầm phủ mạng", "Hàng nghìn km²  ·  quét 100 km, trễ 5 ms"),
        ("Điểm yếu", "Năng lượng dự trữ cạn sau ~2 giờ cường độ cao"),
        ("Mục tiêu", "Miles Morales"),
    ),

    blurb="Không có tổng hành dinh để đánh sập, không có AI trung tâm để rút "
          "điện, không có dây chuyền nào để ném bom. Muốn ngăn cô ta, phải "
          "ngăn được chính mặt đất, nguồn nước và không khí của một quốc gia — "
          "vì đến lúc ấy tất cả đều đã là cô ta.",

    art=draw_absolute_tinkerer,
    caption="Dựng lại từ dữ liệu mạng lưới  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Tinkerer_(Marvel_Comics)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Phin_Mason_(Earth-1048)"),
    ),
)
