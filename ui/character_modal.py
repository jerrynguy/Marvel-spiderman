"""
Tấm hồ sơ nhân vật: mở đè lên cửa sổ chính thay vì mở trình duyệt.

Chuỗi chuyển cảnh (kiểu PowerPoint Morph):
    1. Màn phủ tối dần lên, kèm lưới halftone.
    2. Tờ giấy phóng ra từ đúng vị trí con chip vừa bấm, giữ nguyên tỉ lệ.
    3. Tờ giấy đứng yên, từng khối nội dung mới trượt lên và hiện dần,
       lệch nhau vài phần trăm giây.
    4. Đóng lại: đảo ngược đúng thứ tự đó, tờ giấy thu về chỗ con chip.

Hồ sơ nào khai `evolution=` thì mọc thêm nút tiến hoá ở chân trang. Bấm vào:
tờ giấy rung lên, nứt ra, nổ tung thành mảnh, rồi dạng mới được quét lại từ
giữa màn hình trên nền void. Từ đó trở đi hai dạng nằm ở hai tai hồ sơ nhô
lên trên mép giấy, bấm qua lại được — lần sau chỉ quét một nhát chứ không
nổ lại.

Bấm Esc, bấm nút ĐÓNG hoặc bấm ra ngoài tờ giấy để thoát.
"""

import inspect
import math
import time

from PySide6.QtCore import (Property, QEasingCurve, QParallelAnimationGroup,
                            QPoint, QPointF, QPropertyAnimation, QRectF, QSize,
                            Qt, QTimer, Signal)
from PySide6.QtGui import (QBrush, QColor, QFontMetrics, QLinearGradient,
                           QPainter, QPainterPath, QPen, QPixmap, QPolygonF,
                           QRadialGradient)
from PySide6.QtWidgets import (QGraphicsOpacityEffect, QHBoxLayout, QLabel,
                               QScrollArea, QSizePolicy, QVBoxLayout, QWidget)

from theme import PULP, VOID, Type, blend, halftone_tile

SHADOW = 12      # chỗ chừa cho bóng đổ quanh tờ giấy
BAND = 7         # dải màu ở mép trên tờ giấy
_tiles = {}
_grids = {}


def skin_of(profile):
    """Da của một hồ sơ: giấy pulp, hoặc nền void cho các dạng Absolute."""
    return VOID if getattr(profile, "dark", False) else PULP


def _paper_tile(skin):
    if skin.name not in _tiles:
        _tiles[skin.name] = halftone_tile(dot=1.4, step=5, color=skin.dot)
    return _tiles[skin.name]


def _veil_tile(skin):
    if skin.name not in _grids:
        _grids[skin.name] = halftone_tile(dot=1.7, step=6, color=skin.grid)
    return _grids[skin.name]


def _fade(color, alpha):
    """Bản sao của một màu, nhân alpha sẵn có với hệ số `alpha`."""
    c = QColor(color)
    c.setAlpha(max(0, min(255, int(c.alpha() * alpha))))
    return c


def sheet_box(rect, scale=1.0):
    """Phần giấy thật trong một khung, đã trừ chỗ cho bóng đổ."""
    return QRectF(rect.x(), rect.y(),
                  rect.width() - SHADOW * scale,
                  rect.height() - SHADOW * scale)


def paint_sheet(p, box, alpha=1.0, scale=1.0, skin=PULP):
    """Vẽ tờ giấy: bóng đổ, mực lệch trục, nền giấy, dải màu, khung mực.

    `scale` co giãn cả bóng, dải màu và nét viền theo kích thước tờ giấy, để
    lúc đang bay nó trông đúng là cùng một tờ giấy được phóng to.
    """
    alpha = max(0.0, min(1.0, alpha))
    p.setPen(Qt.PenStyle.NoPen)
    for color, dx, dy, a in skin.ghosts:
        c = QColor(color)
        c.setAlpha(int(a * alpha))
        p.setBrush(c)
        p.drawRect(box.translated(dx * scale, dy * scale))

    paper = QColor(skin.paper_hi)
    paper.setAlpha(int(255 * alpha))
    p.setBrush(paper)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(box)

    p.save()
    p.setClipRect(box)
    p.setOpacity(alpha)
    p.fillRect(box, QBrush(_paper_tile(skin)))
    p.restore()

    strip = QRectF(box.x(), box.y(), box.width(), BAND * scale)
    if skin.dark:
        # bản void không in một dải đỏ mà một dải tín hiệu, đỏ chuyển sang lam
        wash = QLinearGradient(strip.topLeft(), strip.topRight())
        wash.setColorAt(0.0, _fade(skin.red, alpha))
        wash.setColorAt(0.5, _fade(QColor("#8C2FA8"), alpha))
        wash.setColorAt(1.0, _fade(skin.blue, alpha))
        p.fillRect(strip, QBrush(wash))
    else:
        p.fillRect(strip, _fade(skin.red, alpha))

    frame = QColor(skin.frame)
    frame.setAlpha(int(255 * alpha))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(frame, 2.2 * scale))
    p.drawRect(box)
    p.drawLine(QPointF(box.x(), box.y() + BAND * scale),
               QPointF(box.right(), box.y() + BAND * scale))


# ═══════════════════════════════════════════════════════ hiệu ứng hiện dần
def reveal(widget, delay, distance=18, duration=340):
    """Trượt lên + hiện dần. Gọi sau khi layout đã đặt xong vị trí."""
    home = widget.pos()
    fx = QGraphicsOpacityEffect(widget)
    fx.setOpacity(0.0)
    widget.setGraphicsEffect(fx)
    widget.move(home.x(), home.y() + distance)

    fade = QPropertyAnimation(fx, b"opacity", widget)
    fade.setDuration(duration)
    fade.setStartValue(0.0)
    fade.setEndValue(1.0)
    fade.setEasingCurve(QEasingCurve.Type.OutCubic)

    slide = QPropertyAnimation(widget, b"pos", widget)
    slide.setDuration(duration)
    slide.setStartValue(QPoint(home.x(), home.y() + distance))
    slide.setEndValue(home)
    slide.setEasingCurve(QEasingCurve.Type.OutCubic)

    group = QParallelAnimationGroup(widget)
    group.addAnimation(fade)
    group.addAnimation(slide)
    # Gỡ hiệu ứng khi xong để chữ in lại sắc nét như bình thường.
    group.finished.connect(lambda w=widget: w.setGraphicsEffect(None))
    QTimer.singleShot(delay, group.start)
    return group


# ═══════════════════════════════════════════════════════════════ mảnh nhỏ
class InkButton(QWidget):
    """Nút kiểu bìa truyện: nhấc nhẹ khi rê chuột, đổ bóng khi là nút chính."""

    clicked = Signal()

    def __init__(self, label, solid=False, pad=22, skin=PULP, parent=None):
        super().__init__(parent)
        self.label, self.solid, self.s = label, solid, skin
        self.f = Type.text(9, bold=True, letter=1.2, caps=True)
        w = QFontMetrics(self.f).horizontalAdvance(label.upper()) + pad * 2
        self._size = QSize(w, 34)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._lift = 0.0
        self._down = False
        self._a = QPropertyAnimation(self, b"lift", self)
        self._a.setDuration(170)
        self._a.setEasingCurve(QEasingCurve.Type.OutCubic)

    def sizeHint(self):
        return self._size

    def get_lift(self):
        return self._lift

    def set_lift(self, v):
        self._lift = v
        self.update()

    lift = Property(float, get_lift, set_lift)

    def _drive(self, target):
        self._a.stop()
        self._a.setEndValue(target)
        self._a.start()

    def enterEvent(self, _):
        self._drive(1.0)

    def leaveEvent(self, _):
        self._drive(0.0)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._down = True
            self.update()

    def mouseReleaseEvent(self, e):
        if self._down and self.rect().contains(e.position().toPoint()):
            self.clicked.emit()
        self._down = False
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        box = QRectF(0, 2, self.width() - 4, self.height() - 6)
        if self._down:
            box.translate(1.5, 1.5)
        off = 2.0 + 1.4 * self._lift
        if self.solid:
            ghost = QColor(self.s.red)
            ghost.setAlpha(190)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(ghost)
            p.drawRect(box.translated(off, off))
            p.setBrush(self.s.ink)
            p.setPen(QPen(self.s.ink, 1.6))
            p.drawRect(box)
            p.setPen(self.s.paper_hi)
        else:
            wash = QColor(self.s.ink if self.s.dark else self.s.paper_hi)
            base, span = (20, 55) if self.s.dark else (70, 120)
            wash.setAlpha(int(base + span * self._lift))
            p.setBrush(wash)
            p.setPen(QPen(self.s.ink_soft if self._lift < 0.5 else self.s.ink,
                          1.3))
            p.drawRect(box)
            p.setPen(self.s.ink if self._lift > 0.4 else self.s.ink_soft)
        p.setFont(self.f)
        p.drawText(box, int(Qt.AlignmentFlag.AlignCenter), self.label)
        p.end()


