"""
Doctor Octopus — Otto Octavius.

Chân dung vẽ bằng code: bốn càng máy vươn ra bốn phía, thân người bè, đầu
tóc bát úp và cặp kính tròn. Muốn dùng ảnh thật thì thả file vào
assets/characters/ rồi điền image="doctor-octopus.jpg".
"""

import math

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainterPath, QPen

from theme import INK, INK_SOFT, PAPER_HI, YELLOW

from .art import curve_at, curve_normal, design, feather, marks, misprint, ribbon
from .profile import Profile

# Bốn càng máy: (gốc, điểm uốn, ngọn). Hai càng trái, hai càng phải đối xứng.
ARMS = (
    (QPointF(45, 74), QPointF(22, 56), QPointF(7, 21)),
    (QPointF(44, 84), QPointF(15, 82), QPointF(5, 55)),
    (QPointF(55, 74), QPointF(78, 56), QPointF(93, 21)),
    (QPointF(56, 84), QPointF(85, 82), QPointF(95, 55)),
)


# ═══════════════════════════════════════════════════ chân dung vẽ bằng code
def _claw(tip, aim):
    """Càng kẹp hai ngạnh ở đầu mỗi cánh tay."""
    claw = feather(tip, aim - 32, 8.5, 1.9)
    return claw.united(feather(tip, aim + 32, 8.5, 1.9))


def _rig():
    """Toàn bộ bộ càng: bốn dải thuôn, mỗi dải kết thúc bằng một cái kẹp."""
    rig = QPainterPath()
    for p0, p1, p2 in ARMS:
        rig = rig.united(ribbon(p0, p1, p2, 5.6, 2.3))
        dx, dy = p2.x() - p1.x(), p2.y() - p1.y()
        rig = rig.united(_claw(p2, math.degrees(math.atan2(dy, dx))))
    return rig


def _torso():
    torso = QPainterPath()
    torso.moveTo(27, 120)
    torso.cubicTo(28, 94, 36, 76, 50, 74)
    torso.cubicTo(64, 76, 72, 94, 73, 120)
    torso.closeSubpath()
    return torso


def _neck():
    neck = QPainterPath()
    neck.addRect(46, 54, 8, 24)
    return neck


def _collar():
    """Cổ áo dựng, che chân cổ để nó không thành một cột trắng."""
    collar = QPainterPath()
    collar.moveTo(35, 85)
    collar.lineTo(47, 70)
    collar.lineTo(53, 70)
    collar.lineTo(65, 85)
    collar.closeSubpath()
    return collar


def _head():
    head = QPainterPath()
    head.moveTo(35, 43)
    head.cubicTo(35, 32, 42, 28, 50, 28)
    head.cubicTo(58, 28, 65, 32, 65, 43)
    head.cubicTo(65, 55, 58, 63, 50, 63)
    head.cubicTo(42, 63, 35, 55, 35, 43)
    head.closeSubpath()
    return head


def _hair():
    """Tóc bát úp: vòm kín, mái cắt ngang phăng phăng trên chân mày."""
    hair = QPainterPath()
    hair.moveTo(34, 40)
    hair.cubicTo(33, 28, 41, 24, 50, 24)
    hair.cubicTo(59, 24, 67, 28, 66, 40)
    hair.closeSubpath()
    # tóc phủ xuống hai bên tai, đúng kiểu cắt bát
    for x0, x1 in ((34.2, 38.4), (61.6, 65.8)):
        tab = QPainterPath()
        tab.moveTo(x0, 38)
        tab.lineTo(x1, 38)
        tab.lineTo(x1 - 0.6, 47)
        tab.lineTo(x0 + 0.6, 47)
        tab.closeSubpath()
        hair = hair.united(tab)
    return hair


