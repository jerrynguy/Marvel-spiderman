"""
Shocker — Herman Schultz.

Mười bảy chân dung trước đều là hình vẽ sạch: mực đặt đúng chỗ, nét nào ra
nét ấy. Cái này thì **không in nổi**. Cả bức được vẽ tử tế trước, rồi mới bị
xẻ thành mấy chục dải ngang và mỗi dải trượt đi một quãng — mạnh nhất ở hai
cái găng, tắt dần về phía chân. Mấy dải bị xô nhiều nhất còn kéo theo một
vệt đỏ và một vệt lam lệch trục, đúng kiểu giấy rung trong lúc máy đang chạy.

Đó là cách duy nhất vẽ đúng thứ hắn làm. Herman Schultz không bắn ra lửa,
không bắn ra tia; hắn phát ra **rung**. Vẽ hắn bằng một hình đứng yên là vẽ
mất toàn bộ nhân vật, mà vẽ mấy vòng tròn bay ra khỏi tay thì chỉ là vẽ tiếng
động. Rung thì phải làm hỏng cái ảnh mới đúng.

Chi tiết thứ hai nằm ở bộ đồ. Cái áo chần bông trông buồn cười ấy không phải
gu thẩm mỹ mà là **thiết bị an toàn**: sóng rung dội ngược từ chính đôi găng
sẽ nghiền nát người mặc, nên hắn tự may một lớp đệm để hứng. Trong cả danh
sách chín mươi mốt cái tên, đây là kẻ hiếm hoi thiết kế trang phục quanh câu
hỏi "thứ này sẽ giết mình kiểu gì" thay vì "trông có ngầu không".
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QImage, QPainter, QPainterPath, QPen,
                           QTransform)

from theme import BLUE, INK, PAPER_HI, RED

from .art import H, W, design, marks, ribbon
from .profile import Profile

CUFF = QPointF(16, 67)           # găng đang bắn — tâm của cơn rung
GRIP = QPointF(78, 88)           # găng chĩa xuống, tay kia
BAND = 2.4                       # bề dày một dải, tính theo khung 100×120


# ═══════════════════════════════════════════════════ người mặc đệm
def _hood():
    """Mũ trùm kín, chần bông như phần còn lại của bộ đồ."""
    hood = QPainterPath()
    hood.moveTo(40, 30)
    hood.cubicTo(40, 16, 60, 16, 60, 30)
    hood.cubicTo(60, 38, 57, 44, 53, 46)
    hood.lineTo(47, 46)
    hood.cubicTo(43, 44, 40, 38, 40, 30)
    hood.closeSubpath()
    return hood


def _torso():
    """Thân dày cộp vì lớp đệm: vai vuông, sườn gần như thẳng đứng."""
    torso = QPainterPath()
    torso.moveTo(46, 44)
    torso.cubicTo(38, 46, 30, 50, 28, 58)     # vai trái
    torso.cubicTo(26, 70, 28, 84, 30, 96)
    torso.cubicTo(31, 108, 32, 116, 32, 120)
    torso.lineTo(69, 120)
    torso.cubicTo(69, 112, 70, 102, 71, 92)
    torso.cubicTo(73, 80, 75, 66, 73, 58)     # sườn phải lên vai
    torso.cubicTo(71, 50, 63, 46, 55, 44)
    torso.closeSubpath()
    return torso


def _arm_up():
    """Tay trái chĩa ngang sang trái, đưa cái găng ra xa đầu — nguồn của cơn rung."""
    return ribbon(QPointF(31, 56), QPointF(22, 60), QPointF(17, 65), 6.4, 5.2)


def _arm_down():
    """Tay phải chĩa xuống, găng thứ hai nhắm vào chỗ khác."""
    return ribbon(QPointF(72, 60), QPointF(79, 74), QPointF(78, 86), 6.0, 5.0)


def _gauntlet(center, angle):
    """Găng rung: một ống dày, hai vành gờ, chụp trọn cả bàn tay."""
    body = QPainterPath()
    body.addRoundedRect(QRectF(-6.5, -7.5, 13, 15), 3.2, 3.2)
    rim = QPainterPath()
    rim.addRoundedRect(QRectF(-7.6, -8.6, 15.2, 4.4), 2.0, 2.0)
    body = body.united(rim)

    t = QTransform()
    t.translate(center.x(), center.y())
    t.rotate(angle)
    return t.map(body)


def _figure():
    return (_torso().united(_hood()).united(_arm_up()).united(_arm_down())
            .united(_gauntlet(CUFF, -72)).united(_gauntlet(GRIP, 8)))


def _quilt(p, figure):
    """Ô chần bông: lưới nét sáng phủ kín người, ô hơi phồng ở giữa.

    Bộ đồ này là lớp đệm chống dội, nên nó phải đọc ra *đệm* chứ không ra
    áo liền. Ô vuông đều thì thành bàn cờ; cho mỗi đường ngang võng nhẹ
    xuống thì từng ô mới phồng lên như một tấm chăn bông thật.
    """
    p.save()
    p.setClipPath(figure, Qt.ClipOperation.IntersectClip)
    p.setBrush(Qt.BrushStyle.NoBrush)
    seam = QColor(PAPER_HI)
    seam.setAlpha(104)
    p.setPen(QPen(seam, 1.1))
    for i in range(3, 17):                    # đường ngang, mỗi đường võng nhẹ
        y = i * 8.0
        row = QPainterPath()
        row.moveTo(20, y)
        row.cubicTo(38, y + 2.4, 62, y + 2.4, 84, y)
        p.drawPath(row)
    for i in range(2, 10):                    # đường dọc, hơi cong theo khối
        x = i * 10.0
        col = QPainterPath()
        col.moveTo(x, 12)
        col.cubicTo(x - 2.2, 50, x - 2.2, 86, x, 122)
        p.drawPath(col)
    p.restore()


def _rings(p):
    """Sóng rung bật ra khỏi găng: mấy cung tròn đồng tâm, thưa dần ra ngoài."""
    for i, r in enumerate((12.5, 17.5, 22.5)):
        tone = QColor(INK)
        tone.setAlpha(int(170 - i * 40))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(tone, 2.2 - i * 0.5))
        box = QRectF(CUFF.x() - r, CUFF.y() - r, r * 2, r * 2)
        p.drawArc(box, int(120 * 16), int(120 * 16))


def _face(p):
    """Hai khe mắt trên mũ — chỗ duy nhất bộ đồ hở ra."""
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(PAPER_HI))
    for cx, ang in ((45.5, -14), (55.5, 12)):
        p.save()
        p.translate(cx, 28.5)
        p.rotate(ang)
        p.drawEllipse(QPointF(0, 0), 3.6, 1.5)
        p.restore()


def _sharp(p):
    """Bức vẽ lúc chưa rung — vẽ tử tế, rồi mới đem đi xô lệch."""
    _rings(p)
    figure = _figure()
    p.setPen(QPen(INK, 1.6))
    p.setBrush(INK)
    p.drawPath(figure)
    _quilt(p, figure)

    p.setBrush(Qt.BrushStyle.NoBrush)         # vành gờ trên hai cái găng
    p.setPen(QPen(PAPER_HI, 1.4))
    for center, angle in ((CUFF, -72), (GRIP, 8)):
        p.save()
        p.translate(center.x(), center.y())
        p.rotate(angle)
        p.drawLine(QPointF(-6.6, -3.6), QPointF(6.6, -3.6))
        p.drawLine(QPointF(-5.6, 1.2), QPointF(5.6, 1.2))
        p.restore()

    _face(p)
    marks(p)


# ═══════════════════════════════════════════════════ cơn rung
def _shift(y):
    """Độ trượt ngang của dải nằm ở độ cao y, tính theo khung 100×120.

    Sóng hình sin để các dải xô theo nhịp chứ không nhảy loạn, nhân với một
    bao hình tắt dần từ cái găng xuống chân: chỗ phát rung thì lệch nhiều,
    càng xa càng đứng yên.
    """
    near = math.exp(-((y - 74.0) / 32.0) ** 2)
    return math.sin(y * 0.78) * 2.9 * (0.20 + near)


def _tinted(source, color):
    """Bản sao của ảnh, nhuộm nguyên một màu, giữ nguyên vùng trong suốt."""
    out = QImage(source)
    q = QPainter(out)
    q.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    q.fillRect(out.rect(), color)
    q.end()
    return out


def _shake(sharp, scale):
    """Xẻ bức vẽ thành dải ngang rồi đặt lại, mỗi dải lệch đi một quãng.

    Hai bản nhuộm đỏ và lam đặt lệch thêm về hai phía trước khi dán bản mực
    đen lên trên: dải nào xô mạnh thì tự nhiên hiện ra viền màu, đúng kiểu
    tờ giấy rung trong lúc máy in đang chạy. Dải nào gần như đứng yên thì
    ba bản chồng khít, không thấy màu.
    """
    out = QImage(sharp.size(), QImage.Format.Format_ARGB32_Premultiplied)
    out.fill(Qt.GlobalColor.transparent)
    red = _tinted(sharp, QColor(RED.red(), RED.green(), RED.blue(), 150))
    blue = _tinted(sharp, QColor(BLUE.red(), BLUE.green(), BLUE.blue(), 130))

    q = QPainter(out)
    step = max(1.0, BAND * scale)
    y = 0.0
    while y < sharp.height():
        h = min(step, sharp.height() - y)
        band = QRectF(0, y, sharp.width(), h)
        dx = _shift(y / scale) * scale
        for layer, extra in ((red, dx * 0.4 + 1.1), (blue, -dx * 0.4 - 1.0)):
            q.drawImage(QPointF(dx + extra, y), layer, band)
        q.drawImage(QPointF(dx, y), sharp, band)
        y += step
    q.end()
    return out


_STILL = {}


def draw_shocker(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước.

    Bức này phải qua hai lượt ảnh: một lượt vẽ sạch, một lượt xô dải. Cả hai
    đều đắt nên dựng sẵn đúng cỡ điểm ảnh thật rồi dán, như `electro.py`.
    """
    scale = p.transform().m11() or 1.0
    key = (round(rect.width(), 1), round(rect.height(), 1), round(scale, 2))
    ready = _STILL.get(key)
    if ready is None:
        if len(_STILL) > 6:
            _STILL.clear()
        w = max(1, math.ceil(rect.width() * scale))
        h = max(1, math.ceil(rect.height() * scale))
        sharp = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
        sharp.fill(Qt.GlobalColor.transparent)
        q = QPainter(sharp)
        q.setRenderHint(QPainter.RenderHint.Antialiasing)
        q.scale(scale, scale)
        with design(q, QRectF(0, 0, rect.width(), rect.height())):
            _sharp(q)
        q.end()

        # một đơn vị khung 100×120 dài bao nhiêu điểm ảnh, để xẻ dải cho đúng
        unit = min(rect.width() / W, rect.height() / H) * scale
        ready = _shake(sharp, unit)
        _STILL[key] = ready
    p.drawImage(rect, ready)


