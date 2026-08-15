"""
Tinkerer — Phineas Mason.

Ba nhân vật trước đều vẽ được bằng sức mạnh của họ. Ông này thì không có gì
để vẽ ngoài cái nghề, nên chân dung kể bằng bối cảnh: một ông già ngồi dưới
ngọn đèn xưởng, kính lúp gạt lên trán, tạp dề cắm đầy đồ nghề.
"""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainterPath, QPen

from theme import INK, INK_SOFT, PAPER_HI, YELLOW

from .art import design, marks, misprint
from .profile import Profile
from .tinkerer_absolute import ABSOLUTE


# ═══════════════════════════════════════════════════ chân dung vẽ bằng code
def _cone():
    """Quầng sáng của ngọn đèn, loe từ bóng đèn xuống hết khung."""
    cone = QPainterPath()
    cone.moveTo(50, 20)
    cone.lineTo(-22, 140)
    cone.lineTo(122, 140)
    cone.closeSubpath()
    return cone


def _gloom():
    """Phần tối ngoài quầng sáng. Vẽ tràn ra ngoài khung, khung sẽ tự cắt."""
    gloom = QPainterPath()
    gloom.addRect(-60, -40, 220, 200)
    return gloom.subtracted(_cone())


def _lamp():
    """Chao đèn treo và sợi dây."""
    shade = QPainterPath()
    shade.moveTo(41, 5)
    shade.lineTo(59, 5)
    shade.lineTo(70, 19)
    shade.lineTo(30, 19)
    shade.closeSubpath()
    cord = QPainterPath()
    cord.addRect(49.2, -12, 1.6, 17)
    return shade.united(cord)


def _body():
    body = QPainterPath()
    body.moveTo(19, 120)
    body.cubicTo(23, 92, 34, 77, 50, 75)
    body.cubicTo(66, 77, 77, 92, 81, 120)
    body.closeSubpath()
    return body


def _head():
    head = QPainterPath()
    head.moveTo(35, 48)
    head.cubicTo(35, 35, 42, 31, 50, 31)
    head.cubicTo(58, 31, 65, 35, 65, 48)
    head.cubicTo(65, 60, 59, 68, 50, 68)
    head.cubicTo(41, 68, 35, 60, 35, 48)
    head.closeSubpath()
    return head


def _tuft(cx, sign):
    """Túm tóc bạc còn sót lại hai bên thái dương."""
    tuft = QPainterPath()
    for dx, dy, r in ((0, 0, 3.0), (2.2 * sign, 2.0, 2.6), (3.4 * sign, 4.6, 2.1)):
        blob = QPainterPath()
        blob.addEllipse(QPointF(cx + dx, 41 + dy), r, r)
        tuft = tuft.united(blob)
    return tuft


def _moustache():
    """Hai vệt ria rủ xuống hai bên, chỗ giữa mỏng — không phải cái miệng."""
    m = QPainterPath()
    for sign in (-1, 1):
        wing = QPainterPath()
        wing.moveTo(50, 56.2)
        wing.cubicTo(50 + 4 * sign, 55.6, 50 + 8 * sign, 56.4,
                     50 + 10.5 * sign, 60.5)
        wing.cubicTo(50 + 8.5 * sign, 60.2, 50 + 5 * sign, 58.8, 50, 58.6)
        wing.closeSubpath()
        m = m.united(wing)
    return m


def _apron():
    apron = QPainterPath()
    apron.moveTo(37, 85)
    apron.lineTo(63, 85)
    apron.lineTo(65, 120)
    apron.lineTo(35, 120)
    apron.closeSubpath()
    for x0, x1 in ((37.5, 41.5), (58.5, 62.5)):     # hai quai vắt lên vai
        strap = QPainterPath()
        strap.moveTo(x0, 85)
        strap.lineTo(x1, 85)
        strap.lineTo(x1 + (2 if x0 > 50 else -1), 76)
        strap.lineTo(x0 + (3 if x0 > 50 else 0), 76)
        strap.closeSubpath()
        apron = apron.united(strap)
    return apron


