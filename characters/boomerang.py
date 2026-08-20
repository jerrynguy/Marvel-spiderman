"""
Boomerang — Fred Myers.

Mười lăm chân dung trước đều nhìn ngang tầm mắt, trừ Green Goblin nằm dưới
đất ngước lên. Bức này nhìn **chếch từ trên cao xuống**, và đó là điều kiện
bắt buộc chứ không phải một cách bày cho lạ: đường bay của cái boomerang là
một vòng khép nằm ngang, hạ mắt xuống ngang tầm người thì cả cái vòng ấy
dẹp thành một vạch.

Bố cục dựng quanh đúng một chỗ chồng lấp. Vòng bay cắt làm hai nửa: nửa gần
vẽ **đè lên chân hắn**, nửa xa bị chính hắn che mất. Một chỗ giao nhau ấy
thôi là mặt giấy có chiều sâu, thay vì một sợi dây nằm bẹp. Cộng thêm hai
thứ nữa của mặt đất: bóng đổ kéo dài sang phải, và đám sỏi mái nhà thưa dần
về phía trên.

Trên vòng chỉ có đúng hai cái boomerang: một cái vừa rời khỏi tay, một cái
đang lao về sau gáy hắn. Toàn bộ khúc giữa để cho nét đứt gánh. Hai vật ấy
là cùng một vật ở hai đầu một vòng — cũng là toàn bộ tiểu sử Fred Myers:
ném đi cái gì rồi cũng quay lại đúng chỗ cũ, và lần cuối cùng, thứ quay về
là chính hắn.

Bản đầu nhìn thẳng đứng từ trên xuống, đúng kiểu người ta vẽ sơ đồ đường
bay thật. Vẽ ra bốn lần đều hỏng: từ góc ấy một con người rút lại còn đỉnh
đầu với hai vai, và tất cả đọc ra một con bọ nằm ngửa. Ghi lại đây để khỏi
ai thử lại — góc cao chếch giữ được nguyên cái vòng mà vẫn còn ra người.
"""

import math
from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QPainter, QPainterPath, QPen,
                           QTransform)

from theme import INK, INK_SOFT, PAPER_HI, RED

from .art import Rolls, design, marks, misprint, ribbon
from .profile import Profile

HEAD = QPointF(46, 34)           # đỉnh đầu — nhìn chếch từ trên nên bẹt lại
FOOT = 102.0                     # đường chân đứng, cũng là gốc của bóng đổ
THROWN = QPointF(20.5, 27.0)     # chỗ cái boomerang vừa rời khỏi tay
BACK = QPointF(63.0, 29.0)       # chỗ nó đang lao về, ngay sau gáy


# ═══════════════════════════════════════════════════ mặt đất, nhìn từ trên
def _gravel(p):
    """Sỏi trên mái nhà.

    Nhìn chếch từ trên thì hai phần ba khung là mặt đất. Sỏi thưa dần về
    phía trên — xa thì hạt nhỏ lại và sát vào nhau — nên chính đám sỏi này
    làm cái mặt phẳng ấy lùi ra sau.
    """
    r = Rolls(81071966)                       # Tales to Astonish #81, 07/1966
    p.setPen(Qt.PenStyle.NoPen)
    for _ in range(120):
        y = r(16, 118)
        far = (y - 16) / 102.0                # 0 ở xa, 1 ở gần
        speck = QColor(INK_SOFT)
        speck.setAlpha(int(12 + far * 30))
        p.setBrush(speck)
        p.drawEllipse(QPointF(r(3, 97), y),
                      0.4 + far * 1.0, 0.3 + far * 0.7)


# ═══════════════════════════════════════════════════ cái boomerang
def _rang(cx, cy, angle, size):
    """Một cái boomerang: hai cánh chụm ở khuỷu, thuôn dần ra hai đầu.

    Bản trước dựng bằng hai đường cong nối hai đầu cánh — ra một chiếc lá chứ
    không ra chữ V. Phải là hai nhánh rời chụm ở khuỷu thì mới đọc ra.
    """
    rang = QPainterPath()
    for side in (1, -1):
        a = math.radians(side * 52)
        tip = QPointF(math.cos(a) * size, math.sin(a) * size)
        mid = QPointF(math.cos(a) * size * 0.55 + size * 0.10,
                      math.sin(a) * size * 0.55)
        rang = rang.united(ribbon(QPointF(0, 0), mid, tip, 2.6, 1.0))
    elbow = QPainterPath()
    elbow.addEllipse(QPointF(0, 0), 2.6, 2.6)
    rang = rang.united(elbow)

    t = QTransform()
    t.translate(cx, cy)
    t.rotate(angle)
    return t.map(rang)


