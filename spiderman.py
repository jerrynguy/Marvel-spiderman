"""
Ác nhân của Spider-Man — dòng thời gian.
Bản Silver Age: giấy pulp ố vàng, lưới halftone, mực in lệch trục.

Chạy:  pip install PySide6
       python3 spiderman.py

Click vào một nhân vật đã có hồ sơ (chip có góc gấp) để mở tấm hồ sơ ngay
trong app; nhân vật chưa có hồ sơ thì vẫn mở trang web như trước.
Hồ sơ nằm trong thư mục characters/ — mỗi nhân vật một file.
Dữ liệu đã đối chiếu với Wikipedia và các nguồn Marvel (8/2026).
"""

import sys
import webbrowser
from urllib.parse import quote_plus

from PySide6.QtCore import (Property, QEasingCurve, QPoint, QPointF,
                            QParallelAnimationGroup, QPropertyAnimation, QRect,
                            QRectF, QSize, Qt, QTimer, Signal)
from PySide6.QtGui import (QColor, QFontMetrics, QPainter, QPainterPath, QPen)
from PySide6.QtWidgets import (QApplication, QComboBox, QGraphicsOpacityEffect,
                               QHBoxLayout, QLabel, QLayout, QLineEdit,
                               QScrollArea, QSizePolicy, QVBoxLayout, QWidget)

import characters
from theme import (ACCENT, BLUE, INK, INK_SOFT, PAPER_HI, RED, YELLOW, Paper,
                   Type)
from ui.character_modal import CharacterStage

