"""
Absolute Green Goblin — Norman Osborn, và quả bom bí ngô cuối cùng.

Bản sắc riêng, khác cả chín dạng Absolute trước:
    · bộ da `smog` — chín bộ kia bộ nào cũng hoặc gần đen hoặc gần trắng,
      bộ này lấy đúng khoảng **giữa**: một tờ giấy ám khói hoá chất, ố vàng
      ôliu. Màn phủ cũng không tối sầm cũng không loà lên mà chìm vào một
      đám hơi độc.
    · `evolve_fx="press"` — tờ giấy cũ không vỡ mà bị **dập**: một cái khuôn
      đi xuống, đục cả trang thành lưới phôi bom bí ngô, phôi rời khuôn rồi
      trôi xuống theo hàng như trên băng chuyền. Tấm mới cũng được dập lại
      từng ô một theo thứ tự đọc. Đây là dây chuyền của Oscorp chứ không
      phải một vụ nổ — và đó mới là chỗ đáng sợ.
    · chân dung giữ nguyên lối chiếu sáng của hồ sơ gốc rồi đổi quy mô. Ở
      ASM #14, nguồn sáng nằm *trong* quả bom và thoát ra qua mấy lỗ khoét.
      Ở đây vẫn đúng như thế, chỉ có điều quả bom bây giờ là **Trái Đất**:
      các đường gân bí ngô cũng chính là kinh tuyến, và ánh lửa trong lòng
      nó hắt ra qua cái mặt cười đã khoét sẵn.

Ngôn ngữ chuyển động cũng chưa ai dùng: **một nhịp**. Chín dạng kia đều
chuyển động trơn hoặc nháy loạn; hình này thở theo **nhịp cười** — hai nhịp
ngắn rồi một nhịp dài, lặp mãi, trong lúc tia lửa bò dần xuống cái ngòi.
"""

import math
from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QPainter, QPainterPath, QPen,
                           QPolygonF, QRadialGradient)

from theme import SMOG

from .art import H, W, Rolls, design, glow, marks
from .profile import Profile, Section, Tier

GOB = SMOG.blue                  # lục Goblin
OSB = SMOG.red                   # tím Osborn
WARN = SMOG.yellow               # vàng cảnh báo
CRUST = QColor("#101208")        # vỏ hành tinh, phía không quay về nguồn sáng
RIB = QColor("#2C2E1A")          # gân bí ngô, cũng là kinh tuyến
CORE = QPointF(50, 66)           # tâm quả bom
R = 34.0                         # bán kính
FUSE = 2.6                       # số giây mỗi vòng lửa bò trên ngòi


def _tone(color, alpha):
    out = QColor(color)
    out.setAlpha(max(0, min(255, int(alpha))))
    return out


def _laugh(t):
    """Nhịp cười: hai nhịp ngắn, một nhịp dài, rồi lặp lại.

    Đây là chỗ cả bức chân dung sống hay chết. Cho nó thở đều như mọi hình
    khác thì ra một quả cầu đẹp; cho nó thở theo nhịp cười thì ra Norman.
    """
    beat = t % 2.2
    out = 0.26
    for at, amp in ((0.0, 1.0), (0.20, 0.85), (0.40, 0.95), (0.74, 1.35)):
        gap = beat - at
        if gap >= 0:
            out += amp * math.exp(-gap * 5.5)
    return min(1.7, out)


