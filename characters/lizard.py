"""
Lizard — Curtis Connors.

Chân dung vẽ bằng code: đầu bò sát mõm dài nhìn nghiêng, hàng gai chạy dọc
sọ xuống gáy, cái đuôi vắt lên phía sau — và chiếc áo blouse trắng rách bươm
trên vai, thứ duy nhất còn nhắc rằng bên trong từng là một bác sĩ.
"""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainterPath, QPen

from theme import INK, INK_SOFT, PAPER_HI

from .art import design, fan, marks, misprint, ribbon
from .lizard_absolute import ABSOLUTE
from .profile import Profile


# ═══════════════════════════════════════════════════ chân dung vẽ bằng code
def _head():
    """Sọ dẹt, mõm dài vươn ra trước, hàm bạnh về sau."""
    head = QPainterPath()
    head.moveTo(60, 32)
    head.cubicTo(54, 26, 42, 26, 33, 30)      # đỉnh sọ thấp và phẳng
    head.cubicTo(26, 33, 18, 37, 11, 42)      # mõm vươn dài ra trước
    head.lineTo(12, 47)                       # đầu mõm cụt
    head.cubicTo(20, 50, 28, 52, 36, 53)      # hàm dưới
    head.cubicTo(45, 54, 53, 53, 59, 49)      # góc hàm bạnh
    head.cubicTo(64, 45, 64, 37, 60, 32)      # gáy khép lại
    return head


def _neck():
    """Cổ bạnh, nối gáy xuống vai — cũng là chỗ bám của nửa hàng gai dưới."""
    neck = QPainterPath()
    neck.moveTo(48, 44)
    neck.lineTo(63, 39)
    neck.lineTo(78, 74)
    neck.lineTo(44, 68)
    neck.closeSubpath()
    return neck


def _crest():
    """Hàng gai chạy từ đỉnh sọ vòng xuống gáy rồi tắt dần ở vai."""
    crest = QPainterPath()
    for x, y, angle, length in ((47, 28, 283, 9), (54, 29, 298, 10),
                                (60, 33, 313, 10), (64, 41, 326, 9),
                                (68, 51, 338, 8), (72, 62, 350, 6.5)):
        crest = crest.united(fan(QPointF(x, y), [(angle, length, 2.6)]))
    return crest


def _tail():
    """Đuôi vòng lên phía sau vai phải."""
    return ribbon(QPointF(66, 104), QPointF(96, 92), QPointF(89, 44),
                  7.5, 2.2)


def _body():
    body = QPainterPath()
    body.moveTo(20, 120)
    body.cubicTo(23, 90, 36, 62, 52, 58)
    body.cubicTo(68, 62, 79, 90, 82, 120)
    body.closeSubpath()
    return body


def _coat():
    """Áo blouse: cổ chữ V, gấu rách nham nhở."""
    coat = QPainterPath()
    coat.moveTo(24, 76)
    coat.lineTo(41, 66)                       # ve áo bên trái
    coat.lineTo(50, 84)                       # đáy cổ chữ V
    coat.lineTo(60, 66)                       # ve áo bên phải
    coat.lineTo(78, 76)
    coat.lineTo(84, 116)                      # sườn phải
    coat.lineTo(78, 103)                      # gấu rách, đi từ phải sang trái
    coat.lineTo(71, 121)
    coat.lineTo(66, 111)
    coat.lineTo(59, 119)
    coat.lineTo(51, 100)
    coat.lineTo(45, 118)
    coat.lineTo(38, 108)
    coat.lineTo(30, 121)
    coat.lineTo(25, 109)
    coat.lineTo(18, 114)                      # sườn trái
    coat.closeSubpath()
    return coat


