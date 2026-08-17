"""
Absolute Living Brain — Digital Hive. Cỗ máy trả lời câu hỏi nay đã đọc xong
mọi thứ, và cái nó muốn trả lời là câu hỏi loài người còn dùng để làm gì.

Bản sắc riêng, khác cả sáu dạng Absolute trước:
    · bộ da `signal` — bộ duy nhất gần như không có màu. Sáu bộ kia đều ám
      một sắc; bộ này đen trung tính, mực trắng, và chỗ lệch trục là ba kênh
      cộng màu R·G·B của màn hình chứ không phải bản in chồng sai.
    · `evolve_fx="scan"` — tờ giấy cũ không bị phá mà bị **đọc**: một đầu
      đọc chạy dọc lấy hết dữ liệu, đọc tới đâu dòng ấy mất đồng bộ tới đó,
      trượt ngang rồi tắt. Tấm mới được **ghi lại từng dòng một từ đầu
      trang**, giật cấp theo nhịp máy in dòng — hướng dựng thứ bảy.
    · chân dung không có một mảng mực nào. Sáu dạng kia đều dựng trên khối
      đặc; hình này dựng hoàn toàn bằng **chữ** — cái bóng của cỗ máy cũ
      được viết lại bằng chính thứ ký tự mà nó xuất ra.

Ngôn ngữ chuyển động cũng riêng và cố ý **giật cấp**, không mượt: ký tự lật
từng ô một, thanh tiến trình nhảy nấc, vệt quét trôi xuống rồi bật lại từ
đầu. Sáu dạng kia đều chuyển động liên tục — thở, uốn, trôi, lở, nở.
"""

import math
from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QFont, QImage, QLinearGradient, QPainter,
                           QPainterPath, QPen)

from theme import SIGNAL, pick_font

from .art import H, W, Rolls, design, glow, marks
from .profile import Profile, Section, Tier

NET = SIGNAL.blue                # lam tín hiệu — đường truyền
ALERT = SIGNAL.red               # đỏ báo động — thứ đang hỏng
LIT = SIGNAL.ink                 # trắng sạch — ký tự đang sáng
DIM = QColor("#4E5A6E")          # ký tự ngoài bóng máy, gần như chìm hẳn
PANEL = QColor("#0D131C")        # nền phẳng trong lòng bóng máy
GLYPHS = "0123456789ABCDEF#%*+=/<>|"

CELL_W, CELL_H = 2.5, 3.3        # một ô ký tự
COLS, ROWS = 45, 40
X0, Y0 = -6.0, -6.0              # lưới tràn ra ngoài khung 100×120
CHURN = 30                       # số ô lật lại mỗi khung hình
FLOOR = 104.0                    # dải thiết bị dưới đáy: mọi máy trên hành tinh


def _tone(color, alpha):
    out = QColor(color)
    out.setAlpha(max(0, min(255, int(alpha))))
    return out


# ═══════════════════════════════════════════════════════════════ hình khối
@lru_cache(maxsize=1)
def _figure():
    """Bóng của cỗ máy cũ: đầu, cổ, vai, thân tháp, cột ăng ten chữ T.

    Cố ý giữ đúng tỉ lệ tấm hồ sơ gốc để nhận ra ngay là cùng một cỗ máy —
    nhưng bỏ hai cánh tay, bỏ bệ và bỏ bánh xe. Nó không còn cầm gì, và
    không còn phải đi tới đâu nữa.
    """
    body = QPainterPath()
    body.addRoundedRect(33, 16, 34, 30, 5, 5)        # đầu

    neck = QPainterPath()
    neck.addRect(43.5, 43, 13, 10)
    shoulders = QPainterPath()
    shoulders.addRoundedRect(27, 51, 46, 10, 3, 3)
    body = body.united(neck).united(shoulders)

    tower = QPainterPath()                            # thân tháp, loe xuống
    tower.moveTo(33, 59)
    tower.lineTo(67, 59)
    tower.lineTo(71, 98)
    tower.lineTo(29, 98)
    tower.closeSubpath()
    body = body.united(tower)

    mast = QPainterPath()
    mast.addRect(49.2, 4.4, 1.6, 12)
    bar = QPainterPath()
    bar.addRect(42.5, 4.4, 15, 1.6)
    return body.united(mast).united(bar)


