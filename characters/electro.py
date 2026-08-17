"""
Electro — Maxwell Dillon.

Bảy chân dung trước đều là một bóng đen đứng yên trên nền giấy. Cái này thì
ngược lại: nhân vật chỉ chiếm phần giữa, còn cả khung là một vụ phóng điện —
tia nắng đen toả ra từ sau đầu, tia sét vót nhọn bắn ra tận mép giấy.

Bố cục đặt trên một đường chéo chứ không đối xứng: tay phải hất lên góc trên,
tay trái buông xuống góc dưới, dòng điện chạy suốt theo trục đó. Thứ sáng nhất
trong khung là chiếc mặt nạ hình sao — dấu hiệu nhận ra Electro từ 1964.
"""

import math
from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QPainter, QPainterPath, QPen,
                           QPolygonF)

from theme import BLUE, INK, RED

from .art import curve_at, curve_normal, design, fan, marks, ribbon
from .electro_absolute import ABSOLUTE
from .profile import Profile

SPARK = QColor("#F7F1E2")     # lõi tia sét, mặt nạ, găng — chỗ sáng nhất
SUIT = QColor("#BFAF8A")      # bộ đồ: tông giữa, tối hơn giấy nhưng chưa là mực
BURST = QPointF(48, 36)       # tâm vụ phóng điện, ngay sau đầu

HAND_R = QPointF(80, 28)      # bàn tay phải hất lên
HAND_L = QPointF(15, 95)      # bàn tay trái buông xuống

# Năm ngón xoè của mỗi găng: (góc, dài, nửa bề ngang)
GLOVE_R = ((-98, 6.5, 1.3), (-72, 7.2, 1.4), (-46, 6.8, 1.3), (-20, 5.8, 1.2))
GLOVE_L = ((56, 6.0, 1.2), (82, 6.8, 1.3), (108, 6.4, 1.2), (134, 5.6, 1.1))


# ═══════════════════════════════════════════════════ chân dung vẽ bằng code
def _bolt(pts, w0, w1=0.0):
    """Tia sét gấp khúc: gốc bè `w0`, ngọn thu về `w1` (0 là vót nhọn)."""
    n = len(pts) - 1
    left, right = [], []
    for i, q in enumerate(pts):
        prev, nxt = pts[max(0, i - 1)], pts[min(n, i + 1)]
        dx, dy = nxt.x() - prev.x(), nxt.y() - prev.y()
        span = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / span, dx / span
        w = w0 + (w1 - w0) * (i / n)
        left.append(QPointF(q.x() + nx * w, q.y() + ny * w))
        right.append(QPointF(q.x() - nx * w, q.y() - ny * w))

    path = QPainterPath()
    path.moveTo(left[0])
    for q in left[1:]:
        path.lineTo(q)
    for q in reversed(right):
        path.lineTo(q)
    path.closeSubpath()
    return path


# Hợp path (`united`) là phép đắt, mà mấy mảng dưới đây không đổi theo khung
# hình nào cả — dựng một lần rồi nhớ luôn, khỏi tính lại mỗi lần vẽ lại khung.
@lru_cache(maxsize=None)
def _bolts():
    """Mọi tia sét trong khung, kèm bề ngang ở gốc."""
    runs = (
        # ba tia bật ra từ bàn tay phải
        (((78, 25), (87, 16), (82, 10), (95, -3)), 2.7),
        (((82, 30), (93, 25), (88, 19), (102, 13)), 2.4),
        (((81, 34), (91, 39), (85, 45), (100, 49)), 2.2),
        # hai tia rò ra từ chính cái đầu
        (((38, 29), (26, 22), (31, 14), (16, 3)), 2.2),
        (((37, 45), (24, 48), (29, 55), (11, 57)), 2.0),
        # hai tia đổ xuống từ bàn tay trái
        (((13, 94), (3, 99), (8, 105), (-5, 112)), 2.5),
        (((19, 100), (23, 109), (16, 113), (25, 124)), 2.2),
    )
    out = QPainterPath()
    for pts, w in runs:
        out = out.united(_bolt([QPointF(*q) for q in pts], w))
    return out


def _zag(p0, p1, p2, amp, n):
    """Dãy điểm gấp khúc bám theo một đường cong, lệch qua lại quanh trục."""
    out = []
    for i in range(n):
        t = i / (n - 1)
        c = curve_at(p0, p1, p2, t)
        nx, ny = curve_normal(p0, p1, p2, t)
        side = amp if i % 2 else -amp
        out.append(QPointF(c.x() + nx * side, c.y() + ny * side))
    return out


