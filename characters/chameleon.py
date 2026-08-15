"""
Chameleon — Dmitri Smerdyakov.

Mẫu để chép cho các nhân vật sau. Chỉ cần một biến `PROFILE`.
Chân dung ở đây vẽ bằng code (hàm `art`) vì mặt nạ trắng trơn chính là đặc
điểm nhận dạng của nhân vật. Muốn dùng ảnh thật: thả file vào
assets/characters/ rồi điền `image="chameleon.jpg"` — ảnh sẽ được ưu tiên.
"""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainterPath, QPen

from theme import BLUE, INK, PAPER_HI, RED

from .art import design, marks, misprint
from .chameleon_absolute import ABSOLUTE
from .profile import Profile


# ═══════════════════════════════════════════════════ chân dung vẽ bằng code
def _figure():
    """Bóng người trong khung 100×120: mũ phớt, cổ áo dựng, vai."""
    path = QPainterPath()

    # thân và vai
    path.moveTo(4, 120)
    path.cubicTo(10, 96, 20, 86, 34, 81)
    path.lineTo(50, 88)
    path.lineTo(66, 81)
    path.cubicTo(80, 86, 90, 96, 96, 120)
    path.closeSubpath()

    # cổ
    neck = QPainterPath()
    neck.addRect(43, 58, 14, 26)
    path = path.united(neck)

    # cổ áo măng tô dựng đứng, hai vạt ôm lấy hàm
    for side in (-1, 1):
        lapel = QPainterPath()
        lapel.moveTo(50 + side * 3, 92)
        lapel.lineTo(50 + side * 8, 62)
        lapel.lineTo(50 + side * 20, 72)
        lapel.lineTo(50 + side * 17, 95)
        lapel.closeSubpath()
        path = path.united(lapel)

    # vành mũ
    brim = QPainterPath()
    brim.addEllipse(QPointF(50, 27), 33, 7.4)
    path = path.united(brim)

    # chỏm mũ, đỉnh hơi lõm
    crown = QPainterPath()
    crown.moveTo(31, 28)
    crown.cubicTo(30, 12, 36, 6, 42, 6)
    crown.cubicTo(46, 6, 47, 10, 50, 10)
    crown.cubicTo(53, 10, 54, 6, 58, 6)
    crown.cubicTo(64, 6, 70, 12, 69, 28)
    crown.closeSubpath()
    return path.united(crown)


def _face():
    face = QPainterPath()
    face.addEllipse(QPointF(50, 45), 18.5, 22.5)
    return face


def draw_chameleon(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước."""
    with design(p, rect):
        face = _face()

        # bóng đen: mũ, cổ áo, vai — kèm hai lớp mực in lệch trục
        misprint(p, _figure())

        # gương mặt: một mảng trắng, không mắt, không mũi, không miệng
        wash = QLinearGradient(0, 22, 0, 68)
        wash.setColorAt(0.0, PAPER_HI)
        wash.setColorAt(1.0, QColor("#D9CEB4"))
        p.setBrush(wash)
        p.setPen(QPen(INK, 1.6))
        p.drawPath(face)

        # dấu vết của một khuôn mặt đang chực nổi lên rồi lại chìm xuống
        p.setPen(Qt.PenStyle.NoPen)
        for color, dx, alpha in ((RED, 0.9, 34), (BLUE, -0.9, 30)):
            tint = QColor(color)
            tint.setAlpha(alpha)
            p.setBrush(tint)
            for ex in (42.5, 57.5):
                p.drawEllipse(QPointF(ex + dx, 43), 3.6, 2.3)
            p.drawEllipse(QPointF(50 + dx, 56.5), 6.2, 1.5)

        # bóng đổ hắt lên má, giữ cho mảng trắng không bị phẳng
        shade = QColor(INK)
        shade.setAlpha(26)
        p.setBrush(shade)
        p.setClipPath(face)
        p.drawEllipse(QPointF(72, 45), 20, 24)
        p.setClipping(False)

        marks(p)


# ═══════════════════════════════════════════════════════════════ hồ sơ
PROFILE = Profile(
    name="Chameleon",
    vi_name="Tắc Kè Hoa",
    real_name="Dmitri Nikolayevich Smerdyakov",

    tagline="Ác nhân đầu tiên Spider-Man từng đối mặt — và là kẻ duy nhất "
            "không cần đến một siêu năng lực nào để làm điều đó.",

    summary=(
        "Dmitri Smerdyakov bước ra từ The Amazing Spider-Man #1 (03/1963), "
        "ác nhân mở màn cho toàn bộ danh sách này. Stan Lee và Steve Ditko "
        "không cho hắn tia sét, cũng chẳng cho bộ giáp: toàn bộ sức mạnh của "
        "Chameleon nằm ở chỗ hắn có thể là bất kỳ ai.",

        "Lần chạm trán đầu tiên, hắn giả dạng chính Spider-Man để đánh cắp "
        "tài liệu quốc phòng rồi bán cho điệp viên nước ngoài. Người Nhện mới "
        "vào nghề bị đổ tội và bị cảnh sát săn lùng, phải tự tay lột mặt kẻ đã "
        "mượn khuôn mặt mình. Mô-típ anh hùng bị nghi oan — thứ đi theo "
        "Spider-Man suốt sáu thập kỷ sau đó — bắt đầu từ đây.",

        "Về sau nhân vật được nâng cấp: một loại huyết thanh cho phép nắn lại "
        "cấu trúc gương mặt, và khi không đóng vai ai cả, thứ còn lại là chiếc "
        "mặt nạ trắng trơn không mắt mũi đã thành hình ảnh quen thuộc của hắn. "
        "Trong mạch truyện Lifetheft (ASM #386–388, 1994), hắn dựng lên hai "
        "người máy đóng vai cha mẹ đã khuất của Peter Parker — đòn đánh không "
        "nhắm vào Spider-Man mà nhắm thẳng vào Peter.",
    ),

    powers=(
        "Bậc thầy hoá trang: mặt nạ, phục trang, chất tạo hình da",
        "Huyết thanh nắn lại cấu trúc gương mặt (giai đoạn sau)",
        "Nhại giọng nói, dáng đi và thói quen của người bị giả dạng",
        "Đồ nghề điệp viên: giấy tờ giả, thiết bị nguỵ trang, tin tình báo",
        "Không có sức mạnh siêu phàm — thắng bằng thông tin, không bằng cơ bắp",
    ),

    facts=(
        ("Tên thật", "Dmitri N. Smerdyakov"),
        ("Xuất hiện đầu", "ASM #1  ·  03/1963"),
        ("Tác giả", "Stan Lee & Steve Ditko"),
        ("Quốc tịch", "Nga"),
        ("Quan hệ", "Anh em cùng cha khác mẹ với Kraven"),
        ("Vị trí", "Ác nhân đầu tiên của dòng thời gian"),
    ),

    blurb="Mọi ác nhân khác trong danh sách này đều để lại một gương mặt để "
          "nhớ. Chameleon mở màn tất cả bằng cách không có gương mặt nào.",

    art=draw_chameleon,
    caption="Chân dung dựng lại bằng code",

    # Bấm nút tiến hoá trên tấm hồ sơ để mở dạng Absolute.
    evolution=ABSOLUTE,
    evolve_label="Evolve",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Chameleon_(character)"),
        ("Marvel Fandom", "https://marvel.fandom.com/wiki/Dmitri_Smerdyakov_(Earth-616)"),
    ),
)