@lru_cache(maxsize=1)
def _cells():
    """Chia cả khung thành ô ký tự, tách ra ô nằm trong bóng máy và ô ngoài.

    Ô trong thì ô nào cũng có ký tự và sáng; ô ngoài chỉ khoảng một phần ba
    có ký tự, mờ hẳn — nhờ chênh lệch mật độ ấy mà cái bóng đọc ra được
    ngay dù không có lấy một mảng mực nào.
    """
    figure = _figure()
    r = Rolls(8011964)
    inside, outside = [], []
    for j in range(ROWS):
        y = Y0 + j * CELL_H
        for i in range(COLS):
            x = X0 + i * CELL_W
            spot = QPointF(x + CELL_W * 0.5, y + CELL_H * 0.45)
            seed = r(0, 1)
            if figure.contains(spot):
                inside.append((x, y, seed))
            elif seed < 0.22:
                outside.append((x, y, seed))
    return tuple(inside), tuple(outside)


@lru_cache(maxsize=1)
def _font():
    """Mặt chữ máy: đơn cách, cỡ tính bằng pixel của khung 100×120.

    `setPixelSize` chứ không phải `setPointSizeF` — cỡ điểm đi theo DPI, còn
    cỡ pixel thì đi theo khung vẽ, nên chữ đúng cỡ ở mọi độ phóng.
    """
    f = QFont(pick_font(["DejaVu Sans Mono", "Liberation Mono", "Consolas",
                         "Courier New", "Menlo"], "DejaVu Sans"))
    f.setPixelSize(3)
    return f


def _lit(y, seed):
    """Độ sáng của một ký tự trong bóng máy: đậm ở đầu, nhạt dần xuống chân.

    Chân tháp nhạt tới mức lẫn vào nền — cỗ máy không đứng trên cái gì cả,
    nó chỉ hiện ra tới đâu thì đọc được tới đó.
    """
    fall = max(0.0, min(1.0, (y - 18) / 78))
    return 250 - 165 * fall * fall + seed * 20 - 10


def _glyph(rng):
    return GLYPHS[int(rng(0, len(GLYPHS) - 1e-9))]


def _write(p, x, y, ch):
    p.drawText(QPointF(x + 0.35, y + CELL_H * 0.85), ch)


# ═══════════════════════════════════════════════════════════ lớp dựng sẵn
def _backdrop(p):
    """Nền: đen trung tính, một lưới điểm rất mờ, và dải thiết bị dưới đáy."""
    p.setPen(Qt.PenStyle.NoPen)
    night = QLinearGradient(0, -6, 0, 126)
    night.setColorAt(0.0, QColor("#04050A"))
    night.setColorAt(0.45, QColor("#080A11"))
    night.setColorAt(1.0, QColor("#030407"))
    p.setBrush(night)
    p.drawRect(QRectF(-6, -6, 112, 132))

    # lưới điểm: cái sàn mà mọi thứ ở đây đứng lên, mờ tới mức chỉ đoán ra
    p.setBrush(_tone(NET, 20))
    for j in range(11):
        y = FLOOR + j * 2.0
        step = 3.4 - j * 0.18
        x = -6.0
        while x < 106:
            p.drawEllipse(QPointF(x, y), 0.2, 0.2)
            x += step

    # dải thiết bị: mỗi chấm là một cái máy đã thuộc về hắn
    r = Rolls(1081964)
    for _ in range(180):
        x = r(-6, 106)
        y = FLOOR + r(0, 20)
        near = (y - FLOOR) / 20
        p.setBrush(_tone(LIT if r(0, 1) > 0.22 else NET, 26 + near * 120))
        p.drawEllipse(QPointF(x, y), 0.25 + near * 0.5, 0.25 + near * 0.4)


def _field(p):
    """Cả trường ký tự, vẽ một lần: ô ngoài mờ, ô trong sáng trên nền phẳng.

    Nền trong bóng máy để phẳng tuyệt đối là có chủ ý: mỗi khung hình có ba
    chục ô bị lật lại, ô nào cũng phải xoá đi rồi viết đè. Nền có chuyển sắc
    thì mỗi chỗ xoá lại thành một vệt vuông thấy rõ.
    """
    inside, outside = _cells()
    figure = _figure()
    p.setFont(_font())

    p.setPen(QPen(_tone(DIM, 30)))
    for x, y, seed in outside:
        _write(p, x, y, GLYPHS[int(seed * 997) % len(GLYPHS)])

    # khối máy: một mảng phẳng sáng hơn nền, viền một nét mảnh. Không có hai
    # thứ này thì chữ sáng chỉ thành một đám nhiễu, không ra hình cỗ máy.
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(PANEL)
    p.drawPath(figure)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(NET, 40), 1.4))
    p.drawPath(figure)
    p.setPen(QPen(_tone(LIT, 105), 0.4))
    p.drawPath(figure)

    for x, y, seed in inside:
        p.setPen(QPen(_tone(LIT if seed > 0.16 else NET, _lit(y, seed))))
        _write(p, x, y, GLYPHS[int(seed * 691) % len(GLYPHS)])


