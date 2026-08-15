"""
Vulture — Adrian Toomes.

Chân dung vẽ bằng code: đầu hói nhìn nghiêng với chiếc mũi khoằm như mỏ chim,
cổ áo lông vũ tua tủa quanh hàm, đôi cánh dựng cao ôm lấy đầu. Muốn dùng ảnh
thật thì thả file vào assets/characters/ rồi điền image="vulture.jpg" — ảnh
sẽ được ưu tiên hơn hình vẽ.
"""

import math

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainterPath, QPen

from theme import INK, INK_SOFT, PAPER_HI

from .art import design, fan, marks, mirrored, misprint
from .profile import Profile
from .vulture_absolute import ABSOLUTE

WING_ROOT = QPointF(42, 66)
# (góc, dài, nửa bề ngang) — cánh trái dang ngang rồi vuốt cong lên
WING = ((183, 38, 6.6), (195, 41, 6.4), (208, 40, 6.0),
        (221, 36, 5.4), (234, 30, 4.8))


# ═══════════════════════════════════════════════════ chân dung vẽ bằng code
def _wings():
    left = fan(WING_ROOT, WING)
    return left.united(mirrored(left))


def _ruff():
    """Vòng lông tua tủa quanh cổ — khối riêng, nằm đè lên cánh."""
    return fan(QPointF(50, 64),
               [(a, 18, 5.4) for a in (200, 223, 246, 270, 294, 317, 340)])


def _body():
    body = QPainterPath()
    body.moveTo(37, 58)
    body.cubicTo(34, 78, 32, 98, 31, 120)
    body.lineTo(69, 120)
    body.cubicTo(68, 98, 66, 78, 63, 58)
    body.closeSubpath()
    return body


def _neck():
    neck = QPainterPath()
    neck.moveTo(41, 40)
    neck.lineTo(53, 40)
    neck.lineTo(54, 60)
    neck.lineTo(42, 60)
    neck.closeSubpath()
    return neck


def _head():
    """Đầu hói nhìn nghiêng, quay sang trái, mũi khoằm sắc như mỏ chim."""
    head = QPainterPath()
    head.moveTo(56, 26)
    head.cubicTo(55, 17, 43, 15, 37, 21)      # vòm sọ hói, thấp và hơi bẹt
    head.cubicTo(35, 23, 33, 27, 32, 30)      # trán dốc mạnh ra trước
    head.lineTo(25, 35)                       # sống mũi dài và mảnh
    head.lineTo(30, 38)                       # đầu mũi quặp xuống, sắc
    head.lineTo(34, 37)                       # cánh mũi thu về
    head.cubicTo(32, 40, 33, 42, 35, 43)      # nhân trung, môi mỏng
    head.cubicTo(36, 45, 39, 47, 42, 46)      # cằm lẹm, nhỏ
    head.cubicTo(48, 46, 54, 42, 56, 37)      # hàm chảy xệ về sau
    head.cubicTo(58, 33, 58, 29, 56, 26)      # gáy khép lại
    return head


