"""
Big Man — Frederick Foswell.

Cả trò của nhân vật này nằm ở chuyện cỡ người: một phóng viên cao một mét
sáu lăm dựng lên hình ảnh một gã trùm khổng lồ bằng giày độn và áo độn vai.
Nên chân dung vẽ đúng hai cỡ đó cùng lúc — cái bóng chiếm gần hết bức tường,
còn người thật thì đứng bên dưới, bé tí, tay vẫn cầm quyển sổ ghi chép.

Bóng tô mực nhạt vì bóng thì nhạt; người thật tô đen đặc kèm hai lớp mực
lệch trục. Hai khe sáng trên mặt cái bóng là chỗ duy nhất nó có mắt.
"""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainterPath, QPen

from theme import INK, INK_SOFT

from .art import design, marks, misprint, ribbon
from .profile import Profile

PAGE = QColor("#F1EAD8")      # giấy quyển sổ, thẻ nhà báo, tròng kính
FLOOR = 104.0                 # chỗ chân tường giáp sàn — bóng dừng ở đây


# ═══════════════════════════════════════════════════ chân dung vẽ bằng code
def _shadow():
    """Cái bóng trên tường: gã trùm mà Foswell muốn cả thành phố tin là có thật."""
    crown = QPainterPath()
    crown.addRoundedRect(32, 2, 36, 17, 5, 5)
    brim = QPainterPath()
    brim.addEllipse(QPointF(50, 19.5), 38, 6.5)
    head = QPainterPath()
    head.addEllipse(QPointF(50, 31), 13, 13)

    coat = QPainterPath()                     # vai vuông vì áo độn, không vì người
    coat.moveTo(50, 40)
    coat.cubicTo(66, 41, 78, 44, 84, 53)
    coat.lineTo(90, FLOOR)
    coat.lineTo(10, FLOOR)
    coat.lineTo(16, 53)
    coat.cubicTo(22, 44, 34, 41, 50, 40)
    coat.closeSubpath()

    neck = QPainterPath()                     # cổ thẳng, kẻo cằm nhọn thành râu
    neck.addRect(43.5, 40, 13, 13)
    body = crown.united(brim).united(head).united(neck).united(coat)

    collar = QPainterPath()                   # khoét cổ áo chữ V, ngay dưới cổ
    collar.moveTo(43.5, 53)
    collar.lineTo(56.5, 53)
    collar.lineTo(50, 68)
    collar.closeSubpath()
    body = body.subtracted(collar)

    for sign in (-1, 1):                      # hai mảng hở hình nêm: tay chống nạnh
        gap = QPainterPath()
        gap.moveTo(50 + sign * 20, 57)
        gap.cubicTo(50 + sign * 21, 68, 50 + sign * 26, 78,
                    50 + sign * 31, 86)
        gap.lineTo(50 + sign * 19.5, 86)
        gap.closeSubpath()
        body = body.subtracted(gap)

    for cx in (44.5, 55.5):                   # hai khe mắt, chỗ duy nhất hở sáng
        slit = QPainterPath()
        slit.addRoundedRect(cx - 4.2, 27.5, 8.4, 2.8, 1.3, 1.3)
        body = body.subtracted(slit)
    return body


def _man():
    """Người thật: Foswell, mũ phớt, com lê, quyển sổ trong tay."""
    brim = QPainterPath()
    brim.addEllipse(QPointF(46, 76.6), 8.8, 2.3)
    crown = QPainterPath()
    crown.addRoundedRect(40.6, 69.6, 10.8, 7.4, 2.2, 2.2)
    head = QPainterPath()
    head.addEllipse(QPointF(46, 80.8), 4.4, 5.0)
    body = brim.united(crown).united(head)

    torso = QPainterPath()
    torso.moveTo(38.5, 89.5)
    torso.cubicTo(40, 86, 52, 86, 53.5, 89.5)
    torso.lineTo(54.5, 106)
    torso.lineTo(37.5, 106)
    torso.closeSubpath()
    body = body.united(torso)

    for x in (39.4, 47.4):                    # hai ống quần
        leg = QPainterPath()
        leg.addRect(x, 104, 5.4, 12.5)
        body = body.united(leg)

    body = body.united(ribbon(QPointF(39.5, 90.5), QPointF(36.4, 96),
                              QPointF(37, 103), 2.2, 1.6))
    return body.united(ribbon(QPointF(52.5, 90.5), QPointF(56.4, 93.5),
                              QPointF(55.6, 99), 2.2, 1.6))