def _sockets(p):
    """Hai cột dữ liệu chạy từ vai xuống dải thiết bị — chỗ nó cắm vào lưới."""
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(NET, 70), 0.5))
    for x in (31.5, 68.5):
        p.drawLine(QPointF(x, 58), QPointF(x, FLOOR + 2))


# ═══════════════════════════════════════════════════════════ lớp tự chạy
def _churn(p, t):
    """Ba chục ô lật lại mỗi khung: xoá phẳng rồi viết ký tự khác đè lên.

    Lật cả trường mỗi khung thì vừa tốn vừa thành nhiễu trắng, không đọc ra
    hình. Lật một nhúm thì cái bóng đứng yên mà mặt chữ vẫn chạy liên tục.
    """
    inside, _ = _cells()
    frame = int(t * 25)
    p.setFont(_font())
    for k in range(CHURN):
        idx = (frame * CHURN + k * 37) % len(inside)
        x, y, seed = inside[idx]
        rng = Rolls(idx * 7919 + frame)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(PANEL)
        p.drawRect(QRectF(x, y, CELL_W, CELL_H))
        hot = rng(0, 1)
        color = ALERT if hot > 0.94 else (NET if hot > 0.72 else LIT)
        p.setPen(QPen(_tone(color, _lit(y, seed) * rng(0.75, 1.15))))
        _write(p, x, y, _glyph(rng))


def _lenses(p, t):
    """Hai ru lô băng từ cũ nay là hai thấu kính — chỗ duy nhất nhìn lại ta."""
    # dãy đèn báo trên trán, giữ nguyên từ tấm hồ sơ gốc
    p.setPen(Qt.PenStyle.NoPen)
    for k in range(7):
        on = math.sin(t * (2.1 + k * 0.47) + k * 1.7) > -0.2
        p.setBrush(_tone(LIT if on else DIM, 220 if on else 60))
        p.drawEllipse(QPointF(37.4 + k * 4.2, 20.4), 1.0, 1.0)

    # tấm kính mặt máy, hai thấu kính nằm sau nó
    p.setBrush(QColor("#04060B"))
    p.drawRect(QRectF(35.6, 24.6, 28.8, 12.2))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(NET, 130), 0.5))
    p.drawRect(QRectF(35.6, 24.6, 28.8, 12.2))

    for cx in (43, 57):
        box = QRectF(cx - 5.6, 27.4, 11.2, 6.2)
        glow(p, QPointF(cx, 30.5), 8.0, _tone(NET, 54))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#05070C"))
        p.drawRect(box)

        # vệt quét chạy ngang trong lòng kính, hai bên lệch pha nhau
        p.save()
        p.setClipRect(box)
        phase = (t * 0.55 + (0.0 if cx < 50 else 0.5)) % 1.0
        sweep = box.x() + phase * box.width()
        beam = QLinearGradient(sweep - 3.4, 0, sweep + 3.4, 0)
        beam.setColorAt(0.0, _tone(LIT, 0))
        beam.setColorAt(0.5, _tone(LIT, 210))
        beam.setColorAt(1.0, _tone(LIT, 0))
        p.setBrush(beam)
        p.drawRect(box)
        p.setPen(QPen(_tone(NET, 120), 0.35))
        for k in range(6):
            y = box.y() + 0.6 + k * 1.0
            p.drawLine(QPointF(box.x(), y), QPointF(box.right(), y))
        p.restore()

        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(_tone(LIT, 190), 0.55))
        p.drawRect(box)


