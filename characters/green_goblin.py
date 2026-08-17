"""
Green Goblin — Norman Osborn.

Mười chân dung trước đều là hình chiếu thẳng: nhân vật đứng trước mặt người
xem, phẳng, cùng một mặt phẳng. Cái này bẻ hai chỗ cùng lúc:

    · **Góc nhìn từ dưới lên.** Người xem nằm dưới đất mà ngước lên. Hắn ở
      trên cao, nhỏ; quả bom hắn vừa thả thì to gần kín nửa dưới khung vì nó
      đang rơi *về phía ta*. Chênh lệch kích thước ấy là cả câu chuyện: đây
      là hồ sơ duy nhất mà người xem đứng trong khung chứ không đứng ngoài.

    · **Nguồn sáng nằm trong vật.** Chín hồ sơ kia sáng từ ngoài rọi vào,
      Electro thì tự phát sáng cả người. Ở đây ánh sáng bị nhốt bên trong
      quả bom và chỉ thoát ra qua mấy lỗ khoét hình mặt cười — nên thứ sáng
      nhất tờ giấy lại chính là cái sắp giết ta.

Bảng màu vẫn là pulp bốn màu, không thêm màu nào: mực đen cho bóng, đỏ và
lam cho hai lớp in lệch, và vàng — thứ ánh sáng chui qua lỗ.
"""

import math
from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QPainter, QPainterPath, QPen,
                           QRadialGradient)

from theme import INK, PAPER_HI

from .art import H, W, Rolls, design, marks, mirrored, misprint
from .green_goblin_absolute import ABSOLUTE
from .profile import Profile

BOMB = QPointF(50, 86)           # tâm quả bom, nằm thấp và gần người xem
BOMB_R = 23.0
GLOW = QColor("#FFE9A8")         # ánh sáng chui qua lỗ khoét
EMBER = QColor("#F6C445")        # lõi sáng, đậm hơn một bậc


# ═══════════════════════════════════════════════════ hình khối
def _glider():
    """Ván lượn nhìn từ dưới: hai cánh dơi vuốt ngược, mũi chúc về phía ta.

    Vẽ nửa trái rồi lật, nên hai cánh cân nhau tuyệt đối — một cỗ máy thì
    nên cân, khác với đôi cánh lông của Vulture vốn cố ý so le.
    """
    half = QPainterPath()
    half.moveTo(50, 20)
    half.cubicTo(42, 20.5, 30, 23, 15, 29)     # mép trước vuốt ra ngoài
    half.lineTo(22, 33.5)                       # khấc ngoài
    half.cubicTo(28, 30, 31, 29.5, 35, 30)      # vỏ sò thứ nhất
    half.lineTo(33, 34)                         # khấc trong
    half.cubicTo(39, 30, 45, 29, 50, 29)        # về giữa
    half.closeSubpath()
    both = QPainterPath(half)
    both.addPath(mirrored(half))
    return both


def _rider():
    """Hắn ngồi xổm trên ván: đầu hai tai nhọn, vai gù, tay chống về trước."""
    body = QPainterPath()
    body.moveTo(45.5, 16)
    body.cubicTo(44, 11, 46.5, 7, 50, 7)
    body.cubicTo(53.5, 7, 56, 11, 54.5, 16)
    body.closeSubpath()

    for side in (-1, 1):                       # hai tai nhọn vểnh ngược
        ear = QPainterPath()
        ear.moveTo(50 + side * 3.4, 9.0)
        ear.lineTo(50 + side * 8.6, 2.0)
        ear.lineTo(50 + side * 5.4, 11.5)
        ear.closeSubpath()
        body = body.united(ear)

    # vai gù và hai tay chống về trước — hẹp hơn cánh nhiều, để cái bóng đọc
    # ra hai khối rời chứ không dính thành một vành mũ
    shoulders = QPainterPath()
    shoulders.moveTo(43.5, 17)
    shoulders.cubicTo(45, 14, 55, 14, 56.5, 17)
    shoulders.cubicTo(58.5, 21, 57, 25, 55, 26)
    shoulders.lineTo(45, 26)
    shoulders.cubicTo(43, 25, 41.5, 21, 43.5, 17)
    shoulders.closeSubpath()
    return body.united(shoulders)