def _flight_near():
    """Nửa vòng bay ở phía trước: rời tay, vòng xuống sát người xem."""
    arc = QPainterPath()
    arc.moveTo(21, 31)
    arc.cubicTo(9, 46, 8, 74, 26, 90)
    arc.cubicTo(44, 105, 74, 100, 86, 76)
    return arc


def _flight_far():
    """Nửa vòng bay ở phía sau: leo ngược lên rồi quặt về sau gáy hắn.

    Tách làm hai nửa để nửa gần vẽ đè lên chân hắn còn nửa xa bị người che
    mất — chỉ một chỗ chồng lấp ấy thôi là cả bức có chiều sâu, thay vì một
    vòng dây nằm bẹp trên giấy.
    """
    arc = QPainterPath()
    arc.moveTo(86, 76)
    arc.cubicTo(93, 60, 90, 38, 76, 30)
    arc.cubicTo(72, 28, 68, 28, 65, 29)
    return arc


def _path_line(p, arc):
    """Nét đứt vạch lại đường bay — nét đứt để đọc ra đường đi, không ra vật."""
    trail = QColor(RED)
    trail.setAlpha(185)
    pen = QPen(trail, 1.1)
    pen.setStyle(Qt.PenStyle.DashLine)
    pen.setDashPattern([3.4, 3.0])
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(pen)
    p.drawPath(arc)


# ═══════════════════════════════════════════════════ người, nhìn chếch từ trên
def _skull():
    """Đầu: bẹt theo chiều dọc vì ta đang nhìn xuống đỉnh sọ chứ không nhìn ngang."""
    skull = QPainterPath()
    skull.addEllipse(HEAD, 9.0, 8.0)
    return skull


def _fins():
    """Hai vây trên mũ, chìa ra hai bên thái dương.

    Đây là thứ duy nhất trên người hắn có hình chữ V, và cũng là thứ cứu cái
    đầu khỏi thành một quả trứng vô danh ở góc nhìn này.
    """
    fins = QPainterPath()
    for side in (-1, 1):
        fin = QPainterPath()
        fin.moveTo(HEAD.x() + side * 7.4, HEAD.y() - 1.4)
        fin.lineTo(HEAD.x() + side * 15.0, HEAD.y() + 2.2)
        fin.lineTo(HEAD.x() + side * 13.8, HEAD.y() + 4.8)
        fin.lineTo(HEAD.x() + side * 7.0, HEAD.y() + 2.8)
        fin.closeSubpath()
        fins = fins.united(fin)
    return fins


def _torso():
    """Thân bị nén lại: nhìn chếch từ trên thì vai rộng ra còn thân ngắn đi."""
    torso = QPainterPath()
    torso.moveTo(40, 42)
    torso.cubicTo(35, 44, 32, 49, 32, 56)     # vai trái
    torso.cubicTo(32, 64, 35, 70, 37, 75)     # sườn trái xuống hông
    torso.lineTo(58, 74)
    torso.cubicTo(60, 68, 63, 62, 63, 55)     # sườn phải lên vai
    torso.cubicTo(63, 48, 59, 43, 52, 41)
    torso.closeSubpath()
    return torso


def _arm_throw():
    """Tay ném đã vung hết đà, chìa lên phía trên bên trái, bàn tay vừa buông."""
    arm = ribbon(QPointF(33, 50), QPointF(25, 40), QPointF(22, 31), 5.0, 3.6)
    fist = QPainterPath()
    fist.addEllipse(QPointF(21.6, 30.2), 3.4, 3.0)
    return arm.united(fist)


def _arm_free():
    """Tay kia hất ra sau lấy thăng bằng, đúng kiểu người ném bóng chày."""
    arm = ribbon(QPointF(63, 52), QPointF(72, 60), QPointF(74, 70), 4.6, 3.4)
    fist = QPainterPath()
    fist.addEllipse(QPointF(74.2, 71.4), 3.2, 2.9)
    return arm.united(fist)


def _legs():
    """Hai chân ngắn và chắc: ở góc nhìn này chúng bị nén gần một nửa chiều dài."""
    near = ribbon(QPointF(42, 74), QPointF(40, 86), QPointF(41, 98), 7.0, 5.4)
    far = ribbon(QPointF(56, 73), QPointF(59, 84), QPointF(58, 95), 6.6, 5.2)
    boots = QPainterPath()
    for cx, cy, rx, ry in ((39.5, 100.5, 6.2, 4.0), (57.0, 97.0, 5.8, 3.8)):
        boot = QPainterPath()
        boot.addEllipse(QPointF(cx, cy), rx, ry)
        boots = boots.united(boot)
    return near.united(far).united(boots)


@lru_cache(maxsize=1)
def _figure():
    return (_legs().united(_torso()).united(_arm_throw())
            .united(_arm_free()).united(_fins()).united(_skull()))


