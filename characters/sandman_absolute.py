"""
Absolute Sandman — Flint Marko, cơn bão sa mạc hoá quốc gia.

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
    stamp="PHÂN LOẠI  ·  MỐI ĐE DOẠ CẤP QUỐC GIA",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="dust",
    evolve_fx="erode",       # giấy bị mài mòn, rồi cát bồi lại thành tờ mới

    tagline="Không còn một gã biến thành cát. Là một hệ sinh thái huỷ diệt "
            "biết tư duy — và nó đang biến cả một quốc gia thành sa mạc.",

    summary=(
        "Flint Marko vốn chỉ biến cơ thể thành cát, điều khiển khối lượng và "
        "tái tạo. Ở bản Absolute, mỗi hạt cát trong người hắn là một đơn vị "
        "xử lý độc lập: ý thức không còn nằm trong não mà trải khắp khối cát. "
        "Hắn tách thành hàng triệu hạt, trú trong không khí, nước và đất, rồi "
        "tụ lại lúc nào tuỳ ý.",

        "Điều đó xoá sạch khái niệm “đánh vào chỗ hiểm”. Không có lõi để phá — "
        "chỉ cần một hạt sống sót là hắn dựng lại được toàn bộ. Và hắn không "
        "còn giới hạn ở cát: mọi thứ chứa silicat — thuỷ tinh, bê tông, nhựa "
        "đường, gốm — đều bị bẻ liên kết phân tử rồi nuốt vào người.",

        "Bản phân tích này để ngỏ đúng một lỗ hổng: nhiệt độ cực thấp. Đóng "
        "băng được khối cát thì mới có chuyện để nói.",
    ),

    sections=(
        Section(
            title="Khuyếch đại năng lực vật lý & sinh học",
            intro="Không còn ranh giới giữa cơ thể hắn và mặt đất hắn đứng lên.",
            items=(
                ("Mạng thần kinh phân tán vô hạn",
                 "Mỗi hạt cát tự xử lý, ý thức trải khắp khối. Không có lõi để "
                 "tiêu diệt — một hạt sống sót là tái tạo được tất cả."),
                ("Hấp thụ và phản xạ động năng",
                 "Cát hành xử như chất lỏng phi Newton ở cấp vĩ mô: chịu lực "
                 "thì các hạt xếp lại thành cấu trúc cứng hơn thép, nuốt trọn "
                 "động năng rồi bật ngược bằng sóng xung kích. Đạn pháo và tên "
                 "lửa đều bị nuốt."),
                ("Đồng hoá khoáng vật diện rộng",
                 "Bẻ gãy liên kết phân tử của mọi vật liệu chứa silicat. Một "
                 "toà nhà bê tông cốt thép rã thành cát mịn trong vài phút rồi "
                 "sáp nhập vào cơ thể hắn."),
                ("Hút ẩm và sa mạc hoá",
                 "Rút nước từ mọi sinh vật trong bán kính hàng km: cây héo, "
                 "sông hồ bốc hơi, người mất nước cấp tốc dẫn tới trụy tim. "
                 "Đất màu mỡ thành sa mạc chỉ sau vài giờ."),
                ("Cát siêu mịn cỡ PM2.5",
                 "Bào tử cát cỡ nano phát tán vào khí quyển, chui vào phế nang "
                 "gây viêm phổi cấp và suy hô hấp. Quân đội không có mặt nạ "
                 "chuyên dụng bị loại khỏi vòng chiến ngay từ đầu."),
                ("Áp lực kiến tạo",
                 "Nén hàng nghìn tấn cát ở áp suất cực lớn để tạo mũi tên "
                 "obsidian sắc hơn dao mổ, hoặc kim cương nhân tạo làm đầu đạn "
                 "xuyên giáp."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="Khối cát đã hợp nhất với một hệ điều khiển nano-cơ học: "
                  "Silicat Swarm Intelligence.",
            items=(
                ("Lưới cảm biến bụi thông minh",
                 "Mỗi hạt mang một vi mạch lượng tử thu áp suất, nhiệt độ, "
                 "rung động và sóng điện từ. Rải một lớp bụi phủ kín cả một "
                 "bang là mọi chuyển động quân sự thành dữ liệu thời gian "
                 "thực."),
                ("AI “Dune Mind”",
                 "Cấy thẳng vào mạng cát, tự học và dự đoán chuyển động đối "
                 "thủ từ hàng tỷ điểm dữ liệu; mô phỏng 1.000 kịch bản chiến "
                 "đấu mỗi giây rồi chọn phản ứng tối ưu."),
                ("Phi đội ong cát",
                 "Hàng triệu cụm cát nhỏ tách ra hoạt động như drone siêu nhỏ: "
                 "luồn qua khe hở, khoét rỗng động cơ, làm tắc nòng súng, phá "
                 "bo mạch máy bay."),
                ("Vũ khí thuỷ tinh nóng chảy",
                 "Nung cát trên 1.700°C thành thuỷ tinh lỏng rồi bắn ra như "
                 "dòng plasma bán rắn xuyên thép tấm. Tháp pháo cát tự mọc lên "
                 "từ mặt đất và tự khai hoả, không cần hắn điều khiển."),
                ("Chiến tranh điện tử bằng bụi",
                 "Bụi cát hấp thụ sóng radar, gây nhiễu liên lạc, dựng “bức "
                 "tường cát tĩnh điện” làm mù mọi thiết bị trinh sát."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Từ giác quan báo nguy tới khả năng bám tường, mọi lợi thế "
                  "đều có một biện pháp riêng.",
            items=(
                ("Thuật toán nhiễu giác quan",
                 "Dune Mind điều hàng triệu hạt va chạm để phát tín hiệu rung "
                 "và điện từ giả từ mọi hướng, không theo quy luật nào. Giác "
                 "quan nhện vốn bắt mối đe doạ tức thời, nay ngập trong hàng "
                 "tỷ tín hiệu nhiễu: đau đầu dữ dội, mất phương hướng, rồi tê "
                 "liệt tạm thời."),
                ("“Glass Web-Breaker”",
                 "Hợp chất axit silicic phát tán ở trên 300°C bẻ gãy liên kết "
                 "peptide trong tơ nhện: tơ co rút rồi tan thành bụi. Mất luôn "
                 "phương tiện di chuyển lẫn cách khống chế."),
                ("Bẫy cát lún thông minh",
                 "Độ nhớt mặt cát chỉnh liên tục. Đặt chân xuống là vùng cát "
                 "quanh chân hoá lỏng và nuốt; càng giãy thì hiệu ứng phi "
                 "Newton càng làm cát cứng lại và siết chặt hơn."),
                ("Hút ẩm qua da",
                 "Dựng một vùng vi khí hậu khô cằn quanh Spider-Man, rút nước "
                 "thẳng qua da. Vài phút là cơ co rút, tốc độ và sức mạnh tụt "
                 "hẳn."),
                ("Bão cát tĩnh điện",
                 "Hạt cát cọ xát sinh tĩnh điện phá thiết bị trong bộ đồ, đồng "
                 "thời che tầm nhìn và làm tắc lỗ thở trên mặt nạ."),
                ("Mưa obsidian",
                 "Thả hàng nghìn mảnh thuỷ tinh siêu sắc từ trên cao. Diện phủ "
                 "quá rộng để né, mà giác quan báo nguy thì đang bị nhiễu; "
                 "mảnh còn găm lại trên người gây vết cắt sâu và nhiễm trùng."),
                ("Vô hiệu hoá khả năng bám dính",
                 "Một lớp bụi nano trơn phủ lên mọi bề mặt, phá lực bám tĩnh "
                 "điện ở tay chân. Không trèo tường, không bám trần, và trên "
                 "mặt cát trơn thì đứng cũng không vững."),
            ),
        ),
    ),

    tiers=(
        Tier("Tier 1", "Đô thị",
             "Bão cát trên 300 km/h chôn vùi đường sá, sân bay, nhà ga; nền "
             "đất rung làm sập hàng loạt toà nhà, cầu cống, đê điều. Cát chui "
             "vào máy biến áp và đường dây, nước sạch bị hút cạn, viễn thông "
             "chết lặng.",
             "6 giờ cho một thành phố lớn"),
        Tier("Tier 2", "Vùng lãnh thổ",
             "Nông nghiệp bị xoá sổ vì sa mạc hoá diện rộng, chuỗi cung ứng "
             "thực phẩm đứt gãy. Cảng biển và sân bay bị cồn cát khổng lồ "
             "phong toả; trung tâm dữ liệu bị cát xâm nhập, hệ thống tài chính "
             "sụp theo.",
             "Nhiều thành phố, khủng hoảng khu vực"),
        Tier("Tier 3", "Quốc gia",
             "Xe tăng và xe bọc thép chết máy vì cát chui vào động cơ; tiêm "
             "kích không cất cánh nổi vì turbine bám cát; binh lính khô kiệt "
             "nước và hít phải cát siêu mịn; tên lửa bị bão làm lệch hướng "
             "hoặc bị hấp thụ động năng trước khi chạm mục tiêu.",
             "48 – 72 giờ  ·  đỉnh cấp quốc gia"),
    ),

    facts=(
        ("Tên thật", "William Baker  ·  bí danh Flint Marko"),
        ("Cấp đe doạ", "Tier 3 — đỉnh cấp quốc gia"),
        ("Ý thức", "Phân tán trong từng hạt, không có lõi"),
        ("Đồng hoá", "Mọi vật liệu chứa silicat"),
        ("Sức gió", "Trên 300 km/h"),
        ("Diện phủ", "Cỡ bang Texas, lớp cát dày 1 mét"),
        ("Thời gian", "48 – 72 giờ để phủ trọn một quốc gia"),
        ("Lỗ hổng", "Nhiệt độ cực thấp — đóng băng khối cát"),
    ),

    blurb="Mọi hồ sơ khác trong tập này đều có một chỗ để đánh vào: một cái "
          "đầu, một lò phản ứng, một trung tâm chỉ huy. Hồ sơ này thì không. "
          "Muốn hạ hắn thì phải hạ cả sa mạc — hoặc tìm cho ra chỗ đủ lạnh để "
          "biến nó thành thuỷ tinh.",

    art=draw_absolute_sandman,
    caption="Dựng lại từ ảnh vệ tinh xuyên bụi  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Sandman_(Marvel_Comics)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/William_Baker_(Earth-616)"),
    ),
)
