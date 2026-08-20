"""
Molten Man — Mark Raxton.

Mười bốn chân dung trước đều coi tờ giấy là thứ nằm ngoài câu chuyện: mực
đặt lên trên, giấy nằm im bên dưới. Cái này cho nhân vật ăn vào tờ giấy —
những dòng kẻ in sẵn chạy ngang trang đều oằn xuống khi đi qua chỗ hắn
đứng, đứt hẳn ở vùng sát người, và một dấu canh trục ở góc dưới cũng chảy
nhão rồi nhỏ giọt. Không phải hắn nóng trong truyện; hắn nóng đến mức bản
in hỏng.

Chỗ thứ hai: đây là bóng người duy nhất trong cả bộ **tô bằng mực vàng**.
Mười bốn người kia đều là mảng đen trên giấy sáng, chi tiết thì sáng hơn
nền. Ở đây đảo hẳn: thân hắn là mảng sáng nhất tờ giấy, còn mọi chi tiết —
hốc mắt, mép, các đường nứt trên lớp vỏ — đều là mực đen vạch lên mảng
vàng ấy. Bốn màu của máy in Silver Age, không thêm màu nào: vàng làm da,
đỏ pha vào vàng làm bóng đổ, đen làm vết nứt.

Cuối cùng là mấy giọt đang rơi khỏi bàn tay. Cái mà Raxton định ăn cắp là
một mẻ hợp kim lỏng; nó đổ lên người hắn và thấm vào da. Món hàng ấy giờ
vẫn đang chảy khỏi tay hắn, mỗi ngày, và không cách nào cạo ra được.
"""

import math
from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QPainter, QPainterPath, QPen,
                           QTransform)

from theme import INK, INK_SOFT, PAPER_HI, RED, YELLOW, blend

from .art import H, W, Rolls, design, ribbon
from .profile import Profile

SKIN = QColor(YELLOW)                        # da: mực vàng đặc
SHADE = blend(YELLOW, RED, 0.42)             # bóng đổ: vàng pha đỏ, vẫn bốn màu
HOT = blend(YELLOW, PAPER_HI, 0.55)          # chỗ sáng nhất, gần trắng
AXIS = 50.0                                  # trục người, tâm của vùng nóng


# ═══════════════════════════════════════════════════ tờ giấy bị nung
def _sag(x, y):
    """Độ oằn của một dòng kẻ tại (x, y) — càng gần trục người càng võng sâu.

    Hàm chuông theo trục ngang, nhân với độ cao: dòng ở giữa trang võng
    nhiều nhất, dòng sát mép trên và mép dưới gần như thẳng.
    """
    near = math.exp(-((x - AXIS) / 34.0) ** 2)
    high = math.exp(-((y - 66.0) / 46.0) ** 2)
    return near * high * 18.0


def _rules(p):
    """Những dòng kẻ in sẵn của trang giấy, oằn xuống khi đi qua chỗ hắn.

    Vẽ từng đoạn ngắn rồi nối lại, vì cả cái hiệu ứng nằm ở chỗ đường thẳng
    thôi không còn thẳng. Đoạn nào lọt vào vùng sát người thì bỏ hẳn — ở đó
    mực không bám nổi nữa.
    """
    faint = QColor(INK_SOFT)
    faint.setAlpha(120)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(faint, 0.6))

    for i in range(2, 21):
        y = i * 6.0
        line = QPainterPath()
        drawing = False
        for step in range(0, 53):
            x = -2 + step * 2.0
            gap = 15.0 + 7.0 * math.exp(-((y - 70.0) / 34.0) ** 2)
            if abs(x - AXIS) < gap:           # vùng cháy, không còn nét nào
                drawing = False
                continue
            q = QPointF(x, y + _sag(x, y))
            if drawing:
                line.lineTo(q)
            else:
                line.moveTo(q)
                drawing = True
        p.drawPath(line)