# ═══════════════════════════════════════════════════════════════ hồ sơ
PROFILE = Profile(
    name="Shocker",
    vi_name="Kẻ Gây Chấn Động",
    real_name="Herman Schultz",

    tagline="Bỏ học sớm, tự học kỹ thuật, và dùng cái đầu ấy vào đúng một "
            "việc: mở két người khác. Hắn không muốn nổi tiếng, hắn muốn "
            "được trả tiền.",

    summary=(
        "Herman Schultz bỏ ngang trung học nhưng có đầu óc của một kỹ sư "
        "thật. Không xin được chỗ nào tử tế cho cái tài ấy, hắn đi ăn trộm — "
        "và theo lời hắn thì trở thành tay mở két giỏi nhất thế giới. Rồi bị "
        "bắt, và ngồi tù.",

        "Trong tù, hắn chế ra thứ đáng lẽ phải nằm trong một phòng thí "
        "nghiệm: hai bộ rung nén khí, phát ra sóng chấn động đủ mạnh để lắc "
        "cho một cái két bung ra mà gần như không gây tiếng động. Hắn dùng "
        "chính chúng để vượt ngục. Nhưng chi tiết hay nhất là bộ đồ. Sóng "
        "rung dội ngược sẽ nghiền nát người bắn ra nó, nên Schultz may một "
        "lớp áo chần bông để hứng phần dội ấy. Cái áo trông tức cười ấy là "
        "một thiết bị an toàn — trong cả danh sách này, hiếm ai thiết kế "
        "trang phục quanh câu hỏi thứ mình chế ra sẽ giết mình kiểu gì.",

        "The Amazing Spider-Man #46 (03/1967) của Stan Lee và John Romita Sr. "
        "cho hắn ra mắt bằng một trận thắng: Peter Parker hôm ấy đang phải "
        "băng treo một cánh tay, và Shocker hạ Spider-Man ngay hiệp đầu. Lần "
        "sau thì thua, vì Spider-Man không đánh vào hắn mà bắn tơ bịt cái nút "
        "bấm trên găng. Toàn bộ sức mạnh của Herman Schultz nằm ở hai cái "
        "công tắc, và ai cũng nhận ra điều đó trước hắn.",

        "Từ đó Shocker thành thứ đáng tin nhất trong nghề: không thù oán, "
        "không tuyên ngôn, không tham vọng làm trùm. Hắn nhận việc, làm xong, "
        "lấy tiền, và về. Chính cái tính chuyên nghiệp chán chường ấy khiến "
        "hắn được viết hay nhất khi bị đem ra đùa — trong Superior Foes of "
        "Spider-Man, hắn là gã già nhất, tỉnh nhất và mệt mỏi nhất của cả "
        "băng, người duy nhất chỉ muốn xong việc để đi ăn tối.",
    ),

    powers=(
        "Hai bộ rung nén khí gắn ở găng: sóng chấn động lắc vỡ bê tông và thép",
        "Mở két bằng cách rung cho ổ khoá tự bung, gần như không gây tiếng động",
        "Sóng rung dựng thành tấm chắn, làm chệch cả đạn lẫn tơ nhện",
        "Áo chần bông không phải để đẹp: nó hứng phần sóng dội ngược lại người mặc",
        "Kỹ sư tự học — mọi thứ hắn dùng đều do hắn tự chế và tự sửa",
        "Điểm yếu: tất cả nằm ở hai cái nút bấm trên găng tay",
    ),

    facts=(
        ("Tên thật", "Herman Schultz"),
        ("Xuất hiện đầu", "ASM #46  ·  03/1967"),
        ("Tác giả", "Stan Lee & John Romita Sr."),
        ("Nghề cũ", "Trộm két, tự nhận giỏi nhất"),
        ("Chế đồ ở", "Trong tù"),
        ("Trận đầu", "Thắng — tay Peter đang băng treo"),
    ),

    blurb="Cả danh sách này muốn được nhớ tên. Herman Schultz chỉ muốn cái "
          "két mở ra êm, không ai nghe thấy, và về nhà trước bữa tối.",

    art=draw_shocker,
    caption="Bản in bị rung, xẻ thành dải  ·  dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Shocker_(character)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/Herman_Schultz_(Earth-616)"),
    ),
)
