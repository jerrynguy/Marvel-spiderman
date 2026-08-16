"""
Living Brain — cỗ máy của Giáo sư Petty, hãng I.C.M.

Sáu hồ sơ trước đều là người. Cái này thì không, nên chân dung cũng phải đọc
ra ngay là một cỗ máy: thân tủ vuông vức, đối xứng tuyệt đối, đứng trên bệ có
bánh xe. Toàn bộ khối máy là mực đen, mọi chi tiết đều là mặt đồng hồ sáng
nổi lên trên nền đen — ngược hẳn với những hồ sơ kia.

Hai thứ kể lại đúng câu chuyện của ASM #8: cuộn băng giấy đục lỗ nhả ra từ
khe in, mang câu trả lời không ai đọc nổi; và vết nứt toác ngay trên bảng
điều khiển giữa ngực, chỗ người thợ bị đẩy ngã vào làm cỗ máy phát điên.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainterPath, QPen, QPolygonF

from theme import INK, PAPER_HI

from .art import (Rolls, curve_at, curve_normal, design, fan, marks, mirrored,
                  misprint, ribbon)
from .profile import Profile

PANEL = QColor("#EFE7D5")     # mặt đồng hồ, mặt kính — chỗ sáng nhất
DIM = QColor("#C6B896")       # phần lõm, mặt số đã ố
SEED = 8                      # đổi số này là đổi thế đục lỗ trên băng giấy

# Băng giấy: nhả ra từ khe in ở cằm rồi rủ thẳng xuống, men theo sườn phải.
TAPE = (QPointF(56, 45.5), QPointF(74, 58), QPointF(76, 118))

ARM = (QPointF(30, 57), QPointF(19, 74), QPointF(21, 90))   # trục cánh tay
ARM_W = (4.6, 3.0)                                           # gốc dày, cổ nhỏ


# ═══════════════════════════════════════════════════ chân dung vẽ bằng code
def _arm_curve(sign):
    """Ba điểm điều khiển của cánh tay; sign > 0 là bên phải."""
    if sign > 0:
        return tuple(QPointF(100 - q.x(), q.y()) for q in ARM)
    return ARM


def _arm(sign):
    """Một cánh tay ống nối đốt, đầu là càng kẹp hai ngạnh."""
    if sign > 0:
        return mirrored(_arm(-1))
    tube = ribbon(*ARM, *ARM_W)
    return tube.united(fan(QPointF(21, 90.5), ((62, 11, 1.7), (118, 11, 1.7))))


def _chassis():
    """Toàn bộ khối máy hợp thành một bóng liền — không chồng path rời."""
    body = QPainterPath()
    body.addRoundedRect(33, 15, 34, 32, 5, 5)         # đầu

    neck = QPainterPath()
    neck.addRect(43.5, 43, 13, 11)
    shoulders = QPainterPath()
    shoulders.addRoundedRect(28, 50, 44, 10, 3, 3)
    body = body.united(neck).united(shoulders)

    cabinet = QPainterPath()                          # thân tủ, hơi loe xuống
    cabinet.moveTo(34, 58)
    cabinet.lineTo(66, 58)
    cabinet.lineTo(68, 99)
    cabinet.lineTo(32, 99)
    cabinet.closeSubpath()
    body = body.united(cabinet)

    plinth = QPainterPath()                           # bệ máy
    plinth.moveTo(28, 97)
    plinth.lineTo(72, 97)
    plinth.lineTo(78, 109)
    plinth.lineTo(22, 109)
    plinth.closeSubpath()
    body = body.united(plinth)

    for cx in (32, 68):                               # hai bánh xe dưới bệ
        wheel = QPainterPath()
        wheel.addEllipse(QPointF(cx, 109), 6.0, 6.0)
        body = body.united(wheel)

    mast = QPainterPath()                             # cột ăng ten chữ T
    mast.addRect(49.1, 4.2, 1.8, 13)
    bar = QPainterPath()
    bar.addRect(42.5, 4.2, 15, 1.7)
    body = body.united(mast).united(bar)

    return body.united(_arm(-1)).united(_arm(1))


def _star(p, cx, cy, r):
    """Mặt kính vỡ sao: các tia nứt toả ra từ điểm va, cắt gọn trong vành."""
    p.save()
    clip = QPainterPath()
    clip.addEllipse(QPointF(cx, cy), r, r)
    p.setClipPath(clip, Qt.ClipOperation.IntersectClip)

    hit = QPointF(cx - 1.3, cy + 1.1)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(INK, 0.85))
    for deg in (-158, -108, -46, 16, 74, 132, -80):
        a = math.radians(deg)
        p.drawLine(hit, QPointF(hit.x() + math.cos(a) * r * 1.6,
                                hit.y() + math.sin(a) * r * 1.6))
    p.setPen(QPen(INK, 0.7))
    p.drawPolyline(QPolygonF([
        QPointF(hit.x() + math.cos(math.radians(d)) * 2.1,
                hit.y() + math.sin(math.radians(d)) * 2.1)
        for d in (-158, -108, -46, 16, 74, 132, -158)]))
    p.restore()


def _dial(p, cx, cy, r, angle, star=False):
    """Một mặt đồng hồ tròn: vành, vạch chia, kim chỉ."""
    p.setBrush(PANEL)
    p.setPen(QPen(INK, 1.2))
    p.drawEllipse(QPointF(cx, cy), r, r)
    p.setPen(QPen(INK, 0.7))
    for k in range(8):
        a = math.radians(-200 + k * 34)
        p.drawLine(QPointF(cx + math.cos(a) * (r - 1.6),
                           cy + math.sin(a) * (r - 1.6)),
                   QPointF(cx + math.cos(a) * (r - 0.5),
                           cy + math.sin(a) * (r - 0.5)))
    a = math.radians(angle)
    p.setPen(QPen(INK, 1.3))
    p.drawLine(QPointF(cx, cy),
               QPointF(cx + math.cos(a) * (r - 1.8),
                       cy + math.sin(a) * (r - 1.8)))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(INK)
    p.drawEllipse(QPointF(cx, cy), 0.9, 0.9)
    if star:
        _star(p, cx, cy, r)


def _reel(p, cx, cy):
    """Một ru lô băng từ sau tấm kính — cặp này thay cho hai con mắt."""
    p.setBrush(DIM)
    p.setPen(QPen(INK, 1.3))
    p.drawEllipse(QPointF(cx, cy), 5.8, 5.8)
    p.setBrush(PANEL)
    p.setPen(QPen(INK, 0.9))
    p.drawEllipse(QPointF(cx, cy), 3.4, 3.4)
    p.setPen(QPen(INK, 0.8))
    for k in range(3):
        a = math.radians(k * 120 + (18 if cx < 50 else -42))
        p.drawLine(QPointF(cx, cy),
                   QPointF(cx + math.cos(a) * 3.2, cy + math.sin(a) * 3.2))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(INK)
    p.drawEllipse(QPointF(cx, cy), 1.1, 1.1)


def _tape_holes(rng):
    """Toạ độ từng lỗ đục trên băng giấy, kèm bán kính."""
    p0, p1, p2 = TAPE
    out = []
    for i in range(30):
        t = 0.035 + i * (0.93 / 29)
        c = curve_at(p0, p1, p2, t)
        nx, ny = curve_normal(p0, p1, p2, t)
        out.append((c.x(), c.y(), 0.3))                      # lỗ răng cưa
        for off in (-1.35, 1.35):                            # cột dữ liệu
            if rng() < 0.55:
                out.append((c.x() + nx * off, c.y() + ny * off, 0.55))
    return out


def _crack():
    """Vết toác trên bảng điều khiển — chỗ cỗ máy bị đẩy ngã vào."""
    return QPolygonF([QPointF(*q) for q in (
        (40.3, 73.8), (37.5, 78.4), (40.3, 82.6), (36.9, 88.8))])


def draw_living_brain(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước."""
    with design(p, rect, h=118):
        misprint(p, _chassis())

        # vạch chia đốt trên hai cánh tay
        seam = QColor(PAPER_HI)
        seam.setAlpha(150)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(seam, 1.1))
        for sign in (-1, 1):
            c0, c1, c2 = _arm_curve(sign)
            for t in (0.22, 0.42, 0.62, 0.80):
                c = curve_at(c0, c1, c2, t)
                nx, ny = curve_normal(c0, c1, c2, t)
                w = ARM_W[0] + (ARM_W[1] - ARM_W[0]) * t
                p.drawLine(QPointF(c.x() + nx * w, c.y() + ny * w),
                           QPointF(c.x() - nx * w, c.y() - ny * w))

        # khe thoát nhiệt trên khối vai
        p.setPen(QPen(seam, 1.2))
        for sign in (-1, 1):
            for k in range(3):
                x = 50 + sign * (12 + k * 3.4)
                p.drawLine(QPointF(x, 52.6), QPointF(x, 57.4))

        # đinh tán chạy dọc hai mép thân tủ
        rivet = QColor(PAPER_HI)
        rivet.setAlpha(120)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(rivet)
        for y in range(62, 97, 6):
            for x in (35.6, 64.4):
                p.drawEllipse(QPointF(x, y), 0.8, 0.8)

        # dãy đèn báo trên trán
        p.setPen(QPen(INK, 0.7))
        for k in range(7):
            p.setBrush(PANEL if k % 2 == 0 else DIM)
            p.drawEllipse(QPointF(37.4 + k * 4.2, 19.4), 1.3, 1.3)

        # tấm kính mặt máy, sau nó là hai ru lô băng từ
        glass = QPainterPath()
        glass.addRoundedRect(36, 23.5, 28, 15.5, 2.5, 2.5)
        p.setBrush(DIM)
        p.setPen(QPen(INK, 1.5))
        p.drawPath(glass)
        _reel(p, 43, 31.2)
        _reel(p, 57, 31.2)

        # khe in ở cằm — băng giấy chui ra từ đây
        p.setBrush(PANEL)
        p.setPen(QPen(INK, 1.0))
        p.drawRoundedRect(40, 42.2, 20, 2.8, 1.2, 1.2)

        # bảng điều khiển giữa ngực: hai đồng hồ, dãy đèn, hàng công tắc
        board = QPainterPath()
        board.addRoundedRect(36, 62.5, 28, 27, 2, 2)
        p.setBrush(DIM)
        p.setPen(QPen(INK, 1.5))
        p.drawPath(board)

        _dial(p, 43.5, 70.5, 4.6, 168, star=True)   # kim đập hết cỡ, kính vỡ
        _dial(p, 56.5, 70.5, 4.6, -34)

        p.setPen(QPen(INK, 0.6))
        for k in range(6):
            p.setBrush(PANEL if k in (1, 2, 4) else DIM)
            p.drawEllipse(QPointF(38.8 + k * 4.5, 80.2), 1.2, 1.2)

        p.setBrush(PANEL)
        p.setPen(QPen(INK, 0.7))
        for k, up in enumerate((1, 0, 1, 1, 0)):
            p.drawRect(QRectF(38.6 + k * 5.4, 83.6 if up else 85.2, 2.0, 3.4))

        # vết toác chạy từ chỗ đồng hồ vỡ xuống tới mép bảng
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(INK, 1.3))
        p.drawPolyline(_crack())
        p.setPen(QPen(INK, 0.8))
        for (ax, ay), (bx, by) in (((37.5, 78.4), (39.8, 76.4)),
                                   ((40.3, 82.6), (43.6, 84.4))):
            p.drawLine(QPointF(ax, ay), QPointF(bx, by))

        # tấm biển hiệu dưới bảng điều khiển, chữ chỉ còn là mấy gạch
        p.setBrush(DIM)
        p.setPen(QPen(INK, 0.9))
        p.drawRect(QRectF(41, 91.6, 18, 5.0))
        p.setPen(QPen(INK, 0.8))
        for x0, x1 in ((42.6, 46.4), (48, 53.4), (55, 57.4)):
            p.drawLine(QPointF(x0, 94.2), QPointF(x1, 94.2))

        # hai bánh xe dưới bệ
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(PAPER_HI, 1.3))
        for cx in (32, 68):
            p.drawEllipse(QPointF(cx, 109), 3.4, 3.4)
            p.drawEllipse(QPointF(cx, 109), 1.2, 1.2)

        # cuộn băng giấy đục lỗ: câu trả lời không ai đọc nổi
        p.setBrush(PANEL)
        p.setPen(QPen(INK, 1.1))
        p.drawPath(ribbon(*TAPE, 2.4, 2.1))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(INK)
        rng = Rolls(SEED)
        for x, y, r in _tape_holes(rng):
            p.drawEllipse(QPointF(x, y), r, r)

        marks(p)


