"""
Beetle — Abner Jenkins.

Mười hai chân dung trước đều dựng bằng **mảng đặc**: một khối mực làm nên
hình, chi tiết chỉ là thứ đặt lên trên. Cái này bỏ hẳn mảng đặc. Không có
bóng người nào cả — chỉ có nét: đường bao, nét gạch bóng, đường dóng, số
chú thích khoanh tròn, và một tờ giấy kẻ ô phía sau.

Vì Abner Jenkins không phải quái vật, không phải phù thuỷ, không bị phóng
xạ chiếu trúng. Hắn là **thợ máy**. Bộ giáp bọ cánh cứng ấy do chính hắn
ngồi gò ra, nên thứ đúng nhất để vẽ hắn không phải một tấm chân dung mà là
một bản vẽ chế tạo.

Và bản vẽ ấy tháo rời — các mảnh nằm tách nhau, ở giữa không có ai. Đó là
chỗ cả danh sách này không ai giống hắn: Jenkins về sau cởi bộ giáp ra,
đi tù cho xong phần của mình, rồi ở lại phía bên kia. Bộ đồ rỗng là kết
truyện của hắn, không phải một hiệu ứng vẽ cho đẹp.
"""

import math
from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QFont, QImage, QPainter, QPainterPath,
                           QPen)

from theme import BLUE, INK, INK_SOFT, PAPER_HI, RED

from .art import H, W, Rolls, design, marks
from .profile import Profile

LINE = 1.0                       # nét bao chính
THIN = 0.5                       # nét gạch bóng và nét phụ


# ═══════════════════════════════════════════════════ hình khối
def _helmet():
    """Mũ: vòm tròn, khe kính ngang, hai râu ngắn vểnh lên."""
    shell = QPainterPath()
    shell.moveTo(38, 26)
    shell.cubicTo(38, 12, 62, 12, 62, 26)
    shell.cubicTo(60, 30, 40, 30, 38, 26)
    shell.closeSubpath()
    return shell


def _carapace():
    """Mai giáp: vỏ bọ hình giọt, nhọn dần xuống dưới."""
    shell = QPainterPath()
    shell.moveTo(50, 40)
    shell.cubicTo(70, 42, 76, 60, 72, 76)
    shell.cubicTo(68, 90, 58, 98, 50, 100)
    shell.cubicTo(42, 98, 32, 90, 28, 76)
    shell.cubicTo(24, 60, 30, 42, 50, 40)
    shell.closeSubpath()
    return shell


def _elytron(side):
    """Một cánh cứng đã mở bung ra khỏi thân, dựng đứng ở lề khung."""
    x = 50 + side * 34
    wing = QPainterPath()
    wing.moveTo(x, 30)
    wing.cubicTo(x + side * 11, 40, x + side * 12, 62, x + side * 5, 78)
    wing.cubicTo(x + side * 1, 70, x - side * 2, 50, x, 30)
    wing.closeSubpath()
    return wing


def _glove():
    """Găng giác hút: bàn tay ngắn, năm đĩa hút ở mặt trong."""
    hand = QPainterPath()
    hand.moveTo(41, 106)
    hand.cubicTo(41, 100, 59, 100, 59, 106)
    hand.cubicTo(59, 115, 41, 115, 41, 106)
    hand.closeSubpath()
    return hand


_HELMET = _helmet()
_CARAPACE = _carapace()
_ELYTRA = (_elytron(-1), _elytron(1))
_GLOVE = _glove()

# (mảnh, điểm đặt số, số hiệu) — số dóng ra lề, không đè lên hình
_PARTS = ((_HELMET, QPointF(50, 19), QPointF(74, 12), "1"),
          (_ELYTRA[0], QPointF(14, 52), QPointF(8, 30), "2"),
          (_ELYTRA[1], QPointF(86, 52), QPointF(92, 30), "2"),
          (_CARAPACE, QPointF(50, 68), QPointF(88, 90), "3"),
          (_GLOVE, QPointF(50, 107), QPointF(20, 114), "4"))


# ═══════════════════════════════════════════════════════════════ các lớp
def _graph_paper(p):
    """Giấy kẻ ô: nền của mọi bản vẽ chế tạo.

    Ô phải thật nhạt. Kẻ đậm lên thì cái lưới giành mất chỗ của bản vẽ, và
    mảng ô vuông trên diện rộng đọc ra mặt sàn chứ không ra giấy kỹ thuật.
    """
    faint = QColor(BLUE)
    faint.setAlpha(15)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(faint, 0.3))
    for i in range(-1, 15):
        p.drawLine(QPointF(-6, i * 8), QPointF(106, i * 8))
    for i in range(-1, 14):
        p.drawLine(QPointF(i * 8, -6), QPointF(i * 8, 126))

    heavy = QColor(BLUE)
    heavy.setAlpha(26)
    p.setPen(QPen(heavy, 0.45))
    for i in range(0, 4):
        p.drawLine(QPointF(-6, i * 40), QPointF(106, i * 40))
        p.drawLine(QPointF(i * 40 - 6, -6), QPointF(i * 40 - 6, 126))