def draw_lizard(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước."""
    with design(p, rect, h=116):
        dark = (_tail().united(_body()).united(_neck())
                .united(_head()).united(_crest()))
        misprint(p, dark)

        # vảy: mấy vệt sáng cong trên lưng và trên đuôi
        scale_ink = QColor(PAPER_HI)
        scale_ink.setAlpha(58)
        p.setPen(QPen(scale_ink, 1.0))
        p.setClipPath(_tail())
        for t in (0.25, 0.42, 0.58, 0.74, 0.88):
            y = 104 - t * 60
            p.drawLine(QPointF(84 + t * 6, y), QPointF(95 - t * 4, y - 3))
        p.setClipping(False)

        # áo blouse trắng, mảng sáng duy nhất trên người
        p.setBrush(QColor("#EDE5D2"))
        p.setPen(QPen(INK, 1.5))
        p.drawPath(_coat())
        seam = QColor(INK_SOFT)
        seam.setAlpha(160)
        p.setPen(QPen(seam, 1.0))
        p.drawLine(QPointF(41, 67), QPointF(35, 100))     # nếp ve áo trái
        p.drawLine(QPointF(60, 67), QPointF(66, 98))      # nếp ve áo phải
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(60, 86, 13, 10)                        # túi ngực

        # mắt bò sát: hạnh nhân sáng, con ngươi là một khe dọc
        light = QColor("#F2EBDA")
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(light)
        eye = QPainterPath()
        eye.moveTo(31, 36)
        eye.cubicTo(35, 33, 41, 34, 43, 37)
        eye.cubicTo(40, 40, 34, 40, 31, 36)
        p.drawPath(eye)
        p.setBrush(INK)
        p.drawEllipse(QPointF(37, 36.8), 1.0, 2.6)

        # lỗ mũi và hàm răng nhọn dọc mép trên
        p.setBrush(light)
        p.drawEllipse(QPointF(16, 41.5), 1.3, 1.0)
        for x, w, h in ((17, 2.0, 3.4), (22, 2.2, 4.0), (28, 2.2, 3.8),
                        (34, 2.0, 3.4), (40, 1.8, 3.0), (46, 1.6, 2.6)):
            y = 44.6 + x * 0.115
            tooth = QPainterPath()
            tooth.moveTo(x - w / 2, y)
            tooth.lineTo(x + w / 2, y)
            tooth.lineTo(x, y + h)
            tooth.closeSubpath()
            p.drawPath(tooth)

        # đường mép, chạy từ đầu mõm về góc hàm
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(light, 1.2))
        lip = QPainterPath()
        lip.moveTo(12.5, 45)
        lip.cubicTo(26, 46.5, 40, 48.5, 52, 48)
        p.drawPath(lip)

        marks(p)


# ═══════════════════════════════════════════════════════════════ hồ sơ
PROFILE = Profile(
    name="Lizard",
    vi_name="Thằn Lằn",
    real_name="Curtis Connors",

    tagline="Một bác sĩ phẫu thuật cụt tay đi tìm cách mọc lại chi. Ông ta "
            "tìm ra thật — rồi mất luôn phần còn lại của mình.",

    summary=(
        "Curt Connors là bác sĩ phẫu thuật quân y, mất cánh tay phải sau một "
        "ca thương tật ngoài chiến trường. Ông ta dành cả sự nghiệp sau đó để "
        "nghiên cứu khả năng mọc lại chi của loài bò sát, chế ra huyết thanh "
        "từ ADN thằn lằn rồi tự tiêm cho mình. Cánh tay mọc lại thật. Rồi "
        "phần còn lại của cơ thể cũng đi theo.",

        "Xuất hiện trong The Amazing Spider-Man #6 (11/1963), Lizard là ác "
        "nhân đầu tiên trong danh sách này mà Spider-Man không hề muốn đánh. "
        "Connors là người tử tế, là đồng nghiệp, về sau thành thầy và bạn của "
        "Peter Parker ở Đại học Empire State. Mỗi lần hạ được con thằn lằn, "
        "việc tiếp theo của Peter luôn là pha thuốc giải để đưa Connors trở lại.",

        "Ở dạng thằn lằn, hắn khoẻ hơn người thường nhiều lần, có đuôi, có "
        "vuốt, tự lành vết thương và điều khiển được các loài bò sát khác "
        "trong bán kính rộng. Thứ hắn muốn không phải tiền hay quyền lực: hắn "
        "muốn cả thế giới thành nơi của loài bò sát. Mạch truyện Shed (ASM "
        "#630–633, 2010) đẩy nhân vật tới chỗ tăm tối nhất, khi con thằn lằn "
        "giết chính con trai của Connors.",
    ),

    powers=(
        "Sức mạnh, tốc độ và sức chịu đòn vượt xa người thường",
        "Vuốt sắc và cái đuôi dài dùng như vũ khí",
        "Tự lành vết thương, mọc lại phần chi bị mất",
        "Điều khiển được các loài bò sát trong bán kính rộng",
        "Trí óc bác sĩ Connors vẫn còn đâu đó bên trong — và đó là điểm yếu",
    ),

    facts=(
        ("Tên thật", "Dr. Curtis Connors"),
        ("Xuất hiện đầu", "ASM #6  ·  11/1963"),
        ("Tác giả", "Stan Lee & Steve Ditko"),
        ("Nghề cũ", "Bác sĩ phẫu thuật, nhà sinh học"),
        ("Chỗ dạy", "Đại học Empire State"),
        ("Trên màn ảnh", "Rhys Ifans, The Amazing Spider-Man (2012)"),
    ),

    blurb="Cả danh sách này toàn những kẻ chọn làm ác nhân. Connors không "
          "chọn gì cả — ông ta chỉ muốn có lại cánh tay của mình.",

    # Bấm nút tiến hoá để mở dạng Absolute — Connors không còn trong đó nữa.
    evolution=ABSOLUTE,
    evolve_label="Evolve",

    art=draw_lizard,
    caption="Chân dung dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Lizard_(character)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Curtis_Connors_(Earth-616)"),
    ),
)