# ═══════════════════════════════════════════════════════════════ dữ liệu
# (tên, năm, tháng — 0 nghĩa là không rõ, số báo, cờ: "" | "fix" | "new")
VILLAINS = [
    ("Chameleon", 1963, 3, "ASM #1", ""),
    ("Vulture", 1963, 5, "ASM #2", ""),
    ("Tinkerer", 1963, 5, "ASM #2", ""),
    ("Doctor Octopus", 1963, 7, "ASM #3", ""),
    ("Sandman", 1963, 9, "ASM #4", ""),
    ("Lizard", 1963, 11, "ASM #6", ""),
    ("Living Brain", 1964, 1, "ASM #8", ""),
    ("Electro", 1964, 2, "ASM #9", ""),
    ("Big Man", 1964, 3, "ASM #10", ""),
    ("Mysterio", 1964, 6, "ASM #13", ""),
    ("Green Goblin", 1964, 7, "ASM #14", ""),
    ("Kraven the Hunter", 1964, 8, "ASM #15", ""),
    ("Beetle", 1964, 8, "Strange Tales #123", ""),
    ("Scorpion", 1965, 1, "ASM #20", ""),
    ("Smythe / Spider-Slayers", 1965, 6, "ASM #25", ""),
    ("Crime Master", 1965, 7, "ASM #26", ""),
    ("Molten Man", 1965, 9, "ASM #28", ""),
    ("Looter", 1966, 5, "ASM #36", ""),
    ("Robot Master / Gaunt", 1966, 6, "ASM #37", ""),
    ("Boomerang", 1966, 7, "Tales to Astonish #81", ""),
    ("Rhino", 1966, 10, "ASM #41", ""),
    ("Shocker", 1967, 3, "ASM #46", ""),
    ("Kingpin", 1967, 7, "ASM #50", ""),
    ("Finisher", 1968, 11, "ASM Annual #5", ""),
    ("Mephisto", 1968, 12, "Silver Surfer #3", ""),
    ("Man Mountain Marko", 1969, 6, "ASM #73", ""),
    ("Silvermane", 1969, 6, "ASM #73", ""),
    ("Speed Demon", 1969, 10, "Avengers #69", "fix"),
    ("Prowler", 1969, 11, "ASM #78", ""),
    ("Kangaroo", 1970, 2, "ASM #81", ""),
    ("Schemer", 1970, 4, "ASM #83", ""),
    ("Morbius", 1971, 10, "ASM #101", ""),
    ("Gog", 1971, 12, "ASM #103", ""),
    ("Gibbon", 1972, 7, "ASM #110", ""),
    ("Hammerhead", 1972, 10, "ASM #113", ""),
    ("Man-Wolf", 1973, 9, "ASM #124", ""),
    ("Jackal", 1974, 2, "ASM #129", ""),
    ("Stegron", 1974, 3, "Marvel Team-Up #19", ""),
    ("Tarantula", 1974, 7, "ASM #134", ""),
    ("Mindworm", 1974, 11, "ASM #138", ""),
    ("Grizzly", 1974, 12, "ASM #139", ""),
    ("Witch-Slayer", 1976, 1, "Marvel Team-Up #41", ""),
    ("Human Fly", 1976, 0, "ASM Annual #10", ""),
    ("Lightmaster", 1977, 2, "PPSSM #3", ""),
    ("Will o' the Wisp", 1977, 4, "ASM #167", ""),
    ("Ringer", 1977, 6, "The Defenders #51", ""),
    ("Swarm", 1977, 7, "The Champions #14", ""),
    ("Big Wheel", 1978, 7, "ASM #182", ""),
    ("Carrion", 1978, 12, "PPSSM #25", ""),
    ("Black Cat", 1979, 7, "ASM #194", ""),
    ("Iguana", 1979, 7, "PPSSM #32", ""),
    ("Calypso", 1980, 10, "ASM #209", ""),
    ("Hydro-Man", 1981, 1, "ASM #212", ""),
    ("Jack O'Lantern", 1981, 2, "Machine Man #19", ""),
    ("Magma", 1981, 10, "Marvel Team-Up #110", ""),
    ("Vermin", 1982, 8, "Captain America #272", ""),
    ("Hobgoblin", 1983, 3, "ASM #238", ""),
    ("White Rabbit", 1983, 7, "Marvel Team-Up #131", ""),
    ("Rose", 1984, 6, "ASM #253", ""),
    ("Answer", 1984, 6, "PPSSM #91", ""),
    ("Puma", 1984, 9, "ASM #256", ""),
    ("Black Abbot", 1984, 11, "Marvel Team-Up #147", ""),
    ("Spot", 1985, 1, "PPSSM #98", ""),
    ("Incandescent Man", 1985, 1, "Marvel Team-Up #149", ""),
    ("Sin-Eater", 1985, 10, "PPSSM #107", "fix"),
    ("Slyde", 1986, 1, "ASM #272", ""),
    ("Foreigner", 1986, 6, "PPSSM #115", ""),
    ("Tombstone", 1988, 3, "Web of Spider-Man #36", ""),
    ("Venom", 1988, 5, "ASM #300", ""),
    ("Lobo Brothers", 1988, 10, "PPSSM #143", "fix"),
    ("Styx and Stone", 1988, 11, "ASM #309", ""),
    ("Carnage", 1992, 4, "ASM #361", ""),
    ("Doppelganger", 1992, 7, "The Infinity War #1", ""),
    ("Shriek", 1993, 5, "Spider-Man Unlimited #1", ""),
    ("Coldheart", 1994, 6, "Spider-Man #49", ""),
    ("Spidercide", 1995, 1, "Spectacular Spider-Man #222", ""),
    ("Delilah", 1996, 8, "ASM #414", "fix"),
    ("Black Tarantula", 1997, 1, "ASM #419", ""),
    ("Proto-Goblin", 1997, 7, "Spider-Man #-1", ""),
    ("Morlun", 2001, 6, "ASM vol. 2 #30", ""),
    ("Shathra", 2002, 11, "ASM vol. 2 #46", ""),
    ("Gray Goblin", 2004, 8, "ASM #509", ""),
    ("Overdrive", 2007, 5, "Swing Shift", ""),
    ("Mister Negative", 2008, 1, "ASM #546", ""),
    ("Freak", 2008, 1, "ASM #546", ""),
    ("Screwball", 2008, 5, "ASM #559", ""),
    ("Hippo", 2009, 8, "Sinister Spider-Man #1", ""),
    ("Massacre", 2011, 4, "ASM #655", ""),
    ("Panda-Mania", 2014, 6, "ASM vol. 3 #1", "new"),
    ("Regent", 2015, 12, "ASM vol. 4 #1", "new"),
    ("Kindred", 2018, 7, "ASM vol. 5 #1", "new"),
]

