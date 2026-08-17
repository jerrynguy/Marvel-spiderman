"""
Absolute Kraven — Sergei Kravinoff, đỉnh của chuỗi thức ăn.

Bản sắc riêng, khác cả mười dạng Absolute trước:
    · bộ da `pelt` — khác ở **chất liệu** chứ không ở sắc độ, vì thang
      sáng–tối đã hết chỗ từ `smog`. Chấm halftone to và thưa nhất cả dàn,
      to tới mức thôi đọc ra là hạt in mà thành đốm trên một tấm da; và chỉ
      có **một** lớp mực lệch trục, một cái bóng sẫm đi sau lưng tờ giấy.
    · `evolve_fx="stalk"` — khác ở **nhịp**. Mười kiểu kia đều là một quá
      trình chạy đều; kiểu này hơn nửa thời gian không có gì xảy ra cả, chỉ
      có mấy cặp mắt lần lượt mở ra trong tối và tờ giấy giật mình hai lần.
      Rồi bốn vệt cào, và cả tờ bị lôi tuột khỏi khung. Tấm mới thì đi từ
      trong tối **tới chỗ ta**, nhỏ rồi lớn dần lên.
    · chân dung đổi **chỗ đứng của máy quay**. Hai mươi chân dung kia đều
      nhìn thẳng vào nhân vật; hình này đứng *sau lưng* hắn — ta thấy bờ vai
      và cái bờm, còn thứ được chiếu sáng là con mồi, hiện ra dưới dạng
      Kraven nhìn thấy nó: vệt nhiệt, đường đồng mức thân nhiệt, và cái
      vòng đang siết dần.

Ngôn ngữ chuyển động cũng riêng: **siết dần rồi thả**. Chín dạng kia chuyển
động liên tục, Goblin thì đập theo nhịp cười; hình này gần như đứng yên,
chỉ có cái vòng vây quanh con mồi mỗi lúc một nhỏ lại trong sáu giây, rồi
bung về chỗ cũ và bắt đầu lại. Đó là toàn bộ tính cách của hắn.
"""

import math
from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QPainter, QPainterPath, QPen,
                           QPolygonF, QRadialGradient)

from theme import PELT

from .art import H, W, Rolls, design, glow, marks, ribbon
from .profile import Profile, Section, Tier

MOON = PELT.blue                 # ánh trăng lọt tán lá
BLOOD = PELT.red                 # máu
BONE = PELT.ink                  # xương, răng, và chỗ nóng nhất của con mồi
IVORY = PELT.yellow              # ngà
DARK = QColor("#0A0605")         # bóng của chính hắn
PREY = QPointF(64, 38)           # chỗ con mồi đang đu qua
HUNT = 6.0                       # số giây một vòng siết


def _tone(color, alpha):
    out = QColor(color)
    out.setAlpha(max(0, min(255, int(alpha))))
    return out


# ═══════════════════════════════════════════════════════════════ hình khối
@lru_cache(maxsize=1)
def _hunter():
    """Đầu và vai Kraven nhìn từ sau lưng, hơi quay sang phải.

    Không có mặt. Cả bộ đã có một chân dung nhìn xuyên khe lá vào mặt hắn
    rồi; cái đáng vẽ lần này là chỗ đứng của người đi săn, không phải khuôn
    mặt người bị săn nhìn thấy.
    """
    body = QPainterPath()
    body.moveTo(-6, 126)
    body.cubicTo(QPointF(-2, 96), QPointF(14, 86), QPointF(30, 85))
    body.cubicTo(QPointF(46, 86), QPointF(58, 96), QPointF(64, 126))
    body.closeSubpath()

    head = QPainterPath()
    head.addEllipse(QPointF(31, 72), 12.5, 13.5)
    neck = QPainterPath()
    neck.addRect(QRectF(22, 78, 18, 12))
    return body.united(head).united(neck)