def _shadow(p):
    """Bóng đổ, hắt về phía người xem: lật ngược quanh đường chân và ép dẹt.

    Không có nó thì cả bức chỉ là mấy mảng mực nằm bẹp trên giấy; có nó thì
    lập tức đọc ra một người đang đứng trên mặt đất, còn ta thì ở trên cao.
    Bóng tô mực nhạt và không kèm bản in lệch trục — nó vốn không có thật.
    """
    # (x, y) -> (x + 0.55*(FOOT - y), FOOT + 0.16*(FOOT - y)): càng cao khỏi
    # mặt đất thì bóng càng bị kéo dài sang phải và ép sát xuống
    t = QTransform(1.0, 0.0, -0.55, -0.16, 0.55 * FOOT, 1.16 * FOOT)
    dim = QColor(INK)
    dim.setAlpha(58)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(dim)
    p.drawPath(t.map(_figure()))


def _goggles(p):
    """Hai mắt kính: mảng sáng đặc, thứ duy nhất trên mặt.

    Bản trước vẽ mép kính bằng một nét cong vắt ngang dưới đỉnh đầu — ở cỡ
    thật nó đọc ra một cái miệng đang cười. Mảng đặc thì thành kính.
    """
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(PAPER_HI))
    for cx, cy, rx, ry, ang in ((42.0, 37.4, 2.9, 1.4, 14),
                                (50.2, 36.6, 2.5, 1.25, -6)):
        p.save()
        p.translate(cx, cy)
        p.rotate(ang)
        p.drawEllipse(QPointF(0, 0), rx, ry)
        p.restore()


def _seams(p, figure):
    """Nét chia mảng và mấy đường trên mũ — cắt theo bóng người."""
    p.save()
    p.setClipPath(figure, Qt.ClipOperation.IntersectClip)
    seam = QColor(PAPER_HI)
    seam.setAlpha(108)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(seam, 1.3))

    crown = QPainterPath()                    # sống mũ chạy dọc đỉnh đầu
    crown.moveTo(40.5, 30)
    crown.cubicTo(45, 31.6, 49, 31.6, 52.5, 30.4)
    p.drawPath(crown)

    jaw = QPainterPath()                      # cằm, tách đầu khỏi ngực
    jaw.moveTo(40, 40)
    jaw.cubicTo(43.5, 42.6, 49, 42.6, 52.5, 39.6)
    p.drawPath(jaw)

    collar = QPainterPath()                   # đường vai, chỗ cổ chìm vào thân
    collar.moveTo(33, 47)
    collar.cubicTo(40, 53, 54, 53, 62, 46)
    p.drawPath(collar)

    belt = QPainterPath()                     # thắt lưng, mốc chia thân với chân
    belt.moveTo(35, 72)
    belt.cubicTo(43, 77, 52, 77, 60, 71)
    p.drawPath(belt)

    arm = QPainterPath()                      # rìa trong tay phải, tách khỏi sườn
    arm.moveTo(63, 50)
    arm.cubicTo(67, 56, 70, 62, 71, 68)
    p.drawPath(arm)

    other = QPainterPath()                    # rìa trong tay ném
    other.moveTo(34, 49)
    other.cubicTo(31, 44, 28, 38, 26, 33)
    p.drawPath(other)

    p.setPen(QPen(seam, 1.1))
    for x0, y0, x1, y1 in ((36, 76, 38, 92), (57, 75, 58, 90)):
        gap = QPainterPath(QPointF(x0, y0))   # khe giữa hai chân
        gap.quadTo(QPointF((x0 + x1) / 2 - 1, (y0 + y1) / 2), QPointF(x1, y1))
        p.drawPath(gap)
    p.restore()


# ═══════════════════════════════════════════════════ dựng cả bức
def _paint(p, rect):
    with design(p, rect):
        _gravel(p)
        _shadow(p)
        _path_line(p, _flight_far())          # nửa xa: người sẽ che bớt

        figure = _figure()
        misprint(p, figure)
        _seams(p, figure)
        _goggles(p)

        _path_line(p, _flight_near())         # nửa gần: vẽ đè lên chân hắn

        # hai cái boomerang: cùng một vật, ở hai đầu của một vòng
        p.setBrush(INK)
        p.setPen(QPen(PAPER_HI, 0.9))
        p.drawPath(_rang(THROWN.x(), THROWN.y(), -140, 8.4))
        p.drawPath(_rang(BACK.x(), BACK.y(), 40, 8.4))

        marks(p)


_STILL = {}