# ═══════════════════════════════════════════════════════════════ hình khối
@lru_cache(maxsize=1)
def _grin():
    """Cái mặt khoét trên vỏ hành tinh: hai mắt, cái mũi, và hàm răng nhe."""
    face = QPainterPath()
    for sign in (-1, 1):
        eye = QPolygonF([
            QPointF(CORE.x() + sign * 8, CORE.y() - 16),
            QPointF(CORE.x() + sign * 20, CORE.y() - 11),
            QPointF(CORE.x() + sign * 9.5, CORE.y() - 5)])
        path = QPainterPath()
        path.addPolygon(eye)
        face = face.united(path)

    nose = QPainterPath()
    nose.addPolygon(QPolygonF([QPointF(50, CORE.y() - 3),
                               QPointF(54.5, CORE.y() + 4),
                               QPointF(45.5, CORE.y() + 4)]))
    face = face.united(nose)

    # miệng nhe răng, cong theo mặt cầu
    mouth = QPainterPath()
    mouth.moveTo(28, CORE.y() + 9)
    teeth = ((33, 15), (38, 9), (43, 16), (48, 10),
             (53, 16), (58, 9), (63, 15), (68, 10))
    for x, dy in teeth:
        mouth.lineTo(x, CORE.y() + dy)
    mouth.lineTo(72, CORE.y() + 9)
    mouth.cubicTo(QPointF(64, CORE.y() + 22), QPointF(36, CORE.y() + 22),
                  QPointF(28, CORE.y() + 9))
    mouth.closeSubpath()
    return face.united(mouth)


_GRIN = _grin()


@lru_cache(maxsize=1)
def _globe():
    path = QPainterPath()
    path.addEllipse(CORE, R, R)
    return path


def _fuse_path():
    """Cuống bí ngô kéo dài thành một sợi ngòi cong, cháy dần từ ngọn xuống."""
    path = QPainterPath(QPointF(50, CORE.y() - R + 1))
    path.cubicTo(QPointF(52, 22), QPointF(64, 20), QPointF(70, 11))
    return path


_FUSE = _fuse_path()


# ═══════════════════════════════════════════════════════════ lớp dựng sẵn
def _sky(p):
    """Nền: không phải khoảng không đen, mà là nhìn qua chính đám khí của hắn."""
    p.setPen(Qt.PenStyle.NoPen)
    haze = QRadialGradient(CORE, 78)
    haze.setColorAt(0.0, QColor("#4A4A2C"))
    haze.setColorAt(0.55, QColor("#33341E"))
    haze.setColorAt(1.0, QColor("#1A1B10"))
    p.setBrush(haze)
    p.drawRect(QRectF(-6, -6, 112, 132))

    r = Rolls(14071964)
    for _ in range(90):                      # bụi hoá chất lơ lửng
        p.setBrush(_tone(WARN if r(0, 1) > 0.7 else GOB, r(12, 40)))
        p.drawEllipse(QPointF(r(-6, 106), r(-6, 126)), r(0.3, 0.9), r(0.3, 0.9))


