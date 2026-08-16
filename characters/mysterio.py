"""
Mysterio — Quentin Beck.

Chín chân dung trước đều cho người xem thấy một thứ để nhìn vào: cái mặt nạ
trắng của Chameleon, mặt nạ sao của Electro, hàm bò sát của Lizard. Cái này
thì cho một quả cầu thuỷ tinh — và bên trong quả cầu không có gì cả, chỉ có
sương. Không phải giấu mặt như Chameleon, mà là **không có mặt để giấu**.

Ba lớp, dựng đúng theo cách một hiệu ứng sân khấu được dựng:
    · hai bóng ma hai bên — bản chiếu lệch của chính hắn, chỉ có đường viền
    · bóng thật ở giữa, in kiểu lệch trục (`misprint`) nên đã sẵn chồng ba màu
    · quả cầu úp lên trên, thứ duy nhất bắt sáng trong cả khung

Người xem phải tự chọn cái nào là hắn — và cả ba đều không có mặt. Đó là
toàn bộ trò của Quentin Beck, gói vào một khung 100×120.
"""

from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QPainter, QPainterPath, QPen,
                           QRadialGradient)

from theme import BLUE, INK, INK_SOFT, PAPER_HI, RED

from .art import H, W, Rolls, design, marks, misprint
from .profile import Profile

DOME = QPointF(50, 38)           # tâm quả cầu
DOME_R = 19.5                    # bán kính quả cầu
GLASS = QColor("#EFE7D4")        # thuỷ tinh bắt sáng
FOG = QColor("#B9AE95")          # sương bên trong, tối hơn giấy một bậc
FOGLINE = 88.0                   # từ đây trở xuống, khói bắt đầu ăn vào vai


# ═══════════════════════════════════════════════════ hình khối
def _figure():
    """Bán thân: vai xoè, cộng cổ áo dựng cao vút hai bên quả cầu.

    Cố ý dựng theo đúng lối của `chameleon.py` — cũng là một bức bán thân
    không có mặt. Hai hồ sơ ấy nói cùng một chuyện theo hai cách, nên để
    chúng vần với nhau về bố cục.
    """
    body = QPainterPath()
    body.moveTo(33, 57)
    body.cubicTo(25, 68, 14, 84, 9, 112)
    body.lineTo(91, 112)
    body.cubicTo(86, 84, 75, 68, 67, 57)
    body.closeSubpath()

    # cổ áo: hai vạt vót nhọn dựng cao ngang đỉnh cầu, xoè hẳn ra ngoài vai
    for side in (-1, 1):
        wing = QPainterPath()
        wing.moveTo(50 + side * 11, 62)
        wing.lineTo(50 + side * 19, 27)
        wing.lineTo(50 + side * 29, 47)
        wing.lineTo(50 + side * 24, 72)
        wing.closeSubpath()
        body = body.united(wing)
    return body


_FIGURE = _figure()

_DOME = QPainterPath()
_DOME.addEllipse(DOME, DOME_R, DOME_R)


# ═══════════════════════════════════════════════════════════════ các lớp
def _ghosts(p):
    """Hai bản chiếu lệch sang hai bên: chỉ đường viền quả cầu và cổ áo.

    Cố ý để rất mờ và rất mảnh. Vẽ đậm hơn thì chúng tranh mất chỗ của bóng
    thật, mà trò của Beck là thứ người ta chỉ nhận ra khi đã nhìn kỹ lần hai.
    """
    for dx, color in ((-13, BLUE), (13, RED)):
        tint = QColor(color)
        tint.setAlpha(48)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(tint, 0.55))
        p.drawPath(_DOME.translated(dx, 2))
        p.drawPath(_FIGURE.translated(dx, 2))