# Bài Wikipedia đã xác minh. Tên không có ở đây sẽ mở trang tìm kiếm.
WIKI = {
    "Chameleon": "Chameleon_(character)",
    "Vulture": "Vulture_(Marvel_Comics)",
    "Tinkerer": "Tinkerer_(Marvel_Comics)",
    "Doctor Octopus": "Doctor_Octopus",
    "Sandman": "Sandman_(Marvel_Comics)",
    "Lizard": "Lizard_(character)",
    "Electro": "Electro_(Marvel_Comics)",
    "Big Man": "Frederick_Foswell",
    "Mysterio": "Mysterio",
    "Green Goblin": "Green_Goblin",
    "Kraven the Hunter": "Kraven_the_Hunter",
    "Beetle": "Beetle_(comics)",
    "Scorpion": "Mac_Gargan",
    "Smythe / Spider-Slayers": "Spencer_Smythe",
    "Molten Man": "Molten_Man",
    "Rhino": "Rhino_(character)",
    "Shocker": "Shocker_(character)",
    "Kingpin": "Kingpin_(character)",
    "Mephisto": "Mephisto_(Marvel_Comics)",
    "Silvermane": "Silvermane",
    "Speed Demon": "Speed_Demon_(Marvel_Comics)",
    "Prowler": "Prowler_(Marvel_Comics)",
    "Kangaroo": "Kangaroo_(character)",
    "Morbius": "Morbius",
    "Hammerhead": "Hammerhead_(character)",
    "Jackal": "Jackal_(Marvel_Comics_character)",
    "Tarantula": "Tarantula_(Marvel_Comics)",
    "Carrion": "Carrion_(comics)",
    "Black Cat": "Black_Cat_(Marvel_Comics)",
    "Hydro-Man": "Hydro-Man",
    "Hobgoblin": "Hobgoblin_(Marvel_Comics)",
    "Puma": "Puma_(character)",
    "Venom": "Venom_(character)",
    "Carnage": "Carnage_(character)",
    "Morlun": "Morlun",
    "Mister Negative": "Mister_Negative",
    "Tombstone": "Tombstone_(character)",
    "Kindred": "Kindred_(Marvel_Comics)",
}

SOURCES = ("Wikipedia", "Marvel Fandom", "Marvel.com")
DECADES = (1960, 1970, 1980, 1990, 2000, 2010)
HINT = ("Click vào một nhân vật để xem hồ sơ. "
        "Chip có góc gấp là đã có hồ sơ trong app.")


def kind_of(name, flag):
    if name in (VILLAINS[0][0], VILLAINS[-1][0]):
        return "edge"
    return flag or "plain"


def note_of(name, flag):
    if name == VILLAINS[0][0]:
        return "ĐẦU TIÊN"
    if name == VILLAINS[-1][0]:
        return "MUỘN NHẤT"
    return {"new": "MỚI BỔ SUNG", "fix": "ĐÃ SỬA"}.get(flag, "")


def url_for(name, source):
    if source == "Wikipedia":
        slug = WIKI.get(name)
        if slug:
            return "https://en.wikipedia.org/wiki/" + slug
        return ("https://en.wikipedia.org/w/index.php?search="
                + quote_plus(name + " Spider-Man"))
    if source == "Marvel Fandom":
        return ("https://marvel.fandom.com/wiki/Special:Search?query="
                + quote_plus(name))
    return "https://www.marvel.com/search?limit=20&query=" + quote_plus(name)