def _crust(p):
    """Vỏ hành tinh: tối, có gân chạy dọc, và đèn thành phố rắc dọc mấy lục địa."""
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(CRUST)
    p.drawPath(_globe())

    p.save()
    p.setClipPath(_globe())

    # gân bí ngô — cũng chính là kinh tuyến, nên hình vừa là quả bom vừa là
    # quả địa cầu, không phải chọn một trong hai
    p.setBrush(Qt.BrushStyle.NoBrush)
    for k in range(-3, 4):
        wide = R * (1 - abs(k) / 4.4)
        p.setPen(QPen(_tone(RIB, 170 - abs(k) * 22), 1.3 - abs(k) * 0.14))
        p.drawEllipse(QRectF(CORE.x() - wide, CORE.y() - R, wide * 2, R * 2))
    p.setPen(QPen(_tone(RIB, 150), 1.0))
    for k in (-2, -1, 1, 2):                 # vĩ tuyến, mảnh hơn
        tall = R * (1 - abs(k) / 3.6)
        p.drawEllipse(QRectF(CORE.x() - R, CORE.y() - tall, R * 2, tall * 2))

    # Lục địa. Không có chúng thì hình này chỉ là một quả bí ngô có kẻ ô;
    # có chúng thì mới đọc ra đây là quả bom bí ngô **cỡ hành tinh**.
    r = Rolls(14071965)
    p.setPen(Qt.PenStyle.NoPen)
    lands = ((-0.42, -0.44, 0.34), (-0.30, 0.30, 0.30), (0.34, -0.30, 0.26),
             (0.44, 0.34, 0.22), (0.02, -0.62, 0.18), (0.10, 0.66, 0.16))
    for fx, fy, fr in lands:
        cx, cy = CORE.x() + fx * R, CORE.y() + fy * R
        edge = QPolygonF()
        for k in range(13):
            a = k / 13 * math.tau
            rad = fr * R * r(0.62, 1.35)
            edge.append(QPointF(cx + math.cos(a) * rad,
                                cy + math.sin(a) * rad * 0.8))
        p.setBrush(QColor("#24260F"))
        p.drawPolygon(edge)
        p.setBrush(_tone(QColor("#3A3C18"), 150))
        p.drawPolygon(edge.translated(-0.6, -0.6))
        # đèn thành phố bám dọc bờ và trong lòng lục địa
        for _ in range(16):
            a = r(0, math.tau)
            rad = fr * R * r(0.15, 1.0)
            p.setBrush(_tone(WARN, r(120, 240)))
            q = QPointF(cx + math.cos(a) * rad, cy + math.sin(a) * rad * 0.8)
            p.drawEllipse(q, r(0.3, 0.72), r(0.3, 0.68))

    # rìa hành tinh tối hẳn lại, cho ra khối cầu
    limb = QRadialGradient(CORE, R)
    limb.setColorAt(0.0, _tone(QColor("#000000"), 0))
    limb.setColorAt(0.72, _tone(QColor("#000000"), 26))
    limb.setColorAt(1.0, _tone(QColor("#000000"), 190))
    p.setBrush(limb)
    p.drawPath(_globe())

    # vành khí quyển bắt sáng, để quả cầu tách khỏi nền khói
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(GOB, 130), 1.4))
    p.drawArc(QRectF(CORE.x() - R + 0.7, CORE.y() - R + 0.7,
                     R * 2 - 1.4, R * 2 - 1.4), 150 * 16, 150 * 16)
    p.setPen(QPen(_tone(WARN, 60), 0.7))
    p.drawArc(QRectF(CORE.x() - R + 0.7, CORE.y() - R + 0.7,
                     R * 2 - 1.4, R * 2 - 1.4), 300 * 16, 90 * 16)
    p.restore()

    # cuống bí ngô
    p.setBrush(QColor("#3A2A12"))
    p.setPen(Qt.PenStyle.NoPen)
    stem = QPainterPath()
    stem.addPolygon(QPolygonF([QPointF(45, CORE.y() - R + 3),
                               QPointF(55, CORE.y() - R + 3),
                               QPointF(53, CORE.y() - R - 6),
                               QPointF(47, CORE.y() - R - 6)]))
    p.drawPath(stem)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(QColor("#5A4520"), 220), 1.4))
    p.drawPath(_FUSE)


_STILL = {}


def _still(scale):
    key = round(scale, 2)
    ready = _STILL.get(key)
    if ready is None:
        if len(_STILL) > 6:
            _STILL.clear()
        ready = QImage(max(1, math.ceil(112 * scale)),
                       max(1, math.ceil(132 * scale)),
                       QImage.Format.Format_ARGB32_Premultiplied)
        ready.fill(Qt.GlobalColor.transparent)
        q = QPainter(ready)
        q.setRenderHint(QPainter.RenderHint.Antialiasing)
        q.scale(scale, scale)
        q.translate(6, 6)
        _sky(q)
        _crust(q)
        q.end()
        _STILL[key] = ready
    return ready