def _stagelight(p):
    """Quầng đèn sân khấu sau lưng, mép mềm — Beck tự kê đèn cho mình."""
    halo = QRadialGradient(QPointF(50, 40), 62)
    warm = QColor(PAPER_HI)
    # nhiều chặng và biên độ thấp: ba chặng thì dải chuyển bị vằn thành vòng
    for stop, alpha in ((0.0, 58), (0.22, 46), (0.44, 32), (0.66, 18),
                        (0.84, 7), (1.0, 0)):
        tone = QColor(warm)
        tone.setAlpha(alpha)
        halo.setColorAt(stop, tone)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(halo)
    p.drawRect(QRectF(-6, -6, 112, 132))


def _smoke(p):
    """Khói dâng lên ăn mất chân bức chân dung.

    Ít thuỳ nhưng to và chồng nhau nhiều, để chúng dính thành một khối; vẽ
    nhiều thuỳ nhỏ thì ra một đám sỏi. Khói của Mysterio là vũ khí chính chứ
    không phải hiệu ứng kèm theo, nên nó được quyền nuốt hẳn chân bức hình.

    Và khói vẽ **sáng** chứ không vẽ tối: trên nền giấy nhạt, mảng tối tròn
    nào cũng ra hòn sỏi. Khói phải là thứ ăn mòn bóng đen từ dưới lên, cộng
    một nét viền mảnh trên đỉnh mỗi thuỳ kiểu nét mực truyện tranh.
    """
    r = Rolls(13061964)          # ASM #13, 06/1964
    lobes = []
    for _ in range(15):
        cx = r(2, 98)
        cy = r(FOGLINE + 2, 124)
        rx = r(14, 26)
        lobes.append((cx, cy, rx, rx * r(0.40, 0.58)))

    p.setPen(Qt.PenStyle.NoPen)
    for cx, cy, rx, ry in lobes:
        deep = (cy - FOGLINE) / (124 - FOGLINE)      # càng thấp càng đặc
        mass = QColor(PAPER_HI)
        mass.setAlpha(int(120 + 105 * deep))
        p.setBrush(mass)
        p.drawEllipse(QPointF(cx, cy), rx, ry)

    # nét viền chỉ chạy trên đỉnh mỗi thuỳ, nên khói có khối mà không thành ô
    p.setBrush(Qt.BrushStyle.NoBrush)
    edge = QColor(INK)
    edge.setAlpha(64)
    p.setPen(QPen(edge, 0.6))
    for cx, cy, rx, ry in lobes:
        box = QRectF(cx - rx, cy - ry, rx * 2, ry * 2)
        p.drawArc(box, 20 * 16, 140 * 16)

    # vài sợi mỏng liếm lên mép khói. Để chúng dẹt và bám sát mặt khói —
    # thả cao lên áo thì không ra sợi khói, chỉ ra mấy vết xám lơ lửng.
    p.setPen(Qt.PenStyle.NoPen)
    for _ in range(4):
        x = r(14, 86)
        top = r(FOGLINE - 5, FOGLINE + 3)
        wisp = QColor(PAPER_HI)
        wisp.setAlpha(96)
        p.setBrush(wisp)
        p.drawEllipse(QPointF(x, top), r(7.0, 12.0), r(1.2, 2.0))


def _fog_in_dome(p):
    """Sương cuộn bên trong quả cầu — thứ thay cho khuôn mặt.

    Cắt theo đúng hình cầu rồi mới vẽ, nên sương không tràn ra ngoài kính.
    """
    p.save()
    p.setClipPath(_DOME)
    p.setPen(Qt.PenStyle.NoPen)

    wash = QRadialGradient(QPointF(DOME.x() - 5, DOME.y() - 6), DOME_R * 1.5)
    wash.setColorAt(0.0, GLASS)
    wash.setColorAt(0.45, QColor("#D5CAB1"))
    wash.setColorAt(1.0, FOG)
    p.setBrush(wash)
    p.drawPath(_DOME)

    r = Rolls(19640613)
    for _ in range(9):
        cx = DOME.x() + r(-13, 13)
        cy = DOME.y() + r(-11, 13)
        rx = r(4.5, 9.5)
        tone = QColor(INK_SOFT)
        tone.setAlpha(int(r(18, 44)))
        p.setBrush(tone)
        p.drawEllipse(QPointF(cx, cy), rx, rx * r(0.45, 0.7))
    p.restore()