def _hatch(p, path, ang, step, alpha):
    """Gạch bóng chéo trong lòng một mảnh, cắt theo đúng đường bao của nó."""
    p.save()
    p.setClipPath(path)
    tone = QColor(INK)
    tone.setAlpha(alpha)
    p.setPen(QPen(tone, THIN))
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    for k in range(-40, 40):
        c = k * step
        p.drawLine(QPointF(50 + dx * c - dy * 90, 60 + dy * c + dx * 90),
                   QPointF(50 + dx * c + dy * 90, 60 + dy * c - dx * 90))
    p.restore()


def _parts(p):
    """Năm mảnh giáp: chỉ đường bao và nét gạch, tuyệt đối không tô đặc."""
    p.setBrush(PAPER_HI)         # tô màu giấy để mảnh nọ che được mảnh kia
    p.setPen(QPen(INK, LINE))
    for path, _, _, _ in _PARTS:
        p.drawPath(path)

    _hatch(p, _CARAPACE, 34, 2.6, 54)
    for wing in _ELYTRA:
        _hatch(p, wing, -34, 2.4, 60)
    _hatch(p, _HELMET, 34, 2.2, 40)

    # khe kính trên mũ, và hai râu
    p.setBrush(INK)
    p.setPen(Qt.PenStyle.NoPen)
    slit = QPainterPath()
    slit.moveTo(41.5, 24.0)
    slit.cubicTo(46, 21.6, 54, 21.6, 58.5, 24.0)
    slit.cubicTo(54, 25.8, 46, 25.8, 41.5, 24.0)
    slit.closeSubpath()
    p.drawPath(slit)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(INK, THIN + 0.2))
    for side in (-1, 1):
        feeler = QPainterPath(QPointF(50 + side * 5, 14.5))
        feeler.quadTo(QPointF(50 + side * 11, 8), QPointF(50 + side * 16, 7))
        p.drawPath(feeler)

    # đường ghép dọc giữa mai, cộng mấy đốt ngang
    p.save()
    p.setClipPath(_CARAPACE)
    p.setPen(QPen(INK, THIN + 0.25))
    p.drawLine(QPointF(50, 40), QPointF(50, 100))
    for y in (54, 66, 78, 89):
        seam = QPainterPath(QPointF(26, y - 3))
        seam.quadTo(QPointF(50, y + 3), QPointF(74, y - 3))
        p.drawPath(seam)
    p.restore()

    # đĩa giác hút trên găng
    p.setPen(QPen(INK, THIN + 0.2))
    for i in range(5):
        p.drawEllipse(QPointF(43.5 + i * 3.3, 108.6), 1.25, 1.25)


def _callouts(p):
    """Đường dóng và số hiệu khoanh tròn — thứ làm nên một bản vẽ chế tạo."""
    ink = QColor(RED)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(ink, THIN + 0.1))
    for _, anchor, label, text in _PARTS:
        p.drawLine(anchor, label)
        p.drawEllipse(label, 3.6, 3.6)

    # Chữ số dùng font thật. Bản đầu vẽ tay từng nét bằng `drawLine` cho khỏi
    # phụ thuộc font, nhưng ở cỡ hai đơn vị thì mấy đoạn thẳng ấy ra nét
    # nguệch ngoạc chứ không ra con số. `setPixelSize` tính theo đơn vị của
    # khung 100×120, nên chữ giữ đúng cỡ ở mọi độ phóng và mọi DPI.
    p.setPen(ink)
    font = QFont()
    font.setPixelSize(5)
    font.setBold(True)
    p.setFont(font)
    for _, _, label, text in _PARTS:
        box = QRectF(label.x() - 4, label.y() - 4, 8, 8)
        p.drawText(box, int(Qt.AlignmentFlag.AlignCenter), text)


def _dimension(p):
    """Đường đo bề ngang bộ giáp, hai đầu mũi tên — nét cuối cho ra bản vẽ."""
    tone = QColor(INK_SOFT)
    tone.setAlpha(150)
    p.setBrush(tone)
    p.setPen(QPen(tone, THIN))
    y = 119.0
    for x, side in ((28, 1), (72, -1)):
        p.drawLine(QPointF(x, y - 3.4), QPointF(x, y + 3.4))
        head = QPainterPath(QPointF(x, y))
        head.lineTo(x + side * 3.4, y - 1.4)
        head.lineTo(x + side * 3.4, y + 1.4)
        head.closeSubpath()
        p.drawPath(head)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawLine(QPointF(28, y), QPointF(72, y))


def _wear(p):
    """Vết bẩn của một tờ giấy đã nằm lâu trên bàn nguội: mấy vệt mờ, lệch."""
    r = Rolls(12308196)          # Strange Tales #123, 08/1964
    p.setPen(Qt.PenStyle.NoPen)
    for _ in range(7):
        smudge = QColor(INK_SOFT)
        smudge.setAlpha(int(r(4, 9)))
        p.setBrush(smudge)
        p.drawEllipse(QPointF(r(2, 98), r(4, 120)), r(5, 11), r(3, 7))


