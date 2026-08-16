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

    Đây là vùng Swarm đã phủ kín, nhìn từ trên mặt đất: mọi vật chất trong
    tầm đều đã là của cô, và sóng lan trên lưới chính là tín hiệu kích hoạt
    đang chạy tới từng hạt.
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


def _node(p, t):
    """Hai Node nhô lên khỏi lưới, đang nhả Swarm lên trời.

    Chỗ này cố ý vẽ thưa: mỗi Node chỉ thả ba hạt thấy được. Cái đáng sợ
    không phải số hạt trong hình mà là còn bốn mươi tám khối nữa nằm im dưới
    đất, ngoài khung.
    """
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
    """Bụi Swarm lơ lửng phía trước, nhắc rằng không khí ở đây cũng là của cô.

    Hạt trôi thẳng lên và không né nhau — chúng không nghĩ, chỉ làm đúng vài
    phản ứng đã mã hoá sẵn trong cấu trúc tinh thể.
    """
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
        _node(p, t)
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
    stamp="PHÂN LOẠI  ·  MỐI ĐE DOẠ CẤP HÀNH TINH",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="mesh",
    evolve_fx="dissolve",    # giấy bị ăn dần rồi lắp lại, không nổ không xé

    tagline="Không phải một thiên tài chế đồ nữa. Là một hệ sinh thái vật "
            "chất lập trình tự nhân bản, biến chính nền văn minh công nghệ "
            "thành vũ khí chống lại loài người.",

    summary=(
        "Cái tên Tinkerer chưa bao giờ là tên một người — nó là tên một nghề. "
        "Phineas Mason mở tiệm sửa radio và bán dịch vụ cho giới tội phạm; "
        "đến lượt mình, Phin Mason nhận lấy cái tên ấy ở một dòng thời gian "
        "khác, và không bán cho ai cả. Cô giữ toàn bộ cho riêng mình.",

        "Bản gốc là một thiên tài công nghệ còn rất trẻ, đứng đầu nhóm "
        "Underground, dùng vật chất lập trình và vũ khí năng lượng để trả thù "
        "Roxxon. Sức mạnh của cô nằm ở trí tuệ kỹ thuật, ở mạng lưới đồng "
        "minh, và ở chỗ cô hiểu công nghệ của Miles Morales từ bên trong. "
        "Điểm yếu cũng nằm ở đó: cảm xúc bất ổn, mâu thuẫn chưa bao giờ gỡ "
        "được với Miles, và một tầm nhìn bị thù hận bóp lại còn rất ngắn.",

        "Phiên bản Absolute không cho cô thêm phép màu nào — nó chỉ khuếch "
        "đại đúng cái cô vốn giỏi. Vật chất lập trình được cấy vào chính hệ "
        "thần kinh và cơ xương của cô, rồi cùng công nghệ ấy được thả ra "
        "ngoài thành một hệ sinh thái tự nhân bản, ăn kim loại mà lớn lên, "
        "phủ dần lên hạ tầng của cả hành tinh.",

        "Không có một AI có ý thức nào trong toàn bộ hệ thống đó. Từng hạt "
        "chỉ mang vài phản ứng hoá–lý mã hoá sẵn trong cấu trúc tinh thể của "
        "nó — không suy nghĩ, không tự quyết, không thương lượng được. Người "
        "ra lệnh vẫn luôn là Phin, và mục tiêu của cô không phải Peter "
        "Parker: là Miles Morales.",
    ),

    sections=(
        Section(
            title="Khuyếch đại năng lực vật lý & sinh học",
            intro="Bản gốc là người thường trong một bộ giáp: đánh trực diện "
                  "là cô thua. Absolute xoá khoảng cách giữa người mặc giáp và "
                  "bộ giáp — cô tự cấy một mạng sợi vật chất lập trình vào hệ "
                  "thần kinh ngoại vi và cơ xương, và từ đó cơ thể cô là thứ "
                  "có thể viết lại giữa trận đánh.",
            items=(
                ("Sợi cơ vật chất lập trình",
                 "Mạng sợi cấy vào cơ xương hoạt động như cơ bắp nhân tạo với "
                 "mật độ năng lượng gấp 50 lần cơ người: nâng được hàng chục "
                 "tấn, chạy 120 km/h, phản xạ dưới 10 mili giây. Chúng phản "
                 "ứng thẳng với tín hiệu thần kinh của Phin và tái cấu trúc "
                 "theo thời gian thực, tạo lực kéo cơ học mà không cần đến cơ "
                 "bắp sinh học nữa."),
                ("Áo giáp chất lỏng thông minh",
                 "Lớp phủ trên da nuốt động năng của đạn và mảnh nổ bằng cách "
                 "hoá nó thành nhiệt, rồi tản đi qua hàng triệu kênh dẫn siêu "
                 "nhỏ. Không có mảng giáp nào để bắn vỡ, vì nó không phải "
                 "mảng — nó chảy."),
                ("Tái tạo bằng vật chất môi trường",
                 "Mất một cánh tay không còn là mất vĩnh viễn: cô hút vật chất "
                 "lập trình từ xung quanh và dựng lại chi đó trong vài giây. "
                 "Càng đánh ở nơi có nhiều kim loại, cô càng khó bị làm cho "
                 "yếu đi."),
                ("Thở và tuần hoàn tự động hoá",
                 "Vật chất lập trình nhận luôn việc bơm máu và trao đổi khí, "
                 "nên phổi thôi là điểm chí mạng. Cô sống được trong chân "
                 "không và dưới nước — hai môi trường mà đối thủ nào cũng "
                 "tưởng là chỗ dồn cô vào đường cùng."),
                ("Điểm yếu cố hữu",
                 "Toàn bộ hệ này chạy bằng lò phản ứng mini trong giáp, và cả "
                 "nó lẫn tốc độ tự nhân bản của Swarm đều có giới hạn. Đánh "
                 "cường độ cao liên tục quá hai giờ thì mạng sợi bắt đầu thoái "
                 "hoá, tái tạo chậm hẳn lại — cô buộc phải cắm vào lưới điện "
                 "hoặc một nguồn công nghệ cao nào đó để nạp."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="Không có trung tâm nào để đánh sập, vì cô đã bỏ hẳn khái "
                  "niệm trung tâm — và cũng không có AI nào để thuyết phục hay "
                  "vô hiệu hoá, vì trong toàn hệ thống không có gì biết nghĩ.",
            items=(
                ("Hệ thống “Swarm”",
                 "Hàng tỷ hạt vật chất lập trình cỡ micromet, tự nhân bản bằng "
                 "cách ăn kim loại và vật liệu quanh chúng — một thứ vi khuẩn "
                 "cơ khí. Chúng không có trí tuệ nhân tạo: mỗi hạt chỉ mang "
                 "vài thuật toán hoá–lý đơn giản mã hoá sẵn trong cấu trúc "
                 "tinh thể. Thả một đám mây Swarm vào nhà máy điện là chúng tự "
                 "dò ra dây dẫn, bám vào và đoản mạch liên tục cho tới khi cả "
                 "dây chuyền cháy nổ."),
                ("Tái cấu trúc hạ tầng",
                 "Ở quy mô lớn, Swarm dựng thành những cột vật chất lập trình "
                 "cao hàng trăm mét, hoặc chui vào từng khe nứt của cầu đường "
                 "rồi giãn nở đột ngột. Bê tông không bị nổ tung — nó bị tách "
                 "ra từ bên trong, theo đúng những đường yếu mà người kỹ sư "
                 "nào cũng biết là có."),
                ("Pháo năng lượng “Titan Lance”",
                 "Khẩu pháo cá nhân bắn chùm plasma 50.000°C, cắt xuyên bê "
                 "tông cốt thép dày mười mét. Nguồn là một lò phản ứng hạt "
                 "nhân mini tích hợp trong giáp, và chính vật chất lập trình "
                 "làm nhiệm vụ kìm giữ phản ứng phân hạch — thanh điều khiển "
                 "của lò là thứ cô nghĩ ra được, không phải thứ mua được."),
                ("Mạng lưới Node toàn cầu",
                 "Underground không còn là một nhóm nhỏ ở New York. Phin cho "
                 "chôn các “Node” — khối cầu chứa hàng tấn hạt Swarm — dưới "
                 "lòng đất ở 50 thành phố lớn. Mỗi Node kích hoạt được từ xa "
                 "bằng một tín hiệu vô tuyến mã hoá, giải phóng Swarm đánh vào "
                 "toàn bộ điện, nước và viễn thông của thành phố đó."),
                ("Vì sao không có drone",
                 "Đặt Node vào chỗ là việc của người Underground, ra lệnh kích "
                 "hoạt là việc của Phin. Không máy bay không người lái, không "
                 "robot tự hành, không hệ điều khiển tự trị nào ở giữa. Muốn "
                 "chặn cô thì phải tìm ra người đã chôn Node, hoặc tìm ra "
                 "chính cô — chứ không có máy chủ nào để đánh sập."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Không đòn nào ở đây là công cụ mua sẵn: tất cả đều dựng từ "
                  "chính vật chất lập trình của cô, và từ chỗ cô biết rõ Miles "
                  "Morales — cả cách cậu đánh lẫn cách cậu đau.",
            items=(
                ("Nhiễu vật chất lập trình",
                 "Giác quan nhện đọc các biến động năng lượng và chuyển động "
                 "trong không gian, nên cô dựng một trường hạt bán kính 50 mét "
                 "quanh mình, trong đó vật chất lập trình liên tục đổi vị trí "
                 "và mật độ theo thuật toán ngẫu nhiên. Hàng nghìn biến động "
                 "giả cùng lúc: Miles thấy nguy hiểm từ mọi hướng, và một cảnh "
                 "báo đúng ở khắp nơi thì cũng vô dụng như không có."),
                ("Bẫy “mạng nhện phản xạ”",
                 "Những tấm vật chất lập trình hấp thụ động năng của tơ nhện, "
                 "giữ lại dưới dạng năng lượng đàn hồi rồi bắn ngược lại theo "
                 "đúng hướng tới, với lực gấp đôi. Cùng lúc, một từ trường cục "
                 "bộ làm loạn hướng bám của tơ — cậu đu dây mà không còn tin "
                 "được sợi tơ sẽ dính vào đâu."),
                ("“Bóng ma ký ức”",
                 "Máy chiếu vật chất lập trình dựng ra hình ảnh ba chiều có "
                 "xúc giác: Rio Morales, Ganke, hoặc chính Phin của những ngày "
                 "trước khi thành Tinkerer. Chúng chạm được vào Miles và nói "
                 "được những câu làm cậu đau nhất. Đây không phải ảo giác thần "
                 "kinh — nó là vật thể thật, dựng bằng photon và sóng âm chính "
                 "xác tới từng nguyên tử, nên cậu không có cách nào tự nhủ "
                 "rằng mình đang tưởng tượng."),
                ("Bụi phát quang phá tàng hình",
                 "Miles bẻ cong ánh sáng để biến mất, nên cô không đi tìm cậu "
                 "— cô đánh dấu cậu. Bụi vật chất lập trình bám vào mọi bề mặt "
                 "cậu chạm tới, hấp thụ ánh sáng xung quanh rồi phát lại ở "
                 "bước sóng xanh lam nhạt. Mỗi hạt cỡ micromet và bám chặt vào "
                 "vải lẫn da, nên phủi cũng không sạch: tàng hình xong vẫn "
                 "phát sáng lờ mờ trong bóng tối."),
            ),
        ),
    ),

    # Thang chữ cái Hy Lạp như hai dạng Absolute trước, đọc từ Zeta lên Omega.
    # Ở đây bậc càng cao thì càng chậm, vì thứ quyết định không phải hoả lực
    # mà là số Node đã chôn xong và chờ sẵn dưới đất.
    tiers=(
        Tier("Tier Zeta", "Vài mục tiêu cá nhân",
             "Một nhúm Swarm và khẩu Titan Lance là đủ. Không cần Node, không "
             "cần chuẩn bị: cô đến, và những người có tên trong danh sách thì "
             "không còn.",
             "1 phút"),
        Tier("Tier Epsilon", "Một trung đội hoặc một đoàn xe",
             "Swarm rải vào đội hình tự tìm tới kim loại: khoá nòng, chập "
             "mạch điện xe, cắn đứt hệ dẫn động. Một trung đội quân hay một "
             "đoàn xe cảnh sát tan trước khi kịp gọi chi viện.",
             "10 phút"),
        Tier("Tier Delta", "Một toà cao ốc hoặc một khu phố",
             "Swarm chui vào từng khe nứt của kết cấu rồi giãn nở đồng loạt. "
             "Toà nhà không nổ, nó tự tách ra theo các đường yếu — nhanh hơn "
             "và gọn hơn bất kỳ khối thuốc nổ nào.",
             "30 phút"),
        Tier("Tier Gamma", "Một hạ tầng chiến lược",
             "Sân bay quốc tế, nhà máy điện hạt nhân, hoặc một trung tâm tài "
             "chính: thiệt hại hàng chục tỷ đô la trong hai giờ. Bản gốc phải "
             "mất nhiều tuần lên kế hoạch cho một vụ phá hoại Roxxon nhỏ hơn "
             "thế nhiều.",
             "2 giờ"),
        Tier("Tier Beta", "Một siêu đô thị tê liệt",
             "Một Node dưới New York, Tokyo hay London mở ra là đủ: tàu điện "
             "ngầm, cầu đường, hệ cấp thoát nước hỏng cùng lúc. Thành phố "
             "không bị san phẳng — nó chỉ đơn giản là ngừng chạy được nữa.",
             "6 giờ"),
        Tier("Tier Alpha", "Hệ năng lượng của một quốc gia",
             "Swarm đánh dọc đường ống dẫn khí, nhà máy lọc dầu và lưới truyền "
             "tải của trọn một cường quốc. Không có mặt trận nào để phòng thủ, "
             "vì thứ đang tấn công đã nằm sẵn trong chính hạ tầng ấy.",
             "1 ngày"),
        Tier("Tier Omega", "Sụp đổ nền văn minh công nghệ",
             "Một tín hiệu vô tuyến mã hoá, năm mươi Node mở cùng lúc. Swarm "
             "tràn vào nhà máy điện hạt nhân, trạm biến áp, trung tâm dữ liệu, "
             "sân bay và cảng biển; lưới điện Bắc Mỹ, châu Âu và Đông Á sụp "
             "trong 72 giờ. Hàng tỷ người mất điện, mất nước sạch, mất liên "
             "lạc. Bản gốc cần nhiều tuần để phá vài toà nhà của Roxxon; "
             "Absolute chỉ cần một lệnh kích hoạt và ba ngày — không phải đối "
             "đầu trực diện với quân đội của bất kỳ ai.",
             "3 ngày"),
    ),

    # Nhãn giữ dưới 94 px — bề ngang cột nhãn của FactTable, quá thì bị cắt.
    facts=(
        ("Tên thật", "Phin Mason"),
        ("Dòng thời gian", "Earth-1048 — cái tên đã sang tay"),
        ("Cấp đe doạ", "Hành tinh — sụp đổ nền văn minh công nghệ"),
        ("Nền tảng", "Vật chất lập trình tự nhân bản"),
        ("Thể chất", "Nâng hàng chục tấn · 120 km/h · phản xạ 10 ms"),
        ("Node", "50 thành phố  ·  kích hoạt bằng vô tuyến mã hoá"),
        ("Không dùng", "AI có ý thức — chỉ phản ứng hoá–lý sẵn"),
        ("Điểm yếu", "Năng lượng cạn sau ~2 giờ cường độ cao"),
        ("Mục tiêu", "Miles Morales"),
    ),

    blurb="Không có tổng hành dinh để đánh sập, không có AI để rút điện, "
          "không có dây chuyền nào để ném bom — chỉ có năm mươi khối cầu nằm "
          "im dưới lòng năm mươi thành phố, và một người biết tần số đánh "
          "thức chúng. Muốn ngăn cô ta thì phải tìm ra từng cái một, trước "
          "khi cô bấm nút.",

    art=draw_absolute_tinkerer,
    caption="Dựng lại từ dữ liệu mạng lưới  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Tinkerer_(Marvel_Comics)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Phin_Mason_(Earth-1048)"),
    ),
)