# ═══════════════════════════════════════════════════════════ lớp tự chạy
def _fire(p, t):
    """Lửa trong lòng hành tinh, hắt ra qua chỗ khoét — sáng theo nhịp cười."""
    beat = _laugh(t)
    glow(p, CORE, R * (1.05 + 0.12 * beat), _tone(GOB, 34 + 26 * beat))

    p.save()
    p.setClipPath(_GRIN)
    hot = QRadialGradient(QPointF(CORE.x(), CORE.y() + 2), R * 1.15)
    hot.setColorAt(0.0, _tone(QColor("#FFF6C8"), 255))
    hot.setColorAt(0.28, _tone(WARN, 250))
    hot.setColorAt(0.62, _tone(GOB, 240))
    hot.setColorAt(1.0, _tone(OSB, 225))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(hot)
    p.drawPath(_globe())

    # lò trong ruột sôi lên, vệt sáng chạy qua chỗ khoét
    r = Rolls(int(t * 8) * 31 + 5)
    for _ in range(7):
        p.setBrush(_tone(QColor("#FFF6C8"), r(40, 130) * beat))
        p.drawEllipse(QPointF(r(28, 72), r(CORE.y() - 18, CORE.y() + 20)),
                      r(2, 7), r(1.5, 5))
    p.restore()

    # mép chỗ khoét: vỏ dày, nên có một viền tối rồi mới tới lửa
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(_tone(QColor("#0B0C06"), 235), 1.6))
    p.drawPath(_GRIN)
    p.setPen(QPen(_tone(WARN, 120 + 90 * beat), 0.6))
    p.drawPath(_GRIN)

    # ánh lửa hắt ngược lên đám khí quanh hành tinh
    glow(p, QPointF(CORE.x(), CORE.y() - 4), R * 1.9,
         _tone(WARN, 16 + 20 * beat))


def _bands(p, t):
    """Khí Goblin cuốn quanh hành tinh theo mấy dải vĩ tuyến, trôi rất chậm."""
    p.save()
    p.setClipPath(_globe())
    p.setBrush(Qt.BrushStyle.NoBrush)
    for k in range(4):
        y = CORE.y() - 22 + k * 13
        sweep = math.sin(t * 0.35 + k * 1.4) * 6
        p.setPen(QPen(_tone(GOB, 26 + k * 6), 1.5 + k * 0.4))
        band = QPainterPath(QPointF(CORE.x() - R - 4, y))
        band.cubicTo(QPointF(CORE.x() - 12, y + 5 + sweep),
                     QPointF(CORE.x() + 12, y - 5 - sweep),
                     QPointF(CORE.x() + R + 4, y))
        p.drawPath(band)
    p.restore()


def _spark(p, t):
    """Tia lửa bò dọc ngòi, và tàn rơi lại phía sau."""
    u = 1.0 - (t / FUSE) % 1.0            # cháy từ ngọn ngược về quả bom
    tip = _FUSE.pointAtPercent(u)
    glow(p, tip, 5.0, _tone(WARN, 210))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_tone(QColor("#FFF6C8"), 250))
    p.drawEllipse(tip, 1.1, 1.1)

    r = Rolls(int(t * 12) + 3)
    for _ in range(5):
        q = _FUSE.pointAtPercent(min(1.0, u + r(0.02, 0.16)))
        p.setBrush(_tone(WARN, r(60, 170)))
        p.drawEllipse(QPointF(q.x() + r(-1.5, 1.5), q.y() + r(-1, 2)),
                      r(0.3, 0.8), r(0.3, 0.8))


def _glider(p, t):
    """Sky Reaper lượn ngang qua mặt hành tinh — cái bóng cho ta biết cỡ nào."""
    u = (t / 9.0) % 1.0
    x = -14 + u * 128
    y = CORE.y() - 26 + math.sin(u * math.pi * 1.6) * 10
    p.save()
    p.translate(x, y)
    p.rotate(math.degrees(math.atan2(math.cos(u * math.pi * 1.6) * 10 * 0.05,
                                     1.0)) - 8)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_tone(QColor("#0A0B06"), 240))
    p.drawPolygon(QPolygonF([QPointF(-9, 0), QPointF(-2, -3.4),
                             QPointF(9, 0), QPointF(-2, 2.2)]))
    p.setPen(QPen(_tone(GOB, 150), 0.5))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawLine(QPointF(-9, 0), QPointF(9, 0))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_tone(WARN, 200))
    p.drawEllipse(QPointF(-6, 0), 0.9, 0.5)      # lửa đuôi
    p.restore()