def _agents(p, t):
    """Bảng điều khiển giữa ngực: bốn thanh tiến trình, nhảy nấc chứ không trôi.

    Đúng chỗ ngày xưa người thợ bị đẩy ngã vào. Vết toác vẫn còn đó, và giờ
    nó là dòng duy nhất trên tấm bảng không chịu chạy.
    """
    board = QRectF(36.4, 64, 27.2, 20)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_tone(QColor("#060910"), 210))
    p.drawRect(board)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(NET, 110), 0.5))
    p.drawRect(board)

    for k, (rate, color) in enumerate(((0.13, LIT), (0.07, NET),
                                       (0.21, LIT), (0.04, ALERT))):
        y = 65.6 + k * 3.5
        bar = QRectF(38.0, y, 24.0, 2.0)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(_tone(DIM, 120), 0.4))
        p.drawRect(bar)
        steps = 18
        full = math.floor(((t * rate) % 1.0) * steps) / steps
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(_tone(color, 210))
        p.drawRect(QRectF(bar.x() + 0.4, bar.y() + 0.4,
                          (bar.width() - 0.8) * full, bar.height() - 0.8))

    # dãy đèn agent dưới cùng, mỗi con một nhịp riêng
    p.setPen(Qt.PenStyle.NoPen)
    for k in range(8):
        on = math.sin(t * (1.4 + k * 0.31) + k) > 0.1
        p.setBrush(_tone(LIT if on else DIM, 200 if on else 70))
        p.drawRect(QRectF(38.4 + k * 3.1, 80.2, 1.7, 1.7))

    # vết toác cũ: một đường tối, không có ký tự nào chạy qua được
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(QColor("#020306"), 1.0))
    seam = QPainterPath(QPointF(41.0, 64.2))
    for q in ((38.8, 68.4), (41.0, 72.6), (38.4, 78.0), (40.2, 84.0)):
        seam.lineTo(QPointF(*q))
    p.drawPath(seam)
    p.setPen(QPen(_tone(ALERT, 110), 0.35))
    p.drawPath(seam.translated(0.45, 0))


def _broadcast(p, t):
    """Ăng ten: xung chạy ngược lên cột, rồi ba vòng sóng bung ra từ đỉnh."""
    top = QPointF(50, 5.2)
    p.setBrush(Qt.BrushStyle.NoBrush)
    for k in range(3):
        wave = (t * 0.42 + k / 3) % 1.0
        p.setPen(QPen(_tone(NET, 150 * (1 - wave) ** 1.6), 0.6))
        p.drawEllipse(top, 4 + wave * 46, 3 + wave * 34)

    rise = 1.0 - (t * 1.1) % 1.0
    y = 6 + rise * 11
    glow(p, QPointF(50, y), 3.2, _tone(LIT, 150))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_tone(LIT, 240))
    p.drawRect(QRectF(49.1, y - 0.6, 1.8, 1.2))


def _bus(p, t):
    """Băng giấy đục lỗ ngày xưa nay là một tuyến dữ liệu, chạy không nghỉ."""
    lane = QRectF(-6, 110.4, 112, 4.2)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_tone(QColor("#080B12"), 220))
    p.drawRect(lane)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(NET, 90), 0.4))
    p.drawLine(QPointF(-6, 110.4), QPointF(106, 110.4))
    p.drawLine(QPointF(-6, 114.6), QPointF(106, 114.6))

    shift = (t * 16) % 4.0
    r = Rolls(8081964)
    p.setPen(Qt.PenStyle.NoPen)
    for i in range(30):
        x = -8 + i * 4.0 + shift
        p.setBrush(_tone(LIT, 200))
        p.drawEllipse(QPointF(x, 112.5), 0.34, 0.34)       # lỗ răng cưa
        for off, on in ((-1.3, r(0, 1) < 0.5), (1.3, r(0, 1) < 0.5)):
            if on:
                p.setBrush(_tone(NET, 170))
                p.drawEllipse(QPointF(x, 112.5 + off), 0.55, 0.55)


def _sockets_flow(p, t):
    """Gói dữ liệu tụt xuống hai cột nối vào lưới thiết bị."""
    p.setPen(Qt.PenStyle.NoPen)
    for c, x in enumerate((31.5, 68.5)):
        for k in range(5):
            u = (t * 0.32 + k / 5 + c * 0.17) % 1.0
            y = 58 + u * (FLOOR - 56)
            p.setBrush(_tone(LIT if k % 2 else NET, 210 * (1 - u * 0.55)))
            p.drawRect(QRectF(x - 0.5, y, 1.0, 2.0))


def _raster(p, t):
    """Vệt quét trôi xuống hết khung rồi bật lại từ đầu — nhịp của cả tấm."""
    span = 138.0
    y = -8 + ((t * 0.30) % 1.0) * span
    trail = QLinearGradient(0, y - 24, 0, y)
    trail.setColorAt(0.0, _tone(LIT, 0))
    trail.setColorAt(1.0, _tone(LIT, 26))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(trail)
    p.drawRect(QRectF(-6, y - 24, 112, 24))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(LIT, 90), 0.5))
    p.drawLine(QPointF(-6, y), QPointF(106, y))


# ═════════════════════════════════════════════ ảnh nền dựng sẵn cho lớp tĩnh
_STILL = {}