def draw_boomerang(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước.

    Chín chục hạt sỏi, một bóng đổ hợp từ năm mảng, cộng lớp mực lệch trục:
    dựng sẵn vào ảnh đúng cỡ điểm ảnh thật rồi dán, như `electro.py`.
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
    name="Boomerang",
    vi_name="Người Ném Boomerang",
    real_name="Frederick 'Fred' Myers",
    keys=("Fred Myers",),

    tagline="Một tay ném bóng chày nhà nghề bị cấm thi đấu vì nhận tiền dàn "
            "xếp. Hắn đổi sang ném thứ khác — và thứ ấy thì luôn quay lại.",

    summary=(
        "Fred Myers sinh ở Úc, sang Mỹ từ bé, và lớn lên với đúng một tài "
        "sản: cánh tay ném. Hết trung học là vào giải nhỏ, vài năm sau lên "
        "giải nhà nghề. Rồi trong vòng một mùa, hắn bị cấm thi đấu vĩnh viễn "
        "vì nhận tiền dàn xếp tỉ số. Cánh tay vẫn còn nguyên, chỉ là chẳng "
        "còn sân nào cho nó nữa.",

        "Tổ chức Secret Empire tìm đến đúng lúc ấy. Họ đưa hắn bộ đồ, cặp "
        "giày phản lực điều khiển bằng mạch gắn trong mũ, và một kho vũ khí "
        "chỉ có một hình dáng duy nhất. Tales to Astonish #81 (07/1966) của "
        "Stan Lee và Jack Kirby cho hắn ra mắt bằng một việc vặt: đi cướp "
        "quả tên lửa Orion, và cố hết sức tránh chạm mặt Hulk. Giống Beetle, "
        "hắn không mở màn sự nghiệp bằng Người Nhện — Người Nhện là chỗ hắn "
        "trôi dạt tới sau.",

        "Kho vũ khí ấy là phần vui nhất của hồ sơ này, vì nó nghiêm túc một "
        "cách buồn cười. Shatterang nổ bằng hai chục quả lựu đạn; razorang "
        "cắt đứt thép; gasarang phun hơi cay; screamerang phát sóng âm; còn "
        "có gluemerang, flamerang, tracerang biết bám mục tiêu, và multirang "
        "tách làm nhiều cái nhỏ giữa đường bay. Bản thân hắn không có một "
        "siêu năng lực nào: tất cả nằm ở tay ném và ở cái tủ đồ.",

        "Suốt bốn thập kỷ, Boomerang là hạng ác nhân đi thuê — Sinister "
        "Syndicate, đánh mướn, thua, ra tù, lại đi thuê. Rồi Superior Foes "
        "of Spider-Man (2013, Nick Spencer và Steve Lieber) để hắn tự kể "
        "chuyện đời mình, và cái giọng ba hoa dối trá ấy biến hắn thành nhân "
        "vật được yêu nhất trong đám ác nhân hạng bét. Spencer đẩy tiếp: khi "
        "viết Amazing Spider-Man, ông cho Fred Myers dọn vào ở chung phòng "
        "trọ với Peter Parker. Và trong Sinister War (2021), hắn lao vào "
        "Morlun để cứu chính Peter, bị hút cạn sinh lực, rồi bị quăng sang "
        "một bên. Cú ném cuối cùng của đời hắn là cú duy nhất không quay về.",
    ),

    powers=(
        "Không có siêu năng lực — chỉ có cánh tay ném của một cầu thủ nhà nghề",
        "Ném trúng đích ở tầm xa, tính được cả đường vòng và điểm quay lại",
        "Shatterang nổ, razorang cắt thép, gasarang hơi cay, screamerang sóng âm",
        "Gluemerang, flamerang, tracerang bám mục tiêu, multirang tách giữa đường",
        "Giày phản lực điều khiển bằng ý nghĩ qua mạch trong mũ: hai giờ bay",
        "Điểm yếu là chính hắn: ba hoa, tham vặt, và luôn phản bội trước khi bị phản",
    ),

    facts=(
        ("Tên thật", "Frederick Myers"),
        ("Xuất hiện đầu", "Tales to Astonish #81"),
        ("Thời điểm", "07/1966"),
        ("Tác giả", "Stan Lee & Jack Kirby"),
        ("Nghề cũ", "Ném bóng chày nhà nghề"),
        ("Đối thủ đầu", "Hulk, không phải Nhện"),
    ),

    blurb="Cả danh sách này chờ ngày quay lại để đánh tiếp. Fred Myers thì "
          "quay lại để ở ghép, nấu ăn dở, quỵt tiền nhà — rồi chết thay cho "
          "đúng người mình đã dành cả đời để cướp của.",

    art=draw_boomerang,
    caption="Nhìn chếch từ trên cao  ·  dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Boomerang_(character)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Frederick_Myers_(Earth-616)"),
    ),
)