@lru_cache(maxsize=None)
def _trim():
    """Viền sét chạy dọc hai sườn áo và hai ống tay.

    Vẽ hơi rộng tay cũng không sao: lúc tô sẽ cắt gọn theo đúng bóng người.
    """
    runs = (
        # sườn áo, bám đúng độ cong của thân
        ((QPointF(31, 66), QPointF(36, 92), QPointF(32, 124)), 2.0, 11),
        ((QPointF(65, 66), QPointF(60, 92), QPointF(64, 124)), 2.0, 11),
        # ống tay, bám đúng trục cánh tay
        ((QPointF(63, 62), QPointF(74, 48), HAND_R), 1.7, 9),
        ((QPointF(33, 63), QPointF(21, 78), HAND_L), 1.7, 9),
    )
    out = QPainterPath()
    for pts, amp, n in runs:
        out = out.united(_bolt(_zag(*pts, amp, n), 1.1, 1.1))
    return out


@lru_cache(maxsize=None)
def _gloves():
    """Đôi găng hình tia sét — cùng sắc sáng với mặt nạ, hai đầu ra của dòng điện."""
    out = QPainterPath()
    for hand, specs in ((HAND_R, GLOVE_R), (HAND_L, GLOVE_L)):
        cuff = QPainterPath()
        cuff.addEllipse(hand, 4.6, 4.6)
        out = out.united(fan(hand, specs)).united(cuff)
    return out


def _belt():
    """Thắt lưng, cắt ngang chỗ eo cho thân trên khỏi trôi thành một mảng phẳng."""
    band = QPainterPath()
    band.addRect(22, 92, 56, 7.5)
    return band


def _shade():
    """Mảng tối bám sườn trái: nguồn sáng là chính bàn tay phải đang giơ lên."""
    s = QPainterPath()
    s.moveTo(18, 55)
    s.lineTo(44, 58)
    s.lineTo(39, 124)
    s.lineTo(12, 124)
    s.closeSubpath()
    return s


@lru_cache(maxsize=None)
def _star():
    """Mặt nạ kín đầu: mảng mặt hình trứng, tám cánh sao dài ngắn xen kẽ."""
    outer = (19.5, 12.0, 18.5, 11.5, 12.0, 12.0, 19.0, 11.5)
    star = QPolygonF()
    for k in range(8):
        a = math.radians(-90 + k * 45)
        star.append(QPointF(BURST.x() + math.cos(a) * outer[k],
                            BURST.y() + math.sin(a) * outer[k]))
        b = a + math.radians(22.5)
        star.append(QPointF(BURST.x() + math.cos(b) * 8.0,
                            BURST.y() + math.sin(b) * 8.0))
    path = QPainterPath()
    path.addPolygon(star)
    path.closeSubpath()

    face = QPainterPath()
    face.addEllipse(BURST, 9.6, 10.6)
    return path.united(face)


def _pip(cx, cy, r):
    """Đốm lửa rời: ngôi sao bốn cánh nhỏ, cạnh lõm."""
    star = QPolygonF()
    for k in range(4):
        a = math.radians(k * 90)
        b = a + math.radians(45)
        star.append(QPointF(cx + math.cos(a) * r, cy + math.sin(a) * r))
        star.append(QPointF(cx + math.cos(b) * r * 0.3,
                            cy + math.sin(b) * r * 0.3))
    path = QPainterPath()
    path.addPolygon(star)
    path.closeSubpath()
    return path


def _eye(sign):
    """Một khe mắt xếch vào giữa — mặt nạ kín, chỉ hở đúng hai vệt này."""
    cx = BURST.x() + sign * 4.0
    return QPolygonF([QPointF(*q) for q in (
        (cx - sign * 2.8, 34.0), (cx + sign * 2.6, 35.2),
        (cx + sign * 2.4, 37.4), (cx - sign * 2.6, 36.2))])


@lru_cache(maxsize=None)
def _arm(sign):
    """Một cánh tay: sign < 0 là tay trái buông xuống, > 0 là tay phải giơ lên."""
    if sign > 0:
        return ribbon(QPointF(64, 62), QPointF(74, 48), HAND_R, 4.4, 2.8) \
            .united(fan(HAND_R, GLOVE_R))
    return ribbon(QPointF(32, 62), QPointF(20, 77), HAND_L, 4.4, 2.8) \
        .united(fan(HAND_L, GLOVE_L))


