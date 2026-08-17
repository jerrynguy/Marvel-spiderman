"""
Kraven the Hunter — Sergei Kravinoff.

Mười một chân dung trước đều đặt nhân vật thẳng trên nền giấy: một bóng mực,
một mặt giấy, hết. Cái này chèn thêm một tầng ở giữa và dùng lại đúng màu
mực cho tầng ngoài cùng lẫn tầng trong cùng:

    · **ngoài**: tán lá tô mực kín cả tờ
    · **giữa**: một khe hở rách, để lộ mặt giấy
    · **trong**: Kraven, lại là mực, đứng lọt trong khe ấy

Nên ta không nhìn thấy hắn — ta nhìn thấy *cái khe* mà hắn tình cờ đang đứng
sau. Đó là nghề của hắn: kẻ rình mồi chỉ hiện ra bằng đúng cỡ khoảng trống
mà tán lá chừa lại.

Một bản trước đi xa hơn: bỏ hẳn mực trên người hắn, để hắn là khoảng giấy
âm. Ý thì đúng nhưng hỏng ở chỗ khoảng âm không tô bóng vào trong được, mà
Kraven thì nằm hết ở khuôn mặt — râu, bờm, cái nhìn gằm. Vẽ ra bốn lần đều
thành một bức tượng nhợt nhạt. Ghi lại đây để đừng ai thử lại lần nữa.
"""

import math
from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen

from theme import INK, PAPER, PAPER_HI

from .art import H, W, Rolls, design, marks, misprint
from .kraven_absolute import ABSOLUTE
from .profile import Profile

HEAD = QPointF(48, 42)


# ═══════════════════════════════════════════════════ hình khối
def _leaf(cx, cy, ang, length, half):
    """Một chiếc lá hình hạnh nhân: hai cung phình ra từ trục nối hai đầu."""
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    tip = QPointF(cx + dx * length / 2, cy + dy * length / 2)
    tail = QPointF(cx - dx * length / 2, cy - dy * length / 2)
    leaf = QPainterPath(tail)
    leaf.quadTo(QPointF(cx + nx * half, cy + ny * half), tip)
    leaf.quadTo(QPointF(cx - nx * half, cy - ny * half), tail)
    leaf.closeSubpath()
    return leaf


@lru_cache(maxsize=1)
def _gap():
    """Khe hở trong tán: một lỗ rách, mép lởm chởm chứ không tròn trịa."""
    r = Rolls(15081964)          # ASM #15, 08/1964
    steps = 44
    pts = []
    for i in range(steps):
        a = math.radians(i * 360 / steps)
        rad = 1.0 + r(-0.09, 0.09)   # biên độ nhỏ thôi: nhiễu mạnh thì mép
        pts.append(QPointF(48 + math.cos(a) * 30 * rad,   # mọc ra mấy cái nêm
                           50 + math.sin(a) * 34 * rad))  # nhọn trông như lỗi

    # Nối bằng cung bậc hai qua trung điểm từng cạnh: mép vẫn rách nhưng là
    # rách kiểu lá che nhau, không phải gãy góc kiểu đa giác.
    hole = QPainterPath()
    mid0 = (pts[0] + pts[-1]) / 2
    hole.moveTo(mid0)
    for i in range(steps):
        nxt = (pts[i] + pts[(i + 1) % steps]) / 2
        hole.quadTo(pts[i], nxt)
    hole.closeSubpath()
    return hole


