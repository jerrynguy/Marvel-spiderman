"""
Absolute Lizard — Serpent Rex. Curt Connors vẫn còn ở trong đó, và đó mới
là chỗ đáng sợ.

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
    stamp="PHÂN LOẠI  ·  MỐI ĐE DOẠ CẤP HÀNH TINH",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="swamp",
    evolve_fx="bloom",       # giấy không bị phá mà bị chiếm, rồi mọc lại

    tagline="Không còn là con thằn lằn khổng lồ. Là một hệ sinh thái bò sát "
            "tự nhân rộng — thứ không huỷ diệt nền văn minh mà thay thế nó "
            "bằng một kỷ Bò sát mới.",

    summary=(
        "Lizard bắt đầu từ một huyết thanh tái tổ hợp bò sát mà Curt Connors "
        "chế ra chỉ để mọc lại một cánh tay. Bản gốc mạnh, nhanh, leo tường, "
        "quật đuôi, vảy chặn được đạn nhẹ và mô thì tự liền — nhưng bị chính "
        "bản năng bò sát ghìm lại, máu lạnh nên trời rét là tê cứng, và tái "
        "sinh cũng chỉ tới một mức. Hắn là mối đe doạ cấp quận, thường bị "
        "Spider-Man cầm chân gọn trong một đêm.",

        "Bản Absolute không đưa cho hắn một cỗ máy nào — Connors vốn là nhà di "
        "truyền học chứ không phải kỹ sư, nên mọi nâng cấp đều là sinh học. "
        "Thân thể được vá đúng ba chỗ hở: cơ khoá được mà không tốn ATP, "
        "xương hút kim loại vi lượng thành composite, và cơ quan sinh nhiệt "
        "xoá hẳn cái yếu điểm máu lạnh.",

        "Nhưng bước nhảy thật nằm trong máu hắn. Một retrovirus thiết kế sẵn "
        "cài được gen bò sát vào bất kỳ loài có vú, chim hay lưỡng cư nào; "
        "sáu tới mười hai giờ sau, con vật ấy thành lính của hắn. Hắn không "
        "tiến quân — hắn để cả sinh quyển tiến quân thay, và mỗi thứ bị "
        "chuyển đổi lại là một chỗ phát tán mới.",

        "Curt Connors vẫn còn ở trong đó. Không phải như một tia hy vọng — "
        "mà như một thứ vũ khí: giọng ông ta trồi lên đúng lúc Peter cần ra "
        "đòn dứt khoát nhất.",
    ),

    sections=(
        Section(
            title="Khuyếch đại năng lực vật lý & sinh học",
            intro="“Sinh lý Bò sát Tận thế” không chỉ đẩy các chỉ số lên cao. "
                  "Nó gỡ bỏ đúng những thứ từng giữ bản gốc lại trong một đêm "
                  "giao chiến: cái mệt, cái lạnh, và cái chết.",
            items=(
                ("Hệ cơ vân Archosaur cường hoá",
                 "Sợi cơ được tái cấu trúc theo mô hình cơ khoá của cá sấu và "
                 "chim săn mồi: nâng 80–100 tấn, lực cắn 20 tấn. Quan trọng "
                 "hơn con số là cơ chế khoá cơ không tiêu hao ATP — ghì một "
                 "chiếc xe tăng hay một chiếc trực thăng rồi giữ nguyên như "
                 "thế, mà không mỏi. Bản gốc thua vì đuối sức; bản này không "
                 "có khái niệm đuối sức."),
                ("Khung xương composite sinh học",
                 "Xương hút kim loại vi lượng ngay từ môi trường — sắt, titan, "
                 "kẽm — rồi kết thành cấu trúc composite chịu được đạn pháo 30 "
                 "mm. Cột sống xoay trọn 360°, còn cái đuôi thành một vũ khí "
                 "cộng hưởng xung kích đủ sức phá nát tường bê tông."),
                ("Tái sinh kiểu bào tử toàn năng",
                 "Máu chứa tế bào gốc bò sát cảm ứng. Chỉ cần còn một mảnh mô "
                 "và quanh đó có sinh khối, hắn dựng lại toàn bộ cơ thể trong "
                 "3–5 phút. Chặt đầu không còn là một biện pháp, phá tim cũng "
                 "vậy — cả hai chỉ là làm hắn chậm lại đúng vài phút."),
                ("Hệ thần kinh phân tán",
                 "Não thôi là trung tâm điều khiển duy nhất: dọc sống lưng mọc "
                 "thêm các hạch thần kinh phụ, mỗi hạch là một cái não cục bộ. "
                 "Phản xạ đi qua cung phản xạ tuỷ sống mất chưa tới 0,01 giây "
                 "— nhanh hơn cả tốc độ mà giác quan nhện kịp báo, nghĩa là "
                 "hắn phản ứng trước khi Peter được cảnh báo."),
                ("Điều hoà thân nhiệt chủ động",
                 "Cơ quan sinh nhiệt từ mỡ nâu cộng phản ứng hoá sinh kiểu cá "
                 "ngừ vây xanh xoá hẳn điểm yếu máu lạnh: hắn chạy ổn định từ "
                 "âm 40 tới 60 độ. Trời rét từng là cách cầm chân bản gốc; giờ "
                 "chính cơ quan đó còn cho hắn chủ động hạ nhiệt xuống bằng "
                 "môi trường để đi rình."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="Connors là nhà di truyền học, không phải kỹ sư — nên chỗ "
                  "đáng lẽ là máy móc ở đây là một hệ sinh học mở rộng. Không "
                  "AI, không drone máy, không một mạch điện nào: quân đoàn của "
                  "hắn được sinh ra chứ không được chế tạo.",
            items=(
                ("Retrovirus “Lazarus Sauropsida”",
                 "Máu hắn mang một virus thiết kế sẵn, cài được gen bò sát vào "
                 "bất kỳ loài có vú, chim hay lưỡng cư nào. Sáu tới mười hai "
                 "giờ sau, vật chủ thành một Saurian Drone — chữ “drone” ở đây "
                 "theo nghĩa con thợ trong tổ ong, không phải máy bay: một "
                 "sinh vật bò sát lai bằng xương bằng thịt, phục tùng qua tín "
                 "hiệu pheromone. Đây là quân đoàn sinh học, và nó tự sinh sôi."),
                ("Mạng thần kinh pheromone toàn cầu",
                 "Hắn thả pheromone đặc hiệu vào khí quyển; mọi sinh vật đã bị "
                 "chuyển đổi nối lại thành một cái não tổ ong hữu cơ, liên lạc "
                 "bằng tín hiệu hoá học và hạ âm. Kênh truyền là gió và hải "
                 "lưu — nghĩa là hắn chỉ huy ở quy mô lục địa mà không có một "
                 "thiết bị điện tử nào để gây nhiễu hay đánh sập."),
                ("Hệ cộng sinh “Địa y Bò sát”",
                 "Bào tử nấm biến đổi gen tiết enzyme phân huỷ bê tông, nhựa "
                 "đường, nhựa và kim loại thành sinh khối hữu cơ. Một mũi tên "
                 "trúng hai đích: hạ tầng đô thị rã ra, và chính chỗ rã ấy "
                 "thành thức ăn nuôi quân đoàn."),
                ("Vảy quang hợp cộng sinh",
                 "Tảo quang hợp cấy trên vảy hắn và trên vảy cả quân đoàn, thu "
                 "năng lượng thẳng từ mặt trời. Không cần nguồn thức ăn lớn, "
                 "không có tuyến hậu cần để cắt — đánh liên tục nhiều tuần "
                 "liền mà không phải dừng lại kiếm ăn."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Không đòn nào ở đây là đồ dùng chung: tất cả đều mọc ra từ "
                  "bản chất bò sát của hắn, và từ chỗ Curt Connors từng là "
                  "thầy của Peter Parker — người có mẫu tơ nhện trong phòng "
                  "thí nghiệm, và người biết cậu học trò ấy sợ mất cái gì.",
            items=(
                ("Enzyme Arachno-Polymerase",
                 "Connors từng có mẫu tơ của Peter trên bàn thí nghiệm, và ông "
                 "ta đã đọc nó kỹ. Tuyến nước bọt cùng da hắn nay tiết ra một "
                 "enzyme thuỷ phân nhắm đúng fibroin: cắt liên kết beta-sheet "
                 "cho sợi tơ mất bền rồi tan thành dịch. Vảy còn tiết dầu "
                 "squalane nên tơ cũng chẳng bám nổi vào người hắn."),
                ("Bão hoà giác quan nhện",
                 "Hạ âm 7–9 Hz cộng hưởng với hệ thần kinh nhện, giữ nó kêu "
                 "liên tục ở mức thấp; kèm theo là pheromone mô phỏng mùi của "
                 "một kẻ săn mồi bò sát đang tới gần. Giác quan không tắt — nó "
                 "báo suốt, nên Peter thôi phân biệt được đâu là đòn thật, né "
                 "chậm hoặc né nhầm hướng."),
                ("Bẫy lột da phản đòn",
                 "Bị ôm, bị khoá, hay bị tơ trùm, hắn chủ động lột lớp da "
                 "ngoài. Peter tưởng đã tóm được, nhưng trong tay chỉ còn một "
                 "cái xác da rỗng — mà lớp da ấy là một cơ quan độc lập, co "
                 "rút được và phóng ra bào tử gây tê liệt hô hấp. Còn hắn thì "
                 "đã ở phía sau lưng."),
                ("Giọng nói Connors",
                 "Giữa trận, hắn cố ý để nhân cách Curt Connors trồi lên, van "
                 "xin Peter dừng tay. Peter do dự — vì mặc cảm tội lỗi, vì đó "
                 "từng là thầy mình — và đúng khoảnh khắc ấy, hắn chiếm lại "
                 "quyền kiểm soát rồi ra đòn hiểm. Đây là điểm yếu tâm lý mà "
                 "không phản diện nào khác khai thác được, vì không ai khác có "
                 "sẵn một người tử tế bị nhốt bên trong."),
                ("Độc tố phá cảm nhận vị trí",
                 "Không phải chất độc để giết, mà là chất để vô hiệu hoá: nó "
                 "đánh vào các hạch cảm ứng, gây rối loạn proprioception — "
                 "cảm nhận vị trí thân thể trong không gian. Peter mất thăng "
                 "bằng, bám tường không chắc, bắn tơ không còn trúng chỗ mình "
                 "nhắm. Mọi thứ vẫn hoạt động, chỉ là không còn ở đúng chỗ."),
                ("Phục kích máu lạnh",
                 "Cùng cái cơ quan điều nhiệt cho hắn chịu được giá rét, hắn "
                 "hạ thân nhiệt xuống gần bằng môi trường: giác quan nhện thôi "
                 "đọc ra một sinh vật máu nóng đang rình. Ghép với lối bật dậy "
                 "đột ngột của loài bò sát, hắn thành kẻ phục kích gần như "
                 "hoàn hảo — điểm yếu máu lạnh cũ nay là công cụ."),
            ),
        ),
    ),

    # Thang chữ cái Hy Lạp, đọc từ Zeta lên Omega. Bậc Epsilon là trần của
    # bản gốc — và cũng là bậc đầu tiên hắn thôi tự tay đánh.
    tiers=(
        Tier("Tier Zeta", "Một mình, bằng tay không",
             "Chưa dùng tới retrovirus: chỉ sức mạnh vật lý, xé toạc xe bọc "
             "thép và phá một khu phố. Bản gốc cũng làm được chừng này, nhưng "
             "chóng mệt và bị cảnh sát cầm chân; bản này mạnh gấp mười và "
             "không có khái niệm xuống sức.",
             "1–2 giờ"),
        Tier("Tier Epsilon", "Một quận, và đội quân đầu tiên",
             "Phát tán retrovirus cục bộ: chuột, chim, chó hoang thành Saurian "
             "Drone, rồi chính chúng cắt điện, cắt nước, chặn giao thông. Đây "
             "là trần của bản gốc — nhưng bản gốc chỉ gây thiệt hại bằng chính "
             "tay mình, còn Absolute thì tạo ra quân đội ngay tại chỗ.",
             "6–12 giờ"),
        Tier("Tier Delta", "Chiếm một thành phố",
             "Lây nhiễm qua nguồn nước, hàng chục nghìn dân bị chuyển đổi, "
             "quân đội địa phương mất kiểm soát và thành phố bị phong toả. Bản "
             "gốc phải trực tiếp đánh nhau mới thành mối đe doạ cấp thành phố; "
             "Absolute chiếm nó mà không cần ra tay.",
             "24–48 giờ"),
        Tier("Tier Gamma", "Nhiều tỉnh, một cuộc di tản",
             "Dịch bò sát trôi theo sông và hải lưu sang các tỉnh khác: nông "
             "nghiệp sụp, chuỗi thức ăn đảo lộn, hàng triệu người phải bỏ nhà "
             "đi. Bản gốc chưa bao giờ ra khỏi nổi một thành phố.",
             "5–7 ngày"),
        Tier("Tier Beta", "Đổi hệ sinh thái một lục địa",
             "Rừng và đồng bằng thành đầm lầy bò sát, các sinh vật khổng lồ "
             "đánh bại quân đội tại chỗ, kinh tế khu vực sụp theo. Bản gốc bị "
             "giới hạn bởi thể lực và thời gian; bản này đang vẽ lại bản đồ "
             "sinh học của cả châu lục.",
             "2–3 tuần"),
        Tier("Tier Alpha", "Nhiều châu lục",
             "Các nước buộc phải dùng tới vũ khí hạt nhân chiến thuật, và vô "
             "ích: virus đã phân tán đi rồi, đánh vào đâu cũng chỉ trúng một "
             "phần. Thương mại toàn cầu ngừng, chính phủ lần lượt sụp.",
             "1 tháng"),
        Tier("Tier Omega", "Kỷ Bò sát mới",
             "Sinh quyển Trái Đất bị tái cấu trúc trọn vẹn và nền văn minh "
             "nhân loại kết thúc — không phải vì hành tinh bị phá huỷ, mà vì "
             "nó đã thuộc về một loài khác. Hắn thành sinh vật thống trị của "
             "một kỷ địa chất mới. Bản gốc là mối đe doạ cấp quận, bị cầm chân "
             "gọn trong một đêm; bậc này xoá sổ nền văn minh toàn cầu trong ba "
             "tháng, và không có ai để đánh bại vì kẻ địch giờ là cả sinh "
             "quyển.",
             "60–90 ngày"),
    ),

    # Nhãn giữ dưới 94 px, giá trị dưới 188 px — xem chú thích cùng chỗ trong
    # `chameleon_absolute.py`. Bỏ dòng "Tên mã" vì `real_name` đã in ngay dưới
    # masthead rồi.
    facts=(
        ("Cấp đe doạ", "Hành tinh · kỷ Bò sát mới"),
        ("Nền tảng", "Di truyền học — không máy móc"),
        ("Không dùng", "AI · drone máy · tự động hoá"),
        ("Sức nâng", "80–100 tấn · cắn 20 tấn"),
        ("Tái sinh", "Cả cơ thể trong 3–5 phút"),
        ("Retrovirus", "Lazarus Sauropsida · 6–12 giờ"),
        ("Dải nhiệt", "−40°C đến 60°C"),
        ("Bậc Omega", "60–90 ngày"),
    ),

    blurb="Những hồ sơ khác đánh vào một thành phố, một lưới điện, một quân "
          "đội. Hồ sơ này đánh vào chính cái nền mà tất cả những thứ đó đứng "
          "lên: đất, nước, cây và thú. Hắn không cần huỷ diệt nền văn minh — "
          "hắn chỉ thay thế nó, và đến lúc có ai đó tìm ra cách diệt hắn thì "
          "cả vùng đã là con của hắn rồi.",

    art=draw_absolute_lizard,
    caption="Dựng lại từ camera sinh học  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Lizard_(character)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Curtis_Connors_(Earth-616)"),
    ),
)