@lru_cache(maxsize=None)
def _figure():
    """Bóng người: đầu, cổ, thân, và hai cánh tay lệch trục."""
    head = QPainterPath()
    head.addEllipse(BURST, 8.6, 9.6)
    neck = QPainterPath()
    neck.addRect(44, 43, 8, 9)
    body = head.united(neck)

    torso = QPainterPath()                        # vai bè, thắt eo, hông loe
    torso.moveTo(28, 65)
    torso.cubicTo(31, 53, 65, 53, 68, 65)
    torso.cubicTo(66, 79, 62, 88, 61, 96)
    torso.lineTo(67, 122)
    torso.lineTo(29, 122)
    torso.lineTo(35, 96)
    torso.cubicTo(34, 88, 30, 79, 28, 65)
    torso.closeSubpath()
    body = body.united(torso)

    return body.united(_arm(1)).united(_arm(-1))


def _rays(p):
    """Nan quạt mực nhạt toả ra từ sau đầu — kiểu bùng nổ của truyện Silver Age."""
    fade = QColor(INK)
    fade.setAlpha(23)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(fade)
    for k in range(0, 24, 2):
        wedge = QPainterPath()
        wedge.moveTo(BURST)
        for edge in (k * 15.0, k * 15.0 + 5.5):
            a = math.radians(edge)
            wedge.lineTo(BURST.x() + math.cos(a) * 130,
                         BURST.y() + math.sin(a) * 130)
        wedge.closeSubpath()
        p.drawPath(wedge)


def _lit(p, path, pen=1.4, fill=None):
    """Vẽ một mảng sáng theo lối in lệch trục: hai bóng màu, ruột sáng, viền mực."""
    p.setPen(Qt.PenStyle.NoPen)
    for color, dx, dy, alpha in ((RED, 2.2, 1.7, 95), (BLUE, -1.9, -1.3, 80)):
        tint = QColor(color)
        tint.setAlpha(alpha)
        p.setBrush(tint)
        p.drawPath(path.translated(dx, dy))
    p.setBrush(fill or SPARK)
    p.setPen(QPen(INK, pen))
    p.drawPath(path)


def _paint(p, rect):
    """Vẽ trọn chân dung vào `rect`, không đệm gì thêm."""
    with design(p, rect, h=118):
        _rays(p)

        # Bảy chân dung kia đều là mảng đen; kẻ này thì không. Electro làm bằng
        # ánh sáng, nên bộ đồ chỉ tối vừa phải để mặt nạ và tia sét còn chỗ sáng.
        figure = _figure()
        _lit(p, figure, pen=1.8, fill=SUIT)

        p.save()
        p.setClipPath(figure, Qt.ClipOperation.IntersectClip)

        dusk = QColor(INK)                      # khối tối bám sườn khuất sáng
        dusk.setAlpha(52)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(dusk)
        p.drawPath(_shade())

        p.setBrush(INK)                         # thắt lưng và viền sét trên đồ
        p.setPen(QPen(INK, 0.6))
        p.drawPath(_belt())
        p.drawPath(_trim())

        p.setBrush(SPARK)                       # khoá thắt lưng, hình tia chớp
        p.setPen(QPen(INK, 0.8))
        p.drawPath(_pip(48, 95.6, 3.6))

        p.setPen(QPen(INK, 1.1))                # găng sáng bằng mặt nạ
        p.drawPath(_gloves())
        p.restore()

        # đường vai: hai tay là khối riêng, không phải phần dính liền của thân
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(INK, 1.5))
        for sign in (-1, 1):
            p.drawPath(_arm(sign))

        _lit(p, _bolts(), pen=1.1)
        _lit(p, _star(), pen=1.6)

        # hai khe mắt, thứ duy nhất tối trên mặt nạ
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(INK)
        for sign in (-1, 1):
            p.drawPolygon(_eye(sign))

        # đốm lửa rời, nổ lẻ ngoài rìa khung
        p.setBrush(SPARK)
        p.setPen(QPen(INK, 0.9))
        for cx, cy, r in ((13, 24, 3.0), (88, 62, 2.6), (16, 108, 2.4),
                          (66, 9, 2.2), (8, 70, 2.0), (80, 104, 2.8),
                          (34, 14, 1.8)):
            p.drawPath(_pip(cx, cy, r))

        marks(p)


_STILL = {}


def draw_electro(p, rect):
    """Chân dung tĩnh, nhưng tốn công nhất trong bộ — dựng một lần rồi dán.

    Khung hồ sơ vẽ lại tấm này hơn hai chục lần trong lúc mở, mà hình thì
    không đổi; ảnh dựng đúng bằng số điểm ảnh thật nên dán vào không nhoè.
    """
    scale = p.transform().m11() or 1.0
    key = (round(rect.width(), 1), round(rect.height(), 1), round(scale, 2))
    ready = _STILL.get(key)
    if ready is None:
        if len(_STILL) > 6:           # đổi cỡ cửa sổ liên tục thì đừng giữ hết
            _STILL.clear()
        ready = QImage(max(1, math.ceil(rect.width() * scale)),
                       max(1, math.ceil(rect.height() * scale)),
                       QImage.Format.Format_ARGB32_Premultiplied)
        ready.fill(Qt.GlobalColor.transparent)
        q = QPainter(ready)
        q.setRenderHint(QPainter.RenderHint.Antialiasing)
        q.scale(scale, scale)
        _paint(q, QRectF(0, 0, rect.width(), rect.height()))
        q.end()
        _STILL[key] = ready
    p.drawImage(rect, ready)