def _marks(p):
    """Dấu canh trục bốn góc — riêng góc dưới bên phải thì chảy.

    `marks()` dùng chung vẽ bốn dấu giống hệt nhau. Ở đây ba dấu giữ nguyên
    còn dấu gần hắn nhất bị nung nhão, tụt xuống và nhỏ một giọt: bằng chứng
    rằng thứ hỏng vì sức nóng không chỉ nằm trong tranh mà là cả bản in.
    """
    faint = QColor(INK_SOFT)
    faint.setAlpha(110)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(faint, 0.7))
    for cx, cy in ((9, 11), (91, 11), (9, 109)):
        p.drawLine(QPointF(cx - 3, cy), QPointF(cx + 3, cy))
        p.drawLine(QPointF(cx, cy - 3), QPointF(cx, cy + 3))
        p.drawEllipse(QPointF(cx, cy), 2.2, 2.2)

    cx, cy = 91.0, 109.0                      # dấu đã chảy
    p.drawLine(QPointF(cx - 3, cy + 0.6), QPointF(cx + 3, cy - 0.4))
    p.drawLine(QPointF(cx, cy - 3), QPointF(cx - 0.4, cy + 4.5))
    ring = QPainterPath()
    ring.moveTo(cx - 2.2, cy - 0.4)
    ring.cubicTo(cx - 2.4, cy - 3.0, cx + 2.4, cy - 3.0, cx + 2.2, cy - 0.2)
    ring.cubicTo(cx + 2.0, cy + 3.4, cx - 1.6, cy + 3.6, cx - 2.2, cy - 0.4)
    p.drawPath(ring)
    p.setBrush(faint)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(cx - 0.6, cy + 6.4), 0.9, 1.2)


# ═══════════════════════════════════════════════════ người bằng hợp kim
def _head():
    """Sọ trần, không mũ không mặt nạ — lớp hợp kim chính là da hắn."""
    head = QPainterPath()
    head.moveTo(40.5, 30)
    head.cubicTo(40.5, 18.5, 59.5, 18.5, 59.5, 30)   # vòm sọ
    head.cubicTo(59.5, 34.5, 58.5, 37.5, 57.5, 39.5)  # thái dương
    head.lineTo(55, 44)                       # góc hàm, gãy chứ không tròn
    head.cubicTo(53, 47, 47, 47, 45, 44)      # cằm
    head.lineTo(42.5, 39.5)
    head.cubicTo(41.5, 37.5, 40.5, 34.5, 40.5, 30)
    head.closeSubpath()
    return head


def _torso():
    """Thân trên: vai ngang có múi, eo thắt lại, hông nở ra tới mép khung."""
    torso = QPainterPath()
    torso.moveTo(46, 46)
    torso.cubicTo(39, 49, 32, 53, 28, 62)     # vai trái, có cục cơ delta
    torso.cubicTo(25, 72, 29, 81, 31, 91)     # sườn trái thắt vào eo
    torso.cubicTo(32, 102, 34, 112, 35, 120)
    torso.lineTo(68, 120)
    torso.cubicTo(69, 110, 71, 101, 72, 91)
    torso.cubicTo(75, 81, 78, 72, 75, 62)     # sườn phải lên vai
    torso.cubicTo(71, 53, 64, 49, 57, 46)
    torso.closeSubpath()
    neck = QPainterPath()                     # cổ thuôn, không phải khối hộp
    neck.moveTo(45.5, 41)
    neck.cubicTo(45, 46, 43, 48, 41, 50)
    neck.lineTo(59, 50)
    neck.cubicTo(57, 48, 55, 46, 54.5, 41)
    neck.closeSubpath()
    return torso.united(neck)


def _arm_up():
    """Tay trái giơ lên, bàn tay mở — chỗ hợp kim đang chảy khỏi hắn."""
    arm = ribbon(QPointF(32, 60), QPointF(23, 51), QPointF(19.5, 40), 6.6, 4.4)
    palm = QPainterPath()
    palm.addEllipse(QPointF(18.8, 39.5), 4.8, 4.4)
    return arm.united(palm)


def _arm_down():
    """Tay phải buông xuôi, nắm hờ — cánh tay vẽ đè lên thân nên còn nét nối."""
    arm = ribbon(QPointF(74, 62), QPointF(82, 77), QPointF(80, 93), 6.4, 4.8)
    fist = QPainterPath()
    fist.addEllipse(QPointF(80, 95), 5.0, 4.6)
    return arm.united(fist)


@lru_cache(maxsize=1)
def _figure():
    return (_torso().united(_head()).united(_arm_up())
            .united(_arm_down()))