def _kraven():
    """Bán thân hắn: đầu, râu quai nón, và cái vest bờm sư tử quàng vai."""
    r = Rolls(6408150)
    body = QPainterPath()
    body.addEllipse(HEAD, 10.5, 12.0)

    # tóc và râu quai nón gộp thành một khối bao quanh mặt, chừa phần giữa
    frame = QPainterPath()
    frame.addEllipse(HEAD, 13.4, 15.4)
    face = QPainterPath()
    face.addEllipse(QPointF(HEAD.x(), HEAD.y() + 1.6), 8.6, 10.4)
    body = body.united(frame.subtracted(face))

    for i in range(11):          # chóp tóc xù trên đỉnh, so le
        a = math.radians(-168 + i * 13.6)
        base, tip = 13.4, 13.4 + r(2.0, 5.6)
        wide = math.radians(r(5, 9))
        tuft = QPainterPath()
        tuft.moveTo(HEAD.x() + math.cos(a - wide) * base,
                    HEAD.y() + math.sin(a - wide) * base * 1.15)
        tuft.lineTo(HEAD.x() + math.cos(a) * tip,
                    HEAD.y() + math.sin(a) * tip * 1.15)
        tuft.lineTo(HEAD.x() + math.cos(a + wide) * base,
                    HEAD.y() + math.sin(a + wide) * base * 1.15)
        tuft.closeSubpath()
        body = body.united(tuft)

    # vai
    torso = QPainterPath()
    torso.moveTo(35, 62)
    torso.cubicTo(31, 70, 29, 80, 28, 92)
    torso.lineTo(68, 92)
    torso.cubicTo(67, 80, 65, 70, 61, 62)
    torso.closeSubpath()
    body = body.united(torso)

    # Vest bờm sư tử — dấu hiệu nhận ra Kraven. Mép dưới phải xoã răng cưa và
    # phải thò hẳn ra ngoài vai, nếu nằm gọn trong thân thì hợp path nuốt mất.
    collar = QPainterPath()
    collar.moveTo(24, 64)
    collar.cubicTo(33, 56, 63, 56, 72, 64)
    x = 72
    while x > 24:
        step = r(4.0, 7.0)
        collar.lineTo(x - step * 0.5, 64 + r(10, 21))
        collar.lineTo(x - step, 64 + r(3, 8))
        x -= step
    collar.closeSubpath()
    return body.united(collar)


_GAP = _gap()
_KRAVEN = _kraven()


def _front_leaves():
    """Lá vắt ngang trước khe — để hắn nằm hẳn phía sau tán, không dán lên."""
    r = Rolls(80119640)
    leaves = QPainterPath()
    for _ in range(7):
        leaves = leaves.united(
            _leaf(r(14, 84), r(16, 104), r(-74, 74), r(30, 52), r(3.6, 6.8)))
    return leaves


_FRONT = _front_leaves()


@lru_cache(maxsize=1)
def _thicket():
    """Tán lá: cả tờ giấy trừ đi cái khe."""
    field = QPainterPath()
    field.addRect(QRectF(-6, -6, 112, 132))
    return field.subtracted(_GAP)


# ═══════════════════════════════════════════════════════════════ các lớp
def _veins(p):
    """Gân lá vạch bằng màu giấy trong lòng tán, cho nó khỏi bết thành mảng."""
    p.save()
    p.setClipPath(_thicket())
    r = Rolls(19640815)
    pale = QColor(PAPER)
    pale.setAlpha(58)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(pale, 0.6))
    for _ in range(40):
        x, y = r(-4, 104), r(-4, 124)
        ang = math.radians(r(-80, 80))
        run = r(7, 18)
        p.drawLine(QPointF(x, y),
                   QPointF(x + math.cos(ang) * run, y + math.sin(ang) * run))
    p.restore()