_GLIDER = _glider()
_RIDER = _rider()
_ALOFT = _GLIDER.united(_RIDER)

_BOMB = QPainterPath()
_BOMB.addEllipse(BOMB, BOMB_R, BOMB_R)


def _face():
    """Mặt cười khoét trên vỏ bom: hai mắt tam giác và một cái miệng răng cưa.

    Đây là *lỗ thủng*, không phải nét vẽ — nên phần sáng chính là phần bị lấy
    đi. Vẽ nó như một hình đặc rồi tô sáng, ánh sáng sau lưng lo phần còn lại.
    """
    cut = QPainterPath()
    for side in (-1, 1):
        eye = QPainterPath()
        eye.moveTo(BOMB.x() + side * 4.5, BOMB.y() - 9.5)
        eye.lineTo(BOMB.x() + side * 13.0, BOMB.y() - 5.0)
        eye.lineTo(BOMB.x() + side * 5.5, BOMB.y() - 2.5)
        eye.closeSubpath()
        cut = cut.united(eye)

    # Sáu răng, mỗi răng rộng 4,5 — vừa đúng 27 đơn vị từ -13,5 tới +13,5.
    # Lấy bảy răng thì hàng răng chạy quá mép rồi bị kéo ngược về, để lại
    # một cái gai thừa chìa ra khỏi vành bom.
    mouth = QPainterPath()
    mouth.moveTo(BOMB.x() - 13.5, BOMB.y() + 4.0)
    for i in range(6):
        x = BOMB.x() - 13.5 + i * 4.5
        mouth.lineTo(x + 2.2, BOMB.y() + (9.5 if i % 2 == 0 else 5.5))
        mouth.lineTo(x + 4.5, BOMB.y() + 4.0)
    mouth.lineTo(BOMB.x() + 13.5, BOMB.y() + 11.5)
    mouth.lineTo(BOMB.x() - 13.5, BOMB.y() + 11.5)
    mouth.closeSubpath()
    return cut.united(mouth)


_FACE = _face()


# ═══════════════════════════════════════════════════════════════ các lớp
def _rays(p):
    """Chùm sáng phun ra từ mấy lỗ khoét, toả về phía người xem.

    Vẽ trước quả bom nên chúng nằm dưới; chỉ thấy phần loe ra khỏi vành bom,
    đúng như ánh sáng lọt qua khe.
    """
    # Góc tính theo hệ toạ độ màn hình: y tăng xuống dưới, nên góc dương là
    # hướng xuống. Cả năm chùm phải trải kín nửa dưới — chọn toàn góc cùng
    # dấu cosin thì chúng dồn hết về một bên, và trông như lỗi vẽ.
    p.setPen(Qt.PenStyle.NoPen)
    for deg, spread, reach in ((22, 8, 44), (56, 7, 40), (90, 11, 34),
                               (124, 7, 40), (158, 8, 44)):
        a = math.radians(deg)
        half = math.radians(spread)
        wedge = QPainterPath()
        wedge.moveTo(BOMB)
        wedge.lineTo(BOMB.x() + math.cos(a - half) * reach,
                     BOMB.y() + math.sin(a - half) * reach)
        wedge.lineTo(BOMB.x() + math.cos(a + half) * reach,
                     BOMB.y() + math.sin(a + half) * reach)
        wedge.closeSubpath()
        tone = QColor(GLOW)
        tone.setAlpha(92)
        p.setBrush(tone)
        p.drawPath(wedge)


def _bomb_shell(p):
    """Vỏ bom: mảng đen kèm hai lớp mực lệch, cộng mấy múi bí khắc chìm."""
    misprint(p, _BOMB)
    p.save()
    p.setClipPath(_BOMB)
    rib = QColor(PAPER_HI)
    rib.setAlpha(30)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(rib, 0.7))
    for k in (-2, -1, 1, 2):
        seam = QPainterPath()
        seam.moveTo(BOMB.x() + k * 6.5, BOMB.y() - BOMB_R)
        seam.quadTo(BOMB.x() + k * 10.5, BOMB.y(),
                    BOMB.x() + k * 6.5, BOMB.y() + BOMB_R)
        p.drawPath(seam)
    p.restore()

    # cuống bí, chỗ ngòi cháy cắm vào
    stem = QPainterPath()
    stem.moveTo(BOMB.x() - 3.4, BOMB.y() - BOMB_R + 1.5)
    stem.lineTo(BOMB.x() - 1.8, BOMB.y() - BOMB_R - 5.5)
    stem.lineTo(BOMB.x() + 2.6, BOMB.y() - BOMB_R - 5.0)
    stem.lineTo(BOMB.x() + 3.4, BOMB.y() - BOMB_R + 1.5)
    stem.closeSubpath()
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(INK)
    p.drawPath(stem)