# gốc mỗi ngón nằm trên đường khớp bàn tay, không chụm về một điểm: chụm một
# điểm thì năm ngón xoè ra thành cái quạt giấy chứ không ra bàn tay
KNUCKLES = (((15.2, 36.0), 106, 8.8), ((17.6, 34.6), 95, 10.6),
            ((20.0, 34.8), 85, 10.0), ((22.2, 36.4), 73, 8.0))
THUMB = ((22.6, 40.6), 20, 7.0)


def _hand(p):
    """Bàn tay giơ cao, năm ngón mở — chỗ hợp kim đang chảy khỏi hắn."""
    p.setBrush(SKIN)
    p.setPen(QPen(INK, 1.2))
    for (rx, ry), ang, length in KNUCKLES + (THUMB,):
        a = math.radians(ang)
        finger = ribbon(QPointF(rx, ry),
                        QPointF(rx + math.cos(a) * length * 0.55,
                                ry - math.sin(a) * length * 0.55),
                        QPointF(rx + math.cos(a) * length,
                                ry - math.sin(a) * length),
                        2.5, 1.8)
        p.drawPath(finger)

    palm = QPainterPath()                     # gan tay vẽ đè lên gốc ngón
    palm.moveTo(14.2, 36.4)
    palm.cubicTo(13.6, 40, 15, 43, 18.4, 43.6)
    palm.cubicTo(21.6, 44, 23.6, 41.6, 23.4, 37.2)
    palm.cubicTo(21, 35.4, 16.6, 35.2, 14.2, 36.4)
    palm.closeSubpath()
    p.drawPath(palm)


def _drips(p):
    """Mấy giọt hợp kim rời khỏi người, đang rơi.

    Giọt vẽ thành hình quả lê ngược: đáy tròn, đuôi vuốt lên — đó là dáng
    một giọt đang rơi chứ không phải một cái đốm nằm yên.
    """
    for cx, cy, r, tail in ((16.5, 47.0, 2.2, 6.0), (21.0, 58.0, 1.5, 4.2),
                            (14.0, 66.0, 1.8, 5.0), (82.5, 103.0, 2.0, 5.4),
                            (77.0, 112.0, 1.4, 3.8)):
        drop = QPainterPath()
        drop.moveTo(cx - r, cy)
        drop.cubicTo(cx - r, cy + r * 1.5, cx + r, cy + r * 1.5, cx + r, cy)
        drop.cubicTo(cx + r * 0.7, cy - tail * 0.6, cx + r * 0.3, cy - tail,
                     cx, cy - tail)
        drop.cubicTo(cx - r * 0.3, cy - tail, cx - r * 0.7, cy - tail * 0.6,
                     cx - r, cy)
        drop.closeSubpath()
        p.setBrush(SKIN)
        p.setPen(QPen(INK, 0.9))
        p.drawPath(drop)
        p.setBrush(HOT)                       # ánh sáng đọng ở đáy giọt
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx - r * 0.25, cy + r * 0.35), r * 0.42, r * 0.5)


def _crust(p, figure):
    """Các đường nứt trên lớp vỏ, cắt theo bóng người.

    Đây là thứ làm cho mảng vàng đọc ra kim loại đang nguội chứ không ra một
    bộ đồ bó. Nứt phải chạy vòng theo khối — ngang bụng, quanh vai — chứ kẻ
    dọc thì hoá ra nếp áo.
    """
    p.save()
    p.setClipPath(figure, Qt.ClipOperation.IntersectClip)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(INK, 0.9))
    seams = (((29, 66), (40, 74), (52, 72), (60, 60)),
             ((33, 88), (44, 92), (58, 86), (73, 74)),
             ((31, 104), (45, 112), (60, 104), (70, 92)),
             ((36, 120), (46, 112), (56, 118), (66, 108)))
    for a, b, c, d in seams:
        crack = QPainterPath()
        crack.moveTo(*a)
        crack.cubicTo(b[0], b[1], c[0], c[1], d[0], d[1])
        p.drawPath(crack)

    p.setPen(QPen(INK, 1.0))                  # xương đòn, mốc duy nhất trên ngực
    collar = QPainterPath()
    collar.moveTo(34, 57)
    collar.cubicTo(42, 62, 58, 62, 69, 56)
    p.drawPath(collar)
    r = Rolls(28091965)                       # ASM #28, 09/1965
    p.setPen(QPen(INK, 0.7))                  # nứt phụ, ngắn và rẽ ngang
    for _ in range(14):
        x, y = r(28, 74), r(56, 118)
        branch = QPainterPath(QPointF(x, y))
        branch.quadTo(QPointF(x + r(-5, 5), y + r(-3, 3)),
                      QPointF(x + r(-9, 9), y + r(-5, 5)))
        p.drawPath(branch)
    p.restore()


