"""
Absolute Sandman — Flint Marko, một sa mạc biết suy nghĩ.

Bản sắc riêng, khác cả bốn dạng Absolute trước:
    · bộ da `dust` — bộ da **sáng** duy nhất. Bốn bộ kia mở ra là tối sầm
      lại; bộ này thì loà lên, màn phủ là một trận cát trắng xoá. Mặt giấy
      cũng nhám hơn hẳn, chấm halftone to và dày.
    · `evolve_fx="erode"` — không có mảnh vỡ nào cả. Giấy bị **mài mòn** sau
      một đường biên răng cưa tiến dần, rồi tờ mới được cát **bồi lên từ
      đáy** thành đụn.
    · chân dung là dạng duy nhất mà **bóng nhân vật không cố định**: đường
      viền của hắn dựng lại từ nhiễu ở mỗi khung hình, nên mép người liên
      tục lở ra rồi tụ lại. Otto cử động nhưng hình hắn vẫn là hình ấy;
      Marko thì mỗi khoảnh khắc một hình.

Vì không có gì đứng yên nên đây cũng là chân dung duy nhất không dựng sẵn
ảnh nền — bù lại nó chỉ toàn mảng phẳng và đường gấp khúc, vẽ rất nhẹ.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QLinearGradient, QPainterPath, QPen,
                           QPolygonF, QRadialGradient)

from theme import DUST

from .art import Rolls, design, marks
from .profile import Profile, Section, Tier

RUST = DUST.red                  # sắt trong cát
SLATE = DUST.blue                # thuỷ tinh obsidian
OCHRE = DUST.yellow
DEEP = QColor("#3A2C1C")         # chỗ cát dày nhất, gần như đặc
HOLLOW = QColor("#171009")       # hốc mắt — thứ tối nhất trong cả khung hình
CREST = 76.0                     # đỉnh đụn gần nhất
_SEED = 4091963


def _tone(color, alpha):
    out = QColor(color)
    out.setAlpha(max(0, min(255, int(alpha))))
    return out


def _wobble(x, y, t, scale=1.0):
    """Nhiễu rẻ tiền nhưng đủ mượt, dùng làm mép lở cho mọi thứ bằng cát."""
    return (math.sin(x * 0.21 + t * 0.9) * 1.6
            + math.sin(y * 0.17 - t * 0.7) * 1.2
            + math.sin((x + y) * 0.09 + t * 1.5) * 0.9) * scale


# ═══════════════════════════════════════════════════════════════ các lớp
def _sky(p):
    """Trời bị bụi nuốt: không xanh, không đen, chỉ một màu vàng bệch."""
    p.setPen(Qt.PenStyle.NoPen)
    wash = QLinearGradient(0, -6, 0, 126)
    wash.setColorAt(0.0, QColor("#9C917A"))
    wash.setColorAt(0.34, QColor("#BCAF92"))
    wash.setColorAt(0.62, QColor("#D3C6A6"))
    wash.setColorAt(0.80, QColor("#C0B292"))
    wash.setColorAt(1.0, QColor("#93866C"))
    p.setBrush(wash)
    p.drawRect(QRectF(-6, -6, 112, 132))

    # mặt trời chỉ còn là một quầng mờ, không thấy rìa
    sun = QRadialGradient(QPointF(66, 30), 30)
    sun.setColorAt(0.0, QColor(255, 244, 214, 150))
    sun.setColorAt(0.45, QColor(255, 240, 205, 46))
    sun.setColorAt(1.0, QColor(255, 240, 205, 0))
    p.setBrush(sun)
    p.drawRect(QRectF(30, -6, 72, 72))


def _dunes(p, t):
    """Ba lớp đụn chồng nhau, lớp gần nhất bò chậm theo gió."""
    for layer, (base, tone, speed) in enumerate((
            (CREST - 14, QColor("#A2957A"), 0.5),
            (CREST - 6, QColor("#8E8168"), 0.8),
            (CREST + 4, QColor("#736750"), 1.3))):
        ridge = QPainterPath()
        ridge.moveTo(-8, 128)
        x = -8.0
        while x <= 108:
            y = (base
                 + math.sin(x * 0.06 + t * 0.06 * speed + layer * 2.1) * 4.5
                 + math.sin(x * 0.15 - t * 0.1 * speed) * 1.8)
            ridge.lineTo(x, y)
            x += 4
        ridge.lineTo(108, 128)
        ridge.closeSubpath()
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(tone)
        p.drawPath(ridge)

    # gió liếm trên mặt đụn gần nhất
    p.setBrush(Qt.BrushStyle.NoBrush)
    r = Rolls(_SEED)
    for _ in range(14):
        y = r(CREST + 8, 122)
        x0 = r(-8, 70)
        p.setPen(QPen(_tone(QColor("#C8BB9C"), r(40, 110)), r(0.4, 1.1)))
        p.drawLine(QPointF(x0, y), QPointF(x0 + r(14, 44), y - r(0, 2)))


def _titan(p, t):
    """Bóng hắn: dựng lại từ nhiễu mỗi khung hình nên mép luôn đang lở.

    Không dùng path cố định — mỗi điểm trên đường viền bị đẩy đi theo hàm
    nhiễu, và càng lên cao thì đẩy càng mạnh, nên đỉnh đầu gần như tan hẳn
    vào bão còn phần vai thì vẫn còn ra hình.
    """
    # nửa bề ngang theo độ cao: sọ nhỏ, cổ thắt lại, rồi vai bung ra rất rộng
    spine = ((13, 5), (17, 9), (23, 11.5), (29, 12), (35, 10.5), (39, 7.5),
             (43, 16), (48, 26), (54, 32), (62, 37), (70, 41), (80, 45))

    def _edge(spread, seed):
        """Một đường viền của khối cát, lở theo nhiễu — càng cao càng lở mạnh."""
        left, right = [], []
        for y, half in spine:
            loose = ((1.0 - (y - 13) / 70.0) ** 2 * 3.2 + 0.4) * spread
            left.append(QPointF(50 - half - spread * 1.6
                                + _wobble(50 - half, y, t + seed, loose), y))
            right.append(QPointF(50 + half + spread * 1.6
                                 + _wobble(50 + half, y, t + seed + 11, loose),
                                 y))
        return QPolygonF(left + list(reversed(right)))

    p.setPen(Qt.PenStyle.NoPen)
    # hai lớp thôi, và mỗi lớp lở theo nhiễu riêng. Nếu chỉ co nhỏ cùng một
    # hình thì các lớp thành đường bình độ, nhìn ra bản đồ địa hình.
    p.setBrush(_tone(QColor("#6E6049"), 105))
    p.drawPolygon(_edge(1.9, 5.0))
    p.setBrush(_tone(QColor("#57492F"), 210))
    p.drawPolygon(_edge(0.85, 2.0))
    p.setBrush(_tone(DEEP, 255))
    p.drawPolygon(_edge(0.0, 0.0))

    # chỏm đầu bốc lên thành mấy ngọn khói cát
    for k in range(6):
        base = 43 + k * 2.8
        lean = 6 + k * 2.2 + 4 * math.sin(t * 0.7 + k)
        top = 2 - k * 0.8
        plume = QPolygonF([
            QPointF(base - 1.3, 17), QPointF(base + 1.3, 17),
            QPointF(base + lean, top + 1.2), QPointF(base + lean, top)])
        p.setBrush(_tone(QColor("#7A6C54"),
                         int(26 + 16 * math.sin(t * 1.3 + k))))
        p.drawPolygon(plume)

    # vân cát chảy dọc thân, để khối không thành một mảng bết
    p.setBrush(Qt.BrushStyle.NoBrush)
    for k in range(-3, 4):
        x = 50 + k * 8
        p.setPen(QPen(_tone(QColor("#2A2013"), 60), 0.7))
        vein = QPainterPath(QPointF(x, 46))
        vein.quadTo(QPointF(x + _wobble(x, 60, t, 2.0), 62),
                    QPointF(x + k * 2.5, 80))
        p.drawPath(vein)

    # hai hốc mắt: chỗ tối nhất khung hình, hõm sâu và xếch lên
    p.setPen(Qt.PenStyle.NoPen)
    for sx in (-1, 1):
        ex = 50 + sx * 5.6 + _wobble(50 + sx * 5, 27, t, 0.4)
        socket = QPolygonF([
            QPointF(ex - sx * 4.4, 25.4), QPointF(ex + sx * 3.4, 26.8),
            QPointF(ex + sx * 3.2, 29.4), QPointF(ex - sx * 4.2, 28.6)])
        p.setBrush(_tone(HOLLOW, 240))
        p.drawPolygon(socket)
        p.setBrush(_tone(RUST, int(80 + 60 * math.sin(t * 1.7 + sx))))
        p.drawEllipse(QPointF(ex - sx * 0.6, 27.4), 1.5, 0.9)

    # miệng: một khe ngang không đều, hé ra rồi khép lại
    gap = 1.2 + 1.0 * math.sin(t * 0.8)
    mouth = QPainterPath()
    mouth.moveTo(44, 34)
    for k in range(1, 8):
        u = k / 7
        mouth.lineTo(44 + u * 12, 34 + _wobble(44 + u * 12, 34, t, 0.5))
    mouth.lineTo(56, 34 + gap)
    for k in range(6, 0, -1):
        u = k / 7
        mouth.lineTo(44 + u * 12, 34 + gap
                     + _wobble(44 + u * 12, 36, t + 3, 0.5))
    mouth.closeSubpath()
    p.setBrush(_tone(HOLLOW, 195))
    p.drawPath(mouth)


def _shear(p, t):
    """Dải cát bị gió xé khỏi người hắn, bay chéo rồi tan."""
    r = Rolls(_SEED + 7)
    p.setPen(Qt.PenStyle.NoPen)
    for i in range(80):
        speed = r(0.3, 0.9)
        phase = r(0, 1)
        y0 = r(14, 84)
        x0 = r(30, 70)
        travel = (t * speed + phase) % 1.0
        x = x0 + travel * r(30, 78)
        y = y0 - travel * r(2, 16)
        fade = math.sin(math.pi * travel)
        tone = QColor(RUST if i % 11 == 0 else QColor("#7C6E56"))
        tone.setAlpha(int(150 * fade))
        p.setBrush(tone)
        p.drawRect(QRectF(x, y, r(2.0, 7.0), r(0.35, 0.9)))


def _glass(p, t):
    """Mảnh obsidian bắn ra từ trong bão, cạnh bắt sáng một nhịp rồi tắt."""
    r = Rolls(_SEED + 23)
    for i in range(9):
        speed = r(0.18, 0.4)
        fall = (t * speed + r(0, 1)) % 1.0
        x = r(6, 94) + fall * 10
        y = -6 + fall * 132
        size = r(1.6, 3.6)
        spin = r(0, 360) + t * r(20, 70)
        p.save()
        p.translate(x, y)
        p.rotate(spin)
        shard = QPolygonF([QPointF(0, -size), QPointF(size * 0.5, size * 0.4),
                           QPointF(-size * 0.4, size * 0.7)])
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(_tone(SLATE, 190))
        p.drawPolygon(shard)
        p.setPen(QPen(_tone(QColor("#EDE7D6"),
                            int(90 + 140 * abs(math.sin(t * 2 + i)))), 0.5))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(QPointF(0, -size), QPointF(size * 0.5, size * 0.4))
        p.restore()


def _haze(p, t):
    """Bụi mù phủ đè lên tất cả, dày lên rồi loãng đi theo từng cơn gió."""
    gust = 0.5 + 0.5 * math.sin(t * 0.33)
    p.setPen(Qt.PenStyle.NoPen)
    veil = QLinearGradient(0, 0, 0, 126)
    veil.setColorAt(0.0, _tone(QColor("#D8CCAC"), 40 + 60 * gust))
    veil.setColorAt(0.5, _tone(QColor("#D8CCAC"), 16 + 40 * gust))
    veil.setColorAt(1.0, _tone(QColor("#D8CCAC"), 50 + 70 * gust))
    p.setBrush(veil)
    p.drawRect(QRectF(-6, -6, 112, 132))

    r = Rolls(_SEED + 51)
    for _ in range(90):
        speed = r(1.0, 3.0)
        lane = r(-6, 126)
        drift = (r(0, 1) + t * speed * 0.16) % 1.0
        x = -10 + drift * 124
        p.setBrush(_tone(QColor("#5E5340"), r(30, 110)))
        p.drawRect(QRectF(x, lane + drift * 8, r(1.4, 4.2), r(0.3, 0.7)))


def _readout(p, t):
    """Ẩm kế đang tụt về không, và hoa gió chỉ hướng bão — thay cho khung ngắm."""
    # cột ẩm kế bên trái: vơi dần rồi nhích lên tí, rồi lại vơi
    wet = max(0.02, 0.42 - 0.40 * ((t * 0.06) % 1.0))
    box = QRectF(4.5, 20, 3.0, 46)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(DUST.ink, 120), 0.5))
    p.drawRect(box)
    for k in range(5):
        y = box.y() + k * box.height() / 4
        p.drawLine(QPointF(box.right(), y), QPointF(box.right() + 1.6, y))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_tone(RUST if wet < 0.15 else SLATE, 190))
    p.drawRect(QRectF(box.x() + 0.6, box.bottom() - 0.6 - (box.height() - 1.2) * wet,
                      box.width() - 1.2, (box.height() - 1.2) * wet))

    # hoa gió góc trên phải: kim quay chậm, vành có vạch chia
    c = QPointF(92, 16)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(DUST.ink, 110), 0.5))
    p.drawEllipse(c, 5.0, 5.0)
    for k in range(8):
        a = math.radians(k * 45)
        p.drawLine(QPointF(c.x() + math.cos(a) * 3.8, c.y() + math.sin(a) * 3.8),
                   QPointF(c.x() + math.cos(a) * 5.0, c.y() + math.sin(a) * 5.0))
    a = math.radians(28 + 10 * math.sin(t * 0.5))
    p.setPen(QPen(_tone(RUST, 220), 1.0))
    p.drawLine(QPointF(c.x() - math.cos(a) * 3.0, c.y() - math.sin(a) * 3.0),
               QPointF(c.x() + math.cos(a) * 4.4, c.y() + math.sin(a) * 4.4))


def draw_absolute_sandman(p, rect, t=0.0):
    """Chân dung sống: nhận thêm `t` (giây) nên khung hồ sơ tự vẽ lại."""
    with design(p, rect):
        _sky(p)
        _titan(p, t)
        _shear(p, t)
        _dunes(p, t)
        _glass(p, t)
        _haze(p, t)
        _readout(p, t)
        marks(p, QColor("#5A4C36"))


# ═══════════════════════════════════════════════════════════════ hồ sơ
ABSOLUTE = Profile(
    name="Absolute Sandman",
    vi_name="Người Cát Tuyệt Đối",
    real_name="William Baker  ·  Flint Marko",
    keys=("Sandman Absolute",),

    kicker="Hồ sơ tuyệt đối",
    stamp="PHÂN LOẠI  ·  MỐI ĐE DOẠ CẤP HÀNH TINH",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="dust",
    evolve_fx="erode",       # giấy bị mài mòn, rồi cát bồi lại thành tờ mới

    tagline="Một kẻ bị ruồng bỏ, giờ là một sa mạc biết suy nghĩ. Hắn không "
            "cần đánh bại ai — chỉ cần tồn tại và lan ra là đủ.",

    summary=(
        "Flint Marko chưa bao giờ là kẻ chủ mưu. Hắn là một tội phạm đường "
        "phố bị tai nạn phóng xạ ném vào một hình hài khác, và cái hình hài "
        "ấy nói đúng chủ đề của đời hắn: bào mòn, tan rã, rồi tụ lại. Hắn "
        "đánh trực diện chứ không bày mưu, và thứ giữ hắn sống sót lâu hơn "
        "mọi kẻ khác chỉ là sự bền bỉ.",

        "Bản Absolute không cho hắn thêm một cỗ máy nào — hắn vốn thuần sinh "
        "học và vẫn thuần sinh học. Thứ thay đổi là quy mô và là chất: ý thức "
        "không còn nằm trong một khối cát hình người mà trải ra từng hạt, và "
        "hắn học được cách biến đá thành cát. Từ một cơ thể vài mét, hắn "
        "thành một sa mạc di động rộng hàng chục km².",

        "Điều đó xoá sạch khái niệm “đánh vào chỗ hiểm”. Không có lõi để phá, "
        "không có máy chủ để tắt, không có gì để hack — chỉ cần một hạt sống "
        "sót là hắn dựng lại được tất cả.",

        "Ba điểm yếu cũ thì hắn mới vá được một: nhiệt độ cao từng hoá hắn "
        "thành thuỷ tinh, nay bị lớp polymer chịu nhiệt chặn lại. Nước vẫn "
        "làm cát nặng và rã rời. Còn cái thứ ba thì không có lớp phủ nào bọc "
        "được — một cái đầu bất ổn, dễ bị thao túng, và một đứa con gái.",
    ),

    sections=(
        Section(
            title="Khuyếch đại năng lực vật lý & sinh học",
            intro="Bản gốc là một người có cơ thể bằng cát, tái tạo được "
                  "chừng nào còn cát quanh mình. “Sinh quyển Silicat Tự trị” "
                  "xoá nốt cái ranh giới cuối cùng: giữa cơ thể hắn và mặt đất "
                  "hắn đứng lên không còn gì ngăn cách.",
            items=(
                ("Hạt cát phủ polymer hữu cơ",
                 "Mỗi hạt được bọc một lớp polymer do chính hắn tiết ra, vừa "
                 "tăng kết dính vừa dẫn tín hiệu thần kinh. Nhờ đó hắn điều "
                 "khiển từng hạt riêng lẻ như một tế bào, và thôi phải giữ một "
                 "hình dạng liên tục để còn là mình — đây mới là chỗ bản "
                 "Absolute rẽ khỏi bản gốc."),
                ("Phản ứng khoáng hoá",
                 "Chạm vào granite, bazan hay thạch anh, hắn tiết ra axit "
                 "silicic cùng một loại enzyme xúc tác phá vỡ mạng tinh thể "
                 "silicat: đá cứng rã thành cát bột trong vài giờ. Hắn không "
                 "còn phải đi tìm sa mạc nữa — hắn ăn núi đá và tự làm ra sa "
                 "mạc của mình."),
                ("Phân thân hữu cơ",
                 "Tách ý thức vào hàng trăm khối cát độc lập, hoạt động như "
                 "một bầy. Chúng không phải máy móc và cũng chẳng có trí tuệ "
                 "riêng: chúng là phần mở rộng tự nhiên của hắn, chung đúng "
                 "một ý chí, nên phối hợp được mà không cần ai ra lệnh cho ai."),
                ("Hút ẩm chủ động",
                 "Những xúc tu cát siêu mịn phủ lớp hút ẩm kiểu silica gel, "
                 "diện tích bề mặt cực lớn, rút nước từ không khí, từ đất và "
                 "từ cả sinh vật sống. Đất canh tác thành hoang mạc, còn thứ "
                 "gì đứng trong đó thì khô kiệt dần."),
                ("Tĩnh điện cát",
                 "Ma sát giữa hàng tỷ hạt bay ở tốc độ cao sinh ra điện tích, "
                 "và cơn bão cát bắt đầu phóng ra sét cát: đủ đánh sập lưới "
                 "điện, đủ châm cháy rừng. Một cơn bão thường không làm được "
                 "việc đó; cơn bão này thì có, vì nó có chủ đích."),
                ("Cấu trúc phức hợp",
                 "Hắn không chỉ dựng cột và tường. Hắn mô phỏng cả cơ quan "
                 "sinh học bằng cát: phổi cát lọc độc tố, tim cát tạo áp lực "
                 "bơm cát đi xa, màng cát bán thấm để lọc nước. Cơ thể hắn "
                 "thôi là một khối và thành một cơ thể thật, chỉ khác vật liệu."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="Đây là dạng Absolute duy nhất không có mục công nghệ, vì "
                  "nhân vật gốc chưa từng cầm tới một cái máy nào. Chỗ đáng lẽ "
                  "là máy móc thì hắn mọc ra bằng cát — không AI, không drone, "
                  "chỉ là những cơ quan hữu cơ nối dài ra khỏi thân thể.",
            items=(
                ("Mạng lưới sợi nấm cát",
                 "Dưới lòng đất, hắn đan những sợi cát li ti thành một hệ như "
                 "sợi nấm, truyền tín hiệu bằng rung động cơ học đi hàng chục "
                 "km. Mọi bước chân, mọi bánh xe, mọi tiếng nổ trên mặt đất "
                 "đều được ghi lại và chạy ngược về lõi ý thức của hắn."),
                ("Bãi cát cảm ứng",
                 "Vùng cát hắn kiểm soát đổi áp suất ngay khi có vật đi qua, "
                 "giống một cây bắt ruồi trải rộng hàng mẫu. Dẫm lên là bị "
                 "quấn lấy, giữ chặt, hoặc nuốt hẳn xuống."),
                ("Cơn mưa cát cảm biến",
                 "Hạt cát cỡ micromet lơ lửng khắp không khí, va vào vật thể "
                 "rồi dội rung động về lõi — một thứ radar sinh học không phát "
                 "ra tín hiệu nào để mà dò ngược. Cùng lúc, chính đám bụi ấy "
                 "là vũ khí: hít vào là phổi hỏng."),
                ("Thạch nhũ cát lưu trữ",
                 "Những cấu trúc cát kết tinh dựng sâu dưới đất, tích nước, "
                 "khoáng chất và axit silicic. Đây là kho dự phòng để dựng lại "
                 "cơ thể sau một tổn thất lớn — thứ khiến việc đánh tan hắn "
                 "một lần trở nên vô nghĩa."),
                ("Lò phản ứng hoá học cát",
                 "Trong lòng các khối lớn, hắn mở những buồng phản ứng trộn "
                 "cát với axit để chế ra vật liệu mới: thuỷ tinh lỏng để bắn "
                 "đi, hoặc chất kết dính siêu bền để dựng thứ cần đứng vững. "
                 "Một nhà máy không có lấy một bánh răng."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Không đòn nào ở đây là công cụ mượn từ chỗ khác: tất cả đều "
                  "mọc thẳng ra từ bản chất vô định hình của cát. Hai đòn đầu "
                  "đánh vào giác quan nhện từ hai phía ngược nhau — một bên "
                  "làm ngập tín hiệu, một bên hút sạch tín hiệu.",
            items=(
                ("Trường cát gây nhiễu",
                 "Giác quan nhện đọc rung động và thay đổi áp suất quanh "
                 "người. Hắn thả một màn cát siêu mịn dày đặc, mỗi hạt chuyển "
                 "động ngẫu nhiên, dựng nên một trường nhiễu đẳng hướng — mọi "
                 "phương đều báo nguy hiểm y như nhau. Giác quan không tắt, "
                 "nó chỉ thôi chỉ được hướng nào để né."),
                ("Trường cát hấp thụ rung động",
                 "Cát dập rung rất giỏi, nên lớp cát dày bao quanh chỗ giao "
                 "chiến hoạt động như một tấm đệm giảm chấn: rung động của mọi "
                 "chuyển động bị nuốt trước khi kịp tới chỗ Peter. Ghép với "
                 "trường nhiễu ở trên thì thành một cái kìm — bên ngoài ồn đến "
                 "mức vô nghĩa, bên trong im đến mức không kịp báo."),
                ("Cát ăn mòn mạng nhện",
                 "Hạt cát phủ axit silicic cùng enzyme phân huỷ polymer: chạm "
                 "vào tơ là chuỗi polymer đứt liên kết, tơ giòn ra và mất đàn "
                 "hồi. Cát bám lại còn xoá nốt độ bám dính trên tường. Mất đu "
                 "dây, mất bám, Peter bị ghìm xuống mặt đất — đúng chỗ mà cát "
                 "làm chủ."),
                ("Tấn công qua đường hô hấp",
                 "Cát dưới 10 micromet lọt qua khe mặt nạ và lỗ thông khí của "
                 "bộ đồ, bám vào phế nang gây viêm và dựng dần một lớp màng "
                 "trong phổi. Hắn còn xoáy một cơn lốc quanh Peter để tạo áp "
                 "suất âm ở tâm: không khí bị hút ra khỏi phổi trong khi cát "
                 "bị đẩy vào mọi khe hở. Thiếu oxy thì sức mạnh nào cũng hết."),
                ("Phân tán mối đe doạ",
                 "Hàng chục khối cát mang ý thức của hắn đánh cùng lúc vào "
                 "dân thường, vào hạ tầng, vào người thân của Peter. Cậu không "
                 "ưu tiên được chỗ nào vì chỗ nào cũng thật. Rồi hắn dựng thêm "
                 "những “con tin cát” — hình nộm người bằng cát — để ngay cả "
                 "lòng trắc ẩn cũng thành thứ bị lợi dụng: giác quan báo nguy "
                 "khắp nơi, nhưng không nói được đâu là người, đâu là bẫy."),
                ("Phản đòn nhiệt",
                 "Nhiệt độ cao vốn là cách hoá hắn thành thuỷ tinh, nên hắn vá "
                 "đúng chỗ đó: lớp polymer chịu nhiệt hút lấy nhiệt rồi tản đi "
                 "bằng cách luân chuyển cát nóng ra xa và đưa cát nguội vào. "
                 "Tệ hơn, hắn chủ động hoá thuỷ tinh một phần thân mình để lấy "
                 "mảnh vỡ sắc mà bắn trả. Đòn khắc chế cũ giờ thành kho đạn."),
            ),
        ),
    ),

    # Thang chữ cái Hy Lạp, đọc từ Zeta lên Omega như các dạng Absolute khác.
    # Đây là dạng chậm nhất trong cả tập: không bậc nào tính bằng giây, và
    # bậc cao nhất mất trọn một tháng — sa mạc hoá vốn không biết vội.
    tiers=(
        Tier("Tier Zeta", "Một mục tiêu",
             "Cát trong phạm vi vài mét, một người. Đúng bằng bản gốc lúc mới "
             "biết mình làm được gì — và cũng là bậc duy nhất mà hai bản "
             "ngang nhau.",
             "Tức thời"),
        Tier("Tier Epsilon", "Một toà nhà",
             "Dồn một khối cát khổng lồ đè sập, hoặc luồn vào trong kết cấu bê "
             "tông rồi khoáng hoá cho nó tự đổ từ bên trong. Bản gốc phình hết "
             "cỡ mới làm nổi việc này; Absolute làm mà không cần gắng sức.",
             "Vài phút"),
        Tier("Tier Delta", "Một khu phố",
             "Biến toàn bộ mặt đất trong bán kính 500 mét thành cát lún, nuốt "
             "nhà cửa, xe cộ, cột điện, rồi dựng xúc tu cát quật ngã những gì "
             "còn đứng. Bản gốc phải dồn toàn lực mới gây được ngần ấy thiệt "
             "hại; Absolute chỉ chia ra một phần nhỏ ý thức.",
             "Vài giờ"),
        Tier("Tier Gamma", "Một quận",
             "Một cồn cát di động cao 30 mét, chạy 20 km/h, vùi lấp mọi thứ "
             "trên đường đi, đồng thời hút cạn sông hồ giếng trong vùng. Bản "
             "gốc chỉ nguy hiểm lúc đang đánh nhau; Absolute phá hạ tầng quy "
             "mô lớn mà không cần có mặt.",
             "Một ngày cho 10 km²"),
        Tier("Tier Beta", "Một tỉnh, một bang",
             "Bão cát tĩnh điện phủ hàng trăm km², che khuất mặt trời, sét cát "
             "đánh sập lưới điện, cát chui vào làm hỏng máy móc. Đất nông "
             "nghiệp thành hoang mạc chỉ sau vài ngày. Đây là chỗ hắn bắt đầu "
             "biến thời tiết thành vũ khí — thứ bản gốc chưa từng chạm tới.",
             "3–5 ngày"),
        Tier("Tier Alpha", "Một quốc gia lớn",
             "Hút ẩm từ khí quyển và đất trên hàng trăm nghìn km²: hạn hán "
             "nghiêm trọng, cháy rừng lan rộng, nước ngọt cạn dần. Những sa "
             "mạc nhân tạo cứ thế nới ra và chôn dần các thành phố, trong khi "
             "bão cát làm loạn hàng không và viễn thông.",
             "1–2 tuần"),
        Tier("Tier Omega", "“Sa mạc Hành tinh”",
             "Hắn thả hạt cát của mình vào các dòng hải lưu và gió mậu dịch để "
             "đi khắp địa cầu. Bụi cỡ PM2.5 lơ lửng trong tầng đối lưu phản xạ "
             "ánh nắng, làm lạnh cục bộ nhưng chặn bốc hơi nên hạn hán càng "
             "nặng; nước ngọt bị rút khỏi sông hồ và khỏi cả đất trồng. Vòi "
             "rồng cát cao hàng km cuốn phăng công trình, bão tĩnh điện cấp "
             "lục địa xoá lưới điện. Đáng sợ nhất là hắn phá cấu trúc đất sét "
             "và mùn, để lại cát trơ không trồng được gì nữa — sa mạc vĩnh "
             "viễn. Trong 30 ngày: kinh tế toàn cầu sụp, đói diện rộng, 20–30% "
             "đất canh tác thành hoang mạc. Bản gốc chỉ cần một đội cứu hoả "
             "và Spider-Man là chặn được; bậc này thì không chính phủ hay quân "
             "đội nào đảo ngược nổi.",
             "30 ngày"),
    ),

    # Nhãn giữ dưới 94 px, giá trị dưới 188 px — xem chú thích cùng chỗ trong
    # `chameleon_absolute.py`. Bỏ dòng "Tên thật" vì `real_name` đã in ngay
    # dưới masthead rồi.
    facts=(
        ("Cấp đe doạ", "Hành tinh · sa mạc hoá"),
        ("Ý thức", "Trải khắp từng hạt, không có lõi"),
        ("Không dùng", "Công nghệ · AI · drone"),
        ("Ăn được", "Granite, bazan, thạch anh"),
        ("Sa mạc di động", "Hàng chục km²"),
        ("Sét cát", "Tĩnh điện từ hàng tỷ hạt"),
        ("Điểm yếu", "Nước — và một đứa con gái"),
        ("Bậc Omega", "30 ngày · 20–30% đất trồng"),
    ),

    blurb="Mọi hồ sơ khác trong tập này đều có một chỗ để đánh vào: một cái "
          "đầu, một lò phản ứng, một trung tâm chỉ huy. Hồ sơ này thì không — "
          "và hắn cũng chẳng cần thắng ai. Hắn chỉ cần tồn tại, rồi lan ra, "
          "cho tới lúc thứ người ta phải đánh bại không còn là một kẻ nào cả, "
          "mà là chính mặt đất dưới chân mình.",

    art=draw_absolute_sandman,
    caption="Dựng lại từ ảnh vệ tinh xuyên bụi  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Sandman_(Marvel_Comics)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/William_Baker_(Earth-616)"),
    ),
)
