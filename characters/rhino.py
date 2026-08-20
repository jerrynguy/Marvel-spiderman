"""
Rhino — Aleksei Sytsevich.

Mười sáu chân dung trước đều đặt trọn nhân vật vào trong khung: to nhỏ khác
nhau, nhưng ai cũng vừa. Cái này không vừa. Đầu hắn tràn ra cả bốn mép,
cái sừng đi thẳng lên và cắt qua cạnh trên, còn hai dấu canh trục ở đáy thì
bị chính hắn đè lên — bản in vẽ trước, hắn đi qua sau. Không có cách nào
nói "thứ này quá khổ" bằng một bóng người đứng gọn giữa tờ giấy.

Chỗ thứ hai là chất da. Mười sáu bức kia đều tô mực phẳng rồi vạch nét sáng
lên trên. Ở đây lớp da dựng bằng **chấm đục thủng mực** — hàng nghìn chấm
màu giấy khoét vào mảng đen, dày ở chỗ khuất và thưa ở chỗ bắt sáng. Đó
đúng là cách máy in Silver Age tạo sắc độ, và cũng đúng là bề mặt sần của
một tấm da tê giác.

Và giữa tất cả những thứ ấy có đúng một chi tiết không thuộc về con vật:
con mắt. Nó nhỏ, mí nặng, và mệt. Aleksei Sytsevich là một tay du côn được
chọn vì to xác và ít chữ; bộ da bơm lên người hắn thì gỡ ra không được nữa.
Có một quãng hắn bỏ nghề thật, lấy vợ, sống yên — rồi cái đêm Oksana bị
giết, người ta nói Aleksei chết cùng đêm ấy, chỉ còn lại con tê giác. Con
mắt trong bức này là phần còn sót lại của người kia.
"""

import math
from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QPainter, QPainterPath, QPen,
                           QTransform)

from theme import INK, INK_SOFT, PAPER, PAPER_HI, RED

from .art import H, W, Rolls, design, marks
from .profile import Profile

EYE = QPointF(75, 77)            # con mắt — chi tiết duy nhất còn là người
LIGHT = QPointF(30, 24)          # nguồn sáng, để biết chỗ nào da bắt sáng


# ═══════════════════════════════════════════════════ khối đầu, tràn khỏi khung
def _horn():
    """Sừng trước: gốc bè ngang sống mũi, vuốt lên và cắt qua cạnh trên khung."""
    horn = QPainterPath()
    horn.moveTo(11, 79)
    horn.cubicTo(13, 52, 19, 28, 25, -12)     # cạnh trước, vuốt cong về sau
    horn.lineTo(35, -12)
    horn.cubicTo(37, 28, 39, 52, 41, 71)      # cạnh sau, thoải hơn
    horn.closeSubpath()
    return horn


def _brow_horn():
    """Sừng sau, ngắn và tù — con tê giác nào cũng có hai cái."""
    horn = QPainterPath()
    horn.moveTo(55, 72)
    horn.cubicTo(57, 58, 60, 46, 64, 36)
    horn.cubicTo(70, 44, 73, 54, 74, 62)
    horn.closeSubpath()
    return horn


def _head():
    """Cả khối đầu và vai: vào từ mép trái, ra ở mép phải và mép dưới."""
    head = QPainterPath()
    head.moveTo(-8, 104)                      # mõm, đã nằm ngoài khung trái
    head.cubicTo(-2, 88, 4, 80, 14, 76)       # môi trên lên sống mũi
    head.lineTo(41, 71)                       # gốc sừng
    head.cubicTo(47, 75, 52, 75, 56, 72)      # chỗ lõm sau sừng
    head.cubicTo(66, 64, 80, 54, 92, 48)      # gò má lên gáy
    head.cubicTo(99, 44, 104, 44, 108, 46)    # trán chạy khỏi khung phải
    head.lineTo(108, 126)
    head.lineTo(-8, 126)
    head.closeSubpath()
    return head


def _jaw():
    """Hàm dưới, hơi trễ xuống: chỗ duy nhất đường bao còn gãy được một nhịp."""
    jaw = QPainterPath()
    jaw.moveTo(-8, 104)
    jaw.cubicTo(2, 108, 14, 110, 26, 108)
    jaw.cubicTo(34, 106, 40, 100, 44, 94)
    jaw.lineTo(44, 126)
    jaw.lineTo(-8, 126)
    jaw.closeSubpath()
    return jaw