@lru_cache(maxsize=1)
def _mane():
    """Bờm sư tử trên áo — thứ nhận ra hắn ngay cả khi chỉ thấy sau gáy."""
    mane = QPainterPath()
    r = Rolls(15081964)
    # Hai lớp túm lông, gốc bè và chồng lên nhau. Túm mảnh và thưa thì ra
    # lưỡi cưa chứ không ra bờm — đã thử.
    for ring, count, reach in ((10.5, 22, (5, 11)), (12.5, 24, (8, 16))):
        for k in range(count):
            a = math.radians(-190 + k * (380 / count)) + r(-0.06, 0.06)
            base = QPointF(31 + math.cos(a) * ring, 74 + math.sin(a) * ring * 1.08)
            length = r(*reach)
            lean = a + r(-0.22, 0.22)
            tip = QPointF(base.x() + math.cos(lean) * length,
                          base.y() + math.sin(lean) * length)
            wide = r(4.0, 6.4)
            tuft = QPolygonF([
                QPointF(base.x() + math.cos(a + 1.57) * wide,
                        base.y() + math.sin(a + 1.57) * wide),
                QPointF((base.x() + tip.x()) / 2 + math.cos(a + 1.57) * wide * 0.5,
                        (base.y() + tip.y()) / 2 + math.sin(a + 1.57) * wide * 0.5),
                tip,
                QPointF((base.x() + tip.x()) / 2 - math.cos(a + 1.57) * wide * 0.5,
                        (base.y() + tip.y()) / 2 - math.sin(a + 1.57) * wide * 0.5),
                QPointF(base.x() - math.cos(a + 1.57) * wide,
                        base.y() - math.sin(a + 1.57) * wide)])
            piece = QPainterPath()
            piece.addPolygon(tuft)
            mane = mane.united(piece)
    return mane


@lru_cache(maxsize=1)
def _prey():
    """Con mồi: một bóng người đang đu ngang, gọn trong lòng bàn tay."""
    torso = QPainterPath()
    torso.addEllipse(PREY, 2.6, 4.2)
    limbs = QPainterPath()
    limbs.addPath(ribbon(QPointF(PREY.x() + 1, PREY.y() - 3),
                         QPointF(PREY.x() + 6, PREY.y() - 8),
                         QPointF(PREY.x() + 10, PREY.y() - 15), 1.1, 0.45))
    limbs.addPath(ribbon(QPointF(PREY.x() - 1, PREY.y() - 2),
                         QPointF(PREY.x() - 6, PREY.y() - 1),
                         QPointF(PREY.x() - 11, PREY.y() + 2), 1.1, 0.45))
    limbs.addPath(ribbon(QPointF(PREY.x() + 1, PREY.y() + 3),
                         QPointF(PREY.x() + 5, PREY.y() + 7),
                         QPointF(PREY.x() + 2, PREY.y() + 13), 1.3, 0.5))
    limbs.addPath(ribbon(QPointF(PREY.x() - 1, PREY.y() + 3),
                         QPointF(PREY.x() - 5, PREY.y() + 6),
                         QPointF(PREY.x() - 9, PREY.y() + 11), 1.3, 0.5))
    head = QPainterPath()
    head.addEllipse(QPointF(PREY.x() + 1.5, PREY.y() - 5.6), 2.3, 2.1)
    return torso.united(limbs).united(head)