def _paint(p):
    _graph_paper(p)
    _wear(p)
    _parts(p)
    _callouts(p)
    _dimension(p)
    marks(p)


@lru_cache(maxsize=8)
def _still(w, h):
    """Dựng sẵn cả tấm rồi dán — vài trăm nét gạch bóng thì không nên vẽ lại."""
    img = QImage(max(1, w), max(1, h),
                 QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    q = QPainter(img)
    q.setRenderHint(QPainter.RenderHint.Antialiasing)
    q.scale(w / W, h / H)
    _paint(q)
    q.end()
    return img


def draw_beetle(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước."""
    scale = min(rect.width() / W, rect.height() / H)
    still = _still(max(1, round(W * scale)), max(1, round(H * scale)))
    with design(p, rect):
        p.drawImage(QRectF(0, 0, W, H), still)


# ═══════════════════════════════════════════════════════════════ hồ sơ
PROFILE = Profile(
    name="Beetle",
    vi_name="Bọ Cánh Cứng",
    real_name="Abner Jenkins",

    kicker="Hồ sơ ác nhân",

    tagline="Trong chín mươi mốt cái tên của danh sách này, hắn là người duy "
            "nhất cởi bộ đồ ra, đi tù cho xong phần của mình, rồi ở lại phía "
            "bên kia.",

    summary=(
        "Abner Jenkins là thợ máy máy bay: giỏi nghề, lương thấp, và chán tới "
        "tận cổ. Hắn gò cho mình một bộ giáp từ đồ nghề trong xưởng — vỏ bọc "
        "cứng, cánh bay gấp được, găng tay gắn đĩa giác hút để bám tường — "
        "rồi đi ăn cướp. Đó là toàn bộ nguồn gốc: không phóng xạ, không thí "
        "nghiệm hỏng, không lời nguyền. Chỉ là một người thợ quyết định dùng "
        "tay nghề của mình vào việc khác.",

        "Hắn cũng không ra mắt trong truyện Spider-Man. Strange Tales #123 "
        "(08/1964) của Stan Lee và Carl Burgos cho hắn đánh nhau với Human "
        "Torch, và mãi sau này hắn mới thành cái tên thường trực trong danh "
        "sách kẻ thù của Người Nhện. Trong một dòng thời gian mà gần như ai "
        "cũng bắt đầu bằng việc chạm trán Peter Parker, riêng hắn đi đường "
        "vòng.",

        "Suốt ba thập kỷ, Beetle là hạng ác nhân trung bình: đủ giỏi để gây "
        "phiền, không bao giờ đủ để thành mối đe doạ thật. Hắn nâng cấp bộ "
        "giáp hết lần này tới lần khác, vào Sinister Syndicate, thua, rồi lại "
        "nâng cấp. Một người thợ tận tuỵ với thứ mình chế ra, chỉ có điều thứ "
        "ấy chưa bao giờ đủ tốt.",

        "Rồi tới Thunderbolts (1997). Nhóm Masters of Evil giả làm siêu anh "
        "hùng để lừa cả thế giới, và Jenkins — dưới cái tên MACH-1 — đóng vai "
        "người tốt lâu tới mức không còn là đóng nữa. Hắn tự ra đầu thú cho "
        "một án mạng mình từng gây, ngồi tù cho hết, rồi quay lại làm đúng "
        "công việc ấy thật. MACH-II, MACH-IV, MACH-V: cùng một người thợ, "
        "cùng một bộ giáp tự gò, chỉ khác chỗ đứng.",
    ),

    powers=(
        "Không có siêu năng lực nào — tất cả nằm ở bộ giáp hắn tự chế",
        "Vỏ giáp chịu đạn, cánh gấp cho bay, đĩa giác hút để bám tường",
        "Kỹ sư cơ khí bậc thầy: tự thiết kế, tự sửa, tự nâng cấp",
        "Các bản sau gắn thêm vũ khí, cảm biến và hệ bay phản lực",
        "Điểm yếu suốt ba mươi năm: bộ giáp luôn tốt hơn người mặc nó",
    ),

    facts=(
        ("Tên thật", "Abner Jenkins"),
        ("Xuất hiện đầu", "Strange Tales #123"),
        ("Thời điểm", "08/1964"),
        ("Tác giả", "Stan Lee & Carl Burgos"),
        ("Đối thủ đầu", "Human Torch, không phải Nhện"),
        ("Về sau", "MACH-1 tới MACH-V, Thunderbolts"),
    ),

    blurb="Chín mươi cái tên còn lại trong danh sách này đều kết thúc bằng nhà "
          "tù, cái chết, hoặc một lần tái xuất nữa. Abner Jenkins kết thúc "
          "bằng cách trả án xong rồi đi làm. Đó là lý do bản vẽ kia không có "
          "ai bên trong.",

    art=draw_beetle,
    caption="Bản vẽ chế tạo  ·  dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Beetle_(comics)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Abner_Jenkins_(Earth-616)"),
    ),
)
