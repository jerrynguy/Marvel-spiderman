"""
Absolute Lizard — Serpent Rex. Curt Connors không còn ở trong đó nữa.

Bản sắc riêng, khác cả năm dạng Absolute trước:
    · bộ da `swamp` — bộ duy nhất lấy nền là một *màu* chứ không phải sắc
      trung tính. Năm bộ kia đều gần đen hoặc gần trắng; bộ này xanh rêu
      đậm, mực vàng lưu huỳnh và tím nọc.
    · `evolve_fx="bloom"` — tờ giấy cũ không bị phá mà bị **chiếm**: rễ bò
      vào từ mép, bào tử đáp xuống rồi phình thành ổ, các ổ loang ra nhập
      vào nhau. Tấm mới thì **nở ra từ một hạt ở giữa** theo hình tròn.
    · dáng nằm ngang, bò rình — năm dạng kia đều đứng thẳng hoặc toả tròn.
      Cái đầu chiếm gần nửa khung, chúc xuống phía người xem.

Ngôn ngữ chuyển động cũng riêng: cả thân phập phồng theo nhịp thở, một sóng
chạy dọc từ gáy xuống chót đuôi, con ngươi khe dọc co giãn, và bào tử phát
quang bay *lên* — bốn dạng kia đều có hạt trôi ngang hoặc quay vòng.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QLinearGradient, QPainter,
                           QPainterPath, QPen, QPolygonF, QRadialGradient)

from theme import SWAMP

from .art import H, W, Rolls, design, glow, marks, ribbon
from .profile import Profile, Section, Tier

BILE = SWAMP.red                 # vàng lưu huỳnh — nọc và bào tử
VENOM = SWAMP.blue               # tím nọc
MINT = SWAMP.yellow
HIDE = QColor("#0A1C13")         # da lưng, sẫm hơn cả nền đầm
BELLY = QColor("#1E3A26")        # phần bụng bắt sáng
WATER = 104.0                    # mặt nước


def _tone(color, alpha):
    out = QColor(color)
    out.setAlpha(max(0, min(255, int(alpha))))
    return out


# ═══════════════════════════════════════════════════════════ hình khối
def _skull():
    """Sọ bò sát: dài gấp gần ba lần chiều cao, mõm nhọn, gò mày nhô."""
    path = QPainterPath()
    path.moveTo(11, 79)                       # chóp mõm
    path.lineTo(21, 72)                       # sống mũi, một nét thẳng
    path.cubicTo(29, 67, 37, 65, 45, 65)      # lên tới gò mày
    path.lineTo(49, 62)                       # gờ mày nhô hẳn ra
    path.cubicTo(60, 63, 68, 68, 71, 77)      # đỉnh sọ dốc về gáy
    path.lineTo(69, 88)                       # gáy
    path.lineTo(34, 85)                       # hàm trên, gần như thẳng
    path.closeSubpath()
    return path


def _jaw():
    """Hàm dưới rời và mảnh, để nó há ra được."""
    path = QPainterPath()
    path.moveTo(13, 82)
    path.lineTo(36, 86)
    path.lineTo(68, 88)
    path.lineTo(67, 93)
    path.cubicTo(48, 93, 28, 90, 12, 85)
    path.closeSubpath()
    return path


def _hull():
    """Khối thân lùi về sau bên phải: dài và thấp, không phải quả bóng."""
    path = QPainterPath()
    path.moveTo(64, 70)
    path.cubicTo(76, 64, 90, 68, 97, 78)
    path.cubicTo(102, 87, 98, 97, 88, 100)
    path.cubicTo(76, 103, 66, 96, 63, 88)
    path.closeSubpath()
    return path


def _foreleg():
    """Chi trước chống xuống bùn ở tiền cảnh, năm vuốt xoè."""
    path = QPainterPath()
    path.addPath(ribbon(QPointF(60, 86), QPointF(48, 96), QPointF(38, 104),
                        5.0, 3.2))
    for tip, bend in (((28, 108), (33, 104)), ((34, 112), (36, 107)),
                      ((42, 111), (40, 107))):
        path.addPath(ribbon(QPointF(38, 103), QPointF(*bend), QPointF(*tip),
                            2.4, 0.3))
    return path


_SKULL = _skull()
_HULL = _hull()
_FORELEG = _foreleg()
_BODY = _SKULL.united(_HULL).united(_FORELEG)


# ═══════════════════════════════════════════════════════════════ các lớp
def _swamp(p, t):
    """Đầm: trời mù, cây chết đứng, sương thấp, nước đọng dưới chân."""
    p.setPen(Qt.PenStyle.NoPen)
    sky = QLinearGradient(0, -6, 0, 126)
    sky.setColorAt(0.0, QColor("#0A1A12"))
    sky.setColorAt(0.38, QColor("#16301F"))
    sky.setColorAt(0.62, QColor("#204028"))
    sky.setColorAt(0.86, QColor("#0E2418"))
    sky.setColorAt(1.0, QColor("#07130D"))
    p.setBrush(sky)
    p.drawRect(QRectF(-6, -6, 112, 132))

    haze = QRadialGradient(QPointF(58, 46), 52)
    haze.setColorAt(0.0, _tone(MINT, 40))
    haze.setColorAt(0.5, _tone(MINT, 12))
    haze.setColorAt(1.0, _tone(MINT, 0))
    p.setBrush(haze)
    p.drawRect(QRectF(-6, -6, 112, 110))

    # cây chết: thân mảnh, cành gãy, càng xa càng nhạt
    r = Rolls(11061963)
    for _ in range(11):
        x = r(-4, 104)
        top = r(6, 46)
        fade = r(30, 90)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(_tone(QColor("#08150E"), int(fade)), r(0.6, 2.0)))
        trunk = QPainterPath(QPointF(x, WATER))
        trunk.quadTo(QPointF(x + r(-4, 4), (top + WATER) / 2), QPointF(x + r(-6, 6), top))
        p.drawPath(trunk)
        for _ in range(2):
            u = r(0.3, 0.8)
            b = trunk.pointAtPercent(u)
            p.drawLine(b, QPointF(b.x() + r(-9, 9), b.y() - r(3, 9)))

    # sương nằm ngang, trôi rất chậm
    for k in range(4):
        y = 62 + k * 9 + math.sin(t * 0.3 + k) * 1.5
        band = QLinearGradient(0, y - 4, 0, y + 4)
        band.setColorAt(0.0, _tone(MINT, 0))
        band.setColorAt(0.5, _tone(MINT, 26 + k * 5))
        band.setColorAt(1.0, _tone(MINT, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(band)
        p.drawRect(QRectF(-6, y - 4, 112, 8))

    # nước: mặt phẳng tối, có vệt sáng gợn
    p.setBrush(QColor("#061109"))
    p.drawRect(QRectF(-6, WATER, 112, 132 - WATER))
    for k in range(9):
        y = WATER + 2 + k * 2.4
        wob = math.sin(t * 0.8 + k * 0.9) * 3
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(_tone(MINT, 26 + k * 4), 0.5))
        p.drawLine(QPointF(10 + wob, y), QPointF(56 + wob * 1.6, y))


def _tail(p, t):
    """Đuôi: một sóng chạy dọc từ gáy ra chót, đốt nào tới lượt đốt ấy uốn."""
    pts = []
    for i in range(11):
        u = i / 10
        wave = math.sin(t * 2.2 - u * 4.4) * (3 + 9 * u)
        x = 88 + u * 26 - u * u * 12
        y = 74 - u * 46 + wave * 0.5
        pts.append(QPointF(x + wave * 0.5, y))

    band = QPainterPath()
    for i in range(len(pts) - 1):
        wide = 6.2 * (1 - i / len(pts)) + 0.8
        band.addPath(ribbon(pts[i], pts[i], pts[i + 1], wide, wide * 0.82))
    p.setPen(Qt.PenStyle.NoPen)
    for color, dx, dy in ((BILE, 0.9, 0.7), (VENOM, -0.9, -0.7)):
        p.setBrush(_tone(color, 70))
        p.drawPath(band.translated(dx, dy))
    p.setBrush(HIDE)
    p.drawPath(band)

    # gai lưng chạy dọc sống đuôi
    p.setBrush(_tone(BILE, 120))
    for i in range(1, len(pts) - 1):
        a = math.atan2(pts[i + 1].y() - pts[i - 1].y(),
                       pts[i + 1].x() - pts[i - 1].x()) - math.pi / 2
        h = 4.4 * (1 - i / len(pts)) + 1.0
        spike = QPolygonF([
            QPointF(pts[i].x() + math.cos(a - 0.3) * 1.6,
                    pts[i].y() + math.sin(a - 0.3) * 1.6),
            QPointF(pts[i].x() + math.cos(a) * h, pts[i].y() + math.sin(a) * h),
            QPointF(pts[i].x() + math.cos(a + 0.3) * 1.6,
                    pts[i].y() + math.sin(a + 0.3) * 1.6)])
        p.drawPolygon(spike)


def _bulk(p, breath):
    """Thân, sọ và chi trước — khối tĩnh, chỉ phồng lên xẹp xuống theo thở."""
    p.setPen(Qt.PenStyle.NoPen)
    for color, dx, dy in ((BILE, 1.1, 0.8), (VENOM, -1.1, -0.8)):
        p.setBrush(_tone(color, 76))
        p.drawPath(_BODY.translated(dx, dy))
    p.setBrush(HIDE)
    p.drawPath(_BODY)

    # bụng và hàm dưới bắt sáng hắt từ mặt nước
    p.save()
    p.setClipPath(_BODY)
    belly = QLinearGradient(0, 78, 0, 104)
    belly.setColorAt(0.0, _tone(BELLY, 0))
    belly.setColorAt(1.0, _tone(BELLY, 235))
    p.setBrush(belly)
    p.drawRect(QRectF(10, 74, 92, 34))

    # vảy: hàng chấm chạy dọc lưng và sườn
    r = Rolls(6031963)
    p.setBrush(_tone(QColor("#254A30"), 150))
    for _ in range(120):
        p.drawEllipse(QPointF(r(18, 96), r(60, 100)), r(0.5, 1.3), r(0.4, 0.9))
    p.restore()

    # chỉ viền cái bóng chung. Viền riêng từng khối thì lộ đường nối, và con
    # vật trông như hai quả bóng chồng lên nhau.
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(BILE, 100), 0.6))
    p.drawPath(_BODY)
    # gờ sống mũi, một nét ngắn chạy dọc sọ cho có khối
    p.setPen(QPen(_tone(BILE, 60), 0.5))
    ridge = QPainterPath(QPointF(16, 76))
    ridge.cubicTo(QPointF(30, 69), QPointF(42, 67), QPointF(52, 66))
    p.drawPath(ridge)


def _maw(p, t):
    """Hàm há theo nhịp, răng nhọn, và cái lưỡi chẻ thò ra nếm không khí."""
    gape = (0.5 + 0.5 * math.sin(t * 0.62)) ** 2
    p.save()
    p.translate(68, 88)
    p.rotate(-15 * gape)
    p.translate(-68, -88)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_tone(QColor("#2B0E14"), 240))
    p.drawPath(_jaw())
    p.setBrush(HIDE)
    p.drawPath(_jaw().translated(0, 1.6))
    # răng hàm dưới
    p.setBrush(QColor("#E6E9D4"))
    for k in range(9):
        u = k / 8
        x = 16 + u * 48
        y = 85.5 + u * 2.0
        tooth = QPolygonF([QPointF(x, y), QPointF(x + 1.7, y),
                           QPointF(x + 0.85, y - 4.4 - (k % 2) * 1.3)])
        p.drawPolygon(tooth)
    p.restore()

    # răng hàm trên
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#E6E9D4"))
    for k in range(10):
        u = k / 9
        x = 14 + u * 52
        y = 80.5 + u * 4.2
        tooth = QPolygonF([QPointF(x, y), QPointF(x + 1.7, y),
                           QPointF(x + 0.85, y + 4.6 + (k % 2) * 1.5)])
        p.drawPolygon(tooth)

    # lưỡi chẻ, chỉ thò khi hàm há đủ rộng
    if gape > 0.45:
        out = (gape - 0.45) / 0.55
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(_tone(QColor("#C8446A"), 220), 1.2))
        base = QPointF(18, 84)
        tip = QPointF(base.x() - 8 * out, base.y() + 5 * out)
        for fork in (-1.8, 1.8):
            p.drawLine(base, QPointF(tip.x() + fork, tip.y() + fork * 0.6))


def _eye(p, t):
    """Mắt vàng, con ngươi khe dọc co giãn — thứ duy nhất nhìn thẳng vào ta."""
    c = QPointF(43, 72.5)
    glow(p, c, 5.0, _tone(BILE, 90))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#D9D33C"))
    p.drawEllipse(c, 3.3, 2.7)
    p.setBrush(_tone(QColor("#6B5A12"), 160))
    p.drawEllipse(QPointF(c.x(), c.y() + 0.5), 3.3, 1.1)

    slit = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 0.5))
    p.setBrush(QColor("#08120A"))
    p.drawEllipse(c, 1.15 * slit + 0.3, 2.5)
    p.setBrush(QColor("#F4F0D0"))
    p.drawEllipse(QPointF(c.x() - 1.0, c.y() - 1.1), 0.55, 0.45)

    # gò mày nặng đè xuống nửa trên con mắt
    p.setBrush(HIDE)
    brow = QPainterPath()
    brow.moveTo(36, 71)
    brow.cubicTo(40, 66.5, 47, 66, 51, 69)
    brow.lineTo(51, 63.5)
    brow.cubicTo(46, 61, 39, 62, 35, 67)
    brow.closeSubpath()
    p.drawPath(brow)


def _spores(p, t):
    """Bào tử phát quang bay **lên** — không dạt ngang, không quay vòng."""
    r = Rolls(9091963)
    p.setPen(Qt.PenStyle.NoPen)
    for i in range(70):
        speed = r(0.08, 0.26)
        phase = r(0, 1)
        x0 = r(4, 96)
        rise = (t * speed + phase) % 1.0
        y = WATER + 6 - rise * 108
        x = x0 + math.sin(rise * 7 + phase * 6) * 3.4
        fade = math.sin(math.pi * rise)
        tone = QColor(VENOM if i % 5 == 0 else BILE)
        tone.setAlpha(int(180 * fade))
        p.setBrush(tone)
        size = r(0.4, 1.0)
        p.drawEllipse(QPointF(x, y), size, size)


def _vines(p, t):
    """Dây leo tiền cảnh đung đưa — nhắc rằng đầm này cũng là của hắn."""
    for k, (x0, length, phase) in enumerate(((6, 40, 0.0), (94, 34, 2.1),
                                             (78, 24, 4.0))):
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(_tone(QColor("#0B2014"), 220), 2.2 - k * 0.4))
        sway = math.sin(t * 0.55 + phase) * 5
        vine = QPainterPath(QPointF(x0, -4))
        vine.quadTo(QPointF(x0 + sway, length * 0.6), QPointF(x0 + sway * 1.7, length))
        p.drawPath(vine)
        p.setPen(QPen(_tone(BILE, 70), 0.6))
        p.drawPath(vine)
        # lá
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(_tone(QColor("#123A20"), 220))
        for u in (0.4, 0.7, 0.95):
            q = vine.pointAtPercent(u)
            p.drawEllipse(q, 3.4, 1.5)


def _readout(p, t):
    """Nhịp thở và độ phủ bào tử — hai chỉ số duy nhất đáng theo dõi."""
    # vạch nhịp thở chạy ngang mép dưới, kiểu điện tâm đồ
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(MINT, 120), 0.6))
    trace = QPainterPath(QPointF(6, 118))
    for k in range(60):
        u = k / 59
        x = 6 + u * 52
        beat = math.sin((u * 3 - t * 0.5) * math.tau)
        y = 118 - (beat ** 9) * 5
        trace.lineTo(x, y)
    p.drawPath(trace)

    # thanh phủ bào tử: đầy dần rồi tràn
    cover = (t * 0.05) % 1.0
    box = QRectF(66, 115, 28, 3.0)
    p.setPen(QPen(_tone(SWAMP.ink_soft, 110), 0.5))
    p.drawRect(box)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_tone(BILE if cover < 0.8 else VENOM, 200))
    p.drawRect(QRectF(box.x() + 0.5, box.y() + 0.5,
                      (box.width() - 1) * cover, box.height() - 1))


# ═════════════════════════════════════════════ ảnh nền dựng sẵn cho lớp tĩnh
_STILL = {}


def _still(scale):
    """Khối thân đứng yên; đuôi, hàm, mắt và bào tử thì vẽ lại mỗi khung."""
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
        _bulk(q, 0.0)
        q.end()
        _STILL[key] = ready
    return ready


def draw_absolute_lizard(p, rect, t=0.0):
    """Chân dung sống: nhận thêm `t` (giây) nên khung hồ sơ tự vẽ lại."""
    scale = min(rect.width() / W, rect.height() / H)
    still = _still(scale)
    breath = 1.0 + 0.018 * math.sin(t * 1.15)
    with design(p, rect):
        _swamp(p, t)
        _tail(p, t)
        # cả khối thân phồng lên xẹp xuống theo nhịp thở
        p.save()
        p.translate(52, 88)
        p.scale(breath, breath)
        p.translate(-52, -88)
        p.drawImage(QRectF(-6, -6, still.width() / scale,
                           still.height() / scale), still)
        _maw(p, t)
        _eye(p, t)
        p.restore()
        _vines(p, t)
        _spores(p, t)
        _readout(p, t)
        marks(p, QColor("#4E7A5C"))


# ═══════════════════════════════════════════════════════════════ hồ sơ
ABSOLUTE = Profile(
    name="Absolute Lizard",
    vi_name="Thằn Lằn Tuyệt Đối",
    real_name="Serpent Rex  ·  nguyên là Curt Connors",
    keys=("Lizard Absolute", "Serpent Rex"),

    kicker="Hồ sơ tuyệt đối",
    stamp="PHÂN LOẠI  ·  MỐI ĐE DOẠ CẤP QUỐC GIA",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="swamp",
    evolve_fx="bloom",       # giấy không bị phá mà bị chiếm, rồi mọc lại

    tagline="Không còn là con thằn lằn khổng lồ. Là một hệ sinh thái tự nhân "
            "bản, có trí tuệ nhân tạo cầm lái, đồng hoá cả một quốc gia trong "
            "một tuần.",

    summary=(
        "Bản chất Curt Connors không còn tồn tại trong đó nữa. Thứ còn lại là "
        "một thực thể bò sát thống nhất, tối ưu hoá tới giới hạn của sinh học "
        "và vật lý — và điều đáng sợ nhất không nằm ở cơ bắp hay bộ vảy, mà ở "
        "chỗ hắn không cần tự tay làm gì cả.",

        "Bào tử của hắn xâm nhập DNA của cây cối, côn trùng và thú vật, biến "
        "chúng thành những dạng bò sát lai phục tùng ý chí hắn. Một lần phun "
        "phủ 10 km²; bào tử tự nhân lên trong môi trường ẩm và sống 72 giờ. "
        "Hắn không tiến quân — hắn để cả hệ sinh thái tiến quân thay.",
    ),

    sections=(
        Section(
            title="Khuyếch đại năng lực vật lý & sinh học",
            intro="Mọi chỉ số đều bị đẩy tới đỉnh của cái mà quy luật sinh học "
                  "còn cho phép.",
            items=(
                ("Cơ bắp và bộ xương",
                 "Sợi cơ xoắn nano-sinh học cho tỉ lệ sức mạnh trên trọng "
                 "lượng gấp 15 lần thú săn mồi: nâng 40–60 tấn, cú đấm 12.000 "
                 "PSI xé được thép cường độ cao. Đuôi dài 4 mét quật ở 200 "
                 "km/h, sóng xung kích phá bán kính 15 mét."),
                ("Giáp vảy composite",
                 "Keratin nano trộn canxi, sắt và graphene sinh học: chặn đạn "
                 "12,7 mm, đạn pháo 20 mm, mảnh lựu đạn; chịu 1.200°C trong 5 "
                 "phút. Lớp gel dưới vảy phân tán 85% động năng va đập nên nội "
                 "tạng không việc gì."),
                ("Tái tạo cực đoan",
                 "Tế bào gốc bò sát đa năng mọc lại chi trong 4–6 giây, mọc "
                 "lại cả mắt, tim, và một phần não nếu tổn thương dưới 30%. "
                 "Đổi lại hắn cần sinh khối: enzyme tiết qua da phân huỷ vật "
                 "chất hữu cơ quanh mình — cây, thú, người — làm nguyên liệu, "
                 "và nuốt đủ thì phình to gấp rưỡi."),
                ("Giác quan siêu việt",
                 "Mắt kép nhìn hồng ngoại, tử ngoại và ánh sáng phân cực, quét "
                 "360° không cần quay đầu. Lưỡi Jacobson đánh hơi adrenaline, "
                 "tơ nhện và thuốc nổ từ 300 mét. Cơ quan cảm rung dưới da bắt "
                 "bước chân, xe tăng, máy bay từ 1 km ở độ nhạy 0,001 Hz."),
                ("Nọc thần kinh",
                 "Phun tia xa 25 mét: tê liệt thần kinh vận động trong 0,5 "
                 "giây, đông máu tức thời, phá huỷ khớp thần kinh khi vào máu. "
                 "Một lít pha vào nguồn nước đủ giết 200.000 người."),
                ("Bào tử đồng hoá sinh thái",
                 "Phát tán qua da, hơi thở hoặc dịch phun; xâm nhập DNA của "
                 "sinh vật rồi biến chúng thành bò sát lai phục tùng. Một lần "
                 "phủ 10 km², tự nhân lên chỗ ẩm, sống 72 giờ. Cây cối nhiễm "
                 "bào tử tiết enzyme ăn mòn bê tông và thép."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="Sinh học đột biến ghép thẳng vào khí tài quân sự, thành một "
                  "mạng chiến tranh sinh học khép kín.",
            items=(
                ("AI “Ophidian”",
                 "Cấy vào não bò sát qua giao diện thần kinh. Quan sát 30 giây "
                 "là dự đoán quỹ đạo mục tiêu với độ chính xác 98%, và nó "
                 "không có điểm mù: drone nano, vệ tinh mini, cảm biến địa "
                 "chấn và camera sinh học từ bào tử cùng dựng một bản đồ 3D "
                 "cập nhật liên tục."),
                ("Bầy drone “Nanoserpent”",
                 "Drone 2 cm nuôi từ chính bào tử biến đổi gen, gắn vi mạch "
                 "sinh học. Một tổ hợp thả 5.000 con: tuần tra bán kính 10 km, "
                 "mang nọc thần kinh, phun dung môi phá tơ, nhả khói gây ảo "
                 "giác — tất cả đồng bộ dưới tay Ophidian."),
                ("Bộ giáp “Crypsis Frame”",
                 "Xương ngoài titan pha graphene sinh học gắn thẳng lên người, "
                 "piston thuỷ lực sinh học nhân đôi sức nâng. Kèm gai phóng "
                 "tầm 50 m xuyên giáp 10 cm, súng phun enzyme phá tơ, máy phát "
                 "hạ âm 7 Hz, và lớp da tinh thể đổi màu che cả thân nhiệt "
                 "trước cảm biến hồng ngoại."),
                ("Mạng “Serpent Grid”",
                 "Bào tử cảm biến bám lên mọi bề mặt trong vùng, bắt rung "
                 "động, nhiệt độ, hoá chất, tơ nhện và sóng radio rồi gửi về "
                 "AI. Trong 50 km², không một chuyển động nào lọt."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Từ giác quan báo nguy tới ý chí chiến đấu, mỗi thứ có một "
                  "biện pháp riêng.",
            items=(
                ("Giao thức quá tải giác quan",
                 "Ophidian đọc ra tần số hoạt động của giác quan nhện rồi bơm "
                 "tín hiệu giả không ngừng: sóng âm ngẫu nhiên 10–20 kHz từ "
                 "bầy drone, hologram 3D giả lập đòn đánh từ mọi hướng, rung "
                 "địa chấn giả. Phản xạ của Peter chậm 60%, có khi co giật nhẹ "
                 "— và pheromone gây ảo giác phun kèm khiến anh ta không còn "
                 "phân biệt nổi đòn thật."),
                ("Dung môi “Protease-9”",
                 "Enzyme tiết từ tuyến nọc, hoạt hoá bằng nhiệt ở 80°C, bẻ gãy "
                 "liên kết peptide của fibroin trong 0,3 giây. Phun tia 25 m, "
                 "và drone nano còn bắn thẳng vào sợi tơ ngay khi nó vừa rời "
                 "cổ tay."),
                ("Vảy chống bám dính",
                 "Cấu trúc nano siêu kỵ nước giảm 90% ma sát bề mặt: tơ không "
                 "bám được vào người hắn, mà lớp nhờn tiết ra từ da cũng khiến "
                 "Spider-Man không giữ nổi để tung đòn cận chiến."),
                ("Tấn công không điểm mù",
                 "5.000 drone cộng 200 bò sát lai đánh đồng loạt từ mọi góc và "
                 "mọi độ cao: drone giăng lưới lửa chéo không chừa khoảng "
                 "trống, bò sát lai quấy rối cận chiến, còn Lizard vào từ đúng "
                 "điểm mù mà AI đã tính. Áp sát dưới 3 mét là gai phóng tự "
                 "động khai hoả."),
                ("Nọc ức chế thần kinh vận động",
                 "Một vết vuốt hoặc một mũi tên nọc từ drone là cơ bắp mất khả "
                 "năng co duỗi và mất luôn lực bám. Liều nhẹ thì chậm chạp, "
                 "liều nặng thì ngã quỵ sau 5 giây — đủ để kết liễu."),
                ("Pheromone khủng bố",
                 "Ức chế dopamine, đẩy cortisol lên: hoảng loạn tột độ, mất "
                 "tập trung, hiệu suất chiến đấu rơi một nửa và sai lầm chiến "
                 "thuật bắt đầu xuất hiện."),
            ),
        ),
    ),

    tiers=(
        Tier("Tier 1", "Đô thị",
             "Đấm sập 5–7 toà nhà 20 tầng, quật đuôi phá cầu và cao tốc. Bào "
             "tử biến 100–200 người dân thành bò sát lai hung hãn quay lại "
             "đánh hạ tầng, còn bầy drone thì cắt điện và cắt liên lạc. Cứu "
             "hoả và cảnh sát bị áp đảo hoàn toàn.",
             "Trong 1 giờ"),
        Tier("Tier 2", "Vùng / bang",
             "Bào tử phủ 50.000 km²: rừng và đồng ruộng thành đầm lầy bò sát, "
             "cây tiết enzyme ăn mòn đường sá và đường ống dẫn dầu. 80% giếng, "
             "sông, hồ nhiễm nọc. Lưới điện bị bầy drone và quái vật cắn đứt. "
             "Mất điện, mất nước, nông nghiệp sụp, dịch bệnh biến đổi gen bùng "
             "phát.",
             "Trong 24 giờ"),
        Tier("Tier 3", "Quốc gia",
             "Hàng triệu bò sát lai sinh ra từ động vật, côn trùng và cả con "
             "người. Xe tăng bị xé nóc và phun nọc vào khe hở, trực thăng bị "
             "đuôi và gai phóng bắn hạ, radar cùng kho vũ khí bị drone phá. "
             "Cảng biển và sân bay bị cá sấu lai phong toả; quân đội mất 70% "
             "khả năng chiến đấu trong 72 giờ.",
             "Trong 1 tuần"),
    ),

    facts=(
        ("Tên mã", "Serpent Rex"),
        ("Cấp đe doạ", "Tier 3 — quốc gia"),
        ("Sức nâng", "40 – 60 tấn  ·  cú đấm 12.000 PSI"),
        ("Đuôi", "Dài 4 m, quật 200 km/h, xung kích 15 m"),
        ("Tái tạo", "Mọc lại chi trong 4 – 6 giây"),
        ("Bào tử", "10 km² mỗi lần phun  ·  sống 72 giờ"),
        ("AI", "Ophidian  ·  dự đoán 98% sau 30 giây"),
        ("Bầy drone", "5.000 Nanoserpent cỡ 2 cm"),
    ),

    blurb="Những hồ sơ khác đánh vào một thành phố, một lưới điện, một quân "
          "đội. Hồ sơ này đánh vào chính cái nền mà tất cả những thứ đó đứng "
          "lên: đất, nước, cây và thú. Diệt được hắn cũng chẳng còn gì để cứu "
          "— vì đến lúc ấy cả vùng đã là con của hắn.",

    art=draw_absolute_lizard,
    caption="Dựng lại từ camera sinh học  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Lizard_(character)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Curtis_Connors_(Earth-616)"),
    ),
)