# ═══════════════════════════════════════════════════════════════ hồ sơ
PROFILE = Profile(
    name="Living Brain",
    vi_name="Bộ Não Sống",
    real_name="Máy tính I.C.M.",

    kicker="Hồ sơ khí tài",

    tagline="Cỗ máy được chở tới trường Midtown để trả lời mọi câu hỏi. Học "
            "sinh hỏi nó Spider-Man là ai — và nó trả lời đúng.",

    summary=(
        "Trong The Amazing Spider-Man #8 (01/1964), Giáo sư Petty của hãng "
        "International Computing Machines mang tới hội trường trường trung học "
        "Midtown thứ ông ta gọi là cỗ máy thông minh nhất từng được chế: nạp "
        "đủ dữ kiện thì nó giải được bất kỳ câu hỏi nào. Đám học sinh chọn "
        "ngay câu hỏi nóng nhất thành phố — Spider-Man là ai.",

        "Và người được gọi lên nạp dữ liệu cho máy, đúng kiểu trớ trêu của Lee "
        "với Ditko, là Peter Parker. Cậu ta đứng đó khai vào cỗ máy từng mẩu "
        "thông tin mà cả lớp biết về Spider-Man, thừa hiểu rằng nếu cái máy "
        "chạy đúng thì nó sẽ in ra tên mình. Nó chạy đúng thật. Câu trả lời "
        "nhả ra dưới dạng một dãy mã toán học mà không ai trong hội trường đọc "
        "nổi — kể cả Peter, người phải mang băng giấy về nhà giải cả đêm.",

        "Buổi trình diễn hỏng vì một chuyện chẳng liên quan gì đến khoa học: "
        "hai người thợ đi theo đoàn gây sự với Petty, một người bị đẩy ngã vào "
        "đúng bảng điều khiển đặt giữa ngực cỗ máy. Living Brain mất kiểm "
        "soát, đập tan hành lang Midtown, và Spider-Man phải hạ nó — vừa đánh "
        "vừa lo chuyện lộ mặt ngay giữa ngôi trường của chính mình.",

        "Đây là cái tên lạc loài nhất trong cả danh sách: không động cơ, không "
        "thù oán, không đòi hỏi gì. Living Brain không phải kẻ ác, nó là một "
        "thiết bị hỏng. Về sau Otto Octavius dựng lại nó thành trợ lý phòng "
        "thí nghiệm, rồi có một quãng chính ý thức của Otto trú trong cái thân "
        "máy ấy, ngày ngày đóng vai trợ lý ngoan ngoãn bên cạnh Peter ở Parker "
        "Industries — Anna Maria Marconi là người phát hiện ra.",
    ),

    powers=(
        "Giải được gần như mọi câu hỏi, miễn là được nạp đủ dữ kiện",
        "In kết quả ra băng giấy đục lỗ, dưới dạng mã toán học",
        "Vỏ thép và sức của máy: đấm thủng tường, giật tung cửa",
        "Hai càng kẹp thuỷ lực thay cho bàn tay",
        "Bảng điều khiển đặt ngay giữa ngực — điểm yếu chí mạng",
    ),

    facts=(
        ("Loại", "Máy tính tự hành, không phải người"),
        ("Người chế", "Giáo sư Petty  ·  hãng I.C.M."),
        ("Xuất hiện đầu", "ASM #8  ·  01/1964"),
        ("Tác giả", "Stan Lee & Steve Ditko"),
        ("Nơi gây án", "Hội trường trường Midtown"),
        ("Về sau", "Otto Octavius dựng lại làm trợ lý"),
    ),

    blurb="Nó là cái tên duy nhất ở đây chưa từng muốn hại ai. Người ta hỏi nó "
          "đúng một câu, và nó trả lời đúng — chỉ là bằng thứ chữ không ai đọc "
          "được.",

    art=draw_living_brain,
    caption="Chân dung dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Living_Brain"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Living_Brain_(Earth-616)"),
    ),
)