# ═══════════════════════════════════════════════════════════ flow layout
class FlowLayout(QLayout):
    def __init__(self, parent=None, hgap=7, vgap=7):
        super().__init__(parent)
        self._items = []
        self._h, self._v = hgap, vgap
        self.setContentsMargins(0, 0, 0, 0)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, i):
        return self._items[i] if 0 <= i < len(self._items) else None

    def takeAt(self, i):
        return self._items.pop(i) if 0 <= i < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, w):
        return self._arrange(QRect(0, 0, w, 0), test=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._arrange(rect, test=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        s = QSize()
        for it in self._items:
            s = s.expandedTo(it.minimumSize())
        return s

    def _arrange(self, rect, test):
        x, y, line = rect.x(), rect.y(), 0
        for it in self._items:
            sz = it.sizeHint()
            if line and x + sz.width() > rect.right() + 1:
                x, y, line = rect.x(), y + line + self._v, 0
            if not test:
                it.setGeometry(QRect(QPoint(x, y), sz))
            x += sz.width() + self._h
            line = max(line, sz.height())
        return y + line - rect.y()


# ═══════════════════════════════════════════════════════════════ con chip
class Chip(QWidget):
    """Nhãn nhân vật. Rê chuột thì lớp mực đỏ và xanh tách khỏi lớp đen."""

    clicked = Signal(str)
    hovered = Signal(str, str)
    left = Signal()

    GHOST = 4.0  # chỗ chừa cho mực lệch
    FOLD = 13.0  # cạnh góc gấp báo hiệu nhân vật đã có hồ sơ

    def __init__(self, entry, parent=None):
        super().__init__(parent)
        self.name, self.year, self.month, self.issue, self.flag = entry
        self.kind = kind_of(self.name, self.flag)
        self.note = note_of(self.name, self.flag)
        self.has_profile = characters.has(self.name)
        self._reg = 0.0
        self._flash = 0.0
        self._pressed = False

        self.f_name = Type.text(11, bold=True)
        self.f_meta = Type.text(8, letter=0.8, caps=True)
        self.date = f"{self.month}/{self.year}" if self.month else str(self.year)
        self.meta = self.date + ("  ·  " + self.note if self.note else "")

        fm_n, fm_m = QFontMetrics(self.f_name), QFontMetrics(self.f_meta)
        w = 22 + fm_n.horizontalAdvance(self.name) + 12 + \
            fm_m.horizontalAdvance(self.meta)
        if self.has_profile:
            w += self.FOLD + 3      # chừa chỗ cho góc gấp, không đè lên chữ
        self._size = QSize(int(w + self.GHOST), 40)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        self._anim = QPropertyAnimation(self, b"reg", self)
        self._anim.setDuration(220)
        self._flash_anim = QPropertyAnimation(self, b"flash", self)
        self._flash_anim.setDuration(520)
        self._flash_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def sizeHint(self):
        return self._size

    # ---- thuộc tính động cho QPropertyAnimation
    def get_reg(self):
        return self._reg

    def set_reg(self, v):
        self._reg = v
        self.update()

    reg = Property(float, get_reg, set_reg)

    def get_flash(self):
        return self._flash

    def set_flash(self, v):
        self._flash = v
        self.update()

    flash = Property(float, get_flash, set_flash)

    def _drive(self, target, curve, ms):
        self._anim.stop()
        self._anim.setStartValue(self._reg)
        self._anim.setEndValue(target)
        self._anim.setEasingCurve(curve)
        self._anim.setDuration(ms)
        self._anim.start()

    def enterEvent(self, _):
        self._drive(1.0, QEasingCurve.Type.OutBack, 260)
        self.hovered.emit(self.name, self.issue)

    def leaveEvent(self, _):
        self._drive(0.0, QEasingCurve.Type.OutCubic, 200)
        self.left.emit()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self._drive(0.0, QEasingCurve.Type.OutCubic, 90)
            self.update()

    def mouseReleaseEvent(self, e):
        if not self._pressed:
            return
        self._pressed = False
        self.update()
        if self.rect().contains(e.position().toPoint()):
            self._flash_anim.stop()
            self._flash_anim.setStartValue(1.0)
            self._flash_anim.setEndValue(0.0)
            self._flash_anim.start()
            self._drive(1.0, QEasingCurve.Type.OutBack, 240)
            self.clicked.emit(self.name)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        g = self.GHOST
        box = QRectF(0, 0, self.width() - g, self.height() - g)
        if self._pressed:
            box.translate(1, 1)
        off = self._reg * 2.7

        # Hai lớp mực lệch trục — chỉ lộ ra ở viền, như bản in sai chồng màu.
        if off > 0.05:
            p.setPen(Qt.PenStyle.NoPen)
            for color, dx, dy, alpha in ((RED, off, off, 150),
                                         (BLUE, -off * 0.75, -off * 0.75, 130)):
                tint = QColor(color)
                tint.setAlpha(int(alpha * min(1.0, self._reg)))
                p.setBrush(tint)
                p.drawRect(box.translated(dx, dy))

        plain = self.kind == "plain"
        edge, fill = ACCENT.get(self.kind, (INK_SOFT, PAPER_HI))
        p.setBrush(fill)
        p.setPen(QPen(edge, 1.1 if plain else 1.5))
        p.drawRect(box)

        # Vệt bút dạ vàng khi vừa click.
        if self._flash > 0.01:
            sweep = QColor(YELLOW)
            sweep.setAlpha(int(120 * self._flash))
            p.fillRect(box.adjusted(1, 1, -1, -1), sweep)

        # Góc gấp ở mép trên phải: nhân vật này đã có hồ sơ để mở.
        if self.has_profile:
            fold = QPainterPath()
            fold.moveTo(box.right() - self.FOLD, box.y())
            fold.lineTo(box.right(), box.y())
            fold.lineTo(box.right(), box.y() + self.FOLD)
            fold.closeSubpath()
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(INK if plain else edge)
            p.drawPath(fold)
            p.setPen(QPen(PAPER_HI, 1.0))
            p.drawLine(QPointF(box.right() - self.FOLD, box.y()),
                       QPointF(box.right(), box.y() + self.FOLD))

        # Chấm đầu dòng: viên mực đặc, màu theo loại.
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(INK if plain else edge)
        p.drawEllipse(QPointF(box.x() + 11, box.center().y()), 3.1, 3.1)

        fm_n = QFontMetrics(self.f_name)
        tx = box.x() + 22
        p.setFont(self.f_name)
        name_box = QRectF(tx, box.y(), box.width(), box.height())
        flags = int(Qt.AlignmentFlag.AlignVCenter)
        if off > 0.05:
            for color, dx, dy in ((RED, off, off * 0.8),
                                  (BLUE, -off * 0.8, -off * 0.6)):
                c = QColor(color)
                c.setAlpha(int(165 * min(1.0, self._reg)))
                p.setPen(c)
                p.drawText(name_box.translated(dx, dy), flags, self.name)
        p.setPen(INK)
        p.drawText(name_box, flags, self.name)

        tx += fm_n.horizontalAdvance(self.name) + 12
        p.setFont(self.f_meta)
        p.setPen(edge if self.note else INK_SOFT)
        p.drawText(QRectF(tx, box.y(), box.width(), box.height()),
                   int(Qt.AlignmentFlag.AlignVCenter), self.meta)
        p.end()


# ═══════════════════════════════════════════════════════════ nút thập niên
class Tab(QWidget):
    picked = Signal(int)

    def __init__(self, label, value, parent=None):
        super().__init__(parent)
        self.label, self.value, self.on = label, value, False
        self.f = Type.text(9, bold=True, letter=1.2, caps=True)
        w = QFontMetrics(self.f).horizontalAdvance(label.upper()) + 26
        self._size = QSize(w, 30)
        self.setMinimumSize(self._size)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._lift = 0.0
        self._a = QPropertyAnimation(self, b"lift", self)
        self._a.setDuration(180)
        self._a.setEasingCurve(QEasingCurve.Type.OutCubic)

    def sizeHint(self):
        return self._size

    def get_lift(self):
        return self._lift

    def set_lift(self, v):
        self._lift = v
        self.update()

    lift = Property(float, get_lift, set_lift)

    def set_on(self, on):
        self.on = on
        self.update()

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
            self.picked.emit(self.value)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        box = QRectF(0, 2, self.width() - 2, self.height() - 4)
        if self.on:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(RED)
            p.drawRect(box.translated(2, 2))
            p.setBrush(INK)
            p.setPen(QPen(INK, 1.4))
            p.drawRect(box)
            p.setPen(PAPER_HI)
        else:
            p.setBrush(QColor(240, 232, 214, int(90 + 110 * self._lift)))
            p.setPen(QPen(INK_SOFT if self._lift < 0.5 else INK, 1.2))
            p.drawRect(box)
            p.setPen(INK if self._lift > 0.5 else INK_SOFT)
        p.setFont(self.f)
        p.drawText(box, int(Qt.AlignmentFlag.AlignCenter), self.label)
        p.end()


# ═══════════════════════════════════════════════════════════════ masthead
class Masthead(QWidget):
    """Logo bìa: lớp đen chồng lên lớp đỏ và xanh in lệch."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(96)
        self.title = "ÁC NHÂN CỦA SPIDER-MAN"
        first, last = VILLAINS[0], VILLAINS[-1]
        self.sub = (f"{len(VILLAINS)} nhân vật   ·   {first[0]} "
                    f"{first[2]}/{first[1]}   →   {last[0]} {last[2]}/{last[1]}")

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        size = 40
        while size > 20:
            f = Type.head(size, letter=1.5)
            if QFontMetrics(f).horizontalAdvance(self.title) <= self.width() - 8:
                break
            size -= 1
        p.setFont(f)
        base = QRectF(0, 4, self.width(), 54)
        for color, dx, dy in ((RED, 2.6, 2.2), (BLUE, -2.2, -1.6)):
            c = QColor(color)
            c.setAlpha(170)
            p.setPen(c)
            p.drawText(base.translated(dx, dy),
                       int(Qt.AlignmentFlag.AlignLeft
                           | Qt.AlignmentFlag.AlignVCenter), self.title)
        p.setPen(INK)
        p.drawText(base, int(Qt.AlignmentFlag.AlignLeft
                             | Qt.AlignmentFlag.AlignVCenter), self.title)

        f_sub = Type.text(9, letter=1.4, caps=True)
        sub = self.sub
        if QFontMetrics(f_sub).horizontalAdvance(sub) > self.width() - 4:
            sub = f"{len(VILLAINS)} nhân vật   ·   1963 → 2018"
        p.setFont(f_sub)
        p.setPen(INK_SOFT)
        p.drawText(QRectF(2, 60, self.width(), 20),
                   int(Qt.AlignmentFlag.AlignLeft
                       | Qt.AlignmentFlag.AlignVCenter), sub)

        p.setPen(QPen(INK, 2.4))
        p.drawLine(0, self.height() - 8, self.width(), self.height() - 8)
        p.setPen(QPen(RED, 1.0))
        p.drawLine(0, self.height() - 4, self.width(), self.height() - 4)
        p.end()


class YearMark(QWidget):
    """Số năm ở lề trái, in như số tập trên bìa."""

    def __init__(self, year, parent=None):
        super().__init__(parent)
        self.year = str(year)
        self.setFixedSize(96, 40)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setFont(Type.head(23, letter=0.5))
        box = QRectF(0, 0, self.width() - 16, 40)
        c = QColor(RED)
        c.setAlpha(150)
        p.setPen(c)
        p.drawText(box.translated(2, 1.6),
                   int(Qt.AlignmentFlag.AlignRight
                       | Qt.AlignmentFlag.AlignVCenter), self.year)
        p.setPen(INK)
        p.drawText(box, int(Qt.AlignmentFlag.AlignRight
                            | Qt.AlignmentFlag.AlignVCenter), self.year)
        p.end()


# ═══════════════════════════════════════════════════════════════ cửa sổ
class Window(Paper):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ác nhân của Spider-Man — dòng thời gian")
        self.resize(1060, 780)
        self.setMinimumSize(1000, 560)

        self.decade = 0
        self.query = ""
        self.chips = []
        self._anims = []
        self._fade = None
        self.stage = None

        root = QVBoxLayout(self)
        root.setContentsMargins(34, 24, 34, 18)
        root.setSpacing(0)
        root.addWidget(Masthead())
        root.addSpacing(14)
        root.addLayout(self._controls())
        root.addSpacing(10)
        root.addWidget(self._legend())
        root.addSpacing(10)
        root.addWidget(self._scroller(), 1)
        root.addWidget(self._status())

        self.set_decade(0)
        self.search.setFocus()

    # ------------------------------------------------------------ khung
    def _controls(self):
        row = QHBoxLayout()
        row.setSpacing(6)
        self.tabs = []
        for label, value in [("Tất cả", 0)] + [(f"{d}s", d) for d in DECADES]:
            t = Tab(label, value)
            t.picked.connect(self.set_decade)
            row.addWidget(t)
            self.tabs.append(t)
        row.addStretch(1)
        return row

    def _fields(self):
        css = f"""
            QLineEdit, QComboBox {{
                background: rgba(240,232,214,150);
                border: 1.2px solid {INK_SOFT.name()};
                padding: 5px 9px; color: {INK.name()};
                selection-background-color: {YELLOW.name()};
                selection-color: {INK.name()};
            }}
            QLineEdit:focus, QComboBox:focus {{ border-color: {RED.name()}; }}
            QComboBox::drop-down {{ border: none; width: 18px; }}
            QComboBox QAbstractItemView {{
                background: {PAPER_HI.name()}; color: {INK.name()};
                border: 1.2px solid {INK.name()}; outline: none;
                selection-background-color: {YELLOW.name()};
                selection-color: {INK.name()};
            }}
        """
        self.source = QComboBox()
        self.source.addItems(SOURCES)
        self.source.setFont(Type.text(9))
        self.source.setFixedWidth(132)
        self.source.setStyleSheet(css)
        self.source.setCursor(Qt.CursorShape.PointingHandCursor)

        self.search = QLineEdit()
        self.search.setPlaceholderText("tìm tên hoặc số báo")
        self.search.setFont(Type.text(9))
        self.search.setFixedWidth(172)
        self.search.setStyleSheet(css)
        self.search.textChanged.connect(self.set_query)
        return (("MỞ BẰNG", self.source), ("TÌM", self.search))

    def _legend(self):
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        for color, text in ((BLUE, "đầu tiên / muộn nhất"),
                            (RED, "mới bổ sung"),
                            (YELLOW, "đã sửa dữ liệu")):
            dot = QLabel()
            dot.setFixedSize(9, 9)
            dot.setStyleSheet(f"background:{color.name()};border-radius:4px")
            lab = QLabel(text)
            lab.setFont(Type.text(8, letter=0.8, caps=True))
            lab.setStyleSheet(f"color:{INK_SOFT.name()}")
            lab.setSizePolicy(QSizePolicy.Policy.Fixed,
                              QSizePolicy.Policy.Fixed)
            row.addWidget(dot)
            row.addSpacing(6)
            row.addWidget(lab)
            row.addSpacing(16)
        row.addStretch(1)

        for text, widget in self._fields():
            lab = QLabel(text)
            lab.setFont(Type.text(8, bold=True, letter=1.2))
            lab.setStyleSheet(f"color:{INK_SOFT.name()}")
            lab.setSizePolicy(QSizePolicy.Policy.Fixed,
                              QSizePolicy.Policy.Fixed)
            row.addWidget(lab)
            row.addSpacing(6)
            row.addWidget(widget)
            row.addSpacing(16)
        row.addSpacing(-16)
        return box

    def _scroller(self):
        self.body = QWidget()
        self.body.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.vbox = QVBoxLayout(self.body)
        self.vbox.setContentsMargins(0, 4, 8, 20)
        self.vbox.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setWidget(self.body)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.viewport().setAutoFillBackground(False)
        self.scroll.setStyleSheet(f"""
            QScrollArea, QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: transparent; width: 9px; margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {INK_SOFT.name()}; min-height: 40px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {RED.name()}; }}
            QScrollBar::add-line, QScrollBar::sub-line {{ height: 0 }}
            QScrollBar::add-page, QScrollBar::sub-page {{ background: none }}
        """)
        return self.scroll

    def _status(self):
        self.status = QLabel(HINT)
        self.status.setFont(Type.text(9))
        self.status.setStyleSheet(f"color:{INK_SOFT.name()};padding-top:8px")
        return self.status

    # ------------------------------------------------------------ hành vi
    def set_decade(self, value):
        self.decade = value
        for t in self.tabs:
            t.set_on(t.value == value)
        self.rebuild()

    def set_query(self, text):
        self.query = text.strip().lower()
        self.rebuild()

    def matches(self, v):
        name, year, _, issue, _ = v
        if self.decade and year // 10 * 10 != self.decade:
            return False
        if self.query and self.query not in name.lower() \
                and self.query not in issue.lower():
            return False
        return True

    def on_click(self, name):
        profile = characters.get(name)
        if profile is None:
            # Chưa có file hồ sơ cho nhân vật này — giữ nguyên nếp cũ.
            self.open_web(url_for(name, self.source.currentText()))
            return
        self.open_profile(profile, self.sender())

    def open_web(self, target):
        webbrowser.open_new_tab(target)
        self.status.setText("Đang mở  ·  " + target)

    def on_hover(self, name, issue):
        tail = "  ·  bấm để xem hồ sơ" if characters.has(name) else ""
        self.status.setText(f"{name}  ·  xuất hiện lần đầu: {issue}{tail}")

    def on_leave(self):
        self.status.setText(HINT)

    # ------------------------------------------------------------- hồ sơ
    def open_profile(self, profile, chip):
        """Mở tấm hồ sơ, phóng ra từ đúng con chip vừa bấm."""
        if self.stage is not None:
            return
        origin = QRect(0, 0, 180, 40)
        if isinstance(chip, Chip):
            origin = QRect(chip.mapTo(self, QPoint(0, 0)), chip.size())

        meta = {"stamp": "", "note": "", "kind": "plain"}
        for v in VILLAINS:
            if v[0] == profile.name:
                date = f"{v[2]}/{v[1]}" if v[2] else str(v[1])
                meta = {"stamp": f"{v[3]}  ·  {date}",
                        "note": note_of(v[0], v[4]),
                        "kind": kind_of(v[0], v[4])}
                break

        self.stage = CharacterStage(self, profile, meta, origin)
        self.stage.link_asked.connect(
            lambda url, name=profile.name: self.open_web(
                url or url_for(name, self.source.currentText())))
        self.stage.form_changed.connect(self.on_form_changed)
        self.stage.closed.connect(self.on_stage_closed)
        self.stage.open()
        self.status.setText(self.stage_hint(profile))

    @staticmethod
    def stage_hint(profile):
        tail = ("   —   bấm EVOLVE để mở dạng tiến hoá"
                if profile.evolution is not None
                else "   —   Esc hoặc bấm ra ngoài để đóng")
        return f"Hồ sơ  ·  {profile.name}{tail}"

    def on_form_changed(self, profile):
        self.status.setText(self.stage_hint(profile))

    def on_stage_closed(self):
        self.stage = None
        self.status.setText(HINT)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self.stage is not None:
            self.stage.relayout()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape and self.stage is not None:
            self.stage.dismiss()
        else:
            super().keyPressEvent(e)

    # --------------------------------------------------------- dựng lại
    def rebuild(self):
        for a in self._anims:
            a.stop()
        self._anims.clear()
        self.chips.clear()
        while self.vbox.count():
            item = self.vbox.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        shown = [v for v in VILLAINS if self.matches(v)]
        if not shown:
            empty = QLabel("Không có nhân vật nào khớp. Thử xoá bớt từ khoá.")
            empty.setFont(Type.text(11))
            empty.setStyleSheet(f"color:{INK_SOFT.name()};padding:26px 0")
            self.vbox.addWidget(empty)
            self.vbox.addStretch(1)
            return

        year = None
        row = None
        for v in shown:
            if v[1] != year:
                year = v[1]
                band = QWidget()
                band.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
                h = QHBoxLayout(band)
                h.setContentsMargins(0, 9, 0, 9)
                h.setSpacing(0)
                h.addWidget(YearMark(year), 0, Qt.AlignmentFlag.AlignTop)
                holder = QWidget()
                holder.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
                row = FlowLayout(holder)
                h.addWidget(holder, 1)
                self.vbox.addWidget(band)
            chip = Chip(v)
            chip.clicked.connect(self.on_click)
            chip.hovered.connect(self.on_hover)
            chip.left.connect(self.on_leave)
            row.addWidget(chip)
            self.chips.append(chip)
        self.vbox.addStretch(1)
        QTimer.singleShot(0, self.play_entrance)

    def play_entrance(self):
        """Mực thấm dần vào giấy: từng chip hiện lên lệch nhau vài phần trăm giây."""
        for i, chip in enumerate(self.chips):
            fx = QGraphicsOpacityEffect(chip)
            fx.setOpacity(0.0)
            chip.setGraphicsEffect(fx)

            fade = QPropertyAnimation(fx, b"opacity", chip)
            fade.setDuration(300)
            fade.setStartValue(0.0)
            fade.setEndValue(1.0)
            fade.setEasingCurve(QEasingCurve.Type.OutCubic)

            ink = QPropertyAnimation(chip, b"reg", chip)
            ink.setDuration(340)
            ink.setStartValue(0.85)
            ink.setEndValue(0.0)
            ink.setEasingCurve(QEasingCurve.Type.OutCubic)

            group = QParallelAnimationGroup(chip)
            group.addAnimation(fade)
            group.addAnimation(ink)
            group.finished.connect(
                lambda c=chip: c.setGraphicsEffect(None))
            QTimer.singleShot(min(i * 7, 900), group.start)
            self._anims.append(group)


def main():
    app = QApplication(sys.argv)
    Type.load()
    app.setFont(Type.text(10))
    win = Window()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()