def _lit_face(p):
    """Ánh sáng thoát ra qua lỗ: lõi trắng vàng, viền loe, quầng hắt ra ngoài."""
    p.setPen(Qt.PenStyle.NoPen)

    bleed = QRadialGradient(BOMB, BOMB_R * 1.15)
    for stop, alpha in ((0.0, 74), (0.45, 40), (0.78, 14), (1.0, 0)):
        tone = QColor(EMBER)
        tone.setAlpha(alpha)
        bleed.setColorAt(stop, tone)
    p.setBrush(bleed)
    p.drawEllipse(BOMB, BOMB_R * 1.15, BOMB_R * 1.15)

    p.setBrush(QColor(EMBER))
    p.drawPath(_FACE)
    p.setBrush(QColor("#FFF6D8"))
    p.drawPath(_FACE.translated(-0.7, -0.7))


def _fuse(p):
    """Ngòi cháy: một vệt lửa kéo ngược lên, vì quả bom đang rơi xuống ta."""
    r = Rolls(14071964)          # ASM #14, 07/1964
    p.setPen(Qt.PenStyle.NoPen)
    top = BOMB.y() - BOMB_R - 5.0
    for i in range(11):
        u = i / 10.0
        y = top - u * 26
        x = BOMB.x() + math.sin(u * 5.2) * (2.0 + u * 5.5)
        rad = (3.4 - u * 2.4) * r(0.75, 1.25)
        tone = QColor(EMBER if i % 3 else GLOW)
        tone.setAlpha(int(180 * (1 - u) ** 1.3))
        p.setBrush(tone)
        p.drawEllipse(QPointF(x, y), rad, rad * 1.5)


def _speedlines(p):
    """Vệt trượt ngắn giữa ván lượn và quả bom — dấu vết của cú vừa thả.

    Vạch dài chạy suốt khung thì thành sợi dây, và quả bom hoá ra đang *treo*
    chứ không phải đang rơi. Nên chúng phải ngắn, chỉ nằm trong khoảng hở
    giữa hai khối, và mảnh dần về phía dưới.
    """
    p.setBrush(Qt.BrushStyle.NoBrush)
    for dx, y0, y1, alpha in ((-19, 38, 52, 34), (-9, 35, 56, 46),
                              (0, 34, 58, 52), (9, 35, 56, 46),
                              (19, 38, 52, 34)):
        faint = QColor(INK)
        faint.setAlpha(alpha)
        p.setPen(QPen(faint, 0.55))
        p.drawLine(QPointF(50 + dx * 0.55, y0), QPointF(50 + dx, y1))


def _paint(p):
    _speedlines(p)
    misprint(p, _ALOFT)
    _rays(p)
    _bomb_shell(p)
    _lit_face(p)
    _fuse(p)
    marks(p)


