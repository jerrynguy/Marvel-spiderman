"""
Scorpion — Mac Gargan.

Mười ba chân dung trước đều vẽ một khoảnh khắc đứng yên: nhân vật ở đó,
người xem nhìn vào, hết chuyện. Cái này vẽ thời gian — cùng một cái đuôi in
bốn lần trên cùng tờ giấy, ba lần mờ ở phía sau và một lần đặc ở cuối, như
một tấm ảnh phơi sáng quá lâu bắt trọn cả cú quật thay vì một tư thế của nó.

Vì thứ đáng sợ ở Mac Gargan không phải hình dáng mà là tốc độ: trong mấy số
báo đầu, hắn là kẻ duy nhất vừa nhanh hơn vừa khoẻ hơn Spider-Man. Vẽ hắn
đứng yên là vẽ mất phần ấy.

Chuỗi phơi sáng ấy khép thành một vòng cung vắt qua đỉnh khung, và mũi kim ở
cuối cung chúc xuống — nhắm đúng vào cái đầu của chính hắn. Đó không phải bố
cục cho đẹp. Jameson mua cái đuôi này về để giết một người khác, còn thứ nó
giết trước tiên là Mac Gargan: đột biến không đảo ngược được, và hắn mất dần
trí óc kể từ hôm nhận tiền. Kẻ ngồi trong vòng cung là kẻ bị nó nhắm.

Chi tiết cuối cùng là cái ổ bắt vít ở vai. Stillwell hàn cái đuôi ấy từ đồ
phụ tùng trong phòng thí nghiệm rồi lắp lên người Gargan — nó không mọc ra
từ hắn, nó được bắt vào hắn. Bốn con vít quanh cổ vai là chỗ nói ra điều đó.
"""

import math
from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QPainter, QPainterPath, QPen,
                           QTransform)

from theme import INK, INK_SOFT, PAPER_HI

from .art import curve_normal, design, marks, misprint, ribbon
from .profile import Profile

ROOT = QPointF(80, 108)          # chỗ đuôi bắt vào vai — trục của cả cú quật
BEND = QPointF(108, 50)          # điểm điều khiển của vòng cung đuôi
TIP = QPointF(46, 32)            # mũi đuôi ở vị trí cuối
LENS = QColor("#F2EBDA")         # kính mắt, chỗ sáng nhất trên người
GHOSTS = ((20.0, 16, 68), (13.0, 23, 92), (6.0, 31, 118))    # độ lệch, ruột, viền


# ═══════════════════════════════════════════════════ cái đuôi
@lru_cache(maxsize=8)
def _tail(angle=0.0):
    """Đuôi ở một thời điểm của cú quật: gốc bè, thân thuôn, vắt qua đỉnh khung.

    `angle` là số độ quay quanh gốc đuôi — 0 là vị trí cuối, số dương là các
    vị trí trước đó, còn chếch về bên phải.
    """
    path = ribbon(ROOT, BEND, TIP, 8.0, 2.6, steps=28)
    bulb = QPainterPath()                 # đốt cuối phình ra, chỗ chứa nọc
    bulb.addEllipse(QPointF(49.5, 33.5), 5.6, 4.8)
    path = path.united(bulb)

    sting = QPainterPath()                # kim: móc cong chúc thẳng xuống đầu hắn
    sting.moveTo(47.0, 29.0)
    sting.cubicTo(41.5, 32.5, 37.6, 38.5, 36.4, 47.5)
    sting.cubicTo(40.5, 39.5, 43.8, 34.5, 49.0, 32.8)
    sting.closeSubpath()
    path = path.united(sting)

    if not angle:
        return path
    t = QTransform()
    t.translate(ROOT.x(), ROOT.y())
    t.rotate(angle)
    t.translate(-ROOT.x(), -ROOT.y())
    return t.map(path)


def _segments(p):
    """Vạch đốt trên đuôi: mấy nét sáng cắt ngang, thưa dần về phía ngọn."""
    seam = QColor(PAPER_HI)
    seam.setAlpha(140)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(seam, 1.2))
    for t in (0.13, 0.27, 0.4, 0.52, 0.63, 0.73, 0.82):
        u = 1.0 - t
        x = u * u * ROOT.x() + 2 * u * t * BEND.x() + t * t * TIP.x()
        y = u * u * ROOT.y() + 2 * u * t * BEND.y() + t * t * TIP.y()
        nx, ny = curve_normal(ROOT, BEND, TIP, t)
        w = 8.6 - 5.6 * t
        p.drawLine(QPointF(x - nx * w, y - ny * w),
                   QPointF(x + nx * w, y + ny * w))