def _glass(p):
    """Kính: vành cầu, một vệt loá chéo, và cái đế xiết quanh chân cầu."""
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(INK, 1.5))
    p.drawPath(_DOME)

    # vệt loá góc trên trái — thứ duy nhất nói cho ta biết đây là thuỷ tinh
    p.save()
    p.setClipPath(_DOME)
    p.setPen(Qt.PenStyle.NoPen)
    flare = QPainterPath()
    flare.moveTo(DOME.x() - 13.5, DOME.y() - 5.5)
    flare.quadTo(DOME.x() - 11, DOME.y() - 15, DOME.x() - 2, DOME.y() - 16.5)
    flare.quadTo(DOME.x() - 8.5, DOME.y() - 12, DOME.x() - 10.5, DOME.y() - 4)
    flare.closeSubpath()
    p.setBrush(QColor("#FBF6E9"))
    p.drawPath(flare)
    p.restore()

    # đế: vòng kim loại chỗ cầu cắm vào cổ áo
    ring = QPainterPath()
    ring.moveTo(DOME.x() - 13, DOME.y() + 13.5)
    ring.quadTo(DOME.x(), DOME.y() + 22.5, DOME.x() + 13, DOME.y() + 13.5)
    ring.quadTo(DOME.x(), DOME.y() + 18.0, DOME.x() - 13, DOME.y() + 13.5)
    ring.closeSubpath()
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(INK)
    p.drawPath(ring)


def _drape(p):
    """Nếp gấp áo choàng: vài đường cong xuôi theo dáng rủ, không phải lưới.

    Kẻ ô vuông lên đây thì mảng áo hoá ra một mặt đường; mấy nếp cong thì
    mới ra vải.
    """
    p.save()
    p.setClipPath(_FIGURE)
    faint = QColor(INK)
    faint.setAlpha(58)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(faint, 0.6))
    for k in (-3, -2, -1, 1, 2, 3):
        fold = QPainterPath()
        fold.moveTo(50 + k * 4.5, 60)
        fold.quadTo(50 + k * 8.5, 86, 50 + k * 12, 112)
        p.drawPath(fold)
    p.restore()


def _paint(p):
    """Toàn bộ bảy lớp, vẽ trong hệ toạ độ 100×120."""
    _stagelight(p)
    _ghosts(p)
    misprint(p, _FIGURE)
    _drape(p)
    _fog_in_dome(p)
    _glass(p)
    _smoke(p)
    marks(p)