@lru_cache(maxsize=1)
def _mass():
    return _head().united(_jaw()).united(_horn()).united(_brow_horn())


# ═══════════════════════════════════════════════════ da: chấm đục thủng mực
def _pebble(p, mass):
    """Lớp da sần, dựng bằng chấm màu giấy khoét vào mảng mực.

    Không tô sáng lên trên mà **đục thủng** xuống: chấm càng gần nguồn sáng
    thì càng to và càng dày, ra sắc độ đúng kiểu bản in bốn màu. Cắt theo
    khối đầu nên rắc thoải mái không sợ tràn.
    """
    p.save()                                  # trừ hai cái sừng ra: sừng nhẵn,
    p.setClipPath(mass.subtracted(_horn().united(_brow_horn())),
                  Qt.ClipOperation.IntersectClip)   # chỉ da mới sần
    p.setPen(Qt.PenStyle.NoPen)
    r = Rolls(41101966)                       # ASM #41, 10/1966
    for _ in range(5200):
        x, y = r(-8, 108), r(-12, 126)
        far = math.hypot(x - LIGHT.x(), y - LIGHT.y()) / 130.0
        if r(0, 1) < far * 0.82:              # xa nguồn sáng thì bỏ bớt chấm
            continue
        dot = QColor(PAPER)
        dot.setAlpha(int(max(26, 92 - far * 56)))
        p.setBrush(dot)
        size = 0.28 + (1.0 - far) * 0.62
        p.drawEllipse(QPointF(x, y), size, size * 0.86)
    p.restore()


def _folds(p, mass):
    """Nếp gấp của tấm da: mấy đường sáng dày, chạy vòng theo khối.

    Da tê giác không nhăn lăn tăn mà gấp thành từng tấm lớn. Ít nếp mà dày
    thì ra tấm giáp; nhiều nếp mảnh thì ra một cái chăn nhàu.
    """
    p.save()
    p.setClipPath(mass, Qt.ClipOperation.IntersectClip)
    p.setBrush(Qt.BrushStyle.NoBrush)
    seam = QColor(PAPER_HI)
    seam.setAlpha(96)
    p.setPen(QPen(seam, 2.0))
    for a, b, c, d in (((-6, 116), (16, 118), (34, 112), (48, 102)),
                       ((46, 126), (60, 114), (78, 108), (108, 106)),
                       ((60, 88), (74, 92), (88, 90), (108, 84)),
                       ((-4, 92), (8, 94), (16, 92), (22, 88))):
        fold = QPainterPath()
        fold.moveTo(*a)
        fold.cubicTo(b[0], b[1], c[0], c[1], d[0], d[1])
        p.drawPath(fold)

    ridge = QColor(PAPER_HI)                  # gờ nối hai cái sừng
    ridge.setAlpha(70)
    p.setPen(QPen(ridge, 1.4))
    bridge = QPainterPath()
    bridge.moveTo(41, 70)
    bridge.cubicTo(46, 70, 51, 70, 55, 69)
    p.drawPath(bridge)
    p.restore()


def _horn_grain():
    """Vân sừng: mấy cung ngang, thứ phân biệt cái sừng với khối đầu."""
    grain = QPainterPath()
    for t, span in ((0.14, 22.0), (0.34, 19.0), (0.54, 16.0), (0.74, 13.0)):
        y = 74 - t * 76
        x = 13 + t * 8
        arc = QPainterPath()
        arc.moveTo(x, y)
        arc.quadTo(x + span * 0.5, y + 3.0, x + span, y - 1.5)
        grain.addPath(arc)
    return grain