def _face(p):
    """Mắt, gờ mày và hàm răng nghiến — tô bằng màu giấy trên nền mực.

    Cả bức chỉ có mấy nét này là sáng. Hắn nhìn gằm lên, đúng tư thế của kẻ
    nấp thấp hơn con mồi.
    """
    p.setPen(Qt.PenStyle.NoPen)
    for side in (-1, 1):
        eye = QPainterPath()
        eye.moveTo(HEAD.x() + side * 1.8, HEAD.y() - 0.6)
        eye.quadTo(HEAD.x() + side * 4.4, HEAD.y() - 2.6,
                   HEAD.x() + side * 6.8, HEAD.y() - 0.4)
        eye.quadTo(HEAD.x() + side * 4.3, HEAD.y() + 1.4,
                   HEAD.x() + side * 1.8, HEAD.y() - 0.6)
        eye.closeSubpath()
        p.setBrush(PAPER_HI)
        p.drawPath(eye)
        p.setBrush(INK)          # con ngươi, hơi chếch vào trong
        p.drawEllipse(QPointF(HEAD.x() + side * 4.0, HEAD.y() - 0.4), 1.0, 1.0)

    # hàm răng nghiến: một dải sáng có khe dọc cắt ngang
    p.setBrush(PAPER_HI)
    grin = QPainterPath()
    grin.moveTo(HEAD.x() - 5.2, HEAD.y() + 6.2)
    grin.quadTo(HEAD.x(), HEAD.y() + 5.2, HEAD.x() + 5.2, HEAD.y() + 6.2)
    grin.quadTo(HEAD.x(), HEAD.y() + 9.6, HEAD.x() - 5.2, HEAD.y() + 6.2)
    grin.closeSubpath()
    p.drawPath(grin)
    p.setBrush(INK)              # khe răng: thưa, rộng hẹp khác nhau
    for x, w in ((-3.1, 0.7), (-1.2, 0.5), (0.9, 0.8), (3.0, 0.5)):
        p.drawRect(QRectF(HEAD.x() + x, HEAD.y() + 5.4, w, 4.2))


def _paint(p):
    # Tán lá tô mực trơn, KHÔNG in lệch trục: `misprint` lệch 2–3 đơn vị, áp
    # lên một bóng người cỡ vừa thì ra chất pulp, áp lên cả khu rừng phủ kín
    # tờ giấy thì mọi đường biên hoá dải đỏ-lam dày cộp. Chất in lệch để dành
    # cho hai thứ nhỏ và cần nổi: chính hắn, và mấy chiếc lá trước mặt.
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(INK)
    p.drawPath(_thicket())
    _veins(p)

    p.save()
    p.setClipPath(_GAP)          # hắn chỉ hiện ra trong phạm vi cái khe
    misprint(p, _KRAVEN)
    # Viền sáng chạy quanh bóng hắn: ánh sáng lọt qua khe nằm sau lưng, nên
    # mép người phải bắt sáng. Thiếu nét này thì chỗ nào hắn chạm mép khe là
    # dính luôn vào tán lá, và bóng người mất mất một bên sườn.
    rim = QColor(PAPER_HI)
    rim.setAlpha(150)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(rim, 0.8))
    p.drawPath(_KRAVEN)
    _face(p)
    p.restore()

    misprint(p, _FRONT)
    marks(p)


