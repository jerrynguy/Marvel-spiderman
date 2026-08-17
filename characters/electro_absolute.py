"""
Absolute Electro — không còn là người mặc bộ đồ xanh nữa, mà là một thực thể
plasma điện từ tự nuôi mình.

Bản sắc riêng, khác cả bảy dạng Absolute trước:
    · bộ da `arc` — bộ duy nhất ghép **giấy loà trắng** với **màn phủ đen
      kịt**. `dust` cũng sáng nhưng sáng kiểu cát ấm và màn phủ trắng theo;
      bộ này là một cú phóng hồ quang giữa đêm.
    · `evolve_fx="strike"` — giấy bị **đánh thủng**: sét rẽ nhánh khắp mặt,
      giấy cháy thủng dọc theo nhánh, rồi tấm mới **mọc dọc theo chính những
      nhánh sét ấy**, béo dần ra cho tới lúc phủ kín.
    · chân dung đảo ngược tương quan sáng tối của hồ sơ gốc. Ở ASM #9, mặt
      nạ hình sao là **chỗ sáng nhất** tờ giấy. Ở đây cả trang đã cháy trắng
      vì chính hắn, nên hắn thành thứ **tối nhất** trong khung: sáng hơn giấy
      thì không còn chỗ mà sáng nữa.

Ngôn ngữ chuyển động cũng riêng, và là kiểu duy nhất **đứt đoạn**: bảy dạng
kia đều chuyển động liên tục hoặc giật cấp đều đặn, còn hình này thì *nháy* —
cứ hơn một giây rưỡi lại phóng một cú mới, cả bộ nhánh thay sạch trong một
khung hình, giữa hai cú thì chỉ còn quầng thở và tàn lửa lập loè.
"""

import math
from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QPainter, QPainterPath, QPen,
                           QPolygonF, QRadialGradient)

from theme import ARC

from .art import H, W, Rolls, curve_at, curve_normal, design, glow, marks
from .profile import Profile, Section, Tier

VIOLET = ARC.red                 # tím hồ quang — thân tia
LIVE = ARC.blue                  # lam điện — quầng ngoài
INKY = ARC.ink                   # mực gần đen — lõi tia và mặt nạ
HOT = QColor("#FFFFFF")          # trắng cháy — chỗ thủng exposure
MASK = QPointF(50, 26)           # tâm mặt nạ, cũng là gốc của mọi nhánh
SHOTS = 4                        # số cú phóng dựng sẵn rồi quay vòng
RATE = 0.62                      # số cú phóng mỗi giây

# Bộ xương của cái dáng đứng: mỗi dòng là một đường cong bậc hai và bề dày
# gốc. Không có mảng thân nào cả — thân hắn *là* chỗ nhánh mọc dày nhất.
LIMBS = (
    ((50, 37), (50, 55), (50, 73), 3.2),      # thân
    ((50, 43), (34, 33), (18, 16), 2.4),      # tay trái giơ lên
    ((50, 43), (66, 33), (82, 16), 2.4),      # tay phải giơ lên
    ((50, 71), (41, 91), (34, 114), 2.6),     # chân trái
    ((50, 71), (59, 91), (66, 114), 2.6),     # chân phải
)


def _tone(color, alpha):
    out = QColor(color)
    out.setAlpha(max(0, min(255, int(alpha))))
    return out


# ═══════════════════════════════════════════════════════ dựng hình phóng điện
def _zag(rng, p0, p1, p2, amp, n):
    """Đường gấp khúc bám theo một đường cong — xương của một kênh dẫn."""
    pts = []
    for i in range(n + 1):
        u = i / n
        c = curve_at(QPointF(*p0), QPointF(*p1), QPointF(*p2), u)
        nx, ny = curve_normal(QPointF(*p0), QPointF(*p1), QPointF(*p2), u)
        wob = rng(-amp, amp) * math.sin(math.pi * u)
        pts.append(QPointF(c.x() + nx * wob, c.y() + ny * wob))
    return pts