@lru_cache(maxsize=8)
def _still(w, h):
    """Dựng sẵn cả tấm vào một ảnh đúng cỡ thật rồi dán.

    Chân dung này đứng yên nhưng nặng — gradient, vùng cắt và hơn ba chục
    hình bầu dục — mất 26 ms mỗi lần vẽ thẳng. Khung hồ sơ thì vẽ lại tấm
    chân dung hơn hai chục lần trong lúc mở, nên `electro.py` đã đi trước
    một nước; đây làm y như vậy, xuống còn dưới một mili giây.
    """
    img = QImage(max(1, w), max(1, h), QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    q = QPainter(img)
    q.setRenderHint(QPainter.RenderHint.Antialiasing)
    q.scale(w / W, h / H)
    _paint(q)
    q.end()
    return img


def draw_mysterio(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước."""
    scale = min(rect.width() / W, rect.height() / H)
    still = _still(max(1, round(W * scale)), max(1, round(H * scale)))
    with design(p, rect):
        p.drawImage(QRectF(0, 0, W, H), still)


# ═══════════════════════════════════════════════════════════════ hồ sơ
PROFILE = Profile(
    name="Mysterio",
    vi_name="Bậc Thầy Ảo Ảnh",
    real_name="Quentin Beck",

    tagline="Một chuyên gia hiệu ứng đặc biệt của Hollywood, giỏi nghề nhưng "
            "không ai nhớ tên. Hắn quyết định đổi nghề — và lần này thì cả "
            "thành phố nhớ.",

    summary=(
        "Quentin Beck làm hiệu ứng đặc biệt và đóng thế cho các hãng phim. "
        "Hắn dựng được quái vật, dựng được cháy nổ, dựng được cả những cú ngã "
        "từ nóc nhà mà khán giả tưởng là thật — nhưng tên hắn chỉ chạy ở hàng "
        "cuối bảng chữ chạy. Kết luận hắn rút ra rất gọn: cùng bộ kỹ năng ấy, "
        "làm tội phạm thì được chú ý hơn nhiều.",

        "The Amazing Spider-Man #13 (06/1964) mở màn bằng việc Spider-Man đi "
        "cướp — hoặc trông y như vậy. Có nhân chứng, có ảnh chụp, có cả một "
        "kẻ mặc đồ Người Nhện leo tường giữa ban ngày. Rồi Mysterio xuất hiện, "
        "tự nhận là người duy nhất đủ sức bắt tên tội phạm ấy, và cả New York "
        "vỗ tay.",

        "Đòn hiểm của số báo không nhắm vào cơ thể Peter mà nhắm vào trí nhớ "
        "của cậu. Bằng chứng chồng lên bằng chứng, tới mức Peter bắt đầu tự "
        "hỏi liệu mình có làm những việc đó trong lúc không tỉnh táo hay "
        "không. Chameleon từng mượn khuôn mặt cậu; Mysterio đi xa hơn một "
        "bước — hắn khiến cậu nghi ngờ chính mình.",

        "Cách gỡ lại rất đúng chất một phóng viên ảnh: Peter mang theo máy ghi "
        "âm, dụ Beck khoe khoang, rồi thu trọn lời thú nhận. Không có cú đấm "
        "nào phá được ảo ảnh, nhưng một cuộn băng thì có. Beck sau đó là một "
        "trong sáu cái tên sáng lập Sinister Six, và chiếc mũ cầu thuỷ tinh "
        "trở thành một trong những hình bóng dễ nhận ra nhất của cả danh sách "
        "này.",
    ),

    powers=(
        "Không có một siêu năng lực nào — tất cả là nghề sân khấu",
        "Hologram và ảnh chiếu: dựng ra quái vật, người khổng lồ, bản sao",
        "Khói dày chặn tầm nhìn, và làm nhiễu cả giác quan nhện",
        "Hoá chất gây ảo giác, khí mê, chất ăn mòn tơ nhện",
        "Cơ khí và robot điều khiển từ xa, dựng như đạo cụ trường quay",
        "Võ thuật và nhào lộn từ những năm làm diễn viên đóng thế",
    ),

    facts=(
        ("Tên thật", "Quentin Beck"),
        ("Xuất hiện đầu", "ASM #13  ·  06/1964"),
        ("Tác giả", "Stan Lee & Steve Ditko"),
        ("Nghề cũ", "Hiệu ứng đặc biệt & đóng thế"),
        ("Băng nhóm", "Sinister Six — thành viên sáng lập"),
        ("Trên màn ảnh", "Jake Gyllenhaal — Far From Home"),
    ),

    blurb="Beck đổi nghề vì muốn có người nhớ mặt mình. Rồi hắn tự úp lên đầu "
          "một quả cầu mà không ai nhìn xuyên qua được — và trở nên nổi tiếng "
          "đúng theo cái cách hắn không hề tính tới.",

    art=draw_mysterio,
    caption="Chân dung dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Mysterio"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Quentin_Beck_(Earth-616)"),
    ),
)