@lru_cache(maxsize=8)
def _still(w, h):
    """Dựng sẵn cả tấm rồi dán — cùng cách `electro.py` và `mysterio.py` làm."""
    img = QImage(max(1, w), max(1, h),
                 QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    q = QPainter(img)
    q.setRenderHint(QPainter.RenderHint.Antialiasing)
    q.scale(w / W, h / H)
    _paint(q)
    q.end()
    return img


def draw_green_goblin(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước."""
    scale = min(rect.width() / W, rect.height() / H)
    still = _still(max(1, round(W * scale)), max(1, round(H * scale)))
    with design(p, rect):
        p.drawImage(QRectF(0, 0, W, H), still)


# ═══════════════════════════════════════════════════════════════ hồ sơ
PROFILE = Profile(
    name="Green Goblin",
    vi_name="Yêu Tinh Xanh",
    real_name="Norman Osborn",

    tagline="Kẻ thù duy nhất không đánh vào Spider-Man. Hắn đánh vào những "
            "người đứng quanh Peter Parker — và hắn không trượt lần nào.",

    summary=(
        "The Amazing Spider-Man #14 (07/1964) cho ra mắt một gã mặc đồ yêu "
        "tinh cưỡi cây chổi bay, dụ Spider-Man sang Hollywood đóng phim rồi "
        "phục sẵn ở đó cùng băng Enforcers. Ở số đó hắn chưa có gì đặc biệt "
        "hơn những kẻ khác. Thứ khiến hắn thành nhân vật lớn là câu hỏi Stan "
        "Lee và Steve Ditko cố tình bỏ ngỏ suốt hai năm sau đó: dưới cái mặt "
        "nạ ấy là ai.",

        "Ditko muốn đó là một người hoàn toàn xa lạ — đúng như đời thật, kẻ "
        "gây hoạ cho ta có thể là người ta chưa từng gặp. Lee muốn đó phải là "
        "một người đã có mặt sẵn trong truyện. Bất đồng ấy là một trong những "
        "lý do Ditko rời Marvel, và người vẽ ra khoảnh khắc lột mặt nạ ở ASM "
        "#39 (08/1966) là John Romita Sr. Bên dưới là Norman Osborn: nhà công "
        "nghiệp, chủ Oscorp, và bố của Harry — bạn thân nhất của Peter.",

        "Sức mạnh của hắn đến từ một công thức thí nghiệm phát nổ ngay trên "
        "mặt hắn: khoẻ hơn người thường nhiều lần, nhanh hơn, lành vết thương "
        "nhanh hơn, và sắc sảo hơn hẳn cái đầu vốn đã thuộc hàng thiên tài. "
        "Kèm theo đó là chứng điên. Bộ trang bị thì đúng chất một ông trùm "
        "công nghiệp tự chế đồ chơi: ván lượn có lưỡi ở mũi, bom bí ngô, dơi "
        "dao, găng tay phóng điện, và khí gây ảo giác.",

        "Nhưng thứ khiến hắn đứng riêng một bậc không nằm trong danh sách vũ "
        "khí. Hắn biết Peter Parker là ai. Hắn biết Peter yêu quý những ai. "
        "Và ở ASM #121 (1973), hắn ném Gwen Stacy khỏi thành cầu — cô chết, "
        "hắn chết ngay số sau vì chính chiếc ván lượn của mình, còn truyện "
        "tranh Mỹ thì bước hẳn ra khỏi Thời đại Bạc và không quay lại nữa.",
    ),

    powers=(
        "Công thức Goblin: sức mạnh, tốc độ và khả năng lành vết thương",
        "Trí tuệ vốn đã là thiên tài, bị công thức mài sắc thêm — kèm chứng điên",
        "Ván lượn bay, điều khiển bằng giáp, có lưỡi cắt gắn ở mũi",
        "Bom bí ngô, dơi dao, khí ảo giác, găng tay phóng điện",
        "Tài sản và cả một tập đoàn đứng sau mỗi món đồ hắn dùng",
        "Sẵn sàng nhắm vào người thân của đối thủ — chỗ không ai khác dám đi",
    ),

    facts=(
        ("Tên thật", "Norman Osborn"),
        ("Xuất hiện đầu", "ASM #14  ·  07/1964"),
        ("Tác giả", "Stan Lee & Steve Ditko"),
        ("Lộ danh tính", "ASM #39  ·  08/1966"),
        ("Quan hệ", "Bố của Harry, bạn thân Peter"),
        ("Trên màn ảnh", "Willem Dafoe — 2002 và 2021"),
    ),

    blurb="Mọi ác nhân khác trong danh sách này đều thua vì đánh vào Spider-"
          "Man. Norman Osborn là kẻ duy nhất hiểu rằng bộ đồ ấy không phải chỗ "
          "yếu nhất — người mặc nó mới là, và cách hạ người mặc nó là lấy đi "
          "những người khiến anh ta còn muốn mặc.",

    evolution=ABSOLUTE,
    evolve_label="Evolve",

    art=draw_green_goblin,
    caption="Chân dung dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Green_Goblin"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Norman_Osborn_(Earth-616)"),
    ),
)