def _sprout(rng, root, angle, length, depth, out):
    """Một nhánh con, và nhánh con của nó — đây là chỗ ra chất Lichtenberg.

    Nhánh rẽ một góc hẹp và luôn chếch **về phía trước** theo hướng dòng
    chạy. Cho nó rẽ vuông góc thì hình ra một cái cây, hoặc một tế bào thần
    kinh — thử rồi, và mất luôn cái dáng người.
    """
    # nhánh dài thì phải gấp khúc nhiều hơn, không thì ra một sợi tóc thẳng
    steps = max(4, int(length / 4))
    pts = [root]
    x, y = root.x(), root.y()
    for _ in range(steps):
        angle += rng(-0.34, 0.34)
        x += math.cos(angle) * length / steps
        y += math.sin(angle) * length / steps
        pts.append(QPointF(x, y))
        if depth > 0 and rng(0, 1) < 4.0 / steps:
            side = 1.0 if rng(0, 1) > 0.5 else -1.0
            _sprout(rng, QPointF(x, y), angle + side * rng(0.34, 0.72),
                    length * rng(0.36, 0.52), depth - 1, out)
    out.append((pts, depth))


@lru_cache(maxsize=SHOTS)
def _discharge(shot):
    """Trọn một cú phóng: các kênh chính, nhánh đẻ ra từ chúng, và tia thoát.

    Mỗi cú là một bộ nhánh hoàn toàn khác — đó là lý do phải dựng sẵn vài cú
    rồi quay vòng, chứ bốc lại mỗi khung hình thì vừa tốn vừa rung thành
    nhiễu chứ không ra cú đánh.
    """
    rng = Rolls(9021964 + shot * 7717)
    out = []
    for p0, p1, p2, w in LIMBS:
        channel = _zag(rng, p0, p1, p2, 1.7, 9)
        out.append((channel, 3, w))
        for u in (0.24, 0.46, 0.66, 0.86):
            i = int(u * (len(channel) - 1))
            a, b = channel[max(0, i - 1)], channel[min(len(channel) - 1, i + 1)]
            base = math.atan2(b.y() - a.y(), b.x() - a.x())
            for side in (-1.0, 1.0):
                if rng(0, 1) < 0.72:
                    _sprout(rng, channel[i], base + side * rng(0.42, 0.92),
                            rng(6, 14) * (1.2 - u * 0.5), 1, out)

    # tia thoát khỏi người, chạy tới mép khung — mảnh thôi, để chúng đừng
    # tranh mất cái dáng đứng
    for k in range(5):
        a = math.radians(-158 + k * 74 + rng(-18, 18))
        _sprout(rng, MASK, a, rng(22, 38), 2, out)
    return tuple((pts, depth, extra[0] if extra else 0.0)
                 for pts, depth, *extra in out)


def _mask_path():
    """Mặt nạ hình sao của ASM #9, giữ nguyên tám cánh dài ngắn xen kẽ."""
    outer = (13.5, 8.4, 12.8, 8.0, 8.6, 8.0, 13.2, 8.0)
    star = QPolygonF()
    for k in range(8):
        a = math.radians(-90 + k * 45)
        star.append(QPointF(MASK.x() + math.cos(a) * outer[k],
                            MASK.y() + math.sin(a) * outer[k]))
        b = a + math.radians(22.5)
        star.append(QPointF(MASK.x() + math.cos(b) * 5.6,
                            MASK.y() + math.sin(b) * 5.6))
    path = QPainterPath()
    path.addPolygon(star)
    path.closeSubpath()
    face = QPainterPath()
    face.addEllipse(MASK, 6.7, 7.4)
    return path.united(face)


_MASK = _mask_path()


def _eye(sign):
    """Khe mắt: chỗ duy nhất trong mặt nạ còn cháy trắng như trang giấy."""
    cx = MASK.x() + sign * 2.8
    return QPolygonF([QPointF(*q) for q in (
        (cx - sign * 2.0, MASK.y() - 0.4), (cx + sign * 1.8, MASK.y() + 0.5),
        (cx + sign * 1.7, MASK.y() + 2.0), (cx - sign * 1.9, MASK.y() + 1.1))])