# ═══════════════════════════════════════════════════════════ lớp dựng sẵn
def _night(p):
    """Rừng đêm: tối gần như đặc, chỉ còn một quầng trăng và mấy tán lá."""
    p.setPen(Qt.PenStyle.NoPen)
    night = QRadialGradient(PREY, 74)
    night.setColorAt(0.0, QColor("#16241E"))
    night.setColorAt(0.42, QColor("#0E1512"))
    night.setColorAt(1.0, QColor("#070605"))
    p.setBrush(night)
    p.drawRect(QRectF(-6, -6, 112, 132))

    # tán lá ở mép khung, nhắc lại khe rách của hồ sơ gốc
    r = Rolls(15081965)
    for _ in range(16):
        cx, cy = r(-8, 108), r(-8, 34) if r(0, 1) > 0.4 else r(-8, 126)
        leaf = QPainterPath(QPointF(cx, cy))
        span = r(7, 18)
        a = r(0, math.tau)
        tip = QPointF(cx + math.cos(a) * span, cy + math.sin(a) * span)
        leaf.quadTo(QPointF(cx + math.cos(a + 0.8) * span * 0.7,
                            cy + math.sin(a + 0.8) * span * 0.7), tip)
        leaf.quadTo(QPointF(cx + math.cos(a - 0.8) * span * 0.7,
                            cy + math.sin(a - 0.8) * span * 0.7),
                    QPointF(cx, cy))
        p.setBrush(_tone(QColor("#050807"), r(180, 240)))
        p.drawPath(leaf)


def _shape(p):
    """Kraven: mảng đen đặc, bờm sáng hơn nền, và ánh trăng chỉ liếm một bên.

    Hai chỗ dễ hỏng, đã hỏng cả hai rồi mới ra: bờm mà tô gần bằng màu nền
    thì chỉ còn thấy cái viền, hoá ra hình mặt trời; và viền sáng chạy vòng
    quanh cả bóng người thì nhân vật thành một miếng dán. Bờm phải là một
    mảng có màu, còn ánh trăng thì chỉ được đậu vào **một** bên mép.
    """
    p.setPen(Qt.PenStyle.NoPen)
    mane = _mane()
    p.setBrush(QColor("#2A1A12"))
    p.drawPath(mane)

    # mấy sợi lông chạy trong lòng bờm, cho nó ra chất tóc chứ không ra mảng
    p.save()
    p.setClipPath(mane)
    p.setBrush(Qt.BrushStyle.NoBrush)
    r = Rolls(15081967)
    for _ in range(30):
        a = r(-3.4, 0.3)
        base = QPointF(31 + math.cos(a) * 9, 74 + math.sin(a) * 10)
        far = r(10, 22)
        p.setPen(QPen(_tone(QColor("#4A2E1E"), r(120, 220)), r(0.4, 0.9)))
        p.drawLine(base, QPointF(base.x() + math.cos(a + r(-0.2, 0.2)) * far,
                                 base.y() + math.sin(a + r(-0.2, 0.2)) * far))
    p.restore()

    figure = _hunter()
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(DARK)
    p.drawPath(figure)

    # ánh trăng: vẽ nét dày của chính bóng người đã dịch sang phải, rồi cắt
    # theo bóng gốc — chỉ còn lại một vệt sáng bám mép trái
    p.save()
    p.setClipPath(figure)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(MOON, 85), 2.1))
    p.drawPath(figure.translated(3.2, -1.4))
    p.setPen(QPen(_tone(IVORY, 60), 1.0))
    p.drawPath(figure.translated(4.6, -2.0))
    p.restore()


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
        _night(q)
        _thermal(q)
        q.end()
        _STILL[key] = ready
    return ready


# ═══════════════════════════════════════════════════════════ lớp tự chạy
def _thermal(p):
    """Con mồi hiện ra dưới dạng Kraven đọc được: nóng ở lõi, nguội ra rìa.

    Vẽ từ ngoài vào: vòng ngoài cùng lạnh và dày, càng vào càng nóng và
    mảnh, cuối cùng là cái lõi trắng. Nằm trong ảnh dựng sẵn vì con mồi
    không đi đâu cả — bốn lượt nét trên một path phức tạp mà vẽ lại mỗi
    khung thì tốn gần nửa ngân sách.
    """
    prey = _prey()
    p.setBrush(Qt.BrushStyle.NoBrush)
    for color, w, a in ((MOON, 5.6, 0.18), (IVORY, 3.6, 0.32),
                        (BLOOD, 2.0, 0.6), (BONE, 0.9, 0.9)):
        p.setPen(QPen(_tone(color, 255 * a), w))
        p.drawPath(prey)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_tone(BONE, 250))
    p.drawPath(prey)

    # sợi tơ nó đang đu — thứ duy nhất trong khung không phải thịt
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(BONE, 90), 0.5))
    p.drawLine(QPointF(PREY.x() + 9, PREY.y() - 14), QPointF(88, -6))