# ═══════════════════════════════════════════════════ người ngồi trong vòng cung
def _head():
    """Mũ trùm kín, quay hẳn sang trái: trán vát ngược, mõm cụt, gáy dày.

    Bản trước vẽ cả người đang lao tới. Ở khung 100×120 thì thân, hai chân và
    cái đuôi tranh nhau chỗ, và cả ba cùng thua: người thành một khối tròn
    không đọc ra tay chân. Cắt sát lấy đầu và vai thì cái mũ đủ to để có nét
    mặt, còn vòng cung đuôi đủ chỗ để khép hẳn lại trên đỉnh đầu.
    """
    head = QPainterPath()
    head.moveTo(16, 84)                   # đầu mõm, chỗ nhô ra xa nhất
    head.quadTo(17, 74, 23, 67)           # mặt trước mũ, dốc ngược ra sau
    head.lineTo(34, 60)                   # trán phẳng
    head.quadTo(46, 56, 55, 61)           # đỉnh mũ
    head.lineTo(64, 65)                   # gờ mũ vuốt ngược ra sau, thấp và ngắn
    head.quadTo(61, 70, 59, 75)
    head.quadTo(58, 86, 50, 93)           # gáy đổ xuống
    head.lineTo(37, 98)
    head.quadTo(26, 98, 21, 91)           # góc hàm khép về mõm
    head.closeSubpath()
    return head


def _shoulders():
    """Hai vai và ngực trên, cắt ngang bởi mép dưới khung — vai phải nhô cao
    hơn vì cái đuôi bắt vào đúng chỗ đó và dồn cả sức nặng lên nó."""
    body = QPainterPath()
    body.moveTo(2, 120)
    body.cubicTo(4, 112, 10, 106, 20, 104)   # ngực trước, dưới cằm
    body.cubicTo(30, 101, 38, 97, 47, 96)    # cổ nối lên hàm
    body.cubicTo(60, 95, 70, 100, 78, 107)   # vai phải, chỗ bắt đuôi
    body.cubicTo(88, 113, 92, 116, 94, 120)
    body.lineTo(2, 120)
    body.closeSubpath()
    return body


@lru_cache(maxsize=1)
def _figure():
    return _shoulders().united(_head())


def _lens(cx, cy, half, rise, angle):
    """Kính mắt hình hạnh nhân, nhọn hai đầu và xếch theo `angle` độ.

    Bản trước dùng hình bầu dục: hai vòng trắng tròn vành vạnh trên nền đen
    đọc ra mặt cười chứ không ra mặt nạ. Nhọn hai đầu thì mới ra cái nhìn.
    """
    a = math.radians(angle)
    dx, dy = math.cos(a), math.sin(a)
    px, py = -dy, dx
    lens = QPainterPath()
    lens.moveTo(cx - dx * half, cy - dy * half)
    lens.quadTo(cx + px * rise * 1.7, cy + py * rise * 1.7,
                cx + dx * half, cy + dy * half)
    lens.quadTo(cx - px * rise * 1.3, cy - py * rise * 1.3,
                cx - dx * half, cy - dy * half)
    lens.closeSubpath()
    return lens


def _face(p):
    """Hai kính mắt và một tấm khe thở — cả cái mặt nạ chỉ có ba mảng sáng.

    Bản trước rắc lên mũ đủ thứ nét mảnh: gờ trán, sống mũi, gò má, mép
    mõm. Ở cỡ thật thì sáu nét xám ấy không đọc ra chi tiết nào, chỉ ra một
    mảng lấm tấm. Ít mảng mà đặc thì mới thành mặt nạ.
    """
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(LENS)
    p.drawPath(_lens(28.0, 76.0, 6.4, 2.6, -36))
    p.drawPath(_lens(42.0, 70.5, 4.4, 1.9, -28))

    grille = QPainterPath()               # tấm thở trên mõm, mảng sáng thứ ba
    grille.moveTo(17.5, 83.5)
    grille.lineTo(27.5, 88.5)
    grille.lineTo(26.5, 93.5)
    grille.lineTo(17.0, 88.0)
    grille.closeSubpath()
    p.setBrush(LENS)
    p.drawPath(grille)

    p.setBrush(Qt.BrushStyle.NoBrush)     # hai khe chạy dọc tấm thở
    p.setPen(QPen(INK, 1.0))              # cắt ngang thì ra hàm răng, không ra khe
    for dy in (1.7, 3.4):
        p.drawLine(QPointF(17.3 + dy * 0.1, 85.0 + dy),
                   QPointF(27.1 - dy * 0.1, 90.0 + dy))