def _modelling(p, figure):
    """Ba sắc độ trên cùng một mảng vàng, dựng bằng chính đường bao.

    Bản trước cắt tờ giấy làm đôi rồi tô nửa phải bằng màu bóng: cả cánh tay
    buông xuôi lọt trong nửa ấy và hoá thành một khúc dồi đỏ. Cách đúng là
    lấy bóng người trừ đi chính nó đã dịch chỗ — kết quả là một dải men theo
    đường bao, dày đều, tự vòng quanh cả tay lẫn đầu.
    """
    p.save()
    p.setClipPath(figure, Qt.ClipOperation.IntersectClip)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(SHADE)                         # mép phải: bóng
    p.drawPath(figure.subtracted(figure.translated(-6, -2)))
    p.setBrush(HOT)                           # mép trái: ánh sáng
    p.drawPath(figure.subtracted(figure.translated(5, 2)))
    p.restore()


def _face(p):
    """Mắt, mày và mép — vạch đen trên nền vàng, ngược hẳn mười bốn bức kia."""
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(INK)
    for cx, sign in ((45.5, -1), (54.5, 1)):
        eye = QPainterPath()
        eye.moveTo(cx - 3.0 * 1, 31.5)
        eye.cubicTo(cx - 1.0, 29.6, cx + 1.6, 29.9, cx + 3.0, 31.4)
        eye.cubicTo(cx + 1.4, 33.4, cx - 1.2, 33.4, cx - 3.0, 31.5)
        eye.closeSubpath()
        p.drawPath(eye)

    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(INK, 1.2))
    for cx, dx in ((45.5, -1), (54.5, 1)):    # lông mày chau vào giữa
        brow = QPainterPath()
        brow.moveTo(cx - 3.6 * 1, 28.6 - dx * 0.9)
        brow.quadTo(cx, 26.4 + dx * 1.2, cx + 3.6, 28.4 + dx * 0.9)
        p.drawPath(brow)

    mouth = QPainterPath()                    # mép mím, hai đầu trễ xuống
    mouth.moveTo(45, 40.5)
    mouth.cubicTo(48, 39.4, 52, 39.4, 55, 40.3)
    p.drawPath(mouth)

    p.setPen(QPen(INK, 0.9))                  # gò má, chỗ khối mặt gãy góc
    for cx, side in ((44.0, -1), (56.0, 1)):
        cheek = QPainterPath()
        cheek.moveTo(cx, 33.5)
        cheek.quadTo(cx + side * 1.2, 37, cx + side * 0.2, 40.5)
        p.drawPath(cheek)


# ═══════════════════════════════════════════════════ dựng cả bức
def _paint(p, rect):
    with design(p, rect):
        _rules(p)
        _drips(p)

        # thân vẽ trước, hai cánh tay vẽ đè lên và có viền riêng: hợp hết vào
        # một bóng thì chỗ tay giáp sườn mất nét, cả người thành một khối
        figure = _figure()
        p.setBrush(SKIN)
        p.setPen(QPen(INK, 1.6))
        p.drawPath(_torso().united(_head()))
        p.drawPath(_arm_down())
        p.drawPath(_arm_up())

        _modelling(p, figure)
        p.setBrush(Qt.BrushStyle.NoBrush)     # viền vẽ lại đè lên hai sắc độ
        p.setPen(QPen(INK, 1.6))
        p.drawPath(_torso().united(_head()))
        p.drawPath(_arm_down())
        p.drawPath(_arm_up())

        _hand(p)
        _crust(p, figure)
        _face(p)
        _marks(p)


_STILL = {}