def _pulse(p, t):
    """Cái lõi nóng phập phồng — chỗ duy nhất của con mồi còn động đậy."""
    heat = 0.5 + 0.5 * math.sin(t * 2.1)
    glow(p, PREY, 8 + heat * 3, _tone(BONE, 30 + 26 * heat))


def _ring(p, t):
    """Vòng vây: siết dần trong sáu giây rồi bung về chỗ cũ, và siết lại.

    Không có nhịp tim, không có đồng hồ đếm ngược — chỉ một cái vòng mỗi
    lúc một nhỏ. Cả sự kiên nhẫn của hắn nằm ở đây.
    """
    close = (t / HUNT) % 1.0
    rad = 30 - 15 * close ** 0.7
    beat = 1.0 + 0.05 * math.sin(t * 6.9)

    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(BLOOD, 60 + 80 * close), 0.7))
    p.drawEllipse(PREY, rad * beat, rad * beat * 0.86)

    # vạch chia trên vòng, quay chậm ngược chiều kim đồng hồ
    p.setPen(QPen(_tone(IVORY, 90 + 90 * close), 0.8))
    for k in range(12):
        a = math.radians(k * 30) - t * 0.22
        inner = 0.86 if k % 3 else 0.74
        p.drawLine(QPointF(PREY.x() + math.cos(a) * rad * inner,
                           PREY.y() + math.sin(a) * rad * 0.86 * inner),
                   QPointF(PREY.x() + math.cos(a) * rad,
                           PREY.y() + math.sin(a) * rad * 0.86))

    if close > 0.88:                     # sát nút thì vòng đỏ hẳn lên
        glow(p, PREY, rad * 1.3, _tone(BLOOD, 60 * (close - 0.88) / 0.12))


def _scent(p, t):
    """Hạt mùi trôi từ con mồi về phía hắn — thông tin chảy vào, không ra."""
    r = Rolls(15081966)
    p.setPen(Qt.PenStyle.NoPen)
    for _ in range(26):
        speed = r(0.05, 0.14)
        u = (t * speed + r(0, 1)) % 1.0
        wob = math.sin(u * 7 + r(0, 6)) * 4
        x = PREY.x() + (36 - PREY.x()) * u + wob
        y = PREY.y() + (66 - PREY.y()) * u + wob * 0.4
        fade = math.sin(math.pi * u)
        p.setBrush(_tone(MOON if r(0, 1) > 0.35 else IVORY, 150 * fade))
        p.drawEllipse(QPointF(x, y), r(0.4, 1.0), r(0.4, 1.0))


def _eye(p, t):
    """Khoé mắt hắn, lộ ra vì đang quay đầu. Chớp một cái mỗi mấy giây."""
    c = QPointF(41.5, 70)
    blink = 1.0
    phase = t % 4.3
    if phase < 0.16:
        blink = abs(phase - 0.08) / 0.08
    glow(p, c, 5.0, _tone(IVORY, 70 * blink))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_tone(IVORY, 240))
    lid = QPainterPath()
    lid.moveTo(c.x() - 3.4, c.y())
    lid.quadTo(QPointF(c.x(), c.y() - 2.6 * blink),
               QPointF(c.x() + 3.0, c.y() - 0.4))
    lid.quadTo(QPointF(c.x(), c.y() + 2.2 * blink),
               QPointF(c.x() - 3.4, c.y()))
    p.drawPath(lid)
    if blink > 0.4:
        p.setBrush(_tone(QColor("#120A06"), 245))
        p.drawEllipse(QPointF(c.x() + 0.4, c.y() - 0.2), 1.25, 1.5 * blink)
        p.setBrush(_tone(QColor("#FFFFFF"), 220))
        p.drawEllipse(QPointF(c.x() - 0.2, c.y() - 0.9), 0.4, 0.4)