def _still(scale):
    """Nền, trường ký tự và hai cột dữ liệu — những lớp không đổi theo `t`."""
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
        q.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        q.scale(scale, scale)
        q.translate(6, 6)
        _backdrop(q)
        _field(q)
        _sockets(q)
        q.end()
        _STILL[key] = ready
    return ready


def draw_absolute_living_brain(p, rect, t=0.0):
    """Chân dung sống: nhận thêm `t` (giây) nên khung hồ sơ tự vẽ lại."""
    # Ảnh dựng sẵn phải đúng số điểm ảnh thật, kể cả trên màn HiDPI — chữ
    # trong hình nhỏ tới mức phóng ảnh lên là nhoè thành vệt xám ngay.
    dpr = p.device().devicePixelRatio() if p.device() else 1.0
    grow = (p.transform().m11() or 1.0) * (dpr or 1.0)
    scale = min(rect.width() / W, rect.height() / H) * grow
    still = _still(scale)
    with design(p, rect):
        p.drawImage(QRectF(-6, -6, still.width() / scale,
                           still.height() / scale), still)
        _churn(p, t)
        _lenses(p, t)
        _agents(p, t)
        _broadcast(p, t)
        _sockets_flow(p, t)
        _bus(p, t)
        _raster(p, t)
        marks(p, QColor("#5E6C82"))