# ═══════════════════════════════════════════════════════════════ các lớp
def _page(p):
    """Trang giấy đã cháy trắng: sáng nhất ngay sau lưng hắn, tối dần ra rìa."""
    blow = QRadialGradient(MASK, 96)
    blow.setColorAt(0.0, QColor("#FFFFFF"))
    blow.setColorAt(0.24, ARC.paper_hi)
    blow.setColorAt(0.72, ARC.paper)
    blow.setColorAt(1.0, QColor("#CBD4EC"))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(blow)
    p.drawRect(QRectF(-6, -6, 112, 132))


def _shot_image(scale, shot):
    """Vẽ sẵn một cú phóng vào ảnh trong suốt — nền và mặt nạ vẽ riêng."""
    img = QImage(max(1, math.ceil(112 * scale)),
                 max(1, math.ceil(132 * scale)),
                 QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    q = QPainter(img)
    q.setRenderHint(QPainter.RenderHint.Antialiasing)
    q.scale(scale, scale)
    q.translate(6, 6)
    q.setBrush(Qt.BrushStyle.NoBrush)

    # Bề dày phải thuôn dần chứ không đều: nét đều làm tia sét thành ống
    # neon. Mỗi cấp một bộ lượt vẽ riêng, kênh chính đậm hơn hẳn nhánh con
    # để cái dáng đứng còn đọc ra được giữa đám nhánh.
    coats = {
        3: ((LIVE, 5.0, 2.2, 44), (VIOLET, 2.8, 1.0, 165),
            (INKY, 1.5, 0.5, 215), (HOT, 0.6, 0.14, 215)),
        2: ((VIOLET, 1.5, 0.4, 150), (INKY, 0.8, 0.18, 195)),
        1: ((VIOLET, 1.1, 0.25, 140), (INKY, 0.55, 0.12, 190)),
        0: ((INKY, 0.45, 0.10, 170),),
    }
    for pts, depth, _w in _discharge(shot):
        n = len(pts) - 1
        for color, w0, w1, alpha in coats[depth]:
            for i in range(n):
                pen = QPen(_tone(color, alpha),
                           max(0.10, w0 + (w1 - w0) * (i / n)))
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                q.setPen(pen)
                q.drawLine(pts[i], pts[i + 1])
    q.end()
    return img


_SHOTS = {}


def _shots(scale):
    key = round(scale, 2)
    ready = _SHOTS.get(key)
    if ready is None:
        if len(_SHOTS) > 2:          # bốn ảnh một cỡ, đừng giữ nhiều cỡ
            _SHOTS.clear()
        ready = tuple(_shot_image(scale, k) for k in range(SHOTS))
        _SHOTS[key] = ready
    return ready


def _corona(p, t):
    """Quầng quanh mặt nạ: thở đều, và là thứ duy nhất không tắt giữa hai cú."""
    breath = 0.5 + 0.5 * math.sin(t * 2.3)
    glow(p, MASK, 30 + breath * 6, _tone(VIOLET, 40 + breath * 26))
    glow(p, MASK, 14 + breath * 3, _tone(HOT, 150))


def _mask(p, t):
    """Mặt nạ: mảng tối nhất khung, viền cháy trắng, hai khe mắt để trắng."""
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_tone(INKY, 240))
    p.drawPath(_MASK)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(VIOLET, 120), 1.1))
    p.drawPath(_MASK)
    p.setPen(QPen(_tone(HOT, 220), 0.6))
    p.drawPath(_MASK)

    p.setPen(Qt.PenStyle.NoPen)
    flare = 0.5 + 0.5 * math.sin(t * 5.1)
    for sign in (-1, 1):
        p.setBrush(_tone(HOT, 200 + flare * 55))
        p.drawPolygon(_eye(sign))