def draw_absolute_kraven(p, rect, t=0.0):
    """Chân dung sống: nhận thêm `t` (giây) nên khung hồ sơ tự vẽ lại."""
    dpr = p.device().devicePixelRatio() if p.device() else 1.0
    grow = (p.transform().m11() or 1.0) * (dpr or 1.0)
    scale = min(rect.width() / W, rect.height() / H) * grow
    still = _still(scale)

    with design(p, rect):
        p.drawImage(QRectF(-6, -6, still.width() / scale,
                           still.height() / scale), still)
        _ring(p, t)
        _pulse(p, t)
        _scent(p, t)
        _shape(p)
        _eye(p, t)
        marks(p, PELT.ink_soft)


# ═══════════════════════════════════════════════════════════════ hồ sơ
ABSOLUTE = Profile(
    name="Absolute Kraven",
    vi_name="Thợ Săn Tuyệt Đối",
    real_name="Sergei Kravinoff  ·  đỉnh chuỗi thức ăn",
    keys=("Kraven Absolute", "Absolute Kraven the Hunter"),

    kicker="Hồ sơ tuyệt đối",
    stamp="PHÂN LOẠI  ·  SINH QUYỂN THÀNH BÃI SĂN",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="pelt",
    evolve_fx="stalk",       # rình hơn nửa thời gian, rồi vồ đúng một cú

    tagline="Không có máy móc, không có phép thuật. Chỉ có một cơ thể đã leo "
            "lên đỉnh chuỗi thức ăn, và cả sinh quyển nghe lời hắn.",

    summary=(
        "Kraven bản gốc mạnh nhờ một thứ nước thảo dược rừng già: nhanh hơn, "
        "khoẻ hơn, giác quan nhạy hơn người thường, sống dai hơn — nhưng vẫn "
        "là một cơ thể người, vẫn phải uống tiếp, và tách hắn khỏi rừng thì "
        "hắn yếu đi. Sức mạnh thật của hắn chưa bao giờ là cơ bắp mà là sự "
        "kiên nhẫn: hắn thắng bằng cách hiểu con mồi hơn con mồi hiểu chính "
        "nó.",

        "Bản Absolute đẩy đúng cái gốc ấy tới cùng chứ không đắp thêm gì lạ. "
        "Cơ thể được viết lại thành một cỗ máy săn: cơ lai bền và bùng nổ, "
        "xương khoáng hoá, nanh vuốt keratin rạch được thép, tuyến nọc pha "
        "được ba loại độc khác nhau, và một hệ tái sinh khiến vết thương "
        "thường không còn là cách giết hắn.",

        "Nhưng chỗ đưa hắn lên cấp hành tinh là bầy đàn. Tuyến pheromone "
        "cùng cái thanh quản phát hạ âm cho hắn ra lệnh cho chuột, chim, "
        "côn trùng, sói, cá mập, rắn — trong bán kính hàng trăm km. Không "
        "một con drone nào, không một dòng mã nào: trí tuệ của mạng lưới ấy "
        "là chính bộ não hắn, còn tay chân là bản năng của muôn loài.",

        "Và bào tử theo dấu thì cộng sinh sẵn trong người hắn. Đã bị đánh "
        "dấu thì đi đâu cũng có gió, nước và đất báo về. Đây là hồ sơ duy "
        "nhất mà mối đe doạ không nằm ở đòn đánh, mà ở chỗ cuộc săn không "
        "bao giờ kết thúc.",
    ),

    sections=(
        Section(
            title="Khuyếch đại năng lực vật lý & sinh học",
            intro="Toàn bộ nâng cấp đều là sinh học, và đều nhằm một việc: "
                  "biến hắn thành sinh vật đứng cuối cùng của chuỗi thức ăn. "
                  "Không cỗ máy nào ở đây cả, vì Kraven mà cầm súng máy thì "
                  "không còn là Kraven.",
            items=(
                ("Hệ cơ lai và xương khoáng hoá",
                 "Myostatin bị chặn hoàn toàn, sợi cơ bền và sợi cơ bùng nổ "
                 "trộn làm một; ty thể tái tổ chức để hô hấp kỵ khí hiệu quả "
                 "gấp tám lần nên chạy 80–100 km/h hàng giờ mà không tích "
                 "axit lactic. Xương đặc gấp ba, sọ có cấu trúc tổ ong chịu "
                 "lực, nanh vuốt keratin rạch được thép. Hắn nâng và ném "
                 "được một xe tăng hạng nhẹ."),
                ("Giác quan của kẻ săn mồi",
                 "Khứu giác mạnh gấp hai mươi lần kèm cơ quan vomeronasal "
                 "đánh hơi được hormone và mùi mồ hôi sợ hãi từ hàng chục "
                 "km. Hố cảm nhiệt dưới mắt như rắn lục cho hắn nhìn thân "
                 "nhiệt trong đêm đặc. Da mang màng điện Lorenzini, đọc được "
                 "điện trường yếu của tim và cơ con mồi — nghĩa là hắn biết "
                 "ta sắp cử động trước cả khi ta cử động."),
                ("Tuyến nọc ba loại",
                 "Tuyến nước bọt được ghép gen rắn, nhện, bọ cạp, sứa và ếch "
                 "độc, pha ra ba thứ khác nhau: độc thần kinh để làm tê "
                 "liệt, độc tan máu để gây xuất huyết trong, và độc gây ảo "
                 "giác để con mồi tự chạy vào bẫy. Nanh hàm lẫn nanh tay đều "
                 "có rãnh dẫn."),
                ("Tái sinh và Trạng thái Điên Săn",
                 "Tế bào gốc đa năng bật liên tục: vết thương sâu liền trong "
                 "vài phút, chi cụt mọc lại sau hai ba tuần nếu có đủ thịt "
                 "tươi. Khi cần, tuyến thượng thận bung một cơn bão hormone "
                 "— mạnh gấp sáu tới mười lần, không còn biết đau. Cái giá "
                 "là sau mười lăm hai mươi phút hắn phải ăn sống con mồi "
                 "ngay tại chỗ, nếu không cơ thể tự phân huỷ cơ bắp."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="Ở đây không có công nghệ, và đó là điểm của cả hồ sơ. Chỗ "
                  "đáng lẽ là máy móc thì Kraven mở rộng bằng chính sự sống: "
                  "mạng lưới của hắn là hệ thần kinh của thế giới hoang dã.",
            items=(
                ("Mạng lưới bầy đàn",
                 "Pheromone đặc hiệu cho từng loài cộng với hạ âm phát từ "
                 "thanh quản biến đổi, truyền đi hàng trăm km: chuột, chim, "
                 "côn trùng, sói, cá mập, voi, rắn đều nhận lệnh. Không có "
                 "AI nào điều phối — bộ não hắn là trung tâm, còn bản năng "
                 "bầy đàn lo phần còn lại. Không có gì để hack, không có tần "
                 "số nào để gây nhiễu."),
                ("Bào tử theo dấu",
                 "Hắn cộng sinh với một loài nấm biến đổi và rắc bào tử lên "
                 "con mồi hoặc lên cả một vùng. Bào tử truyền tín hiệu hoá "
                 "học qua gió, nước và đất, nên đã bị đánh dấu thì đi hết "
                 "lục địa vẫn còn nghe thấy. Trốn không phải là một lựa chọn "
                 "nữa, chỉ còn là trì hoãn."),
                ("Vũ khí mọc từ chính hắn",
                 "Cây thương làm bằng xương khoáng hoá của hắn, mọc dài ra "
                 "như móng tay và tự phủ enzyme cắt tơ. Lưới săn dệt từ gân "
                 "thú, tẩm nọc tê liệt. Dao găm là răng nanh, tự tiết độc "
                 "thần kinh. Không có gì để tịch thu, vì mọi thứ đều là một "
                 "phần cơ thể."),
                ("Săn dược thích ứng",
                 "Uống máu, ăn não hoặc hấp thụ DNA con mồi thì hắn mượn tạm "
                 "được đặc tính của nó: mọc mang để thở dưới nước, đổi màu "
                 "da để nguỵ trang, mắt nhìn đêm, kháng đúng loại độc vừa "
                 "dính. Mỗi con vật hắn giết đều làm hắn thành một thợ săn "
                 "khác đi một chút."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Kraven không cần công nghệ để bóp nghẹt giác quan nhện. "
                  "Hắn chỉ cần hiểu nó là một cơ chế sinh học — và mọi cơ "
                  "chế sinh học đều có thứ làm nó nhiễu, làm nó mỏi, hoặc "
                  "làm nó kêu suốt tới mức vô dụng.",
            items=(
                ("Màn hơi của kẻ săn mồi",
                 "Một hợp chất pheromone dễ bay hơi ức chế hạch hạnh nhân — "
                 "vùng não xử lý phản xạ nguy hiểm. Giác quan nhện không mất "
                 "mà bị trễ lại ba tới bảy phần mười giây. Nghe thì nhỏ, "
                 "nhưng ở cự ly cận chiến với Kraven thì đó là toàn bộ "
                 "khoảng cách giữa né được và không."),
                ("Nhiễu bầy đàn",
                 "Hàng nghìn con côn trùng, chuột, chim vây quanh Peter. Mỗi "
                 "con là một mối nguy bé tí, và giác quan nhện thì báo tất. "
                 "Nó kêu liên tục tới lúc não Peter thôi phân biệt được đâu "
                 "là đòn thật của Kraven. Đây là cách tắt giác quan ấy bằng "
                 "sinh học, không phải bằng máy."),
                ("Nọc nhắm đúng chỗ bám",
                 "Nọc pha từ ong bắt nhện, rắn độc và bọ cạp, nhắm thẳng vào "
                 "nhánh thần kinh điều khiển ngón tay và bàn chân. Dính một "
                 "nhát nanh là Peter tê đầu ngón, mất thăng bằng, cơ co "
                 "giật — không bám tường được, không bắn tơ trúng chỗ mình "
                 "nhắm."),
                ("Enzyme cắt tơ và hạ âm",
                 "Vuốt và thương phủ chitinase cùng keratinase, chạm vào là "
                 "tơ đứt, nên trói hắn là chuyện không xảy ra. Cùng lúc, hạ "
                 "âm 7–19 Hz cộng hưởng với tai trong làm Peter chóng mặt và "
                 "buồn nôn — còn bầy thú của hắn thì đã quen tần số ấy từ "
                 "lâu."),
                ("Bẫy danh dự",
                 "Hắn biết Peter là ai, và biết Peter sẽ chọn gì. Nên hắn "
                 "dựng những cái bẫy chỉ mở được nếu Người Nhện chịu đòn "
                 "thay người khác, rồi đánh dấu pheromone lên những người "
                 "thân của cậu để bầy đàn báo vị trí suốt nhiều tháng. Peter "
                 "không giữ nổi tất cả mọi người cùng lúc — và cuộc săn thì "
                 "không có ngày kết thúc."),
            ),
        ),
    ),

    # Thang chữ cái Hy Lạp, đọc từ Zeta lên Omega. Đo bằng mức sụp đổ của
    # chuỗi thức ăn, không phải bằng sức phá vật lý.
    tiers=(
        Tier("Tier Zeta", "Một người",
             "Săn đúng một mục tiêu, thường là một siêu anh hùng: theo dấu, "
             "dựng bẫy, chọn chỗ và chọn giờ. Đây là mức căn bản của bản "
             "gốc, và bản Absolute vẫn thích bậc này nhất.",
             "Một cuộc săn"),
        Tier("Tier Epsilon", "Một khu dân cư",
             "Khủng bố một khu phố, hạ vài mục tiêu giá trị cao, tạo một "
             "vùng hoảng loạn cục bộ. Đây là mức bản gốc hoạt động thường "
             "xuyên; bản này làm xong trong vài giờ và không để lại dấu.",
             "Vài giờ"),
        Tier("Tier Delta", "Một đô thị thành bãi săn",
             "Thả thú dữ vào khu dân cư, giết người đứng đầu, phá cầu đường, "
             "đẩy cả thành phố vào hoảng loạn. Bản gốc chuẩn bị thật kỹ thì "
             "cũng chạm được mức này — đây là chỗ hai bản gặp nhau lần cuối.",
             "24–48 giờ"),
        Tier("Tier Gamma", "Một quốc gia",
             "An ninh lương thực, nguồn nước sạch và hạ tầng y tế của cả "
             "nước bị phá; quân đội quá tải vì những cuộc tấn công của động "
             "vật mà không có mục tiêu nào để bắn trả.",
             "5–7 ngày"),
        Tier("Tier Beta", "Một vùng",
             "Nhiều quốc gia trong cùng khu vực mất ổn định: hệ lương thực "
             "và năng lượng bị phá, dòng người tị nạn khổng lồ, chính quyền "
             "mất khả năng kiểm soát.",
             "10 ngày"),
        Tier("Tier Alpha", "Một châu lục",
             "Bầy đàn tràn vào các thành phố, mạng giao thông đứt, thú "
             "hoảng loạn gây cháy rừng, dịch bệnh từ xác chết lan ra. Quân "
             "đội bị xé lẻ, biên giới không còn nghĩa gì.",
             "2–3 tuần"),
        Tier("Tier Omega", "Săn lùng sinh quyển",
             "Tín hiệu săn mồi phát đi theo gió, nước và bầy đàn: thú săn "
             "mồi thôi sợ người, côn trùng phá mùa màng, gặm nhấm phá kho, "
             "gia súc giẫm nát hạ tầng. Chuỗi thức ăn sụp theo tầng — cây "
             "chết, vật nuôi chết, nước nhiễm độc từ xác. Ba tới bốn mươi "
             "lăm ngày là nhiều quốc gia mất an ninh lương thực; chín mươi "
             "ngày là đói, dịch và chiến tranh giành tài nguyên. Hắn không "
             "phá hành tinh bằng năng lượng — hắn biến nó thành một cuộc săn "
             "không có hồi kết.",
             "30–45 ngày  ·  90 ngày"),
    ),

    # Nhãn giữ dưới 94 px, giá trị dưới 188 px — xem chú thích cùng chỗ trong
    # `chameleon_absolute.py`.
    facts=(
        ("Cấp đe doạ", "Hành tinh  ·  sinh quyển sụp"),
        ("Nền tảng", "Sinh học thuần, không máy móc"),
        ("Không dùng", "AI  ·  drone  ·  robot"),
        ("Giác quan", "Hơi, nhiệt, điện trường tim"),
        ("Nọc", "Thần kinh · tan máu · ảo giác"),
        ("Điên Săn", "Gấp 6–10 lần, 15–20 phút"),
        ("Bầy đàn", "Pheromone + hạ âm, hàng trăm km"),
        ("Bậc Omega", "30–45 ngày, rồi 90 ngày"),
    ),

    blurb="Mười hồ sơ kia đều phải phóng to một thứ gì đó: một cơn bão, một "
          "lưới điện, một dây chuyền. Kraven thì không phóng to gì cả — hắn "
          "chỉ trèo lên trên cùng của cái chuỗi thức ăn vốn đã có sẵn ở đây "
          "trước loài người rất lâu, rồi gọi nó dậy. Và thứ đáng sợ nhất "
          "trong hồ sơ này không phải một đòn nào, mà là việc cuộc săn không "
          "có ngày kết thúc.",

    art=draw_absolute_kraven,
    caption="Nhìn từ sau vai người đi săn  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Kraven_the_Hunter"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Sergei_Kravinoff_(Earth-616)"),
    ),
)