def _face(p):
    """Mắt, mũi, mép — ba chỗ duy nhất trong bức có nét của một sinh vật."""
    # lỗ mũi: một dấu phẩy sáng ở đầu mõm
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(INK_SOFT))
    nostril = QPainterPath()
    nostril.moveTo(-2, 92)
    nostril.cubicTo(2, 89, 7, 90, 8, 94)
    nostril.cubicTo(5, 93, 1, 94, -2, 92)
    nostril.closeSubpath()
    p.drawPath(nostril)

    # con mắt: hạnh nhân sáng, mí trên nặng trĩu đè xuống gần nửa tròng
    light = QColor("#EFE7D6")
    p.setBrush(light)
    eye = QPainterPath()
    eye.moveTo(EYE.x() - 5.2, EYE.y() + 0.6)
    eye.cubicTo(EYE.x() - 2, EYE.y() - 2.6, EYE.x() + 2.4, EYE.y() - 2.4,
                EYE.x() + 4.6, EYE.y() + 0.4)
    eye.cubicTo(EYE.x() + 2, EYE.y() + 3.2, EYE.x() - 2.6, EYE.y() + 3.2,
                EYE.x() - 5.2, EYE.y() + 0.6)
    eye.closeSubpath()
    p.drawPath(eye)

    p.setBrush(INK)
    p.drawEllipse(QPointF(EYE.x() - 0.4, EYE.y() + 0.6), 1.9, 1.9)
    p.setBrush(light)
    p.drawEllipse(QPointF(EYE.x() - 1.4, EYE.y() - 0.4), 0.6, 0.6)

    p.setBrush(Qt.BrushStyle.NoBrush)         # mí trên, dày và trễ
    p.setPen(QPen(INK, 1.6))
    lid = QPainterPath()
    lid.moveTo(EYE.x() - 6.0, EYE.y() - 0.4)
    lid.cubicTo(EYE.x() - 2, EYE.y() - 3.4, EYE.x() + 2.6, EYE.y() - 3.2,
                EYE.x() + 5.2, EYE.y() - 0.2)
    p.drawPath(lid)

    fold = QColor(PAPER_HI)                   # nếp da trên mí, làm mắt trũng xuống
    fold.setAlpha(90)
    p.setPen(QPen(fold, 1.2))
    brow = QPainterPath()
    brow.moveTo(EYE.x() - 8.0, EYE.y() - 4.6)
    brow.cubicTo(EYE.x() - 2, EYE.y() - 7.4, EYE.x() + 4, EYE.y() - 6.6,
                 EYE.x() + 8.0, EYE.y() - 3.4)
    p.drawPath(brow)

    mouth = QColor(PAPER_HI)                  # mép, chạy từ ngoài khung vào
    mouth.setAlpha(84)
    p.setPen(QPen(mouth, 1.8))
    lip = QPainterPath()
    lip.moveTo(-8, 101)
    lip.cubicTo(2, 104, 14, 105, 24, 102)
    p.drawPath(lip)


# ═══════════════════════════════════════════════════ dựng cả bức
def _paint(p, rect):
    with design(p, rect):
        # dấu canh trục vẽ trước rồi mới đến hắn: bản in có trước, hắn đi qua
        # sau, và hai dấu dưới đáy bị đè mất — đó là cách nói hắn không vừa khung
        marks(p)

        mass = _mass()
        shift = QColor(RED)                   # một lớp mực đỏ trượt, đủ ra chất in
        shift.setAlpha(64)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(shift)
        p.drawPath(mass.translated(1.6, 1.3))

        p.setBrush(INK)
        p.drawPath(mass)

        _pebble(p, mass)
        _folds(p, mass)

        p.save()                              # vân sừng, cắt theo đúng cái sừng
        p.setClipPath(_horn(), Qt.ClipOperation.IntersectClip)
        grain = QColor(PAPER_HI)
        grain.setAlpha(80)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(grain, 1.5))
        p.drawPath(_horn_grain())
        p.restore()

        _face(p)


_STILL = {}