class EvolveButton(QWidget):
    """Nút tiến hoá: một viên mực đang chực nổ, thở đều cho tới lúc bị bấm."""

    clicked = Signal()

    def __init__(self, label="Evolve", skin=PULP, parent=None):
        super().__init__(parent)
        self.label, self.s = label.upper(), skin
        self.f = Type.text(9, bold=True, letter=1.8, caps=True)
        w = QFontMetrics(self.f).horizontalAdvance(self.label) + 62
        self._size = QSize(w, 34)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._lift = 0.0
        self._beat = 0.0
        self._down = False

        self._a = QPropertyAnimation(self, b"lift", self)
        self._a.setDuration(180)
        self._a.setEasingCurve(QEasingCurve.Type.OutCubic)
        # nhịp thở chạy mãi, không cần ai bật
        self._pulse = QPropertyAnimation(self, b"beat", self)
        self._pulse.setDuration(1500)
        self._pulse.setStartValue(0.0)
        self._pulse.setEndValue(1.0)
        self._pulse.setLoopCount(-1)
        self._pulse.start()

    def sizeHint(self):
        return self._size

    def get_lift(self):
        return self._lift

    def set_lift(self, v):
        self._lift = v
        self.update()

    lift = Property(float, get_lift, set_lift)

    def get_beat(self):
        return self._beat

    def set_beat(self, v):
        self._beat = v
        self.update()

    beat = Property(float, get_beat, set_beat)

    def enterEvent(self, _):
        self._a.stop()
        self._a.setEndValue(1.0)
        self._a.start()

    def leaveEvent(self, _):
        self._a.stop()
        self._a.setEndValue(0.0)
        self._a.start()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._down = True
            self.update()

    def mouseReleaseEvent(self, e):
        if self._down and self.rect().contains(e.position().toPoint()):
            self.clicked.emit()
        self._down = False
        self.update()

    def _bolt(self, box):
        """Tia sét nhỏ đứng trước chữ."""
        x, y, h = box.x() + 15, box.center().y(), 9.0
        bolt = QPainterPath()
        bolt.moveTo(x + 3.4, y - h)
        bolt.lineTo(x - 3.4, y + 1.2)
        bolt.lineTo(x - 0.2, y + 1.2)
        bolt.lineTo(x - 3.0, y + h)
        bolt.lineTo(x + 4.2, y - 1.8)
        bolt.lineTo(x + 0.6, y - 1.8)
        bolt.closeSubpath()
        return bolt

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        box = QRectF(0, 2, self.width() - 4, self.height() - 6)
        if self._down:
            box.translate(1.5, 1.5)

        # quầng nổ chực bung ra, mạnh hơn khi con trỏ tới gần
        wave = (self._beat + 0.0) % 1.0
        for k in (0.0, 0.5):
            s = (wave + k) % 1.0
            spread = 3 + 11 * s * (0.55 + 0.45 * self._lift)
            ring = QColor(self.s.red)
            ring.setAlpha(int(110 * (1 - s) * (0.4 + 0.6 * self._lift)))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(ring, 1.4))
            p.drawRect(box.adjusted(-spread, -spread, spread, spread))

        throb = 0.5 + 0.5 * math.sin(self._beat * math.tau)
        off = 2.2 + 1.6 * self._lift + 0.8 * throb
        for color, dx, dy in ((self.s.blue, -off, -off), (self.s.red, off, off)):
            c = QColor(color)
            c.setAlpha(int(150 + 70 * self._lift))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(c)
            p.drawRect(box.translated(dx, dy))

        body = blend(self.s.ink, self.s.red, 0.10 + 0.30 * throb
                     + 0.25 * self._lift)
        p.setBrush(body)
        p.setPen(QPen(self.s.red, 1.5))
        p.drawRect(box)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(blend(self.s.yellow, QColor("#FFF3E2"), throb))
        p.drawPath(self._bolt(box))

        p.setFont(self.f)
        p.setPen(self.s.paper_hi)
        p.drawText(box.adjusted(24, 0, 0, 0),
                   int(Qt.AlignmentFlag.AlignCenter), self.label)
        p.end()


class CloseMark(QWidget):
    """Dấu ✕ ở góc tờ giấy."""

    clicked = Signal()

    def __init__(self, skin=PULP, parent=None):
        super().__init__(parent)
        self.s = skin
        self.setFixedSize(30, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._lift = 0.0
        self._a = QPropertyAnimation(self, b"lift", self)
        self._a.setDuration(160)

    def get_lift(self):
        return self._lift

    def set_lift(self, v):
        self._lift = v
        self.update()

    lift = Property(float, get_lift, set_lift)

    def enterEvent(self, _):
        self._a.stop()
        self._a.setEndValue(1.0)
        self._a.start()

    def leaveEvent(self, _):
        self._a.stop()
        self._a.setEndValue(0.0)
        self._a.start()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        box = QRectF(3, 3, 24, 24)
        wash = QColor(self.s.red)
        wash.setAlpha(int(30 + 150 * self._lift))
        p.setBrush(wash)
        p.setPen(QPen(self.s.ink_soft if self._lift < 0.5 else self.s.ink, 1.3))
        p.drawRect(box)
        p.setPen(QPen(self.s.ink if self._lift < 0.5 else self.s.paper_hi, 1.8))
        m = 7.5
        p.drawLine(box.adjusted(m, m, -m, -m).topLeft(),
                   box.adjusted(m, m, -m, -m).bottomRight())
        p.drawLine(box.adjusted(m, m, -m, -m).topRight(),
                   box.adjusted(m, m, -m, -m).bottomLeft())
        p.end()


class SectionRule(QWidget):
    """Tiêu đề mục: chữ hoa nhỏ rồi một gạch mực kéo hết dòng."""

    def __init__(self, text, color=None, skin=PULP, parent=None):
        super().__init__(parent)
        self.text = text
        self.color = color or skin.ink
        self.f = Type.text(8, bold=True, letter=1.6, caps=True)
        self.setFixedHeight(22)
        self.setSizePolicy(QSizePolicy.Policy.Preferred,
                           QSizePolicy.Policy.Fixed)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setFont(self.f)
        p.setPen(self.color)
        w = QFontMetrics(self.f).horizontalAdvance(self.text.upper())
        p.drawText(QRectF(0, 0, w + 4, self.height()),
                   int(Qt.AlignmentFlag.AlignVCenter), self.text)
        line = QColor(self.color)
        line.setAlpha(110)
        p.setPen(QPen(line, 1.4))
        y = self.height() / 2
        p.drawLine(QPointF(w + 12, y), QPointF(self.width(), y))
        p.end()


class Badge(QWidget):
    """Nhãn nhỏ: ĐẦU TIÊN / MỚI BỔ SUNG / ĐÃ SỬA / ABSOLUTE."""

    def __init__(self, text, kind, skin=PULP, parent=None):
        super().__init__(parent)
        self.text = text
        self.s = skin
        self.edge, self.fill = skin.accent(kind)
        self.f = Type.text(7, bold=True, letter=1.4, caps=True)
        w = QFontMetrics(self.f).horizontalAdvance(text.upper()) + 18
        self.setFixedSize(w, 20)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        box = QRectF(0, 0, self.width() - 1, self.height() - 1)
        p.setBrush(self.fill)
        p.setPen(QPen(self.edge, 1.3))
        p.drawRect(box)
        p.setFont(self.f)
        p.setPen(self.s.ink)
        p.drawText(box, int(Qt.AlignmentFlag.AlignCenter), self.text)
        p.end()


# ═══════════════════════════════════════════════════════════ chân dung
def _wants_clock(art):
    """Hàm vẽ có nhận tham số thời gian không — nếu có thì chân dung tự chạy."""
    if art is None:
        return False
    try:
        return len(inspect.signature(art).parameters) >= 3
    except (TypeError, ValueError):
        return False


class PortraitPlate(QWidget):
    """Khung chân dung: ảnh thật nếu có, không thì hình vẽ trong file nhân vật."""

    def __init__(self, profile, size, skin=PULP, parent=None):
        super().__init__(parent)
        self.profile = profile
        self.s = skin
        self.setFixedSize(size)
        path = profile.image_path()
        self.pixmap = QPixmap(str(path)) if path else QPixmap()
        if self.pixmap.isNull():
            self.pixmap = QPixmap()

        self._t = 0.0
        self._t0 = time.monotonic()
        if self.pixmap.isNull() and _wants_clock(profile.art):
            clock = QTimer(self)
            clock.timeout.connect(self._tick)
            clock.start(40)          # 25 hình/giây là đủ mượt cho một chân dung

    def _tick(self):
        self._t = time.monotonic() - self._t0
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        box = QRectF(1, 1, self.width() - 2, self.height() - 2)

        p.setClipRect(box)
        p.fillRect(box, self.s.paper_hi)
        p.fillRect(box, QBrush(_paper_tile(self.s)))

        if not self.pixmap.isNull():
            # phủ kín khung, cắt phần thừa, giữ đúng tỉ lệ ảnh
            scaled = self.pixmap.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation)
            x = box.center().x() - scaled.width() / 2
            y = box.center().y() - scaled.height() / 2
            p.drawPixmap(QPointF(x, y), scaled)
            p.fillRect(box, QBrush(_paper_tile(self.s)))
        elif self.profile.art:
            art_box = box.adjusted(6, 6, -6, -6)
            if _wants_clock(self.profile.art):
                self.profile.art(p, art_box, self._t)
            else:
                self.profile.art(p, art_box)
        else:
            self._empty(p, box)

        p.setClipping(False)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(self.s.frame, 2.0))
        p.drawRect(box)
        p.end()

    def _empty(self, p, box):
        """Chưa có ảnh và cũng chưa vẽ tay: in chữ cái đầu thật to."""
        letter = self.profile.name[:1].upper()
        f = Type.head(int(box.height() * 0.44), letter=1.0)
        p.setFont(f)
        for color, dx, dy in ((self.s.red, 3, 2.4), (self.s.blue, -2.6, -1.8)):
            c = QColor(color)
            c.setAlpha(150)
            p.setPen(c)
            p.drawText(box.translated(dx, dy),
                       int(Qt.AlignmentFlag.AlignCenter), letter)
        p.setPen(self.s.ink)
        p.drawText(box, int(Qt.AlignmentFlag.AlignCenter), letter)
        p.setFont(Type.text(8, letter=1.2, caps=True))
        p.setPen(self.s.ink_soft)
        p.drawText(box.adjusted(0, 0, 0, -14),
                   int(Qt.AlignmentFlag.AlignHCenter
                       | Qt.AlignmentFlag.AlignBottom), "chưa có ảnh")