def draw_vulture(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước."""
    # h nhỏ hơn 120: hình phóng to hơn một chút, phần thân tràn khỏi mép dưới
    with design(p, rect, h=112):
        wings, ruff = _wings(), _ruff()
        wash = QLinearGradient(0, 12, 0, 60)
        wash.setColorAt(0.0, PAPER_HI)
        wash.setColorAt(1.0, QColor("#C9BCA0"))

        # cổ vẽ trước để vòng lông trùm lên, chỉ hở đúng một khúc
        p.setBrush(wash)
        p.setPen(QPen(INK, 1.3))
        p.drawPath(_neck())

        misprint(p, wings.united(ruff).united(_body()))

        # gân lông: nét sáng chạy dọc từng chiếc cánh cho đỡ bết mực
        vein = QColor(PAPER_HI)
        vein.setAlpha(52)
        p.setPen(QPen(vein, 0.9))
        p.setClipPath(wings)
        mirror_root = QPointF(100 - WING_ROOT.x(), WING_ROOT.y())
        for angle, length, _ in WING:
            a = math.radians(angle)
            for root, sign in ((WING_ROOT, 1), (mirror_root, -1)):
                p.drawLine(
                    QPointF(root.x() + sign * math.cos(a) * 9,
                            root.y() + math.sin(a) * 9),
                    QPointF(root.x() + sign * math.cos(a) * (length - 5),
                            root.y() + math.sin(a) * (length - 5)))
        p.setClipping(False)

        # viền sáng của vòng lông cổ, để nó tách khỏi đôi cánh phía sau
        edge = QColor(PAPER_HI)
        edge.setAlpha(85)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(edge, 1.0))
        p.drawPath(ruff)

        # bộ đai bay vắt chéo ngực — thứ làm nên toàn bộ nhân vật này
        strap = QColor(PAPER_HI)
        strap.setAlpha(70)
        p.setPen(QPen(strap, 1.7))
        p.setClipPath(_body())
        p.drawLine(QPointF(38, 68), QPointF(54, 96))
        p.drawLine(QPointF(62, 68), QPointF(46, 96))
        p.drawLine(QPointF(33, 98), QPointF(67, 98))
        p.setClipping(False)

        # đầu: mảng sáng nổi hẳn lên giữa đám lông đen
        p.setBrush(wash)
        p.setPen(QPen(INK, 1.5))
        p.drawPath(_head())

        # mắt trũng dưới chân mày nặng
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(INK)
        p.drawEllipse(QPointF(37, 28.5), 2.0, 1.5)
        p.setPen(QPen(INK, 1.5))
        p.drawLine(QPointF(32.5, 25.6), QPointF(41, 24.8))

        # vành tai — chi tiết khiến cái đầu thôi giống quả trứng
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(INK, 1.2))
        ear = QPainterPath()
        ear.moveTo(44.5, 27.5)
        ear.cubicTo(49, 26, 51.5, 30, 50, 33.5)
        ear.cubicTo(49, 35.5, 46.5, 36, 44.8, 34.8)
        p.drawPath(ear)
        p.setPen(QPen(INK, 0.9))
        p.drawLine(QPointF(46.6, 30), QPointF(47.6, 32.6))

        # nếp nhăn của tuổi tác
        wrinkle = QColor(INK_SOFT)
        wrinkle.setAlpha(155)
        p.setPen(QPen(wrinkle, 0.8))
        p.drawLine(QPointF(34, 32.5), QPointF(38.5, 33.8))   # rãnh má hóp
        p.drawLine(QPointF(40, 38), QPointF(45, 40))         # nếp hàm
        p.drawLine(QPointF(52, 28), QPointF(54.5, 30))       # nếp thái dương

        marks(p)


# ═══════════════════════════════════════════════════════════════ hồ sơ
PROFILE = Profile(
    name="Vulture",
    vi_name="Kền Kền",
    real_name="Adrian Toomes",

    tagline="Một kỹ sư điện tử đã có tuổi, bị bạn làm ăn lừa sạch, đáp trả "
            "bằng cách tự chế bộ cánh rồi bay lên trời đi cướp.",

    summary=(
        "Adrian Toomes xuất hiện ở The Amazing Spider-Man #2 (05/1963), chỉ "
        "một số báo sau Chameleon. Ông ta là kỹ sư điện tử đã luống tuổi, tự "
        "tay chế ra bộ đai bay chạy bằng từ trường — thứ vừa cho ông ta bay "
        "lượn, vừa bồi cho cơ thể một sức mạnh mà người ở tuổi ấy không thể có.",

        "Động cơ của Toomes bắt đầu từ chuyện bị phản bội: người bạn làm ăn "
        "rút ruột công ty rồi hất ông ta ra ngoài. Thay vì kiện tụng, ông ta "
        "mặc bộ đồ xanh lông vũ vào và biến bầu trời New York thành sân nhà. "
        "Đây cũng là kẻ đầu tiên dạy cho Peter Parker rằng đánh nhau trên "
        "không khác hẳn đánh nhau dưới đất.",

        "Toomes là một trong sáu cái tên sáng lập Sinister Six (ASM Annual #1, "
        "1964). Sức hút của nhân vật nằm ở chỗ nghịch lý: một ông lão gầy gò, "
        "đầu hói, nhưng lì lợm và tàn nhẫn vào loại bậc nhất trong danh sách "
        "kẻ thù của Spider-Man — có giai đoạn ông ta còn hút sinh lực người "
        "khác để tạm giành lại tuổi trẻ.",
    ),

    powers=(
        "Bộ đai bay điện từ tự chế: bay nhanh, lượn êm, bẻ lái gấp",
        "Bộ đai bồi thêm sức mạnh và sức bền, vượt xa tuổi thật",
        "Lối đánh bổ nhào từ trên cao, kiểu chim săn mồi",
        "Đầu óc kỹ sư: tự thiết kế, tự sửa, tự nâng cấp trang bị",
        "Không có siêu năng lực bẩm sinh — tất cả nằm ở bộ cánh",
    ),

    facts=(
        ("Tên thật", "Adrian Toomes"),
        ("Xuất hiện đầu", "ASM #2  ·  05/1963"),
        ("Tác giả", "Stan Lee & Steve Ditko"),
        ("Nghề cũ", "Kỹ sư điện tử"),
        ("Băng nhóm", "Sinister Six — thành viên sáng lập"),
        ("Trên màn ảnh", "Michael Keaton, Homecoming (2017)"),
    ),

    blurb="Ác nhân thứ hai của Spider-Man, và là kẻ đầu tiên buộc cậu nhóc "
          "phải ngước lên trời mà đánh.",

    art=draw_vulture,
    caption="Chân dung dựng lại bằng code",

    # Bấm nút tiến hoá để mở dạng Absolute — bộ da và cú chuyển cảnh riêng.
    evolution=ABSOLUTE,
    evolve_label="Evolve",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Vulture_(Marvel_Comics)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Adrian_Toomes_(Earth-616)"),
    ),
)