def _edges(p, figure):
    """Nét chia mảng.

    Hợp mọi mảng vào một bóng thì chỗ gáy giáp vai không còn nét nào — đầu
    chìm luôn vào ngực. Mấy đường này vẽ đè lên để trả lại đường nối, cắt
    theo bóng người nên không bao giờ tràn ra ngoài.
    """
    p.save()
    p.setClipPath(figure, Qt.ClipOperation.IntersectClip)
    seam = QColor(PAPER_HI)
    seam.setAlpha(100)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(seam, 1.3))

    nape = QPainterPath()                 # gáy đổ xuống vai
    nape.moveTo(56, 84)
    nape.cubicTo(58, 91, 61, 96, 66, 100)
    p.drawPath(nape)

    collar = QPainterPath()               # tấm giáp cổ, vắt ngang hai vai
    collar.moveTo(6, 116)
    collar.cubicTo(22, 108, 42, 105, 60, 109)
    p.drawPath(collar)

    # ổ bắt đuôi: cái đuôi này không mọc ra, nó được bắt vít vào vai
    p.setPen(QPen(seam, 1.4))
    p.save()
    p.translate(ROOT.x() - 2, ROOT.y() - 2)
    p.rotate(-34)
    p.drawEllipse(QPointF(0, 0), 10.5, 7.0)
    p.setBrush(seam)
    for i in range(4):
        a = math.radians(38 + i * 76)
        p.drawEllipse(QPointF(math.cos(a) * 10.5, math.sin(a) * 7.0), 1.0, 1.0)
    p.restore()
    p.restore()


# ═══════════════════════════════════════════════════ dựng cả bức
def _sweep(p):
    """Ba lần in trước của cùng cái đuôi, mờ dần — cú quật chứ không phải tư thế.

    Mỗi bản có cả ruột lẫn viền. Chỉ tô ruột nhạt thì ba bản chồng nhau ra
    một vệt khói; có viền thì đọc ra ba lần bấm máy rời nhau.
    """
    for angle, fill, edge in GHOSTS:
        body = QColor(INK)
        body.setAlpha(fill)
        line = QColor(INK)
        line.setAlpha(edge)
        p.setBrush(body)
        p.setPen(QPen(line, 0.7))
        p.drawPath(_tail(angle))


def _streak(p):
    """Vệt mũi kim vạch qua đỉnh khung, nối các lần in lại thành một đường đi."""
    trail = QColor(INK_SOFT)
    trail.setAlpha(130)
    p.setBrush(Qt.BrushStyle.NoBrush)
    pen = QPen(trail, 0.9)
    pen.setStyle(Qt.PenStyle.DashLine)
    pen.setDashPattern([3.0, 3.0])
    p.setPen(pen)
    arc = QPainterPath()
    arc.moveTo(75, 22)
    arc.cubicTo(64, 16, 53, 19, 45, 28)
    p.drawPath(arc)


def _paint(p, rect):
    """Xếp lớp cả bức: các lần in cũ trước, cái đuôi thật sau, mặt nạ trên cùng."""
    with design(p, rect):
        _sweep(p)
        _streak(p)

        figure = _figure()
        tail = _tail()
        misprint(p, figure.united(tail))

        p.save()
        p.setClipPath(tail, Qt.ClipOperation.IntersectClip)
        _segments(p)
        p.restore()

        _edges(p, figure)
        _face(p)
        marks(p)


_STILL = {}