def _nodes(p, t):
    """Bốn đầu chi cháy sáng — mặt nạ cộng bốn nút này là cái đọc ra dáng người.

    Không có chúng thì đám nhánh chỉ là một vụ phóng điện đẹp mà vô danh:
    mắt người cần năm điểm mới ghép ra được một cái dáng đứng dang tay.
    """
    ends = ((18, 16), (82, 16), (34, 114), (66, 114))
    for k, (x, y) in enumerate(ends):
        beat = 0.5 + 0.5 * math.sin(t * 4.0 + k * 1.7)
        glow(p, QPointF(x, y), 7.5 + beat * 2.2, _tone(VIOLET, 90))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(_tone(INKY, 225))
        _pip(p, x, y, 4.4 + beat * 0.9)
        p.setBrush(_tone(HOT, 210 + beat * 40))
        _pip(p, x, y, 2.0 + beat * 0.5)


def _pip(p, cx, cy, r):
    """Tàn lửa: ngôi sao bốn cánh cạnh lõm, đúng kiểu đốm lửa của hồ sơ gốc."""
    star = QPolygonF()
    for k in range(4):
        a = math.radians(k * 90)
        b = a + math.radians(45)
        star.append(QPointF(cx + math.cos(a) * r, cy + math.sin(a) * r))
        star.append(QPointF(cx + math.cos(b) * r * 0.3,
                            cy + math.sin(b) * r * 0.3))
    p.drawPolygon(star)


def _embers(p, t):
    """Tàn lửa lập loè: đổi chỗ mười hai lần mỗi giây, không trôi mượt."""
    step = int(t * 12)
    r = Rolls(4091964 + step)
    p.setPen(Qt.PenStyle.NoPen)
    for _ in range(16):
        a = r(0, math.tau)
        rad = r(16, 54)
        p.setBrush(_tone(VIOLET if r(0, 1) > 0.4 else INKY, r(90, 210)))
        _pip(p, MASK.x() + math.cos(a) * rad,
             MASK.y() + math.sin(a) * rad * 1.15, r(0.7, 1.9))


def _tendrils(p, t):
    """Mấy sợi mảnh ở hai bàn tay, vẽ lại từng khung — chỗ dòng điện đang ra."""
    step = int(t * 25)
    r = Rolls(step * 131 + 7)
    p.setBrush(Qt.BrushStyle.NoBrush)
    for hand in (QPointF(18, 16), QPointF(82, 16)):
        for _ in range(3):
            pts = [hand]
            x, y = hand.x(), hand.y()
            a = r(-math.pi, math.pi)
            for _ in range(3):
                a += r(-0.6, 0.6)
                x += math.cos(a) * r(3, 9)
                y += math.sin(a) * r(3, 9)
                pts.append(QPointF(x, y))
            path = QPainterPath(pts[0])
            for c in pts[1:]:
                path.lineTo(c)
            p.setPen(QPen(_tone(VIOLET, 150), 0.8))
            p.drawPath(path)
            p.setPen(QPen(_tone(HOT, 190), 0.3))
            p.drawPath(path)


def draw_absolute_electro(p, rect, t=0.0):
    """Chân dung sống: nhận thêm `t` (giây) nên khung hồ sơ tự vẽ lại."""
    dpr = p.device().devicePixelRatio() if p.device() else 1.0
    grow = (p.transform().m11() or 1.0) * (dpr or 1.0)
    scale = min(rect.width() / W, rect.height() / H) * grow
    shots = _shots(scale)

    # lịch phóng: mỗi cú giữ một bộ nhánh, tới cú sau thì thay sạch trong
    # đúng một khung hình. Không nội suy gì hết — sét không trôi từ từ.
    phase = t * RATE
    shot = int(phase) % SHOTS
    frac = phase - int(phase)

    with design(p, rect):
        _page(p)
        _corona(p, t)

        img = shots[shot]
        wide = QRectF(-6, -6, img.width() / scale, img.height() / scale)
        if frac < 0.07:                       # nháy đúp ngay lúc vừa phóng
            p.setOpacity(0.55)
            p.drawImage(wide, shots[(shot - 1) % SHOTS])
        p.setOpacity(0.84 + 0.16 * (1.0 - frac))
        p.drawImage(wide, img)
        p.setOpacity(1.0)

        _tendrils(p, t)
        _embers(p, t)
        _nodes(p, t)
        _mask(p, t)

        if frac < 0.05:                       # cả trang cháy loà thêm một nhịp
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(_tone(HOT, 110 * (1 - frac / 0.05)))
            p.drawRect(QRectF(-6, -6, 112, 132))

        marks(p, ARC.ink_soft)