def draw_rhino(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước.

    Một nghìn rưỡi chấm đục thủng mực là quá đắt cho một khung hình. Dựng
    sẵn vào ảnh đúng cỡ điểm ảnh thật rồi dán, như `electro.py`.
    """
    scale = p.transform().m11() or 1.0
    key = (round(rect.width(), 1), round(rect.height(), 1), round(scale, 2))
    ready = _STILL.get(key)
    if ready is None:
        if len(_STILL) > 6:
            _STILL.clear()
        ready = QImage(max(1, math.ceil(rect.width() * scale)),
                       max(1, math.ceil(rect.height() * scale)),
                       QImage.Format.Format_ARGB32_Premultiplied)
        ready.fill(Qt.GlobalColor.transparent)
        q = QPainter(ready)
        q.setRenderHint(QPainter.RenderHint.Antialiasing)
        q.scale(scale, scale)
        _paint(q, QRectF(0, 0, rect.width(), rect.height()))
        q.end()
        _STILL[key] = ready
    p.drawImage(rect, ready)


# ═══════════════════════════════════════════════════════════════ hồ sơ
PROFILE = Profile(
    name="Rhino",
    vi_name="Tê Giác",
    real_name="Aleksei Sytsevich",

    tagline="Hắn được chọn không phải vì giỏi, mà vì to xác và ít chữ — đúng "
            "hai tiêu chuẩn để làm vật thí nghiệm mà không ai đi hỏi lại.",

    summary=(
        "Aleksei Sytsevich là dân đâm thuê chém mướn cho mấy tổ chức tội phạm "
        "Đông Âu, nghèo, và có một gia đình phải nuôi. Hai nhà khoa học tên "
        "Igor và Georgi cần một cơ thể để thử nghiệm; họ chọn hắn vì thân "
        "hình lớn và vì hắn sẽ không hỏi nhiều. Hắn nhận lời để lấy tiền.",

        "Quy trình gồm phóng xạ gamma và một loạt hoá chất, kết thúc bằng "
        "việc gắn một bộ da polymer dính chặt vào chính da hắn. Mẫu vật họ "
        "chọn để mô phỏng là con tê giác — không phải vì trông dữ tợn, mà vì "
        "theo lập luận của họ, con tê giác là kết quả của hàng triệu năm tiến "
        "hoá về đúng một hướng: lao thẳng vào mục tiêu. Kết quả là một người "
        "nâng được cỡ bảy mươi lăm tấn, chạy nước rút gần trăm cây số giờ, "
        "chịu được sức nổ của cả tấn thuốc, và không cởi bộ da ra được nữa.",

        "The Amazing Spider-Man #41 (10/1966) của Stan Lee và John Romita Sr. "
        "cho hắn ra mắt bằng một việc thuê: bắt cóc John Jameson, con trai "
        "ông chủ báo Daily Bugle. Hắn húc đổ mọi thứ trên đường từ biên giới "
        "vào New York, và thua vì đúng cái khiến hắn đáng sợ — hắn chỉ biết "
        "đi thẳng. Spider-Man thắng bằng cách không đứng yên một chỗ.",

        "Nhưng đoạn đáng nhớ nhất của nhân vật này lại là đoạn hắn thôi làm "
        "ác nhân. Trong The Gauntlet (ASM #617, 2010), Aleksei bỏ nghề, cưới "
        "Oksana — một cô hầu bàn hắn gặp sau lần ra tù cuối — và từ chối mọi "
        "lời rủ rê, kể cả khi bị gọi là hèn. Rồi một gã Rhino mới xuất hiện, "
        "đòi so tài để lấy tiếng, và giết Oksana. Aleksei mặc lại bộ da, giết "
        "kẻ kia, và người ta nói rằng Aleksei chết cùng đêm với vợ mình — từ "
        "đó chỉ còn con tê giác.",
    ),

    powers=(
        "Sức mạnh cỡ bảy mươi lăm tấn, cộng thêm chính bộ da khi mặc",
        "Cú húc: chạy nước rút gần trăm cây số giờ, xuyên qua tường bê tông",
        "Bộ da polymer chịu được sức nổ tương đương một tấn thuốc",
        "Không mệt, không nản, và gần như không có cách nào chặn đứng",
        "Điểm yếu nằm ngay trong thiết kế: hắn chỉ giỏi đi thẳng",
        "Bộ da dính vĩnh viễn: muốn cởi phải mổ, không phải muốn là bỏ",
    ),

    facts=(
        ("Tên thật", "Aleksei Sytsevich"),
        ("Xuất hiện đầu", "ASM #41  ·  10/1966"),
        ("Tác giả", "Stan Lee & John Romita Sr."),
        ("Nghề cũ", "Du côn đánh thuê"),
        ("Người tạo ra", "Hai nhà khoa học Igor & Georgi"),
        ("Vợ", "Oksana, mất ở ASM #617"),
    ),

    blurb="Cả danh sách này chọn nghề ác nhân rồi giữ lấy nó. Aleksei "
          "Sytsevich bỏ được một lần, sống tử tế được một quãng, và mất đúng "
          "cái quãng ấy. Con mắt trong khung là phần còn lại của người đã bỏ.",

    art=draw_rhino,
    caption="Da khắc bằng chấm  ·  dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Rhino_(character)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Aleksei_Sytsevich_(Earth-616)"),
    ),
)