class FactTable(QWidget):
    """Bảng thông tin: nhãn chữ hoa nhỏ, giá trị đậm, gạch ngăn từng dòng.

    Giá trị ngắn nằm cùng dòng với nhãn cho gọn; giá trị dài tự xuống dòng
    dưới nhãn và chiếm hết bề ngang. Chiều cao tính lại mỗi khi đổi bề ngang.
    """

    PAD = 7
    LABEL_W = 94
    GAP = 10

    def __init__(self, facts, width=None, skin=PULP, parent=None):
        super().__init__(parent)
        self.facts = facts
        self.s = skin
        self.f_label = Type.text(7, bold=True, letter=1.2, caps=True)
        self.f_value = Type.text(8, bold=True)
        self._rows = []
        if width:
            self.setFixedWidth(width)
        self._measure(width or 292)

    def _measure(self, w):
        fm_l, fm_v = QFontMetrics(self.f_label), QFontMetrics(self.f_value)
        room = w - self.LABEL_W - self.GAP
        rows, y = [], 0
        for label, value in self.facts:
            lh, vh = fm_l.height(), fm_v.height()
            inline = room > 70 and fm_v.horizontalAdvance(value) <= room
            if inline:
                rows.append((label, value, y, lh, vh, True))
                y += max(lh, vh) + self.PAD
            else:
                vh = fm_v.boundingRect(0, 0, max(60, w), 0,
                                       int(Qt.TextFlag.TextWordWrap),
                                       value).height()
                rows.append((label, value, y, lh, vh, False))
                y += lh + 2 + vh + self.PAD
        self._rows = rows
        if self.height() != y:
            self.setFixedHeight(max(0, y))

    def resizeEvent(self, e):
        if e.oldSize().width() != e.size().width():
            self._measure(e.size().width())
        super().resizeEvent(e)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rule = QColor(self.s.ink_soft)
        rule.setAlpha(70)
        for i, (label, value, y, lh, vh, inline) in enumerate(self._rows):
            if i:
                p.setPen(QPen(rule, 1.0))
                p.drawLine(QPointF(0, y - self.PAD / 2 - 1),
                           QPointF(self.width(), y - self.PAD / 2 - 1))
            row_h = max(lh, vh) if inline else lh
            p.setFont(self.f_label)
            p.setPen(self.s.ink_soft)
            p.drawText(QRectF(0, y, self.LABEL_W, row_h),
                       int(Qt.AlignmentFlag.AlignLeft
                           | Qt.AlignmentFlag.AlignVCenter), label)
            p.setFont(self.f_value)
            p.setPen(self.s.ink)
            if inline:
                p.drawText(QRectF(self.LABEL_W + self.GAP, y,
                                  self.width() - self.LABEL_W - self.GAP, row_h),
                           int(Qt.AlignmentFlag.AlignLeft
                               | Qt.AlignmentFlag.AlignVCenter), value)
            else:
                p.drawText(QRectF(0, y + lh + 2, self.width(), vh),
                           int(Qt.AlignmentFlag.AlignLeft
                               | Qt.AlignmentFlag.AlignTop
                               | Qt.TextFlag.TextWordWrap), value)
        p.end()


class TierLadder(QWidget):
    """Thang bậc tàn phá: mỗi bậc một nấc, càng lên cao mực càng đỏ."""

    NUM_W = 58
    GAP = 14

    def __init__(self, tiers, skin=PULP, parent=None):
        super().__init__(parent)
        self.tiers = tiers
        self.s = skin
        self.f_word = Type.text(7, bold=True, letter=1.5, caps=True)
        self.f_num = Type.head(26, letter=0.5)
        self.f_title = Type.text(10, bold=True)
        self.f_text = Type.text(9)
        self.f_speed = Type.text(7, bold=True, letter=1.1, caps=True)
        self._rows = []
        self.setSizePolicy(QSizePolicy.Policy.Preferred,
                           QSizePolicy.Policy.Fixed)
        self._measure(420)

    def _measure(self, w):
        fm_t = QFontMetrics(self.f_title)
        fm_b = QFontMetrics(self.f_text)
        fm_s = QFontMetrics(self.f_speed)
        room = max(80, w - self.NUM_W - 12)
        rows, y = [], 0
        for i, tier in enumerate(self.tiers):
            th = fm_t.height()
            bh = fm_b.boundingRect(0, 0, room, 0, int(Qt.TextFlag.TextWordWrap),
                                   tier.text).height()
            sh = fm_s.height() if tier.speed else 0
            h = max(56, th + 4 + bh + (5 + sh if sh else 0))
            rows.append((tier, i, y, th, bh, sh, h))
            y += h + self.GAP
        self._rows = rows
        self.setFixedHeight(max(0, y - self.GAP))

    def resizeEvent(self, e):
        if e.oldSize().width() != e.size().width():
            self._measure(e.size().width())
        super().resizeEvent(e)

    def _hue(self, i):
        span = max(1, len(self.tiers) - 1)
        return blend(self.s.yellow, self.s.red, i / span)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        room = max(80, self.width() - self.NUM_W - 12)
        spine = QColor(self.s.ink_soft)
        spine.setAlpha(70)
        x_spine = self.NUM_W - 14

        if self._rows:
            p.setPen(QPen(spine, 1.2))
            p.drawLine(QPointF(x_spine, self._rows[0][2] + 10),
                       QPointF(x_spine, self._rows[-1][2] + self._rows[-1][6]))

        for tier, i, y, th, bh, sh, h in self._rows:
            hue = self._hue(i)
            digits = "".join(c for c in tier.label if c.isdigit()) or str(i + 1)
            word = tier.label.rstrip("0123456789 ").upper() or "TIER"

            # nấc trên cột sống: ô đặc, càng cao càng đỏ
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(hue)
            p.drawRect(QRectF(x_spine - 3.5, y + 6.5, 7, 7))

            p.setFont(self.f_word)
            p.setPen(self.s.ink_soft)
            p.drawText(QRectF(0, y - 1, self.NUM_W - 22, 14),
                       int(Qt.AlignmentFlag.AlignRight
                           | Qt.AlignmentFlag.AlignVCenter), word)
            p.setFont(self.f_num)
            ghost = QColor(hue)
            ghost.setAlpha(150)
            num_box = QRectF(0, y + 8, self.NUM_W - 22, 30)
            flags = int(Qt.AlignmentFlag.AlignRight
                        | Qt.AlignmentFlag.AlignVCenter)
            p.setPen(ghost)
            p.drawText(num_box.translated(2.2, 1.8), flags, digits)
            p.setPen(self.s.ink)
            p.drawText(num_box, flags, digits)

            x = self.NUM_W
            p.setFont(self.f_title)
            p.setPen(hue if self.s.dark else self.s.ink)
            p.drawText(QRectF(x, y, room, th),
                       int(Qt.AlignmentFlag.AlignLeft
                           | Qt.AlignmentFlag.AlignVCenter), tier.title)
            p.setFont(self.f_text)
            p.setPen(self.s.ink)
            p.drawText(QRectF(x, y + th + 4, room, bh),
                       int(Qt.AlignmentFlag.AlignLeft
                           | Qt.AlignmentFlag.AlignTop
                           | Qt.TextFlag.TextWordWrap), tier.text)
            if sh:
                p.setFont(self.f_speed)
                p.setPen(hue)
                p.drawText(QRectF(x, y + th + 4 + bh + 5, room, sh),
                           int(Qt.AlignmentFlag.AlignLeft
                               | Qt.AlignmentFlag.AlignVCenter),
                           "▸  " + tier.speed)
        p.end()