def draw_tinkerer(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước."""
    with design(p, rect, h=116):
        # ngọn đèn: quầng vàng ấm giữa khung, phần còn lại chìm trong tối
        p.setPen(Qt.PenStyle.NoPen)
        glow = QColor(YELLOW)
        glow.setAlpha(46)
        p.setBrush(glow)
        p.drawPath(_cone())
        dusk = QColor(INK)
        dusk.setAlpha(30)
        p.setBrush(dusk)
        p.drawPath(_gloom())

        misprint(p, _lamp().united(_body()))

        # bóng đèn, đốm sáng duy nhất trong khung
        bulb = QColor(YELLOW)
        p.setBrush(bulb)
        p.setPen(QPen(INK, 1.2))
        p.drawEllipse(QPointF(50, 21.5), 3.4, 3.4)

        wash = QLinearGradient(0, 30, 0, 70)
        wash.setColorAt(0.0, PAPER_HI)
        wash.setColorAt(1.0, QColor("#D3C7AC"))

        # cổ, vẽ trước để tạp dề và đầu che hai đầu
        neck = QPainterPath()
        neck.addRect(44.5, 60, 11, 19)
        p.setBrush(wash)
        p.setPen(QPen(INK, 1.3))
        p.drawPath(neck)

        # tạp dề, túi trước và mấy cái tuốc nơ vít cắm trong túi
        p.setBrush(wash)
        p.setPen(QPen(INK, 1.3))
        p.drawPath(_apron())
        p.setBrush(INK)
        p.setPen(Qt.PenStyle.NoPen)
        for x, top in ((44.5, 93), (51.5, 91.5), (57.5, 94)):
            p.drawRect(x, top, 2.6, 13)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(INK, 1.2))
        p.drawRect(41, 100, 18, 13)

        # đầu, mấy túm tóc bạc, rồi bộ ria rậm
        p.setBrush(wash)
        p.setPen(QPen(INK, 1.6))
        p.drawPath(_head())
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(INK)
        p.drawPath(_tuft(35, -1))
        p.drawPath(_tuft(65, 1))
        p.drawPath(_moustache())

        # kính tròn: tròng sáng, có mắt bên trong, không phải kẻ giấu mặt
        p.setBrush(QColor("#EFE7D5"))
        p.setPen(QPen(INK, 1.7))
        for cx in (43, 57):
            p.drawEllipse(QPointF(cx, 49), 5.4, 5.4)
        p.setPen(QPen(INK, 1.4))
        p.drawLine(QPointF(48.4, 49), QPointF(51.6, 49))
        p.drawLine(QPointF(37.6, 48), QPointF(34.6, 47))
        p.drawLine(QPointF(62.4, 48), QPointF(65.4, 47))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(INK)
        for cx in (43.6, 56.4):
            p.drawEllipse(QPointF(cx, 49.4), 1.5, 1.5)

        # kính lúp gạt lên trán — ông ta vừa ngẩng đầu lên khỏi bàn nguội
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(INK, 1.2))
        band = QPainterPath()
        band.moveTo(39.5, 40)
        band.cubicTo(45, 37.4, 55, 37.2, 60.5, 39)
        p.drawPath(band)
        p.setBrush(INK)
        p.setPen(QPen(INK, 1.0))
        p.drawEllipse(QPointF(44.5, 35), 2.9, 2.9)
        p.setBrush(QColor("#EFE7D5"))
        p.drawEllipse(QPointF(44.5, 35), 1.3, 1.3)

        # sống mũi và miệng, nằm dưới bộ ria
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(INK_SOFT, 1.1))
        p.drawLine(QPointF(50, 51), QPointF(48.4, 54.8))
        p.setPen(QPen(INK, 1.3))
        p.drawLine(QPointF(46.5, 61.5), QPointF(53.5, 61.5))

        marks(p)


# ═══════════════════════════════════════════════════════════════ hồ sơ
PROFILE = Profile(
    name="Tinkerer",
    vi_name="Thợ Vặt",
    real_name="Phineas Mason",

    tagline="Không siêu năng lực, không mộng thống trị thế giới. Chỉ là ông "
            "già sửa đồ — nhưng đồ nghề của nửa danh sách này đi qua tay ông ta.",

    summary=(
        "Phineas Mason xuất hiện trong The Amazing Spider-Man #2 (05/1963), "
        "cùng số báo với Vulture. Cửa hàng của ông ta nhận sửa radio, và mỗi "
        "cái radio trả về nhà khách đều kèm theo một thiết bị nghe lén. Ở lần "
        "chạm trán đầu, Spider-Man lột mặt nạ ông ta ra và thấy một gương mặt "
        "người ngoài hành tinh — về sau Marvel giải thích lại: toàn bộ màn "
        "người ngoài hành tinh chỉ là một trò dàn dựng, Mason là người thường "
        "từ đầu đến cuối.",

        "Vai trò thật sự của Tinkerer không nằm ở mấy vụ ông ta tự đi ăn hàng. "
        "Ông ta là thợ của giới tội phạm: chế đồ, sửa đồ, nâng cấp khí tài cho "
        "bất kỳ ai chịu trả tiền. Chiếc bánh xe khổng lồ của Big Wheel (ASM "
        "#182, 1978) là hàng đặt từ xưởng của ông ta. Chạy vặt cho ông ta là "
        "con robot tên Toy.",

        "Đây là nghịch lý đáng chú ý nhất trong cả danh sách: kẻ yếu nhất về "
        "thể chất lại là kẻ dai dẳng nhất. Bắt Vulture thì bầu trời yên được "
        "một thời gian; bắt Tinkerer thì chẳng yên được gì, vì thứ ông ta bán "
        "là dịch vụ, và lúc nào cũng có người cần.",
    ),

    powers=(
        "Không có siêu năng lực, cũng không đánh đấm gì",
        "Chế được gần như mọi thứ từ đồ điện tử nhặt nhạnh",
        "Sửa và nâng cấp khí tài cho bất kỳ ai trả tiền",
        "Con robot Toy làm chân sai vặt",
        "Vỏ bọc hoàn hảo: một cửa hàng sửa đồ tầm thường",
    ),

    facts=(
        ("Tên thật", "Phineas Mason"),
        ("Xuất hiện đầu", "ASM #2  ·  05/1963"),
        ("Tác giả", "Stan Lee & Steve Ditko"),
        ("Nghề", "Thợ sửa đồ, chế khí tài thuê"),
        ("Hàng đã giao", "Big Wheel (ASM #182)"),
        ("Trên màn ảnh", "Michael Chernus, Homecoming (2017)"),
    ),

    blurb="Cả danh sách này đầy những kẻ muốn đoạt lấy thế giới. Tinkerer chỉ "
          "muốn cái hoá đơn được thanh toán đúng hạn.",

    art=draw_tinkerer,
    caption="Chân dung dựng lại bằng code",

    # Bấm nút tiến hoá để mở dạng Absolute — cái tên đã sang tay.
    evolution=ABSOLUTE,
    evolve_label="Evolve",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Tinkerer_(Marvel_Comics)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Phineas_Mason_(Earth-616)"),
    ),
)