def draw_molten_man(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước.

    Gần hai mươi dòng kẻ, mỗi dòng năm chục đoạn, cộng mấy lớp cắt theo bóng
    người: đắt hơn ngân sách một khung hình. Dựng sẵn vào ảnh đúng cỡ điểm
    ảnh thật rồi dán, như `electro.py` và `scorpion.py`.
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
    name="Molten Man",
    vi_name="Người Kim Loại Nóng Chảy",
    real_name="Mark Raxton",

    tagline="Cả danh sách này cất chiến lợi phẩm trong két. Riêng người này "
            "mặc nó trên người, và không cởi ra được nữa.",

    summary=(
        "Mark Raxton làm phụ tá phòng thí nghiệm cho tiến sĩ Spencer Smythe — "
        "đúng cái ông đã chế ra lũ Spider-Slayer. Hai người đang thử một mẻ "
        "hợp kim lỏng chiết từ một khối thiên thạch nhiễm phóng xạ. Raxton "
        "tính chuyện đơn giản hơn khoa học nhiều: ăn cắp mẻ hợp kim ấy đem "
        "bán. Giằng co trong phòng thí nghiệm, cả mẻ đổ lên người hắn, và da "
        "hắn hút sạch.",

        "Món hàng không bán được nữa vì nó đã là hắn. Lớp hợp kim bám thành "
        "một lớp da vàng óng, khoẻ hơn người thường nhiều lần, chịu đòn tốt, "
        "và toả nhiệt đủ để làm bỏng bất cứ ai chạm vào. Đó cũng là hình phạt "
        "gọn nhất trong cả danh sách chín mươi mốt cái tên: kẻ trộm phải mang "
        "thứ mình lấy trên người suốt phần đời còn lại.",

        "The Amazing Spider-Man #28 (09/1965) của Stan Lee và Steve Ditko đặt "
        "hai chuyện cạnh nhau trong đúng một số báo. Peter Parker tốt nghiệp "
        "trung học — và suýt lỡ buổi lễ vì phải đi ngăn đợt cướp đầu tiên của "
        "Molten Man. Cùng một số báo, một người mặc áo lễ tốt nghiệp rồi cởi "
        "ra, một người mặc thứ không bao giờ cởi được.",

        "Về sau lộ ra rằng Liz Allan — bạn cùng lớp của Peter — là em kế của "
        "Raxton. Hắn đi cướp hoá chất để tìm cách hoàn nguyên, thất bại, rồi "
        "phát điên và bắt cóc chính cô. Nhưng Liz là người duy nhất trong nhà "
        "không quay lưng với hắn: khi cô lấy Harry Osborn, hai người cho "
        "Raxton một chân trưởng bộ phận an ninh ở công ty Osborn. Từ đó hắn "
        "đứng về phía Spider-Man nhiều hơn là đứng đối diện.",
    ),

    powers=(
        "Da là hợp kim: khoẻ hơn người thường nhiều lần, chịu đạn và chịu nện",
        "Toả nhiệt khắp cơ thể, đủ làm bỏng người chạm vào và đốt cháy đồ vật",
        "Bắn được những mảng hợp kim nóng chảy như đạn lửa",
        "Nhiệt độ tăng theo cơn giận — càng mất bình tĩnh càng khó lại gần",
        "Điểm yếu là nước lạnh và chỗ đông cứng: lần đầu thua vì bị hất xuống hồ bơi",
        "Không tắt được: mọi lần thử hoàn nguyên đều hỏng",
    ),

    facts=(
        ("Tên thật", "Mark Raxton"),
        ("Xuất hiện đầu", "ASM #28  ·  09/1965"),
        ("Tác giả", "Stan Lee & Steve Ditko"),
        ("Nghề cũ", "Phụ tá của TS. Spencer Smythe"),
        ("Nguồn gốc", "Hợp kim lỏng từ thiên thạch"),
        ("Người nhà", "Liz Allan, em kế"),
    ),

    blurb="Số báo này còn là số Peter Parker tốt nghiệp trung học. Hai người "
          "cùng nhận một bộ đồ mới trong một đêm: một bộ trả lại được sau "
          "buổi lễ, một bộ thì không.",

    art=draw_molten_man,
    caption="Trang giấy oằn vì sức nóng  ·  dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Molten_Man"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Mark_Raxton_(Earth-616)"),
    ),
)