class CardTitle(QWidget):
    """Tên nhân vật in như logo bìa, có hai lớp mực lệch trục."""

    def __init__(self, profile, skin=PULP, parent=None):
        super().__init__(parent)
        self.s = skin
        self.title = profile.name.upper()
        bits = [b for b in (profile.vi_name, profile.real_name) if b]
        self.sub = "   ·   ".join(bits)
        self.setFixedHeight(70 if self.sub else 52)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        size = 40
        while size > 16:
            f = Type.head(size, letter=1.4)
            if QFontMetrics(f).horizontalAdvance(self.title) <= self.width() - 6:
                break
            size -= 1
        p.setFont(f)
        base = QRectF(0, 0, self.width(), 48)
        flags = int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        for color, dx, dy in ((self.s.red, 2.6, 2.0), (self.s.blue, -2.2, -1.5)):
            c = QColor(color)
            c.setAlpha(170)
            p.setPen(c)
            p.drawText(base.translated(dx, dy), flags, self.title)
        p.setPen(self.s.ink)
        p.drawText(base, flags, self.title)

        if self.sub:
            p.setFont(Type.text(9, letter=1.3, caps=True))
            p.setPen(self.s.ink_soft)
            p.drawText(QRectF(1, 48, self.width(), 20), flags, self.sub)
        p.end()


# ═══════════════════════════════════════════════════════════ tai hồ sơ
class SheetTabs(QWidget):
    """Tai hồ sơ nhô lên trên mép giấy — một tai cho mỗi dạng đã mở."""

    picked = Signal(int)

    H = 28          # phần nhô lên trên tờ giấy
    LIP = 6         # phần chân ăn xuống dưới mép, để tai dính vào tờ giấy
    PADX = 20
    GAP = 5

    def __init__(self, entries, parent=None):
        super().__init__(parent)
        self.entries = list(entries)     # ((nhãn, skin), ...)
        self.index = 0
        self._hot = -1
        self.f = Type.text(8, bold=True, letter=1.5, caps=True)
        fm = QFontMetrics(self.f)
        self._w = [fm.horizontalAdvance(label.upper()) + self.PADX * 2
                   for label, _ in self.entries]
        self.setFixedSize(sum(self._w) + self.GAP * (len(self._w) - 1),
                          self.H + self.LIP)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def count(self):
        return len(self.entries)

    def set_index(self, i):
        self.index = i
        self.update()

    def _boxes(self):
        x = 0
        for i, w in enumerate(self._w):
            lift = 0 if i == self.index else 4
            yield i, QRectF(x, lift, w, self.H + self.LIP - lift)
            x += w + self.GAP

    def _at(self, pos):
        for i, box in self._boxes():
            if box.contains(pos):
                return i
        return -1

    def mouseMoveEvent(self, e):
        hot = self._at(e.position())
        if hot != self._hot:
            self._hot = hot
            self.update()

    def leaveEvent(self, _):
        self._hot = -1
        self.update()

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.MouseButton.LeftButton:
            return
        i = self._at(e.position())
        if i >= 0 and i != self.index:
            self.picked.emit(i)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        for i, box in self._boxes():
            label, skin = self.entries[i]
            live = i == self.index
            hot = i == self._hot

            fill = QColor(skin.paper_hi)
            if not live:
                fill = blend(fill, QColor(skin.scrim.red(), skin.scrim.green(),
                                          skin.scrim.blue()),
                             0.10 if hot else 0.28)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(fill)
            p.drawRect(box)
            p.fillRect(QRectF(box.x(), box.y(), box.width(), 3),
                       skin.red if live else _fade(skin.red, 0.5))

            frame = QColor(skin.frame)
            frame.setAlpha(255 if live else 140)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(frame, 1.6))
            p.drawRect(box)
            if live:
                # xoá nét đáy để tai dính liền vào tờ giấy bên dưới
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(fill)
                p.drawRect(QRectF(box.x() + 1.4, box.bottom() - self.LIP,
                                  box.width() - 2.8, self.LIP + 1))

            p.setFont(self.f)
            p.setPen(skin.ink if live or hot else skin.ink_soft)
            p.drawText(QRectF(box.x(), box.y() + 2, box.width(), self.H),
                       int(Qt.AlignmentFlag.AlignCenter), label)
        p.end()