@lru_cache(maxsize=8)
def _still(w, h):
    """Dựng sẵn cả tấm rồi dán — trừ và hợp path ở đây đắt hơn cả phần tô."""
    img = QImage(max(1, w), max(1, h),
                 QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    q = QPainter(img)
    q.setRenderHint(QPainter.RenderHint.Antialiasing)
    q.scale(w / W, h / H)
    _paint(q)
    q.end()
    return img


def draw_kraven(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước."""
    scale = min(rect.width() / W, rect.height() / H)
    still = _still(max(1, round(W * scale)), max(1, round(H * scale)))
    with design(p, rect):
        p.drawImage(QRectF(0, 0, W, H), still)


# ═══════════════════════════════════════════════════════════════ hồ sơ
PROFILE = Profile(
    name="Kraven the Hunter",
    vi_name="Thợ Săn",
    real_name="Sergei Kravinoff",
    keys=("Kraven",),

    tagline="Cả danh sách này chạy đua nhau về công nghệ. Hắn thì bỏ hết, "
            "vào rừng, và vẫn là kẻ đáng sợ nhất trong đám.",

    summary=(
        "Sergei Kravinoff là quý tộc Nga lưu vong, đi săn thú lớn khắp châu "
        "Phi cho tới lúc chẳng còn con nào đáng để đuổi nữa. The Amazing "
        "Spider-Man #15 (08/1964) đưa hắn tới New York vì một lý do rất giản "
        "dị: có người kể cho hắn nghe về một con mồi biết bám tường. Người kể "
        "chuyện ấy là Chameleon — em cùng cha khác mẹ của hắn, và cũng là ác "
        "nhân mở màn danh sách này ở số một.",

        "Sức mạnh của hắn đến từ những bài thuốc thảo dược hắn học được trong "
        "rừng: khoẻ hơn người thường nhiều lần, nhanh hơn, giác quan nhạy hơn, "
        "và già đi chậm hẳn. Nhưng thứ hắn từ chối mới là điều đáng nói. "
        "Không giáp, không súng, không một món máy móc nào — trong một danh "
        "sách đầy pháo laser và bộ xương ngoài, hắn săn Spider-Man bằng tay "
        "không, dao găm, thuốc mê và sự kiên nhẫn. Với hắn, dùng máy là gian "
        "lận, mà gian lận thì cuộc săn chẳng còn nghĩa gì.",

        "Hắn cũng là một trong sáu cái tên sáng lập Sinister Six. Nhưng suốt "
        "hơn hai mươi năm, Kraven vẫn chỉ là một tay săn mồi kỳ quặc trong "
        "bộ vest bờm sư tử — cho tới 1987.",

        "Kraven's Last Hunt (J.M. DeMatteis & Mike Zeck) bắt đầu bằng việc "
        "hắn bắn Spider-Man rồi chôn sống anh trong hai tuần. Trong hai tuần "
        "ấy hắn mặc bộ đồ của Peter, đi tuần thay Peter, và đánh bại Vermin — "
        "thứ Spider-Man từng không hạ nổi một mình. Hắn muốn chứng minh một "
        "điều lớn hơn việc bắt được con mồi: rằng hắn làm được đúng cái việc "
        "của con mồi ấy, và làm giỏi hơn. Chứng minh xong, hắn thả Peter ra, "
        "về nhà, và tự bắn mình. Đó là một trong số ít truyện Spider-Man mà "
        "kẻ phản diện thắng, rồi kết liễu chính mình vì đã hết việc để làm.",
    ),

    powers=(
        "Thảo dược rừng rậm: sức mạnh, tốc độ, giác quan và tuổi thọ",
        "Thợ săn bậc thầy — lần dấu, đặt bẫy, rình hàng tuần không sốt ruột",
        "Đánh tay không, dao găm và giáo; từ chối súng vì cho là hèn",
        "Thuốc mê và độc chiết từ cây cỏ, đủ hạ một người có sức siêu phàm",
        "Hiểu tâm lý con mồi hơn hiểu chính mình — biết Peter sẽ chạy hướng nào",
        "Không giáp, không máy móc: coi công nghệ là gian lận",
    ),

    facts=(
        ("Tên thật", "Sergei Kravinoff"),
        ("Xuất hiện đầu", "ASM #15  ·  08/1964"),
        ("Tác giả", "Stan Lee & Steve Ditko"),
        ("Quan hệ", "Em cùng cha khác mẹ: Chameleon"),
        ("Băng nhóm", "Sinister Six — thành viên sáng lập"),
        ("Truyện đỉnh", "Kraven's Last Hunt  ·  1987"),
    ),

    blurb="Hắn thắng. Đó là chỗ khiến Kraven's Last Hunt khác mọi truyện khác "
          "trong danh sách này — và cũng là chỗ giết hắn. Săn xong con mồi "
          "cuối cùng thì một người thợ săn chẳng còn lý do gì để dậy vào sáng "
          "hôm sau.",

    evolution=ABSOLUTE,
    evolve_label="Evolve",

    art=draw_kraven,
    caption="Chân dung dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Kraven_the_Hunter"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Sergei_Kravinoff_(Earth-616)"),
    ),
)