def draw_scorpion(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước.

    Tấm này tĩnh nhưng nặng: bốn cái đuôi đều phải hợp path, cộng ba mảng
    mực nửa trong suốt phủ chồng nhau. Khung hồ sơ vẽ lại nó hơn hai chục
    lần lúc mở, nên dựng sẵn một lần rồi dán — 8,0 ms xuống còn 0,2 ms. Ảnh
    dựng đúng bằng số điểm ảnh thật nên dán vào không nhoè trên màn HiDPI.
    """
    scale = p.transform().m11() or 1.0
    key = (round(rect.width(), 1), round(rect.height(), 1), round(scale, 2))
    ready = _STILL.get(key)
    if ready is None:
        if len(_STILL) > 6:           # đổi cỡ cửa sổ liên tục thì đừng giữ hết
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
    name="Scorpion",
    vi_name="Bọ Cạp",
    real_name="MacDonald 'Mac' Gargan",
    keys=("Mac Gargan",),

    tagline="Mười ba kẻ trước tự chọn con đường của mình. Người này thì được "
            "đặt hàng làm ra, và hoá đơn ghi rõ hai lần mười nghìn đô: một "
            "cho người chế, một cho người chịu làm vật thí nghiệm.",

    summary=(
        "Mac Gargan là thám tử tư hạng xoàng, được J. Jonah Jameson thuê để "
        "tìm cho ra vì sao một thằng nhóc tên Peter Parker chụp được những "
        "tấm ảnh Spider-Man mà không ai chụp nổi. Gargan theo dõi mãi không "
        "ra gì. Jameson bèn đổi cách: thay vì thuê người đi tìm câu trả lời, "
        "ông ta bỏ tiền ra chế tạo một câu trả lời.",

        "Ý tưởng đến từ một bài báo Jameson đọc được, viết về Farley "
        "Stillwell — nhà sinh học gây đột biến nhân tạo, ghép đặc tính của "
        "loài vật này sang loài vật khác. Jameson trả mười nghìn đô cho ông "
        "ta và mười nghìn nữa cho Gargan, rồi đặt hàng bằng đúng một câu: "
        "cho người này sức mạnh lớn hơn Spider-Man. Con vật được chọn không "
        "phải chọn bừa — bọ cạp là thiên địch của nhện — còn quy trình thì "
        "chẳng có gì hào nhoáng: cạo đầu Gargan, cho uống huyết thanh, rồi "
        "hàn lấy cái đuôi từ đồ phụ tùng có sẵn trong phòng.",

        "The Amazing Spider-Man #20 (01/1965) của Stan Lee và Steve Ditko cho "
        "thấy đơn hàng ấy được giao đúng hẹn. Gargan khoẻ hơn Peter, nhanh "
        "hơn Peter, chịu đòn tốt hơn Peter, cộng thêm cái đuôi quật vỡ tường. "
        "Hai lần chạm trán đầu, Spider-Man thua cả hai. Nhưng Stillwell nhận "
        "ra một thứ nữa trong đám thú thí nghiệm của mình: cùng với sức "
        "mạnh, con vật nào cũng hoá hung dữ rồi mất trí. Ông ta pha thuốc "
        "giải, đuổi theo Gargan lên mái nhà, và rơi xuống chết trước khi kịp "
        "tiêm.",

        "Không có thuốc giải thì không có đường về. Gargan quay lại tìm chính "
        "người đã trả tiền cho hắn — Jameson, kẻ duy nhất biết mặt thật bên "
        "dưới bộ giáp — và ở lại trong bộ giáp ấy suốt bốn mươi năm sau đó. "
        "Năm 2005 hắn bỏ cái tên Scorpion để nhận ký sinh trùng Venom, rồi "
        "làm Spider-Man giả trong đội Dark Avengers của Norman Osborn, rồi "
        "lại về với bộ giáp cũ. Không mốc nào trong số đó là do hắn tự nghĩ "
        "ra: từ đầu tới cuối, Mac Gargan luôn là thứ người khác dựng nên để "
        "dùng.",
    ),

    powers=(
        "Sức mạnh và tốc độ vượt Spider-Man — nâng được cỡ mười lăm tấn",
        "Đuôi máy dài, quật vỡ bê tông; cuộn lại lấy đà thì bật xa cả chục mét",
        "Bản sau của đuôi biết cầm nắm, gắn kim tiêm độc, axit và tia nhiệt",
        "Bộ giáp chịu đạn, bám tường và trèo được như con vật đã tạo ra hắn",
        "Đột biến không đảo ngược: đổi lấy sức mạnh là mất dần trí óc",
    ),

    facts=(
        ("Tên thật", "MacDonald Gargan"),
        ("Xuất hiện đầu", "ASM #20  ·  01/1965"),
        ("Tác giả", "Stan Lee & Steve Ditko"),
        ("Nghề cũ", "Thám tử tư"),
        ("Người trả tiền", "J. Jonah Jameson, 2 × 10.000 đô"),
        ("Người gây đột biến", "TS. Farley Stillwell"),
    ),

    blurb="Jameson bỏ tiền ra chế một con vật chuyên ăn nhện, rồi suốt phần "
          "đời còn lại phải trốn chính nó. Đây là hồ sơ duy nhất trong danh "
          "sách mà phần khó chịu nhất không nằm ở ác nhân, mà ở người đã ký "
          "tấm séc.",

    art=draw_scorpion,
    caption="Cú quật, in chồng bốn lần  ·  dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Mac_Gargan"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/MacDonald_Gargan_(Earth-616)"),
    ),
)