# ═══════════════════════════════════════════════════════════ tờ hồ sơ
class Card(QWidget):
    close_asked = Signal()
    link_asked = Signal(str)
    evolve_asked = Signal()

    MARGIN = 26
    LEFT_W = 292
    GAP = 26
    TITLE_GAP = 12
    FOOT_GAP = 14
    PLATE_MIN = 150     # dưới mức này thì dồn bảng lý lịch sang cột đọc
    PLATE_FLOOR = 120   # nhỏ nhất tuyệt đối cho khung chân dung
    PLATE_MAX = 340

    def __init__(self, profile, meta, size, skin=PULP, parent=None):
        super().__init__(parent)
        self.profile = profile
        self.s = skin
        self._blocks = []
        self._anims = []
        self.setMouseTracking(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(self.MARGIN, self.MARGIN - 6,
                                self.MARGIN + SHADOW, self.MARGIN - 8 + SHADOW)
        root.setSpacing(0)
        self.header = self._header(meta)
        root.addWidget(self.header)
        root.addSpacing(2)

        self.title = CardTitle(profile, skin, self)
        root.addWidget(self.title)
        root.addSpacing(self.TITLE_GAP)

        body = QHBoxLayout()
        body.setSpacing(self.GAP)
        left, plate_col, facts_col = self._left(profile)
        body.addLayout(left, 0)
        body.addWidget(self._right(profile), 1)
        root.addLayout(body, 1)
        root.addSpacing(self.FOOT_GAP)
        self.footer = self._footer(profile)
        root.addWidget(self.footer)

        self.plate_col, self.facts_col = plate_col, facts_col
        # phần cột trái không phải chân dung: chú thích + khoảng cách
        self._plate_extra = (plate_col.sizeHint().height()
                             - self.plate.height())
        self._deep = False
        self.fit(size)

        # thứ tự và độ trễ của từng khối khi hiện ra
        self._blocks = [(self.header, 0), (self.title, 55), (plate_col, 110),
                        (self.scroll, 165), (facts_col, 220),
                        (self.footer, 265)]

    def fit(self, size):
        """Co chân dung cho vừa chiều cao thật của tờ giấy.

        Cửa sổ thấp quá thì bảng lý lịch rời cột trái, xuống nằm cuối cột
        đọc — thà cuộn xuống còn hơn bị cắt mất.
        """
        m = self.layout().contentsMargins()
        chrome = (m.top() + m.bottom() + self.header.sizeHint().height() + 2
                  + self.title.height() + self.TITLE_GAP + self.FOOT_GAP
                  + self.footer.sizeHint().height())
        free = size.height() - chrome - self._plate_extra
        room = free - self.facts_col.sizeHint().height()

        self._deep = room < self.PLATE_MIN
        self.facts_col.setVisible(not self._deep)
        self.facts_deep.setVisible(self._deep)
        if self._deep:
            room = free
        self.plate.setFixedHeight(
            int(max(self.PLATE_FLOOR, min(self.PLATE_MAX, room))))

    # ---------------------------------------------------------- dựng khối
    def _label(self, text, font, color, wrap=True, extra=""):
        lab = QLabel(text)
        lab.setFont(font)
        lab.setWordWrap(wrap)
        lab.setStyleSheet(f"color:{color.name()};{extra}")
        return lab

    def _header(self, meta):
        bar = QWidget(self)
        row = QHBoxLayout(bar)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)
        kicker = QLabel(self.profile.kicker or "Hồ sơ ác nhân")
        kicker.setFont(Type.text(8, bold=True, letter=2.0, caps=True))
        kicker.setStyleSheet(f"color:{self.s.red.name()}")
        row.addWidget(kicker)
        if meta.get("note"):
            row.addWidget(Badge(meta["note"], meta.get("kind", "plain"),
                                self.s))
        row.addStretch(1)
        stamp = QLabel(meta.get("stamp", ""))
        stamp.setFont(Type.text(8, letter=1.2, caps=True))
        stamp.setStyleSheet(f"color:{self.s.ink_soft.name()}")
        row.addWidget(stamp)
        mark = CloseMark(self.s, bar)
        mark.clicked.connect(self.close_asked)
        row.addWidget(mark)
        return bar

    def _left(self, profile):
        col = QVBoxLayout()
        col.setSpacing(0)
        col.setContentsMargins(0, 0, 0, 0)

        plate_col = QWidget(self)
        plate_box = QVBoxLayout(plate_col)
        plate_box.setContentsMargins(0, 0, 0, 0)
        plate_box.setSpacing(7)
        self.plate = PortraitPlate(profile, QSize(self.LEFT_W, self.PLATE_MAX),
                                   self.s)
        plate_box.addWidget(self.plate)
        if profile.caption:
            cap = self._label(profile.caption, Type.text(7, letter=0.8,
                                                         caps=True),
                              self.s.ink_soft)
            cap.setFixedWidth(self.LEFT_W)
            plate_box.addWidget(cap)
        plate_col.setFixedWidth(self.LEFT_W)
        col.addWidget(plate_col)

        # Khoảng hở nằm trong khối lý lịch, để nó biến mất cùng khối khi ẩn.
        facts_col = self._facts_block(profile, self.LEFT_W, self, top=16)
        col.addWidget(facts_col)
        col.addStretch(1)
        return col, plate_col, facts_col

    def _facts_block(self, profile, width, parent, top=0):
        """Khối 'Lý lịch'. Dùng cho cả cột trái lẫn cuối cột đọc."""
        block = QWidget(parent)
        box = QVBoxLayout(block)
        box.setContentsMargins(0, top, 0, 0)
        box.setSpacing(8)
        if profile.facts:      # hồ sơ chưa điền lý lịch thì bỏ hẳn khối này
            box.addWidget(SectionRule("Lý lịch", skin=self.s))
            box.addWidget(FactTable(profile.facts, width, self.s))
        if width:
            block.setFixedWidth(width)
        return block

    def _bullets(self, items):
        """Danh sách gạch đầu dòng; mỗi mục có thể có một tên in đậm dẫn dòng."""
        rows = []
        for item in items:
            if isinstance(item, (tuple, list)):
                lead, text = item
                body = (f"<b style='color:{self.s.ink.name()}'>{lead}</b>"
                        f"&nbsp;—&nbsp;{text}")
            else:
                body = item
            rows.append(f"<p style='margin:0 0 8px 0'>"
                        f"<span style='color:{self.s.red.name()}'>▸</span>"
                        f"&nbsp;&nbsp;{body}</p>")
        lab = QLabel(f"<div>{''.join(rows)}</div>")
        lab.setFont(Type.text(10))
        lab.setWordWrap(True)
        lab.setTextFormat(Qt.TextFormat.RichText)
        lab.setStyleSheet(f"color:{self.s.ink.name()}")
        return lab

    def _right(self, profile):
        self.body = QWidget()
        self.body.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        box = QVBoxLayout(self.body)
        box.setContentsMargins(0, 0, 12, 6)
        box.setSpacing(11)

        if profile.tagline:
            lead = self._label(
                profile.tagline, Type.text(12, italic=True), self.s.ink,
                extra=f"border-left:3px solid {self.s.red.name()};"
                      "padding:2px 0 4px 13px;")
            box.addWidget(lead)
            box.addSpacing(3)

        for para in profile.summary:
            box.addWidget(self._label(para, Type.text(10), self.s.ink,
                                      extra="line-height:150%"))

        if profile.powers:
            box.addSpacing(8)
            box.addWidget(SectionRule("Năng lực & thủ đoạn", skin=self.s))
            box.addWidget(self._bullets(profile.powers))

        for section in profile.sections:
            box.addSpacing(9)
            box.addWidget(SectionRule(section.title, self.s.red, self.s))
            if section.intro:
                box.addWidget(self._label(section.intro,
                                          Type.text(10, italic=True),
                                          self.s.ink_soft))
            if section.items:
                box.addWidget(self._bullets(section.items))

        if profile.tiers:
            box.addSpacing(9)
            box.addWidget(SectionRule("Thang bậc tàn phá", self.s.red, self.s))
            box.addWidget(TierLadder(profile.tiers, self.s))

        if profile.blurb:
            box.addSpacing(10)
            tint = self.s.yellow
            wash = (f"rgba({tint.red()},{tint.green()},{tint.blue()},"
                    f"{40 if self.s.dark else 60})")
            box.addWidget(self._label(
                profile.blurb, Type.text(10, italic=True), self.s.ink,
                extra=f"background:{wash};border:1px solid {tint.name()};"
                      "padding:11px 13px;"))

        # Bản dự phòng của bảng lý lịch, chỉ hiện khi cột trái hết chỗ.
        self.facts_deep = self._facts_block(profile, None, self.body)
        self.facts_deep.hide()
        box.addSpacing(6)
        box.addWidget(self.facts_deep)
        box.addStretch(1)

        self.scroll = QScrollArea(self)
        self.scroll.setWidget(self.body)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.viewport().setAutoFillBackground(False)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(f"""
            QScrollArea, QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: transparent; width: 9px; margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {self.s.ink_soft.name()}; min-height: 40px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self.s.red.name()};
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{ height: 0 }}
            QScrollBar::add-page, QScrollBar::sub-page {{ background: none }}
        """)
        return self.scroll

    def _footer(self, profile):
        bar = QWidget(self)
        row = QHBoxLayout(bar)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(9)
        links = profile.links or (("Mở trang web", ""),)
        for i, (label, url) in enumerate(links):
            btn = InkButton(label, solid=(i == 0), skin=self.s, parent=bar)
            btn.clicked.connect(lambda u=url: self.link_asked.emit(u))
            row.addWidget(btn)
        row.addStretch(1)
        if profile.evolution is not None:
            evolve = EvolveButton(profile.evolve_label or "Evolve", self.s, bar)
            evolve.clicked.connect(self.evolve_asked)
            row.addWidget(evolve)
        close = InkButton("Đóng", skin=self.s, parent=bar)
        close.clicked.connect(self.close_asked)
        row.addWidget(close)
        return bar

    # ------------------------------------------------------ hiện nội dung
    def _showing(self):
        """Các khối thật sự đang có mặt trên tờ giấy."""
        return [(w, d) for w, d in self._blocks
                if not (self._deep and w is self.facts_col)]

    def arm(self):
        """Giấu mọi khối trước khi tờ giấy bay vào."""
        self.layout().activate()
        for widget, _ in self._showing():
            widget.setGraphicsEffect(None)
            fx = QGraphicsOpacityEffect(widget)
            fx.setOpacity(0.0)
            widget.setGraphicsEffect(fx)

    def play(self):
        """Thả từng khối vào chỗ, lệch nhau vài phần trăm giây."""
        self.layout().activate()
        for widget, delay in self._showing():
            widget.setGraphicsEffect(None)
            self._anims.append(reveal(widget, delay))

    def stop(self):
        for a in self._anims:
            a.stop()
        self._anims.clear()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        paint_sheet(p, sheet_box(QRectF(self.rect())), skin=self.s)
        p.end()


