"""
Đồ nghề vẽ chân dung, dùng chung cho mọi file nhân vật.

Khung vẽ quy ước là 100 × 120 đơn vị (dọc, tỉ lệ 5:6). Cứ vẽ theo toạ độ đó,
`design()` lo phần co giãn và căn giữa vào khung thật:

    from .art import design, marks, misprint

    def draw_ai_do(p, rect):
        with design(p, rect):
            misprint(p, than_nguoi)      # bóng đen + hai lớp mực lệch trục
            ...
            marks(p)                     # dấu canh trục ở bốn góc
"""

import math
from contextlib import contextmanager

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainterPath, QPen, QRadialGradient

from theme import BLUE, INK, INK_SOFT, RED

W, H = 100.0, 120.0


class Rolls:
    """Chuỗi số giả ngẫu nhiên cố định theo hạt giống.

    Cùng một hạt giống và cùng thứ tự gọi thì luôn ra cùng dãy số, nên hình
    vẽ đứng yên qua từng khung hình thay vì rung lên như nhiễu.
    """

    def __init__(self, seed):
        self.state = (int(seed) & 0x7FFFFFFF) or 1

    def __call__(self, lo=0.0, hi=1.0):
        self.state = (self.state * 1103515245 + 12345) & 0x7FFFFFFF
        return lo + (hi - lo) * (self.state / 0x7FFFFFFF)

    def pick(self, items):
        return items[int(self(0, len(items) - 1e-9))]


@contextmanager
def design(p, rect, w=W, h=H):
    """Đưa khung vẽ 100×120 vào `rect`, giữ tỉ lệ và căn giữa."""
    p.save()
    scale = min(rect.width() / w, rect.height() / h)
    p.translate(rect.center())
    p.scale(scale, scale)
    p.translate(-w / 2, -h / 2)
    try:
        yield
    finally:
        p.restore()


def misprint(p, path, ink=INK):
    """Vẽ một mảng đen kèm hai bản in đỏ/xanh trượt lệch, như in sai chồng màu."""
    p.setPen(Qt.PenStyle.NoPen)
    for color, dx, dy, alpha in ((RED, 2.6, 2.0, 90), (BLUE, -2.2, -1.5, 78)):
        tint = QColor(color)
        tint.setAlpha(alpha)
        p.setBrush(tint)
        p.drawPath(path.translated(dx, dy))
    p.setBrush(ink)
    p.drawPath(path)


def marks(p, color=None):
    """Dấu canh trục của bản in ở bốn góc."""
    faint = QColor(color or INK_SOFT)
    faint.setAlpha(110)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(faint, 0.7))
    for cx, cy in ((9, 11), (91, 11), (9, 109), (91, 109)):
        p.drawLine(QPointF(cx - 3, cy), QPointF(cx + 3, cy))
        p.drawLine(QPointF(cx, cy - 3), QPointF(cx, cy + 3))
        p.drawEllipse(QPointF(cx, cy), 2.2, 2.2)


def feather(root, angle, length, half):
    """Một chiếc lông: gốc bè, thân phình, ngọn nhọn. Góc tính theo độ, 0 = phải."""
    a = math.radians(angle)
    dx, dy = math.cos(a), math.sin(a)
    px, py = -dy, dx                      # vector vuông góc với thân lông
    mid, bulge = length * 0.5, half * 1.45

    path = QPainterPath()
    path.moveTo(root.x() + px * half, root.y() + py * half)
    path.quadTo(root.x() + dx * mid + px * bulge,
                root.y() + dy * mid + py * bulge,
                root.x() + dx * length, root.y() + dy * length)
    path.quadTo(root.x() + dx * mid - px * bulge,
                root.y() + dy * mid - py * bulge,
                root.x() - px * half, root.y() - py * half)
    path.closeSubpath()
    return path


def curve_at(p0, p1, p2, t):
    """Điểm trên đường cong bậc hai tại tham số t."""
    u = 1.0 - t
    return QPointF(u * u * p0.x() + 2 * u * t * p1.x() + t * t * p2.x(),
                   u * u * p0.y() + 2 * u * t * p1.y() + t * t * p2.y())


def curve_normal(p0, p1, p2, t):
    """Vector pháp tuyến (đã chuẩn hoá) của đường cong tại t."""
    u = 1.0 - t
    dx = 2 * u * (p1.x() - p0.x()) + 2 * t * (p2.x() - p1.x())
    dy = 2 * u * (p1.y() - p0.y()) + 2 * t * (p2.y() - p1.y())
    length = math.hypot(dx, dy) or 1.0
    return -dy / length, dx / length


def ribbon(p0, p1, p2, w0, w1, steps=22):
    """Dải thuôn chạy dọc một đường cong: gốc dày w0, ngọn mảnh w1.

    Dùng cho những thứ vươn dài và nhỏ dần — càng máy, vòi, roi, tia điện.
    """
    left, right = [], []
    for i in range(steps + 1):
        t = i / steps
        c = curve_at(p0, p1, p2, t)
        nx, ny = curve_normal(p0, p1, p2, t)
        w = w0 + (w1 - w0) * t
        left.append(QPointF(c.x() + nx * w, c.y() + ny * w))
        right.append(QPointF(c.x() - nx * w, c.y() - ny * w))

    path = QPainterPath()
    path.moveTo(left[0])
    for q in left[1:]:
        path.lineTo(q)
    for q in reversed(right):
        path.lineTo(q)
    path.closeSubpath()
    return path


def fan(root, specs):
    """Xoè nhiều lông từ cùng một gốc: specs là ((góc, dài, nửa bề ngang), ...)."""
    out = QPainterPath()
    for angle, length, half in specs:
        out = out.united(feather(root, angle, length, half))
    return out


def mirrored(path, axis=W / 2):
    """Bản lật của một mảng vẽ qua trục dọc — dùng cho cánh, vai, tay."""
    from PySide6.QtGui import QTransform
    return QTransform(-1, 0, 0, 1, axis * 2, 0).map(path)


def glow(p, center, radius, color, core=0.0):
    """Quầng sáng toả tròn: đặc ở tâm, tắt dần ra rìa."""
    if radius <= 0:
        return
    g = QRadialGradient(center, radius)
    middle = QColor(color)
    middle.setAlpha(int(color.alpha() * 0.35))
    edge = QColor(color)
    edge.setAlpha(0)
    g.setColorAt(0.0, color)
    if core > 0:
        g.setColorAt(min(0.9, core), color)
    g.setColorAt(0.45, middle)
    g.setColorAt(1.0, edge)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(g)
    p.drawEllipse(center, radius, radius)


def scanlines(p, rect, step, color, offset=0.0):
    """Những vạch quét ngang chạy khắp khung — mặt kính CRT, không phải giấy."""
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(color, step * 0.34))
    y = rect.top() + (offset % step)
    while y < rect.bottom():
        p.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
        y += step