def draw_big_man(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước."""
    with design(p, rect, h=118):
        # cái bóng: mực nhạt, không kèm bóng lệch trục — nó vốn không có thật
        dim = QColor(INK)
        dim.setAlpha(64)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(dim)
        p.drawPath(_shadow())

        # chân tường giáp sàn, để biết cái bóng đang đổ lên đâu
        edge = QColor(INK_SOFT)
        edge.setAlpha(120)
        p.setPen(QPen(edge, 1.0))
        p.drawLine(QPointF(2, FLOOR), QPointF(98, FLOOR))

        # vũng bóng dưới chân, chỗ người thật thực sự đứng
        p.setPen(Qt.PenStyle.NoPen)
        pool = QColor(INK)
        pool.setAlpha(46)
        p.setBrush(pool)
        p.drawEllipse(QPointF(46, 116.5), 14, 2.8)

        misprint(p, _man())

        # thẻ nhà báo giắt trên băng mũ — thứ giúp hắn đi đâu cũng lọt
        p.setBrush(PAGE)
        p.setPen(QPen(INK, 0.6))
        p.drawRect(QRectF(48.6, 73.2, 4.6, 3.0))

        # cổ áo sơ mi và cà vạt — người thật thì mặc com lê, không phải bóng đen
        collar = QPainterPath()
        collar.moveTo(43.2, 86.6)
        collar.lineTo(48.8, 86.6)
        collar.lineTo(46, 93.4)
        collar.closeSubpath()
        p.setBrush(PAGE)
        p.setPen(QPen(INK, 0.5))
        p.drawPath(collar)

        # kính tròn: người thật có mắt, cái bóng thì chỉ có hai khe
        p.setPen(QPen(INK, 0.7))
        for cx in (44.2, 47.8):
            p.drawEllipse(QPointF(cx, 80.6), 1.35, 1.35)
        p.setPen(QPen(INK, 0.6))
        p.drawLine(QPointF(45.6, 80.6), QPointF(46.4, 80.6))

        # quyển sổ ghi chép, đang mở
        p.setBrush(PAGE)
        p.setPen(QPen(INK, 0.8))
        p.drawRect(QRectF(53.6, 95.4, 7.4, 8.4))
        p.setPen(QPen(INK, 0.6))
        for y in (97.6, 99.4, 101.2):
            p.drawLine(QPointF(54.8, y), QPointF(59.8, y))

        marks(p)


# ═══════════════════════════════════════════════════════════════ hồ sơ
PROFILE = Profile(
    name="Big Man",
    vi_name="Ông Trùm",
    real_name="Frederick Foswell",

    tagline="Cả New York đi lùng một gã trùm to lớn. Hắn cao một mét sáu lăm, "
            "ngồi ngay trong toà soạn Daily Bugle, và viết bài về chính mình.",

    summary=(
        "The Amazing Spider-Man #10 (03/1964) mở ra một loại đối thủ mới. Big "
        "Man không leo tường, không bắn tia gì cả — hắn gom các băng đảng rời "
        "rạc của New York về một mối và điều hành chúng từ sau một chiếc mặt "
        "nạ. Phần đấm đá có The Enforcers lo: Montana với sợi thừng, Fancy Dan "
        "nhanh như chớp, và Ox thì to bằng cả hai người kia cộng lại.",

        "Spider-Man không hạ nổi hắn theo cách thông thường, vì vấn đề không "
        "phải là đánh thắng ai — mà là không ai biết phải đi tìm ai. Đến khi "
        "chiếc mặt nạ rơi xuống thì bên dưới là Frederick Foswell: một phóng "
        "viên gầy gò, nhút nhát, cao chừng một mét sáu lăm, chuyên mảng hình "
        "sự và là một trong những cây bút Jameson tin nhất.",

        "Cách hắn làm ra một gã khổng lồ cũng chẳng có gì thần bí — giày độn, "
        "áo độn vai, mặt nạ cao su, một cái máy đổi giọng. Vũ khí thật nằm ở "
        "chỗ khác: tấm thẻ nhà báo. Một phóng viên mảng hình sự thì đi đâu "
        "cũng lọt, hỏi gì cũng được, biết trước cảnh sát biết, và không ai "
        "thấy có gì lạ. Đây là cái tên đầu tiên trong danh sách chứng minh "
        "rằng phòng tin của Daily Bugle là một chỗ nấp rất tốt.",

        "Chuyện chưa dừng ở đó. Ra tù, Foswell được Jameson nhận lại — và hắn "
        "quay về nghề cũ theo cả hai nghĩa, vừa viết báo vừa làm chỉ điểm dưới "
        "cái tên Patch. Đến ASM #52 hắn đã len được vào sát Kingpin, rồi khi "
        "Jameson bị dí súng, hắn lao ra đỡ đạn. Câu cuối cùng của hắn là "
        "Jonah là người duy nhất từng cho hắn một cơ hội thứ hai.",
    ),

    powers=(
        "Không siêu năng lực, không đánh đấm — vốn liếng là thông tin",
        "Giày độn, áo độn vai, mặt nạ cao su, máy đổi giọng",
        "Thẻ nhà báo mảng hình sự: đi đâu cũng lọt, hỏi gì cũng được",
        "Gom được các băng đảng rời rạc của New York về một mối",
        "The Enforcers — Montana, Fancy Dan và Ox — làm tay chân",
    ),

    facts=(
        ("Tên thật", "Frederick Foswell"),
        ("Xuất hiện đầu", "ASM #10  ·  03/1964"),
        ("Tác giả", "Stan Lee & Steve Ditko"),
        ("Nghề", "Phóng viên hình sự, Daily Bugle"),
        ("Tay chân", "Montana, Fancy Dan và Ox"),
        ("Kết cục", "Đỡ đạn cho Jameson — ASM #52"),
    ),

    blurb="Hắn dựng cả một đế chế bằng đôi giày độn và một tấm thẻ nhà báo. "
          "Rồi hắn chết vì một việc chẳng ai bắt hắn phải làm.",

    art=draw_big_man,
    caption="Chân dung dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Frederick_Foswell"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Frederick_Foswell_(Earth-616)"),
    ),
)