def draw_octopus(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước."""
    with design(p, rect, h=114):
        rig = _rig()
        misprint(p, rig.united(_torso()))

        # đốt càng: vạch sáng cắt ngang, cho ra chất kim loại nối khúc
        joint = QColor(PAPER_HI)
        joint.setAlpha(78)
        p.setPen(QPen(joint, 1.1))
        p.setClipPath(rig)
        for p0, p1, p2 in ARMS:
            for i in range(1, 13):
                t = i / 13.0
                c = curve_at(p0, p1, p2, t)
                nx, ny = curve_normal(p0, p1, p2, t)
                w = 5.6 + (2.3 - 5.6) * t + 0.6
                p.drawLine(QPointF(c.x() + nx * w, c.y() + ny * w),
                           QPointF(c.x() - nx * w, c.y() - ny * w))
        p.setClipping(False)

        # đai kim loại quanh thân — chỗ bốn càng cắm vào lưng
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(joint, 1.4))
        p.setClipPath(_torso())
        p.drawLine(QPointF(26, 80), QPointF(74, 80))
        p.drawLine(QPointF(26, 90), QPointF(74, 90))
        p.setPen(QPen(joint, 2.4))
        for x in (36, 50, 64):
            p.drawPoint(QPointF(x, 85))
        p.setClipping(False)

        # cổ, cổ áo, rồi mặt
        wash = QLinearGradient(0, 26, 0, 64)
        wash.setColorAt(0.0, PAPER_HI)
        wash.setColorAt(1.0, QColor("#D3C7AC"))
        p.setBrush(wash)
        p.setPen(QPen(INK, 1.3))
        p.drawPath(_neck())
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(INK)
        p.drawPath(_collar())
        p.setBrush(wash)
        p.setPen(QPen(INK, 1.6))
        p.drawPath(_head())

        # tóc bát úp
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(INK)
        p.drawPath(_hair())

        # cặp kính tròn: gọng dày, tròng tối, một vệt loá vắt qua
        p.setBrush(INK)
        p.setPen(QPen(INK, 2.2))
        for cx in (43, 57):
            p.drawEllipse(QPointF(cx, 46.5), 5.6, 5.6)
        p.drawLine(QPointF(48.6, 46.5), QPointF(51.4, 46.5))   # cầu kính
        p.drawLine(QPointF(37.4, 46.5), QPointF(34.2, 45))     # gọng bên trái
        p.drawLine(QPointF(62.6, 46.5), QPointF(65.8, 45))     # gọng bên phải
        glare = QColor(YELLOW)
        glare.setAlpha(190)
        p.setPen(QPen(glare, 1.7))
        for cx in (43, 57):
            p.drawLine(QPointF(cx - 3.5, 44.3), QPointF(cx + 1.5, 48.3))

        # miệng mím thành một vạch, cùng nếp hằn hai bên
        p.setPen(QPen(INK, 1.6))
        p.drawLine(QPointF(45, 56.5), QPointF(55, 56.5))
        crease = QColor(INK_SOFT)
        crease.setAlpha(150)
        p.setPen(QPen(crease, 0.9))
        p.drawLine(QPointF(41.5, 52.5), QPointF(43.5, 58))
        p.drawLine(QPointF(58.5, 52.5), QPointF(56.5, 58))

        marks(p)


# ═══════════════════════════════════════════════════════════════ hồ sơ
PROFILE = Profile(
    name="Doctor Octopus",
    vi_name="Bác Sĩ Bạch Tuộc",
    real_name="Otto Gunther Octavius",

    tagline="Bốn càng máy điều khiển bằng ý nghĩ, hàn chặt vào lưng một nhà "
            "vật lý hạt nhân — và không gỡ ra được nữa.",

    summary=(
        "Otto Octavius là nhà vật lý hạt nhân có hạng. Ông ta tự thiết kế bộ "
        "đai bốn càng máy để thao tác vật liệu phóng xạ từ xa mà không phải "
        "chạm tay vào. Trong The Amazing Spider-Man #3 (07/1963), một vụ nổ "
        "trong phòng thí nghiệm hàn luôn bộ đai vào cơ thể ông ta — và làm "
        "hỏng thứ gì đó trong đầu.",

        "Bốn càng ấy nghe theo ý nghĩ, vươn dài ra, nhấc được cả tấn và vung "
        "nhanh hơn tay người rất nhiều. Nhưng thứ khiến Octavius nguy hiểm "
        "không nằm ở mấy cái càng, mà ở cái đầu. Ông ta là kẻ đầu tiên đánh "
        "bại Spider-Man một cách trọn vẹn, khiến cậu nhóc mất sạch tự tin, và "
        "cũng chính là người dựng nên Sinister Six (ASM Annual #1, 1964).",

        "Ở mạch Master Planner (ASM #31–33, 1965), Octavius chôn Spider-Man "
        "dưới hàng tấn sắt thép — dẫn tới cảnh Peter gồng mình nâng cả đống "
        "đổ nát lên, một trong những trang truyện được in lại nhiều nhất lịch "
        "sử Marvel. Gần năm mươi năm sau ông ta còn đi xa hơn: tráo ý thức "
        "với Peter Parker rồi tự mình làm Spider-Man suốt mạch Superior "
        "Spider-Man (2013).",
    ),

    powers=(
        "Bốn càng máy điều khiển bằng ý nghĩ, vươn dài và bám được mọi mặt",
        "Mỗi càng nhấc được vài tấn, vung nhanh hơn tay người",
        "Trí óc của một nhà vật lý hạt nhân hàng đầu",
        "Đầu óc chiến thuật: dựng và cầm đầu Sinister Six",
        "Cơ thể vẫn là người thường — điểm yếu nằm đúng ở đó",
    ),

    facts=(
        ("Tên thật", "Otto G. Octavius"),
        ("Xuất hiện đầu", "ASM #3  ·  07/1963"),
        ("Tác giả", "Stan Lee & Steve Ditko"),
        ("Nghề cũ", "Nhà vật lý hạt nhân"),
        ("Băng nhóm", "Sinister Six — người sáng lập"),
        ("Trên màn ảnh", "Alfred Molina, Spider-Man 2 (2004)"),
    ),

    blurb="Green Goblin cướp đi người Peter Parker yêu. Doctor Octopus cướp "
          "đi chính Peter Parker.",

    art=draw_octopus,
    caption="Chân dung dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Doctor_Octopus"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Otto_Octavius_(Earth-616)"),
    ),
)