def draw_absolute_green_goblin(p, rect, t=0.0):
    """Chân dung sống: nhận thêm `t` (giây) nên khung hồ sơ tự vẽ lại."""
    dpr = p.device().devicePixelRatio() if p.device() else 1.0
    grow = (p.transform().m11() or 1.0) * (dpr or 1.0)
    scale = min(rect.width() / W, rect.height() / H) * grow
    still = _still(scale)

    with design(p, rect):
        p.drawImage(QRectF(-6, -6, still.width() / scale,
                           still.height() / scale), still)
        _bands(p, t)
        _fire(p, t)
        _glider(p, t)
        _spark(p, t)
        marks(p, SMOG.ink_soft)


# ═══════════════════════════════════════════════════════════════ hồ sơ
ABSOLUTE = Profile(
    name="Absolute Green Goblin",
    vi_name="Yêu Tinh Xanh Tuyệt Đối",
    real_name="Norman Osborn  ·  Oscorp",
    keys=("Green Goblin Absolute",),

    kicker="Hồ sơ tuyệt đối",
    stamp="PHÂN LOẠI  ·  TRẬT TỰ THẾ GIỚI SỤP ĐỔ",
    note="ABSOLUTE",
    note_kind="new",
    tab="Absolute",
    skin="smog",
    evolve_fx="press",       # giấy bị dập thành phôi rồi trôi khỏi băng chuyền

    tagline="Vẫn đúng ba thứ cũ — hoá chất, xưởng máy và sự tàn ác có tính "
            "toán. Chỉ là bây giờ xưởng máy là cả một tập đoàn, và quả bom "
            "bí ngô thì cỡ hành tinh.",

    summary=(
        "Công thức Goblin bản gốc là một mũi tiêm: nâng sức Norman lên "
        "khoảng mười tấn, cho hắn phản xạ ngang Spider-Man và khả năng hồi "
        "phục nhanh, đổi lại là tổn thương thần kinh và những cơn điên. "
        "Nghĩa là hắn vẫn phải chế, phải tiêm, và vẫn có lúc cạn thuốc.",

        "Bản Absolute bỏ hẳn mũi tiêm. Công thức nay là một dòng tế bào cộng "
        "sinh cấy vào tuỷ và hệ thần kinh trung ương, tự sản xuất Goblin "
        "Serum 2.0 ngay trong người hắn, tự lấy năng lượng từ nhiệt, ánh "
        "sáng, thậm chí bức xạ. Norman thành một lò phản ứng sinh hoá biết "
        "đi: không cần ăn, không cạn sức, và mỗi tuyến trong cơ thể là một "
        "nhà máy hoá chất nhỏ.",

        "Nhưng thứ đẩy hắn lên cấp hành tinh không phải cơ bắp mà là Oscorp. "
        "Bom bí ngô được sản xuất cỡ xe tải, nhả ra đám mây Goblin Gas phủ "
        "bán kính mười cây số; tàu lượn thành Sky Reaper Mach 5 gấp gọn "
        "được thành giáp; và những container Goblin Forge thả xuống chỗ hẻo "
        "lánh nào là trong bốn tám giờ mọc thành một dây chuyền vũ khí ở "
        "chỗ ấy, ăn phế liệu địa phương mà chạy.",

        "Cố ý không có đội quân drone tự hành, không có AI cầm trận thay "
        "hắn. Green Goblin là kẻ khủng bố tâm lý: hắn cần người ta nhìn thấy "
        "hắn, cần đứng giữa đám cháy mà cười. Cái máy đánh hộ thì còn gì là "
        "sân khấu.",
    ),

    sections=(
        Section(
            title="Khuyếch đại năng lực vật lý & sinh học",
            intro="Nâng cấp không nằm ở chỉ số mà ở chỗ Norman thôi dùng hoá "
                  "chất và bắt đầu trở thành hoá chất: cơ thể tự tổng hợp, "
                  "tự vá, tự tiết độc, không còn cái ống tiêm nào để mà đập "
                  "vỡ nữa.",
            items=(
                ("Dòng tế bào cộng sinh Goblin",
                 "Công thức được cấy thẳng vào tuỷ xương và hệ thần kinh "
                 "trung ương, liên tục sản xuất Goblin Serum 2.0 ngay trong "
                 "người. Không còn phụ thuộc liều tiêm — thứ từng là điểm "
                 "yếu cố hữu của bản gốc — và cũng không còn khoảng trống "
                 "giữa hai liều để ai đó kịp hạ hắn."),
                ("Siêu trao đổi chất tự nuôi",
                 "Tế bào Goblin hút năng lượng từ môi trường: nhiệt, ánh "
                 "sáng, cả bức xạ ion hoá. Hắn đánh liên tục nhiều ngày "
                 "không ăn không ngủ. Chiến thuật cầm cự chờ hắn xuống sức "
                 "— cách Peter từng nhiều lần dùng — nay vô nghĩa."),
                ("Tái lập trình mô tạm thời",
                 "Hồi phục không còn là tự lành mà là chủ động đổi hình: hoá "
                 "cứng da thành giáp kitin hữu cơ, tiết chất nhờn để trượt "
                 "khỏi đòn khoá, bịt vết thương lớn bằng màng sinh học trong "
                 "vài giây. Mất một chi hay thủng tim cũng chỉ là chậm lại "
                 "vài phút chứ không phải kết thúc."),
                ("Tuyến độc thần kinh và cơ nén hoá học",
                 "Nước bọt và mồ hôi tiết ra độc thần kinh dạng khí dung: "
                 "một cú vuốt hay một hơi thở gần là đủ gây ảo giác, tê liệt "
                 "hoặc hoảng loạn cấp. Sợi cơ thì được bọc trong các túi áp "
                 "suất giãn nở theo xung thần kinh — cú đấm dồn lực vào một "
                 "điểm đủ xuyên boongke, và phản xạ vượt ngưỡng âm thanh."),
            ),
        ),
        Section(
            title="Đột phá công nghệ & tự động hoá",
            intro="Norman là nhà tư bản công nghiệp, nên nâng cấp công nghệ ở "
                  "đây không phải chế thêm món đồ chơi mà là đưa cả kho vũ "
                  "khí cũ vào sản xuất hàng loạt. Cố ý không có drone tự "
                  "hành: hắn phải có mặt tại chỗ, nếu không thì để làm gì.",
            items=(
                ("Bom bí ngô cỡ công nghiệp",
                 "Mỗi quả to bằng một chiếc xe tải, và nổ ra không phải lửa "
                 "mà là một đám mây Goblin Gas bán kính mười cây số. Khí "
                 "không giết ngay: trong ba mươi phút nó gây hoảng loạn tập "
                 "thể, ảo giác thù địch, mất kiểm soát hành vi — rồi chính "
                 "dân trong vùng đánh nhau. Nó đi theo hệ thông gió và nước "
                 "sinh hoạt, phủ kín một đô thị lớn trong vài giờ."),
                ("Sky Reaper",
                 "Tàu lượn cũ thành một khung thân gấp gọn được thành bộ "
                 "giáp ngoài, mở ra là phi cơ Mach 5: tên lửa hành trình "
                 "siêu nhỏ mang đầu đạn bom bí ngô, đầu phát vi ba hâm nóng "
                 "cả một vùng khí quyển để đốt rừng và phá lưới điện, và lớp "
                 "phủ tàng hình radar bằng vật liệu meta của Oscorp."),
                ("Nhà máy di động Goblin Forge",
                 "Những container thả xuống chỗ hẻo lánh, bốn tám giờ sau tự "
                 "lắp thành một dây chuyền sản xuất bom và đạn. Nguyên liệu "
                 "lấy tại chỗ từ phế liệu kim loại và hoá chất công nghiệp, "
                 "điều khiển bằng cơ khí thuần nên không có gì để hack cũng "
                 "không có gì để gây nhiễu. Đánh sập một cái thì mười cái "
                 "khác đang mọc ở chỗ chưa ai tìm ra."),
                ("Chòm vệ tinh Oscorp Eye",
                 "Mười hai vệ tinh tư nhân, làm đúng một việc: dò tín hiệu "
                 "sinh học đặc trưng của Spider-Man từ trên quỹ đạo rồi báo "
                 "toạ độ xuống. Không phải hệ tự động — đây là con mắt của "
                 "Norman, và người ra đòn vẫn là Norman."),
            ),
        ),
        Section(
            title="Khắc chế phần cứng của Spider-Man",
            intro="Mọi đòn đều mọc ra từ đúng hai thứ Norman giỏi nhất: hoá "
                  "học và việc bẻ gãy tinh thần người khác. Hắn không cần "
                  "mạnh hơn Peter — hắn cần Peter do dự đúng nửa giây.",
            items=(
                ("Goblin Static",
                 "Khí dung mang hạt nano kim loại tích điện, dựng một trường "
                 "điện từ dao động ngẫu nhiên ở dải cực cao. Giác quan nhện "
                 "vốn đọc thay đổi đột ngột của trường quanh mình, nên trong "
                 "đám khí ấy nó chỉ còn là nhiễu trắng: báo động giả liên "
                 "tục, hoặc không phân biệt nổi đâu là đòn thật. Phun ra "
                 "được từ chính tuyến mồ hôi của hắn, hoặc nhồi vào bom."),
                ("Bẫy tội lỗi",
                 "Oscorp Eye theo dõi và ghi hình những người Peter thương, "
                 "rồi công nghệ của Oscorp dựng thành phim giả: cảnh chính "
                 "Spider-Man giết họ. Phim ấy phát trên mọi màn hình công "
                 "cộng của thành phố, kèm giọng Norman thì thầm rằng cậu đã "
                 "giết họ, y như đã giết chú Ben. Peter biết là giả, nhưng "
                 "biết không có nghĩa là không gục — và giác quan nhện thì "
                 "chìm nghỉm khi thần kinh quá tải cảm xúc."),
                ("Enzyme phân huỷ tơ",
                 "Chất xúc tác cắt liên kết peptide trong polymer tơ nhện: "
                 "chỉ vài giây là sợi tơ giòn ra rồi rã. Nhồi vào bom bí ngô "
                 "dạng phun sương thì cả khu vực giao chiến thành vùng không "
                 "đu được, không trói được — đánh thẳng vào món đồ đã thành "
                 "biểu tượng của Người Nhện."),
                ("Hạn chót Goblin",
                 "Bom hẹn giờ đặt ở trường học, bệnh viện, nhà ga, tất cả "
                 "cùng đếm ngược một lượt đúng lúc Peter tới đối mặt hắn. "
                 "Cậu buộc phải chia mình ra, và giác quan nhện chia theo — "
                 "không còn tập trung vào kẻ đang đứng trước mặt. Đây là đòn "
                 "hiểm nhất: nó biến lòng tốt của Peter thành lỗ hổng chiến "
                 "thuật, và Norman không phải làm gì ngoài việc chờ."),
            ),
        ),
    ),

    # Thang chữ cái Hy Lạp, đọc từ Zeta lên Omega, như các hồ sơ Absolute
    # trước. Cột tốc độ đo bằng thời gian tính từ lúc hắn bắt đầu.
    tiers=(
        Tier("Tier Zeta", "Một mình, một mục tiêu",
             "Đột nhập một cơ sở quân sự, ám sát một lãnh đạo, phá một nhà "
             "máy điện. Bản gốc ở bậc này là một kẻ khủng bố đơn lẻ gây "
             "thiệt hại trong một toà nhà; bản này làm xong rồi đi trước khi "
             "còi báo động kịp hú.",
             "Vài phút"),
        Tier("Tier Epsilon", "Một quận thành vùng chiến sự",
             "Bom bí ngô cỡ vừa thả vào trung tâm thương mại, giao thông tê "
             "liệt, hoảng loạn lan ra vài km². Bản gốc làm náo loạn được vài "
             "con phố; bậc này biến cả một quận thành chiến trường.",
             "1 giờ"),
        Tier("Tier Delta", "Một đô thị vô chính phủ",
             "Goblin Gas thả vào hệ thống tàu điện ngầm, cảnh sát tê liệt, "
             "sân bay và cảng biển bị phá, nhiều quả bom nổ đồng loạt. Bản "
             "gốc lúc đỉnh cao chỉ doạ được một phần thành phố.",
             "12 giờ"),
        Tier("Tier Gamma", "Một quốc gia mất hạ tầng",
             "Sky Reaper rải bom xuống nhiều thành phố cùng lúc, Goblin "
             "Forge mọc ở ngoại ô sản xuất liên tục, vũ khí vi ba đánh vào "
             "lưới điện quốc gia. Năng lượng, viễn thông và giao thông của "
             "cả nước sụp theo nhau.",
             "3–5 ngày"),
        Tier("Tier Beta", "Một lục địa đói",
             "Biến thể Goblin Gas lây qua đường nước, đổ vào những con sông "
             "lớn chảy qua nhiều quốc gia; đường sắt và cảng trọng yếu bị "
             "đánh, chuỗi lương thực đứt. Nạn đói và khủng hoảng tị nạn ở "
             "quy mô cả châu lục.",
             "2–3 tuần"),
        Tier("Tier Alpha", "Nửa địa cầu",
             "Nhiều chiếc Sky Reaper sản xuất hàng loạt rải Goblin Gas lên "
             "các tầng khí quyển, mượn dòng jet stream phát tán khắp bán "
             "cầu, trong khi vũ khí điện từ đánh vào các sàn giao dịch làm "
             "sụp thị trường toàn cầu.",
             "1–2 tháng"),
        Tier("Tier Omega", "Trật tự thế giới",
             "Bốn thứ cùng lúc: vệ tinh Oscorp Eye phát đi lời hắn doạ thả "
             "bom vào mọi thủ đô; đầu đạn hoá chất bắn lên tầng bình lưu gây "
             "hạn hán và lũ lụt nhân tạo; bom xung điện từ nổ trên cao xoá "
             "sổ hạ tầng số; và Goblin Gas nồng độ thấp kéo dài đẩy hàng "
             "triệu người vào loạn thần bạo lực. Bản gốc giết vài trăm người "
             "và phá vài toà nhà; bậc này đẩy nền văn minh lùi lại hàng thập "
             "kỷ trong nửa năm.",
             "6 tháng"),
    ),

    # Nhãn giữ dưới 94 px, giá trị dưới 188 px — xem chú thích cùng chỗ trong
    # `chameleon_absolute.py`.
    facts=(
        ("Cấp đe doạ", "Hành tinh  ·  trật tự sụp đổ"),
        ("Nền tảng", "Hoá học, xưởng máy, tâm lý"),
        ("Công thức", "Tế bào cộng sinh, tự sản xuất"),
        ("Không dùng", "Drone tự hành  ·  AI cầm trận"),
        ("Bom bí ngô", "Cỡ xe tải  ·  khí lan 10 km"),
        ("Sky Reaper", "Mach 5  ·  gấp thành giáp"),
        ("Goblin Forge", "Thành nhà máy sau 48 giờ"),
        ("Bậc Omega", "6 tháng"),
    ),

    blurb="Chín hồ sơ kia đều phải trở thành một thứ khác mới lên được cấp "
          "hành tinh — thành plasma, thành sinh quyển, thành một cái não "
          "trong lưới điện. Norman thì không đổi gì cả. Vẫn là một người "
          "đàn ông rất giàu, rất thông minh, có một dây chuyền sản xuất và "
          "một cơn điên; hắn chỉ đơn giản là mở rộng quy mô, và hoá ra chừng "
          "ấy đã đủ.",

    art=draw_absolute_green_goblin,
    caption="Ảnh chụp từ quỹ đạo thấp  ·  khung hình trực tiếp",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Green_Goblin"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Norman_Osborn_(Earth-616)"),
    ),
)