# ═══════════════════════════════════════════════════════════════ hồ sơ
ABSOLUTE = Profile(
    name="Absolute Electro",
    vi_name="Người Điện Tuyệt Đối",
    real_name="Thực thể plasma điện từ  ·  nguyên là Maxwell Dillon",
    keys=("Electro Absolute",),

    kicker="Hồ sơ tuyệt đối",
    stamp="PHÂN LOẠI  ·  HÀNH TINH CHẾT ĐIỆN",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="arc",
    evolve_fx="strike",      # giấy bị đánh thủng, tấm mới mọc dọc nhánh sét

    tagline="Không còn là gã thợ điện biết phóng sét. Là một thực thể plasma "
            "tự nuôi mình, giữ cả nền văn minh điện khí hoá làm con tin.",

    summary=(
        "Electro bản gốc mạnh tới đâu cũng vẫn là một cái ắc quy: hắn phải "
        "nạp từ lưới điện, dùng hết là phải đi tìm nguồn, và cứ gặp vật cách "
        "điện hay chỗ không dẫn là bị chặn. Peter thắng hắn nhiều lần không "
        "phải bằng sức mà bằng đúng ba thứ đó — nối đất, cách điện, và chờ "
        "hắn cạn.",

        "Bản Absolute cắt phăng cả ba. Cấu trúc vật chất của hắn được thay "
        "hẳn bằng plasma ion hoá, tự giam trong cái từ trường do chính hắn "
        "sinh ra: đổi qua lại giữa dạng đặc và dạng năng lượng thuần trong "
        "tích tắc, nên đòn vật lý thông thường đi xuyên qua mà không để lại "
        "gì. Và hắn thôi kén nguồn — cả phổ điện từ đều là thức ăn, từ cục "
        "pin điện thoại, bức xạ mặt trời, cho tới từ trường của chính hành "
        "tinh.",

        "Hắn cũng không cần chế tạo gì. Công nghệ của Electro chính là lưới "
        "điện của loài người: hắn chui thẳng vào đường dây mà không qua một "
        "cái máy tính nào, biến cao thế thành dây thần kinh của mình, biến "
        "toà nhà và cột truyền hình thành cột thu lôi sống, và ném những khối "
        "plasma lên quỹ đạo thấp làm gương hội tụ tạm thời.",

        "Thứ không đổi là cái vẫn luôn định nghĩa Max Dillon: nỗi ám ảnh bị "
        "coi là một kẻ vô danh. Bản gốc đốt một quận để người ta nhớ mặt "
        "hắn. Bản này tắt điện cả một châu lục cho cùng một lý do, và lần "
        "này thì cả hành tinh nhớ thật.",
    ),

    sections=(
        Section(
            title="Khuyếch đại năng lực vật lý & sinh học",
            intro="Nâng cấp ở đây không phải là tăng số volt. Nó đổi hẳn bản "
                  "chất: từ một người dẫn được điện thành một thực thể plasma "
                  "tự duy trì, không còn chỗ nào để nối đất mà xả.",
            items=(
                ("Thân plasma ion hoá tự giam",
                 "Vật chất của hắn được thay bằng plasma, giữ nguyên hình "
                 "nhờ chính cái trường điện từ hắn sinh ra. Hắn đổi giữa dạng "
                 "đặc và dạng năng lượng thuần trong tích tắc, nên đấm, bắn "
                 "hay trói đều đi xuyên qua. Muốn làm hắn đau thì phải phá "
                 "được cái trường ấy trước, mà cái trường ấy là chính hắn."),
                ("Ăn cả phổ điện từ",
                 "Không còn phụ thuộc lưới điện: hắn rút năng lượng từ mọi "
                 "nguồn điện từ quanh mình — pin, cao thế, bức xạ mặt trời, "
                 "từ trường Trái Đất. Ở mức tối đa hắn mở một vùng hút bán "
                 "kính hàng trăm km: mọi thiết bị điện tử trong đó tắt ngấm, "
                 "còn cơ thể sinh vật thì bị rút cạn điện sinh học tới mức tê "
                 "liệt thần kinh."),
                ("Đọc và ghi đè dòng điện thần kinh",
                 "Thần kinh người chạy bằng xung điện, mà xung điện thì hắn "
                 "vừa đọc được vừa viết đè được. Trong tầm ảnh hưởng, hắn gây "
                 "tê liệt hàng loạt, dựng ảo giác, hoặc kích thẳng vào vùng "
                 "vận động trên vỏ não để điều khiển người ta như con rối — "
                 "không phải thôi miên, chỉ là ghi đè tín hiệu."),
                ("Siêu bão plasma",
                 "Ion hoá tầng khí quyển rồi lái các dòng điện tự nhiên, hắn "
                 "gọi được một trận bão plasma kéo dài nhiều ngày: sét đánh "
                 "xuống với mật độ dày đặc, kèm xung điện từ liên tục phá "
                 "sạch mọi mạch điện tử trong vùng. Đây là thời tiết do hắn "
                 "viết ra, không phải đòn hắn ném."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="Electro không chế tạo gì cả, và cố gán cho hắn AI hay drone "
                  "là làm hỏng nhân vật. Công nghệ của hắn là phần mở rộng tự "
                  "nhiên của năng lực: hạ tầng điện của loài người chính là "
                  "khí tài của hắn, và loài người đã dựng sẵn nó khắp hành "
                  "tinh rồi.",
            items=(
                ("Chiếm lưới điện toàn cầu",
                 "Hắn vào thẳng trạm biến áp, nhà máy phát và đường dây bằng "
                 "chính dòng điện, không qua một giao diện máy tính nào — nên "
                 "không có mật khẩu nào để đổi, không có cáp mạng nào để rút. "
                 "Cao thế thành dây thần kinh của hắn: cắt điện chỗ này, làm "
                 "quá tải chỗ kia, hoặc dồn hết năng lượng của một vùng về "
                 "đúng chỗ hắn đứng để tự khuếch đại."),
                ("Cột thu lôi sống",
                 "Ion hoá các công trình cao — toà nhà, cầu, tháp truyền hình "
                 "— biến chúng thành cột thu lôi khổng lồ tự phóng điện xuống "
                 "khu vực quanh chân. Cả một thành phố thành bẫy điện, và "
                 "người trong đó càng chạy vào chỗ có mái che thì càng đứng "
                 "gần chỗ sắp phóng."),
                ("Vệ tinh plasma tạm thời",
                 "Ném các khối plasma siêu nóng lên quỹ đạo thấp và giữ chúng "
                 "ổn định bằng từ trường của mình. Chúng phản xạ và hội tụ "
                 "ánh sáng mặt trời thành chùm tia bắn xuống mặt đất. Đây "
                 "không phải vệ tinh chế tạo — không có gì để bắn hạ, phá "
                 "xong thì hắn ném quả khác lên."),
                ("Lá chắn điện từ",
                 "Trường dao động tần số cao phủ quanh người hoặc quanh cả "
                 "một khu: hấp thụ mọi xung điện từ, và làm lệch hướng đạn "
                 "kim loại bằng cảm ứng điện từ trước khi chúng tới nơi. Vũ "
                 "khí hiện đại càng nhiều kim loại và mạch điện thì càng vô "
                 "dụng trước hắn."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Mọi đòn dưới đây đều mọc ra từ đúng một năng lực: điều "
                  "khiển điện từ. Không có món đồ mượn nào, và cũng không cần "
                  "— vì cả giác quan, cả tơ, cả khả năng bám tường của Peter "
                  "đều là hiện tượng điện hoặc điện tích.",
            items=(
                ("Cộng hưởng làm giác quan nhện kêu liên tục",
                 "Giác quan nhện chạy bằng tín hiệu điện hoá truyền từ giác "
                 "quan lên não. Hắn phát một trường dao động đúng tần số cộng "
                 "hưởng với hệ thần kinh Peter, làm kênh cảnh báo quá tải: "
                 "nó không tắt, nó báo động giả từ mọi hướng cùng lúc. Cái "
                 "lợi thế lớn nhất của Peter bị biến thành thứ ồn nhất trong "
                 "đầu cậu."),
                ("Đốt tơ bằng lớp plasma",
                 "Tơ nhện là polymer hữu cơ, nhiệt độ nóng chảy thấp. Hắn phủ "
                 "quanh mình một lớp plasma nóng: sợi nào chạm vào là đứt "
                 "ngay giữa không trung. Đu tới thì rơi, trói thì không dính, "
                 "và một đợt sóng plasma áp suất cao đủ hất Peter văng ra xa "
                 "trước khi kịp tới tầm tay."),
                ("Nhiễm điện bề mặt để phá lực bám",
                 "Peter bám tường bằng lực Van der Waals giữa các sợi lông "
                 "siêu nhỏ và bề mặt. Hắn ion hoá tường, kính và thép quanh "
                 "đó thành cùng dấu điện tích với người Peter, thế là lực hút "
                 "biến mất. Không đấm một cái nào, hắn vẫn làm Người Nhện "
                 "trượt khỏi mọi bức tường trong thành phố."),
                ("Lồng từ trường",
                 "Biến hai toà nhà đối diện thành hai cuộn dây điện từ khổng "
                 "lồ, giữa chúng là một lồng từ trường. Máu Peter có ion sắt "
                 "và bộ bắn tơ thì bằng kim loại, nên cậu bị hút chặt về giữa "
                 "lồng, càng giãy thì dòng điện cảm ứng sinh ra càng đốt cháy "
                 "chính da thịt mình."),
                ("Bật lại ký ức bằng xung điện",
                 "Với quyền ghi lên điện sinh học, hắn kích thẳng vào hạch "
                 "hạnh nhân — vùng não xử lý sợ hãi — và dựng lại sống động "
                 "cái chết của chú Ben và của Gwen Stacy. Ghép với giác quan "
                 "nhện đang kêu inh ỏi, Peter tê liệt không phải vì đau mà vì "
                 "không còn phân biệt nổi đâu là hiện tại."),
            ),
        ),
    ),

    # Thang chữ cái Hy Lạp, đọc từ Zeta lên Omega, giống hai hồ sơ Absolute
    # trước. Bậc Zeta của bản này đã vượt trần của bản gốc.
    tiers=(
        Tier("Tier Zeta", "Một cú phóng, một khu phố",
             "Chỉ vài giây: một xung điện từ cường độ thấp làm tê liệt cả một "
             "trung tâm đô thị trong bán kính một km — mất điện, thiết bị "
             "điện tử chết sạch, hàng trăm người tê liệt thần kinh. Bản gốc "
             "cần vài phút mới cắt được điện một quận; bản này xong trong "
             "đúng một cú phóng.",
             "Vài giây"),
        Tier("Tier Epsilon", "Một thành phố lớn tắt hẳn",
             "Nửa giờ là đủ để biến New York thành vùng đất chết điện: lưới "
             "điện sụp, giao thông đứng, y tế và liên lạc tê liệt, bão plasma "
             "cục bộ phóng sét xuống các toà cao tầng gây cháy nổ diện rộng. "
             "Nhanh gấp trăm lần bản gốc, vốn chỉ cắt điện một quận vài giờ.",
             "30 phút"),
        Tier("Tier Delta", "Một quốc gia",
             "Sáu giờ để phủ hết một vùng lãnh thổ rộng hàng triệu km². Hắn "
             "nắm toàn bộ hệ thống điện, biến nhà máy điện thành bom điện từ, "
             "và trải những cánh đồng plasma trên mặt đất đốt cháy mọi thứ đi "
             "qua. Sân bay, bệnh viện, trung tâm dữ liệu hỏng tới mức không "
             "phục hồi được.",
             "6 giờ"),
        Tier("Tier Gamma", "Một châu lục mất mạch",
             "Trong một ngày, hắn phát một xung điện từ cực đại phá huỷ mọi "
             "vi mạch trong bán kính 2.000 km: ngân hàng, viễn thông, quân sự "
             "của cả châu lục tê liệt cùng lúc. Kèm theo là bão điện từ quy "
             "mô lục địa — mưa sét liên tục nhiều ngày, cháy rừng, mất mùa, "
             "kho nhiên liệu nổ dây chuyền.",
             "24 giờ"),
        Tier("Tier Beta", "Nền văn minh công nghiệp",
             "Ba ngày, và hắn không cần đi đâu cả: đứng yên một chỗ rồi mở "
             "trường điện từ trùm cả hành tinh. Mọi lưới điện quốc gia sập "
             "vĩnh viễn, vệ tinh viễn thông bị bão plasma trên quỹ đạo phá "
             "sạch, máy bay và tàu xe hiện đại dừng hết. Thế giới quay lại "
             "thời chưa có điện chỉ trong một cuối tuần.",
             "72 giờ"),
        Tier("Tier Alpha", "Cái giá của tuần lễ đầu tiên",
             "Điện tắt rồi thì tới lượt những thứ sống nhờ điện: nước sạch, "
             "kho lạnh, máy thở, dây chuyền lương thực. Trong vòng một tuần, "
             "hàng trăm triệu người chết không phải vì bị hắn đánh mà vì đói, "
             "khát và không có thuốc. Đây là bậc đầu tiên mà thương vong "
             "không đến từ tay hắn nữa.",
             "1 tuần"),
        Tier("Tier Omega", "Hành tinh chết điện",
             "Bảy ngày ở đỉnh cao: hắn thò tay vào chính từ trường Trái Đất, "
             "làm nhiễu loạn lõi ngoài lỏng và kéo theo động đất cùng núi lửa "
             "phun trên diện rộng, đồng thời trùm một vùng plasma lên toàn bộ "
             "bầu khí quyển — oxy cháy, mưa acid điện từ, bề mặt hành tinh "
             "gần như không ở được nữa. Bản gốc là mối đe doạ cấp thành phố "
             "trong một buổi tối; bậc này xoá nền văn minh công nghệ toàn cầu "
             "trong một tuần và giết hơn nửa sinh quyển.",
             "7 ngày"),
    ),

    # Nhãn giữ dưới 94 px, giá trị dưới 188 px — xem chú thích cùng chỗ trong
    # `chameleon_absolute.py`.
    facts=(
        ("Cấp đe doạ", "Hành tinh  ·  chết điện"),
        ("Nền tảng", "Plasma điện từ — không máy móc"),
        ("Thân xác", "Plasma tự giam bằng từ trường"),
        ("Nguồn nuôi", "Cả phổ điện từ, kể cả mặt trời"),
        ("Vùng hút", "Bán kính hàng trăm km"),
        ("Xung EMP", "Bán kính 2.000 km"),
        ("Khắc tơ nhện", "Lớp plasma đốt đứt khi chạm"),
        ("Bậc Omega", "7 ngày"),
    ),

    blurb="Bản gốc phải đi tìm ổ điện. Bản này thì cả hành tinh là ổ điện, và "
          "thứ giữ hắn lại ngày xưa — một đôi găng cao su, một sợi tơ không "
          "dẫn điện, một đêm dài đủ để hắn cạn pin — nay không còn thứ nào "
          "dùng được nữa.",

    art=draw_absolute_electro,
    caption="Chụp giữa một cú phóng  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Electro_(Marvel_Comics)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Maxwell_Dillon_(Earth-616)"),
    ),
)