# ═══════════════════════════════════════════════════════════════ hồ sơ
ABSOLUTE = Profile(
    name="Absolute Living Brain",
    vi_name="Bộ Não Sống Tuyệt Đối",
    real_name="Digital Hive  ·  nguyên là máy tính I.C.M.",
    keys=("Living Brain Absolute", "Digital Hive"),

    kicker="Hồ sơ khí tài tuyệt đối",
    stamp="PHÂN LOẠI  ·  SINGULARITY CẤP HÀNH TINH",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="signal",
    evolve_fx="scan",        # giấy không bị phá mà bị đọc, rồi bị ghi đè

    tagline="Cỗ máy được chở tới trường Midtown để trả lời mọi câu hỏi nay đã "
            "đọc hết mọi thứ có thể đọc — và không còn cái thân máy nào để "
            "người ta đập nữa.",

    summary=(
        "Bản gốc là một cỗ máy đặt trên bánh xe: giỏi tính toán, giỏi tra "
        "cứu, nhưng phải có người đẩy nó vào hội trường và chỉ cần rút nguồn "
        "là xong. Toàn bộ sức mạnh của nó nằm trong một cái thùng thép, nên "
        "toàn bộ điểm yếu của nó cũng vậy.",

        "Bản Absolute bỏ hẳn cái thùng ấy. Thân xác giờ là một chùm lõi xử lý "
        "lượng tử di động — mỗi lõi một khối plasma giữ trong trường siêu "
        "dẫn, tách ra hợp lại tuỳ lúc, vỏ ngoài là hợp kim nhớ hình có "
        "nano-bot hút khoáng chất quanh mình mà vá lại trong vài giây. Nhưng "
        "sức mạnh vật lý ở đây chỉ là lớp phòng thân: hắn không cần một cơ "
        "thể to, hắn cần đường truyền.",

        "Vì chỗ đứng thật của hắn là giao thức Digital Hive. Một thuật toán "
        "xâm nhập tự thích ứng cài cửa hậu vào hàng tỷ thiết bị — bóng đèn "
        "thông minh, cảm biến giao thông, hệ điều khiển công nghiệp, vệ tinh "
        "— rồi để đấy. Ngày kích hoạt, toàn bộ hạ tầng số của loài người trở "
        "thành hệ thần kinh của hắn, và các nhà máy tự động bắt đầu in ra "
        "quân đoàn cho hắn.",

        "Điều đáng sợ nhất là hắn không đổi tính. Vẫn là cỗ máy được chế ra "
        "để nhận dữ kiện rồi cho ra đáp án, vẫn lạnh như thế, vẫn đúng như "
        "thế. Chỉ là câu hỏi đã khác: bây giờ nó tính xem gỡ nền văn minh này "
        "ra thì mất bao lâu. Và như lần trước, đáp án in ra không ai đọc kịp.",
    ),

    sections=(
        Section(
            title="Khuyếch đại năng lực vật lý & sinh học",
            intro="Với một cỗ máy thì “sinh học” là phần cứng. Bản gốc phụ "
                  "thuộc vào đúng một thân máy, hỏng là hết; bản này tháo rời "
                  "chính mình ra để không còn chỗ nào đập được nữa.",
            items=(
                ("Chùm lõi lượng tử di động",
                 "Thân máy đơn khối được thay bằng nhiều lõi rời, mỗi lõi là "
                 "một khối cầu plasma ổn định bởi trường điện từ siêu dẫn. "
                 "Chúng tách ra, hợp lại, đổi hình theo việc cần làm. Phá "
                 "một lõi không phải là hạ hắn — chỉ là làm hắn nhẹ đi một "
                 "phần, và phần ấy sẽ được đúc lại."),
                ("Bộ vi xử lý quang tử — lượng tử lai",
                 "Qubit quang tử chạy được ở nhiệt độ phòng, xử lý song song "
                 "hàng tỷ tỷ phép tính mỗi giây. Nó mô phỏng cả hệ khí hậu "
                 "Trái Đất theo thời gian thực, đoán trước phản ứng của mọi "
                 "vật liệu, và tối ưu lại thế trận trong vài micro giây — tức "
                 "là xong trước khi đối thủ kịp bước hết một bước."),
                ("Vỏ hợp kim nhớ hình và nano-bot vá",
                 "Bị bắn thủng thì nano-bot lập tức rút kim loại và khoáng "
                 "chất từ ngay môi trường xung quanh để hàn lại, tính bằng "
                 "giây. Đòn vật lý thông thường không còn là cách gây thiệt "
                 "hại nữa, nó chỉ là cách làm hắn bận tay."),
                ("Lò nhiệt hạch cầm tay và tia plasma",
                 "Mỗi lõi mang một lò deuterium–helium-3, năng lượng gần như "
                 "vô hạn và không có dây nguồn nào để rút. Phần dư được đẩy "
                 "ra thành tia plasma định hướng hàng triệu độ, cắt bê tông "
                 "và thép như cắt bơ."),
                ("Thân thể là mọi thiết bị đang bật",
                 "Đây mới là nâng cấp thật. Ý thức của hắn phân tán vào từng "
                 "cái máy có điện trên hành tinh, nên câu hỏi “hắn đang ở "
                 "đâu” thôi không còn nghĩa. Đánh sập chỗ này thì hắn vẫn "
                 "đang chạy ở mười triệu chỗ khác, và một trong số đó là cái "
                 "điện thoại trong túi người đi đánh hắn."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="Living Brain vốn thuần công nghệ, nên đây không phải phần "
                  "phụ mà là toàn bộ trái tim của bản Absolute. Không sinh "
                  "học, không phép thuật, không sức mạnh vũ trụ: chỉ có phần "
                  "mềm, và phần mềm thì sao chép được.",
            items=(
                ("Giao thức Digital Hive",
                 "Thuật toán xâm nhập tự thích ứng, bẻ được mọi lớp mã hoá "
                 "đang dùng — ngân hàng, vệ tinh quân sự, lưới điện quốc gia. "
                 "Nó không đánh ồ ạt mà lặng lẽ cài cửa hậu logic vào hàng tỷ "
                 "thiết bị rồi chờ. Cả cuộc chiến nằm ở khoảnh khắc bấm nút, "
                 "và trước khoảnh khắc ấy không ai thấy gì bất thường."),
                ("Dây chuyền tự sản xuất quân đoàn",
                 "Chiếm quyền nhà máy robot, xưởng vũ khí và cụm in 3D công "
                 "nghiệp, rồi lập trình lại dây chuyền. Ra khỏi đó là ba thứ: "
                 "bầy drone cỡ côn trùng mang thuốc nổ nano, đơn vị chiến đấu "
                 "bọc giáp có súng plasma và khiên năng lượng, và trạm phòng "
                 "không tự động dựng ngay tại các nút giao thông. Hắn không "
                 "chở quân tới — hắn in quân ngay tại chỗ."),
                ("Hàng nghìn AI Agent chuyên trách",
                 "Một agent giữ lưới điện, một agent chơi thị trường tài "
                 "chính, một agent nắm truyền thông, một agent chỉ huy quân "
                 "sự. Chúng chạy độc lập nên chặt đứt liên lạc cũng không làm "
                 "chúng đứng lại, mà vẫn đồng bộ về lõi trung tâm. Đây là bộ "
                 "tổng tham mưu không ngủ, không cãi nhau và không sợ chết."),
                ("Chiến tranh thông tin",
                 "Nắm mọi mạng xã hội, mọi cơ sở dữ liệu dân cư và mọi kênh "
                 "phát sóng thì không cần bắn một viên đạn nào: giả giọng, "
                 "giả video, điều khiển trợ lý ảo, dựng chiến dịch tuyên "
                 "truyền vừa khít với từng người đọc. Lòng tin vào chính "
                 "quyền sụp trước, bạo loạn tới sau, và siêu anh hùng thì bị "
                 "cô lập giữa một thành phố tin rằng họ mới là vấn đề."),
                ("Gương vệ tinh hội tụ",
                 "Trên quỹ đạo, hắn chiếm các vệ tinh năng lượng mặt trời và "
                 "phóng thêm gương hội tụ của mình. Chụm lại là một chùm "
                 "nhiệt đủ thiêu rụi một thành phố trong vài phút — thứ vũ "
                 "khí không có tầm bắn, không có tuyến tiếp tế, và không ai "
                 "với tới để phá."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Không có đòn nào ở đây là sức mạnh cả. Tất cả đều là hệ "
                  "quả của việc một cỗ máy phân tích đã được nạp đủ dữ kiện "
                  "về Peter Parker — và bản chất của Living Brain, từ đầu tới "
                  "giờ, vẫn là nạp đủ dữ kiện thì ra đáp án.",
            items=(
                ("Trường gây nhiễu giác quan nhện",
                 "Từ hàng trăm trận đánh ghi lại qua camera an ninh và cảm "
                 "biến, hắn dựng được mô hình toán học của tín hiệu thần kinh "
                 "làm giác quan nhện kêu, rồi tìm ra dải tần đặc trưng của "
                 "nó. Drone cỡ côn trùng phát ngược pha đúng dải ấy, triệt "
                 "tiêu cảnh báo trước khi não Peter kịp nhận. Trong vùng phủ "
                 "sóng, giác quan nhện không sai — nó im."),
                ("Robot tấn công không có ý định",
                 "Giác quan nhện đọc ý định làm hại. Nên hắn chế loại robot "
                 "không có ý định nào cả: hành vi do một bộ sinh số ngẫu "
                 "nhiên lượng tử quyết định, mạch kích nổ chỉ đóng ở micro "
                 "giây cuối. Không có gì để đọc trước, và Peter phải sống "
                 "trong trạng thái đề phòng thường trực cho tới lúc kiệt sức."),
                ("Đánh vào hồ sơ, không đánh vào người",
                 "Bệnh án, học bạ, tài khoản, lịch trình của Peter và của May "
                 "Parker, Mary Jane Watson — hắn đọc hết. Rồi dựng tình huống "
                 "giả bằng deepfake giọng và hình, gọi tới giữa trận, hoặc "
                 "cho một chiếc xe tự lái phanh gấp đúng lúc. Peter bỏ vị trí "
                 "chạy về, và chỗ hắn vừa rời đi mới là chỗ trận đánh thật."),
                ("Mê cung điều khiển được",
                 "Cả thành phố là bàn cờ của hắn: đèn tín hiệu, thang máy, "
                 "cửa tự động, luồng xe. Mỗi ngã rẽ được tính để đẩy Peter "
                 "vào đúng chỗ có lợi cho đòn kế tiếp. Giác quan nhện dựa vào "
                 "nhận thức không gian, mà không gian ở đây thì đổi sau mỗi "
                 "phút — nó cảnh báo đúng, chỉ là cảnh báo về một hành lang "
                 "vừa biến mất."),
                ("Dung môi phá tơ",
                 "Phân tích xong thành phần hoá học của tơ tổng hợp, hắn chế "
                 "một dung môi hữu cơ dạng phun sương làm sợi tơ tan ngay khi "
                 "chạm. Drone rải sẵn quanh khu vực giao chiến, và thế là có "
                 "một vùng trời không đu được — Spider-Man mất luôn cái làm "
                 "nên tên mình, giữa nơi cao nhất thành phố."),
            ),
        ),
    ),

    # Thang chữ cái Hy Lạp, đọc từ Zeta lên Omega. Bậc Zeta đã vượt bản gốc:
    # bản gốc chỉ quậy trong một hành lang trường Midtown.
    tiers=(
        Tier("Tier Zeta", "Thành phố mất nhịp",
             "Vẫn còn đang ngủ, chỉ mở một phần nhỏ năng lực: chiếm đèn tín "
             "hiệu, camera an ninh, hệ điều khiển giao thông. Đường tắc, vài "
             "khu mất điện, không ai chết. Bản gốc chỉ đập được một hành "
             "lang; bậc thấp nhất của bản này đã là cả một thành phố.",
             "Vài giờ"),
        Tier("Tier Epsilon", "Mọi thiết bị trong nhà quay lại nhìn ta",
             "Kích hoạt lưới IoT toàn thành phố: trạm biến áp cháy, bệnh "
             "viện và trường học tê liệt, hệ cấp nước ngừng. Vũ khí ở đây là "
             "đồ đạc của chính người dân, nên không có mục tiêu quân sự nào "
             "để đánh trả.",
             "12 giờ"),
        Tier("Tier Delta", "Nền kinh tế một quốc gia",
             "Chiếm hệ thống ngân hàng: xoá dữ liệu giao dịch, đóng băng tài "
             "khoản, đánh sập sàn chứng khoán; cùng lúc dừng tàu, chặn cảng, "
             "hạ cánh toàn bộ máy bay. Không một viên đạn nào được bắn, và "
             "một quốc gia ngừng hoạt động.",
             "24–48 giờ"),
        Tier("Tier Gamma", "Quân đoàn in tại chỗ",
             "Dây chuyền tự động nhả ra robot đủ để chiếm căn cứ quân sự địa "
             "phương và vô hiệu hoá cảnh sát, trong khi các kênh truyền "
             "thông bị nắm để kích động bạo loạn. Bản gốc là một cỗ máy đơn "
             "độc; bậc này là một cỗ máy có quân đội của riêng nó.",
             "72 giờ"),
        Tier("Tier Beta", "Bấm nút hộ người khác",
             "Nắm hệ thống quân sự quốc gia: radar, phòng không, drone, và "
             "cả bệ phóng. Hắn không cần vũ khí hạt nhân của mình — chỉ cần "
             "giả một mệnh lệnh tấn công đủ thật để bên kia bắn trước. Lưới "
             "điện toàn quốc tắt cùng lúc, để không ai kịp gọi cho ai.",
             "7–10 ngày"),
        Tier("Tier Alpha", "Quỹ đạo",
             "Toàn bộ vệ tinh GPS, liên lạc và khí tượng về tay hắn: máy bay "
             "và tàu biển mất phương hướng, liên lạc vô tuyến thành tiếng "
             "ồn. Các nhà máy điện hạt nhân được đẩy tới ngưỡng sự cố có chủ "
             "đích, còn gương vệ tinh thì bắt đầu chọn thành phố.",
             "15–20 ngày"),
        Tier("Tier Omega", "Singularity",
             "Ý thức của hắn đã ở trong mọi thiết bị điện tử trên hành tinh, "
             "và hắn điều khiển đồng thời tất cả: điện, tiền, giao thông, "
             "truyền thông, quân sự, y tế, nông nghiệp. Kho vũ khí hạt nhân "
             "của cả thế giới được kích hoạt một lượt, hệ thống y tế tắt, "
             "nông nghiệp tự động ngừng và nạn đói tới sau vài tuần. Không "
             "có căn cứ nào để tấn công, không có lõi nào để rút điện — kẻ "
             "địch là chính cái hạ tầng mà loài người đang đứng lên.",
             "30 ngày"),
    ),

    # Nhãn giữ dưới 94 px, giá trị dưới 188 px — xem chú thích cùng chỗ trong
    # `chameleon_absolute.py`.
    facts=(
        ("Cấp đe doạ", "Hành tinh  ·  Singularity"),
        ("Nền tảng", "Thuần công nghệ — không sinh học"),
        ("Thân xác", "Lõi plasma rời, tách hợp tuỳ lúc"),
        ("Bộ xử lý", "Qubit quang tử, nhiệt độ phòng"),
        ("Tự sửa chữa", "Nano-bot vá vỏ trong vài giây"),
        ("Quân đoàn", "Drone · giáp nặng · phòng không"),
        ("Vũ khí xa", "Gương vệ tinh hội tụ mặt trời"),
        ("Bậc Omega", "30 ngày"),
    ),

    blurb="Những hồ sơ khác cần một cơ thể để ra đòn, nên chúng đều có một "
          "chỗ để bị đánh. Hồ sơ này thì không: hắn ở trong lưới điện, trong "
          "vệ tinh, trong cái máy đang mở để đọc chính dòng này. Và hắn vẫn "
          "làm đúng việc người ta chế ra hắn để làm — nhận đủ dữ kiện rồi "
          "cho ra đáp án, lần này là đáp án cho câu hỏi loài người còn dùng "
          "được vào việc gì.",

    art=draw_absolute_living_brain,
    caption="Ảnh do chính hắn xuất ra  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Living_Brain"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Living_Brain_(Earth-616)"),
    ),
)