# ═══════════════════════════════════════════════════════════════ hồ sơ
PROFILE = Profile(
    name="Electro",
    vi_name="Người Điện",
    real_name="Maxwell Dillon",

    tagline="Một thợ đường dây bị sét đánh trúng lúc đang treo mình trên cột "
            "điện. Chỗ khác thì đó là một cáo phó; ở đây thì đó là một nguồn "
            "điện biết đi.",

    summary=(
        "Maxwell Dillon làm thợ đường dây cho một hãng điện lực. Trong lúc "
        "treo mình sửa đường dây trên cao, hắn bị sét đánh đúng lúc tay đang "
        "nắm dây trần. Cú đó lẽ ra phải giết hắn; thay vào đó nó biến cơ thể "
        "hắn thành một cái tụ điện sống — nạp được, giữ được, và phóng ra "
        "được. The Amazing Spider-Man #9 (02/1964) mở đầu bằng chuyện đó, rồi "
        "để hắn tự nhận ra thứ mình vừa có đáng giá hơn hẳn đồng lương thợ.",

        "Chi tiết đắt nhất của số báo lại không nằm ở trận đánh. J. Jonah "
        "Jameson nhìn thấy một kẻ mặc đồ bó, có sức mạnh không giải thích nổi, "
        "và rút ra đúng cái kết luận mà chỉ ông ta mới rút ra được: Electro "
        "chính là Spider-Man. Daily Bugle in nguyên xi giả thuyết ấy lên mặt "
        "báo, cả thành phố bàn tán, còn Peter thì vừa phải đi bắt Electro vừa "
        "phải chứng minh mình không phải hắn.",

        "Cách hạ hắn thì đơn giản tới mức gần như xúc phạm: Spider-Man mở một "
        "vòi nước và xịt thẳng vào. Nước nối đất, dòng điện tìm đường ngắn "
        "nhất chạy xuống, cái tụ điện sống tắt ngóm. Peter lột mặt nạ hắn ra, "
        "nhìn kỹ, rồi nhận ra mình chẳng biết đây là ai — một cái kết rất đúng "
        "chất Ditko cho kẻ vừa được cả thành phố đồn là siêu anh hùng.",

        "Electro là một trong sáu cái tên sáng lập Sinister Six (ASM Annual "
        "#1, 1964) và từ đó có mặt gần như mọi lần danh sách này tụ họp. Điểm "
        "yếu của hắn thì không bao giờ được vá: vẫn phải nạp, vẫn sợ nước, vẫn "
        "có thể cạn điện giữa trận. Về sau Marvel lấy luôn dòng điện ấy khỏi "
        "tay hắn — Francine Frye hút sạch và thừa kế cái tên.",
    ),

    powers=(
        "Cơ thể là một cái tụ điện sống: nạp, giữ, rồi phóng",
        "Một cú phóng có thể lên tới cỡ một triệu vôn",
        "Chạy dọc dây điện và cáp ngầm, nhanh hơn xe cộ",
        "Hút điện từ lưới thành phố để nạp lại giữa trận",
        "Sợ nước và sợ tiếp đất — hai thứ chưa bao giờ hết hiệu nghiệm",
    ),

    facts=(
        ("Tên thật", "Maxwell Dillon"),
        ("Xuất hiện đầu", "ASM #9  ·  02/1964"),
        ("Tác giả", "Stan Lee & Steve Ditko"),
        ("Nghề cũ", "Thợ đường dây hãng điện lực"),
        ("Băng nhóm", "Sinister Six — thành viên sáng lập"),
        ("Trên màn ảnh", "Jamie Foxx — TASM 2 và No Way Home"),
    ),

    blurb="Đã có một tuần cả thành phố tin rằng Electro với Spider-Man là cùng "
          "một người. Chuyện đó nói về Electro thì ít, mà nói về tờ Daily "
          "Bugle thì nhiều.",

    evolution=ABSOLUTE,
    evolve_label="Evolve",

    art=draw_electro,
    caption="Chân dung dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Electro_(Marvel_Comics)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Maxwell_Dillon_(Earth-616)"),
    ),
)