# ═══════════════════════════════════════════════════════════════ sân khấu
class CharacterStage(QWidget):
    """Lớp phủ toàn cửa sổ: màn tối, tờ giấy bay vào, nội dung hiện dần."""

    closed = Signal()
    link_asked = Signal(str)
    form_changed = Signal(object)     # hồ sơ của dạng vừa được mở ra

    PAD = 44          # khoảng hở tối thiểu quanh tờ giấy
    MAX = QSize(980, 700)
    BOOM_MS = 1300    # nứt, nổ, rồi quét lại từ đầu
    SWAP_MS = 620     # đổi tai hồ sơ: chỉ một nhát quét

    def __init__(self, parent, profile, meta, origin):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setGeometry(parent.rect())
        self._veil = 0.0
        self._morph = 0.0
        self._closing = False
        self._origin_hint = QRectF(origin)

        # chuỗi các dạng của nhân vật; lúc đầu chỉ dạng đầu tiên được mở
        self.forms = []
        node = profile
        while node is not None:
            self.forms.append(node)
            node = node.evolution
        self.index = 0
        self.unlocked = 1
        self.base_meta = meta
        self.skin = skin_of(profile)

        self.final = self._frame()
        self.start = self._shrunk(self._origin_hint, self.final)
        self.tabs = None
        self.card = None
        self._build_card()
        self.card.hide()

        # trạng thái của màn tiến hoá
        self._fx = 0.0
        self._fx_boom = False
        self._busy = False
        self._pending = 0
        self._from = self._to = self.skin
        self._noise = [0.5] * 24
        self._shards = []
        self._cracks = []

        self._a_veil = QPropertyAnimation(self, b"veil", self)
        self._a_morph = QPropertyAnimation(self, b"morph", self)
        self._a_fx = QPropertyAnimation(self, b"fx", self)
        self._a_fx.setEasingCurve(QEasingCurve.Type.Linear)
        self._a_fx.finished.connect(self._fx_done)
        self._jitter = QTimer(self)
        self._jitter.setInterval(28)
        self._jitter.timeout.connect(self._reroll)

    # ------------------------------------------------------------ hình học
    def _frame(self):
        """Khung tờ giấy: to nhất có thể trong cửa sổ, chừa lề PAD."""
        w = min(self.MAX.width(), self.width() - self.PAD * 2)
        h = min(self.MAX.height(), self.height() - self.PAD * 2)
        w, h = max(w, 320), max(h, 260)
        return QRectF((self.width() - w) / 2, (self.height() - h) / 2, w, h)

    def _layout_card(self):
        self.final = self._frame()
        if self.card is not None:
            self.card.fit(self.final.size().toSize())
            self.card.setGeometry(self.final.toRect())
        self.start = self._shrunk(self._origin_hint, self.final)
        self._place_tabs()

    @staticmethod
    def _shrunk(origin, final):
        """Khung xuất phát: cùng tỉ lệ tờ giấy, rộng bằng con chip, đúng chỗ."""
        if final.width() <= 0:
            return QRectF(origin)
        scale = max(0.08, min(1.0, origin.width() / final.width()))
        w, h = final.width() * scale, final.height() * scale
        c = origin.center()
        return QRectF(c.x() - w / 2, c.y() - h / 2, w, h)

    @staticmethod
    def _blend(a, b, t):
        return QRectF(a.x() + (b.x() - a.x()) * t,
                      a.y() + (b.y() - a.y()) * t,
                      a.width() + (b.width() - a.width()) * t,
                      a.height() + (b.height() - a.height()) * t)

    def relayout(self):
        self.setGeometry(self.parent().rect())
        self._layout_card()
        self.update()

    # ---------------------------------------------------- thuộc tính động
    def get_veil(self):
        return self._veil

    def set_veil(self, v):
        self._veil = v
        self.update()

    veil = Property(float, get_veil, set_veil)

    def get_morph(self):
        return self._morph

    def set_morph(self, v):
        self._morph = v
        self.update()

    morph = Property(float, get_morph, set_morph)

    def get_fx(self):
        return self._fx

    def set_fx(self, v):
        self._fx = v
        self.update()

    fx = Property(float, get_fx, set_fx)

    # ------------------------------------------------------------- vòng đời
    def _meta_for(self, profile):
        if profile is self.forms[0]:
            return self.base_meta
        return {"stamp": profile.stamp, "note": profile.note,
                "kind": profile.note_kind}

    def _build_card(self):
        profile = self.forms[self.index]
        self.skin = skin_of(profile)
        self.card = Card(profile, self._meta_for(profile),
                         self.final.size().toSize(), self.skin, self)
        self.card.setGeometry(self.final.toRect())
        self.card.close_asked.connect(self.dismiss)
        self.card.link_asked.connect(self.link_asked)
        self.card.evolve_asked.connect(self.evolve)

    def open(self):
        self.show()
        self.raise_()
        self.setFocus()
        self.card.arm()

        self._a_veil.stop()
        self._a_veil.setDuration(250)
        self._a_veil.setStartValue(0.0)
        self._a_veil.setEndValue(1.0)
        self._a_veil.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._a_veil.start()

        self._a_morph.stop()
        self._a_morph.setDuration(460)
        self._a_morph.setStartValue(0.0)
        self._a_morph.setEndValue(1.0)
        # vào chậm - giữa nhanh - ra chậm, đúng nhịp Morph của PowerPoint
        self._a_morph.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._a_morph.finished.connect(self._landed)
        self._a_morph.start()

    def _landed(self):
        if self._closing:
            return
        self.card.show()
        self.card.play()
        self.update()

    def dismiss(self):
        if self._closing:
            return
        self._closing = True
        self._jitter.stop()
        self._a_fx.stop()
        self._busy = False
        if self.tabs is not None:
            self.tabs.hide()
        if self.card is not None:
            self.card.stop()
            self.card.hide()

        self._a_morph.stop()
        self._a_morph.setDuration(300)
        self._a_morph.setStartValue(self._morph)
        self._a_morph.setEndValue(0.0)
        self._a_morph.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._a_morph.start()

        # màn phủ tắt chậm hơn tờ giấy một nhịp, để tờ giấy kịp thu về hẳn
        self._a_veil.stop()
        self._a_veil.setDuration(360)
        self._a_veil.setStartValue(self._veil)
        self._a_veil.setEndValue(0.0)
        self._a_veil.setEasingCurve(QEasingCurve.Type.InCubic)
        self._a_veil.finished.connect(self._gone)
        self._a_veil.start()

    def _gone(self):
        self.closed.emit()
        self.hide()
        self.deleteLater()

    # ------------------------------------------------------------ tiến hoá
    def evolve(self):
        """Nút tiến hoá: sang dạng kế tiếp, nổ tung nếu đây là lần đầu."""
        nxt = self.index + 1
        if nxt < len(self.forms):
            self._go(nxt, boom=nxt >= self.unlocked)

    def _go(self, index, boom):
        if self._busy or self._closing or index == self.index:
            return
        if not 0 <= index < len(self.forms):
            return
        self._busy = True
        self._fx_boom = boom
        self._pending = index
        self._from = self.skin
        self._to = skin_of(self.forms[index])

        box = sheet_box(QRectF(self.final))
        self._cracks = self._make_cracks(box) if boom else []
        self._shards = self._make_shards(box) if boom else []

        old, self.card = self.card, None
        old.stop()
        old.hide()
        old.deleteLater()
        if self.tabs is not None:
            self.tabs.hide()

        self._reroll()
        self._jitter.start()
        self._a_fx.stop()
        self._a_fx.setDuration(self.BOOM_MS if boom else self.SWAP_MS)
        self._a_fx.setStartValue(0.0)
        self._a_fx.setEndValue(1.0)
        self._a_fx.start()

    def _fx_done(self):
        self._jitter.stop()
        self._busy = False
        self._fx = 0.0
        if self._closing:
            return
        self.index = self._pending
        self.unlocked = max(self.unlocked, self.index + 1)
        self._build_card()
        self.card.arm()
        self.card.show()
        self.card.play()
        self._sync_tabs()
        self.form_changed.emit(self.forms[self.index])
        self.update()

    def _reroll(self):
        """Bốc lại nắm số nhiễu — nguồn rung, giật và sọc của cả màn hiệu ứng."""
        seed = int(time.monotonic() * 1000) & 0xFFFF
        out = []
        for i in range(24):
            seed = (seed * 1103515245 + 12345 + i * 7) & 0x7FFFFFFF
            out.append(seed / 0x7FFFFFFF)
        self._noise = out
        self.update()

    def _sync_tabs(self):
        if self.unlocked < 2:
            return
        entries = [(f.tab or f.name, skin_of(f))
                   for f in self.forms[:self.unlocked]]
        fresh = self.tabs is None or self.tabs.count() != len(entries)
        if fresh:
            if self.tabs is not None:
                self.tabs.deleteLater()
            self.tabs = SheetTabs(entries, self)
            self.tabs.picked.connect(lambda i: self._go(i, boom=False))
        self.tabs.set_index(self.index)
        self._place_tabs()
        self.tabs.show()
        self.tabs.raise_()
        if fresh:
            reveal(self.tabs, 90, distance=12, duration=380)

    def _place_tabs(self):
        if self.tabs is None:
            return
        box = sheet_box(QRectF(self.final))
        self.tabs.move(int(box.x()),
                       int(max(2, box.y() - SheetTabs.H)))

    # -------------------------------------------------------------- nhập
    def keyPressEvent(self, e):
        # Không dùng phím Tab để đảo tai hồ sơ: Qt nuốt Tab cho việc chuyển
        # tiêu điểm trước khi widget kịp nhìn thấy. Mũi tên trái/phải thì không.
        step = {Qt.Key.Key_Left: -1, Qt.Key.Key_Right: 1}.get(e.key())
        if e.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Backspace):
            self.dismiss()
        elif step and self.unlocked > 1:
            self._go((self.index + step) % self.unlocked, boom=False)
        else:
            super().keyPressEvent(e)

    def mousePressEvent(self, e):
        if self._busy:
            return
        if not self.final.contains(e.position()):
            self.dismiss()

    # ----------------------------------------------------- mảnh vỡ & nứt
    def _rolls(self, seed):
        state = [(int(seed) & 0x7FFFFFFF) or 1]

        def roll(lo=0.0, hi=1.0):
            state[0] = (state[0] * 1103515245 + 12345) & 0x7FFFFFFF
            return lo + (hi - lo) * (state[0] / 0x7FFFFFFF)
        return roll

    def _make_cracks(self, box):
        """Những đường nứt bò ra từ giữa tờ giấy trước khi nó vỡ."""
        roll = self._rolls(int(box.width()) * 31 + 17)
        c = box.center()
        step = max(box.width(), box.height()) * 0.5 / 6
        cracks = []
        for i in range(9):
            a = math.radians(i * 40 + roll(-15, 15))
            x, y = c.x(), c.y()
            pts = [QPointF(x, y)]
            for _ in range(6):
                a += math.radians(roll(-26, 26))
                x += math.cos(a) * step * roll(0.6, 1.4)
                y += math.sin(a) * step * roll(0.6, 1.4)
                pts.append(QPointF(x, y))
            cracks.append(pts)
        return cracks

    def _make_shards(self, box):
        """Xé tờ giấy thành lưới mảnh méo, mỗi mảnh một hướng và một tốc độ.

        Mảnh gần tâm bay trước, mảnh ngoài rìa đi sau — vụ nổ lan ra chứ
        không bung một lượt như mở quạt.
        """
        roll = self._rolls(int(box.height()) * 13 + 5)
        cols, rows = 7, 5
        jx = box.width() / cols * 0.32
        jy = box.height() / rows * 0.32
        grid = []
        for i in range(cols + 1):
            column = []
            for j in range(rows + 1):
                x = box.x() + box.width() * i / cols
                y = box.y() + box.height() * j / rows
                if 0 < i < cols:
                    x += roll(-jx, jx)
                if 0 < j < rows:
                    y += roll(-jy, jy)
                column.append(QPointF(x, y))
            grid.append(column)

        c = box.center()
        far = math.hypot(box.width(), box.height()) / 2
        shards = []
        for i in range(cols):
            for j in range(rows):
                poly = QPolygonF([grid[i][j], grid[i + 1][j],
                                  grid[i + 1][j + 1], grid[i][j + 1]])
                hub = poly.boundingRect().center()
                vx, vy = hub.x() - c.x(), hub.y() - c.y()
                d = math.hypot(vx, vy) or 1.0
                shards.append((poly, vx / d, vy / d, roll(-200, 200),
                               0.18 * (d / far), roll(0.7, 1.4)))
        return shards

    # -------------------------------------------------------------- vẽ
    def _veil_now(self):
        """Màn phủ đổi màu ngay quanh khoảnh khắc nổ, không đợi tới lúc xong."""
        if not self._busy:
            return self.skin.scrim, _veil_tile(self.skin)
        k = max(0.0, min(1.0, (self._fx - 0.22) / 0.30))
        return (blend(self._from.scrim, self._to.scrim, k),
                _veil_tile(self._to if k > 0.5 else self._from))

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        scrim, grid = self._veil_now()
        p.fillRect(self.rect(), _fade(scrim, self._veil))
        p.setOpacity(self._veil)
        p.fillRect(self.rect(), QBrush(grid))
        p.setOpacity(1.0)

        if self._busy:
            self._paint_fx(p)
        elif self.card is None or self.card.isHidden():
            # Trong lúc bay: tờ giấy trống. Hạ cánh xong thì Card thật lên tiếng.
            t = max(0.0, min(1.0, self._morph))
            rect = self._blend(self.start, self.final, t)
            scale = rect.width() / max(1.0, self.final.width())
            paint_sheet(p, sheet_box(rect, scale),
                        alpha=min(1.0, 0.25 + t * 1.15), scale=scale,
                        skin=self.skin)
        p.end()

    # ------------------------------------------------------ màn tiến hoá
    def _paint_fx(self, p):
        box = sheet_box(QRectF(self.final))
        if self._fx_boom:
            self._paint_boom(p, box)
        else:
            self._paint_wipe(p, box)

    def _paint_boom(self, p, box):
        t = self._fx
        ctr = box.center()
        span = math.hypot(box.width(), box.height()) / 2
        ignite = 0.30

        if t < ignite:                       # ── nạp: rung lên rồi nứt ra
            k = t / ignite
            p.save()
            amp = 6.0 * k * k
            p.translate((self._noise[0] - 0.5) * amp,
                        (self._noise[1] - 0.5) * amp)
            paint_sheet(p, box, skin=self._from)
            p.setClipRect(box)
            self._paint_cracks(p, k)
            # lò lửa nhen dưới lớp giấy, hắt ra từ chính chỗ nứt
            heat = QRadialGradient(ctr, span * (0.4 + 0.8 * k))
            for stop, weight in ((0.0, 0.62), (0.4, 0.20), (1.0, 0.0)):
                tone = QColor(self._to.red)
                tone.setAlpha(int(255 * weight * k * k))
                heat.setColorAt(stop, tone)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(heat)
            p.drawRect(box)
            p.restore()
            return

        prog = (t - ignite) / (1 - ignite)

        # tờ giấy mới được quét lại từ giữa ra
        build = (t - 0.42) / 0.58
        if build > 0:
            self._paint_rebuild(p, box, min(1.0, build))
            self._paint_motes(p, box, min(1.0, build))

        # tờ giấy nguyên vẹn còn ám lại một nhịp, để dải màu và lưới in
        # không biến mất đột ngột ngay khi mảnh đầu tiên bung ra
        ghost = max(0.0, 1.0 - prog / 0.12)
        if ghost > 0:
            paint_sheet(p, box, alpha=ghost, skin=self._from)

        # mảnh giấy cũ văng ra ngoài rồi tan; mảnh chưa tới lượt thì còn nguyên
        reach = span * 2.0
        for poly, dx, dy, spin, lag, speed in self._shards:
            s = (prog - lag) / max(0.05, 1.0 - lag)
            s = min(1.0, max(0.0, s))
            alpha = max(0.0, 1.0 - s * 1.25)
            if alpha <= 0:
                continue
            ease = s ** 0.55          # bung rất nhanh rồi trôi chậm lại
            hub = poly.boundingRect().center()
            p.save()
            p.translate(dx * reach * speed * ease,
                        dy * reach * speed * ease + 26 * ease * ease)
            p.translate(hub)
            p.rotate(spin * ease)
            p.translate(-hub)
            # bóng đổ và nét viền chỉ rõ dần khi mảnh đã rời khỏi tờ giấy
            lift = min(1.0, s * 4)
            tint = QColor(self._from.red)
            tint.setAlpha(int(110 * alpha * lift))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(tint)
            p.drawPolygon(poly.translated(3.0 * ease, 2.6 * ease))
            p.setBrush(_fade(self._from.paper_hi, alpha))
            p.setPen(QPen(_fade(self._from.frame,
                                alpha * (0.2 + 0.6 * lift)), 1.0))
            p.drawPolygon(poly)
            p.restore()

        # sóng xung kích: hai vòng dày, tắt nhanh
        p.setBrush(Qt.BrushStyle.NoBrush)
        for i, color in enumerate((QColor("#FFF4EA"), self._to.red)):
            s = (prog - i * 0.05) / 0.32
            if not 0 < s < 1:
                continue
            r = span * 1.6 * (s ** 0.6)
            ring = QColor(color)
            ring.setAlpha(int(200 * (1 - s) ** 1.5))
            p.setPen(QPen(ring, 1.5 + 15 * (1 - s)))
            p.drawEllipse(ctr, r * 1.08, r * 0.95)

        # loé trắng: một nhịp ngắn, sáng nhất ở tâm
        flash = max(0.0, 1.0 - prog / 0.11)
        if flash > 0:
            burst = QRadialGradient(ctr, span * 1.7)
            for stop, weight in ((0.0, 1.0), (0.35, 0.55), (1.0, 0.0)):
                tone = QColor(255, 248, 240)
                tone.setAlpha(int(255 * weight * flash))
                burst.setColorAt(stop, tone)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(burst)
            p.drawRect(self.rect())
            p.fillRect(self.rect(), QColor(255, 248, 240, int(80 * flash)))

    def _paint_cracks(self, p, k):
        """Vết nứt: rãnh mực đen, trong lòng rãnh có ánh sáng rò lên."""
        p.setBrush(Qt.BrushStyle.NoBrush)
        for pts in self._cracks:
            n = max(2, int(len(pts) * min(1.0, k * 1.3)))
            path = QPainterPath(pts[0])
            for q in pts[1:n]:
                path.lineTo(q)
            for color, w, a in ((self._from.frame, 3.0, 220),
                                (self._to.red, 1.8, 200),
                                (QColor("#FFF4EA"), 0.7, 240)):
                c = QColor(color)
                c.setAlpha(int(a * min(1.0, k * 1.4)))
                p.setPen(QPen(c, max(0.4, w * k)))
                p.drawPath(path)

    # khung xương của tấm hồ sơ, theo tỉ lệ khung giấy: (x, y, rộng, cao)
    WIRE = (((0.030, 0.030, 0.150, 0.016), (0.740, 0.030, 0.230, 0.016),
             (0.030, 0.070, 0.560, 0.070), (0.030, 0.158, 0.300, 0.014)),
            ((0.030, 0.200, 0.300, 0.330), (0.030, 0.548, 0.220, 0.012)),
            ((0.375, 0.200, 0.590, 0.055), (0.375, 0.272, 0.590, 0.011),
             (0.375, 0.298, 0.590, 0.011), (0.375, 0.324, 0.520, 0.011)),
            ((0.030, 0.600, 0.300, 0.011), (0.030, 0.640, 0.300, 0.011),
             (0.030, 0.680, 0.300, 0.011), (0.030, 0.720, 0.300, 0.011),
             (0.375, 0.380, 0.590, 0.011), (0.375, 0.406, 0.590, 0.011),
             (0.375, 0.432, 0.470, 0.011)),
            ((0.375, 0.490, 0.300, 0.020), (0.375, 0.530, 0.590, 0.011),
             (0.375, 0.556, 0.590, 0.011), (0.375, 0.582, 0.540, 0.011),
             (0.375, 0.622, 0.590, 0.011), (0.375, 0.648, 0.500, 0.011)),
            ((0.030, 0.912, 0.130, 0.048), (0.175, 0.912, 0.160, 0.048),
             (0.850, 0.912, 0.120, 0.048)))

    def _paint_rebuild(self, p, box, b):
        """Tờ giấy mới hiện ra như đang được quét, rồi tự dựng lấy bố cục."""
        ease = 1 - (1 - b) ** 3
        h = box.height() * ease
        band = QRectF(box.x() - 30, box.center().y() - h / 2,
                      box.width() + 60, h)
        p.save()
        p.setClipRect(band)
        paint_sheet(p, box, alpha=0.35 + 0.65 * ease, skin=self._to)

        # khung xương hiện dần theo từng đợt, rồi mờ đi khi tấm thật sắp tới
        show = min(1.0, b / 0.72)
        gone = max(0.0, (b - 0.74) / 0.26)
        if gone < 1.0:
            steps = len(self.WIRE)
            for i, group in enumerate(self.WIRE):
                lit = (show * steps) - i
                if lit <= 0:
                    continue
                strength = min(1.0, lit) * (1.0 - gone)
                for k, (fx, fy, fw, fh) in enumerate(group):
                    r = QRectF(box.x() + box.width() * fx,
                               box.y() + box.height() * fy,
                               box.width() * fw, box.height() * fh)
                    if i == 1 and k == 0:      # ô chân dung: chỉ kẻ viền
                        line = QColor(self._to.blue)
                        line.setAlpha(int(150 * strength))
                        p.setBrush(Qt.BrushStyle.NoBrush)
                        p.setPen(QPen(line, 1.4))
                        p.drawRect(r)
                        p.drawLine(r.topLeft(), r.bottomRight())
                        p.drawLine(r.topRight(), r.bottomLeft())
                        continue
                    tone = QColor(self._to.blue if i == 0 or i == 5
                                  else self._to.ink_soft)
                    tone.setAlpha(int((120 if i in (0, 5) else 90) * strength))
                    p.setPen(Qt.PenStyle.NoPen)
                    p.setBrush(tone)
                    p.drawRect(r)

        if b < 0.9:
            for i in range(0, 18, 3):
                n1 = self._noise[i % 24]
                n2 = self._noise[(i + 1) % 24]
                n3 = self._noise[(i + 2) % 24]
                bar = QRectF(box.x() + (n3 - 0.5) * 46 * (1 - b),
                             box.y() + n1 * box.height(),
                             box.width(), 1.5 + n2 * 9)
                tone = QColor(self._to.blue if i % 2 else self._to.red)
                tone.setAlpha(int(95 * (1 - b)))
                p.fillRect(bar, tone)
        p.restore()

        if b < 1:
            edge = QColor(self._to.blue)
            edge.setAlpha(int(230 * (1 - b)))
            p.setPen(QPen(edge, 1.8))
            p.drawLine(band.topLeft(), band.topRight())
            p.drawLine(band.bottomLeft(), band.bottomRight())

    def _paint_motes(self, p, box, b):
        roll = self._rolls(4242)
        ctr = box.center()
        far = math.hypot(box.width(), box.height()) * 0.8
        ease = b ** 0.6
        bright = 1.0 - abs(b * 2 - 1)
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(70):
            a = math.radians(roll(0, 360))
            r0 = far * roll(0.8, 1.35)
            r1 = far * roll(0.08, 0.42)
            r = r0 + (r1 - r0) * ease
            tone = QColor(self._to.red if i % 3 == 0 else self._to.blue)
            tone.setAlpha(int(210 * bright))
            p.setBrush(tone)
            p.drawEllipse(QPointF(ctr.x() + math.cos(a) * r,
                                  ctr.y() + math.sin(a) * r * 0.82),
                          1.5, 1.5)

    def _paint_wipe(self, p, box):
        """Đổi tai hồ sơ: một nhát quét chạy dọc tờ giấy, thay da giữa đường."""
        t = self._fx
        y = box.y() + box.height() * t

        p.save()
        p.setClipRect(QRectF(box.x() - 30, y, box.width() + 60,
                             box.bottom() - y))
        paint_sheet(p, box, skin=self._from)
        p.restore()

        p.save()
        p.setClipRect(QRectF(box.x() - 30, box.y() - 30, box.width() + 60,
                             y - box.y() + 30))
        paint_sheet(p, box, skin=self._to)
        p.restore()

        p.save()
        p.setClipRect(box)
        for i in range(0, 12, 3):
            n1 = self._noise[i % 24]
            n2 = self._noise[(i + 1) % 24]
            tone = QColor(self._to.blue if i % 2 else self._to.red)
            tone.setAlpha(110)
            p.fillRect(QRectF(box.x() + (n2 - 0.5) * 40,
                              y - 14 + n1 * 28, box.width(), 1.5 + n2 * 5),
                       tone)
        p.restore()

        edge = QColor(self._to.blue)
        edge.setAlpha(235)
        p.setPen(QPen(edge, 2.0))
        p.drawLine(QPointF(box.x(), y), QPointF(box.right(), y))
