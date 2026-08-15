"""
Sandman — William Baker, tức Flint Marko.

Chân dung vẽ bằng code: nửa thân trên còn nguyên hình người, một tay nắn
thành búa cát khổng lồ, nửa dưới rã thành hạt rồi đổ xuống thành đống. Đám
hạt rắc bằng bộ sinh số có seed cố định nên lần nào vẽ cũng ra y hệt.
"""

import random

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainterPath, QPen

from theme import INK, PAPER_HI

from .art import design, marks, misprint, ribbon
from .profile import Profile

SEED = 4      # đổi số này là đổi thế rắc của cát


# ═══════════════════════════════════════════════════ chân dung vẽ bằng code
def _torso():
    torso = QPainterPath()
    torso.moveTo(36, 37)
    torso.cubicTo(38, 34, 54, 34, 57, 37)
    torso.cubicTo(63, 46, 65, 64, 64, 84)
    torso.lineTo(31, 84)
    torso.cubicTo(30, 64, 32, 46, 36, 37)
    torso.closeSubpath()
    return torso


def _figure():
    """Phần còn giữ được hình người: đầu, thân, hai tay và cái búa."""
    head = QPainterPath()
    head.addEllipse(QPointF(46, 26), 9.5, 10.0)
    fig = head.united(_torso())

    # tay trái buông thõng, đầu bàn tay đã bắt đầu tơi ra
    fig = fig.united(ribbon(QPointF(34, 45), QPointF(24, 58),
                            QPointF(19, 74), 6.0, 3.2))
    # tay phải giơ lên, nối vào khối búa
    fig = fig.united(ribbon(QPointF(60, 44), QPointF(69, 39),
                            QPointF(77, 31), 6.6, 5.2))

    mallet = QPainterPath()
    mallet.addRoundedRect(71, 11, 25, 27, 6, 6)
    return fig.united(mallet)


def _mound():
    """Đống cát dưới chân, chỗ phần thân dưới đã đổ hết xuống."""
    mound = QPainterPath()
    mound.moveTo(9, 124)
    mound.cubicTo(18, 119, 26, 114, 34, 113)
    mound.cubicTo(40, 112, 42, 108, 48, 107)
    mound.cubicTo(58, 106, 66, 111, 72, 113)
    mound.cubicTo(80, 115, 85, 119, 92, 124)
    mound.closeSubpath()
    return mound


def _grains(rng):
    """Toạ độ và cỡ từng hạt cát: dày sát thân, thưa dần ra ngoài."""
    out = []
    for _ in range(460):                       # vùng rã chính giữa hai khối
        x, y = rng.uniform(16, 84), rng.uniform(76, 108)
        near = 1.0 - min(1.0, abs(x - 48) / 32.0) ** 1.5
        down = 1.0 - (y - 76) / 34.0
        if rng.random() < near * (0.35 + 0.65 * down):
            out.append((x, y, rng.uniform(0.6, 1.9)))
    for _ in range(90):                        # cát văng ra từ cái búa
        x, y = rng.uniform(64, 99), rng.uniform(4, 44)
        if rng.random() < 0.34:
            out.append((x, y, rng.uniform(0.5, 1.4)))
    for _ in range(70):                        # bàn tay trái đang tơi ra
        x, y = rng.uniform(10, 28), rng.uniform(62, 88)
        if rng.random() < 0.42:
            out.append((x, y, rng.uniform(0.5, 1.5)))
    return out


def draw_sandman(p, rect):
    """Vẽ chân dung vào `rect`. Nền giấy và halftone do khung lo trước."""
    with design(p, rect, h=118):
        misprint(p, _figure().united(_mound()))

        # cát rã ra: chấm mực rời, dày sát người rồi thưa dần
        rng = random.Random(SEED)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(INK)
        for x, y, r in _grains(rng):
            p.drawEllipse(QPointF(x, y), r, r)

        # sọc áo, vạch sáng cắt ngang riêng phần thân
        stripe = QColor(PAPER_HI)
        stripe.setAlpha(78)
        p.setPen(QPen(stripe, 1.6))
        p.setClipPath(_torso())
        for y in (50, 60, 70):
            p.drawLine(QPointF(28, y), QPointF(68, y + 1))
        p.setClipping(False)

        # mắt: hai khe sáng hẹp, không phải hai con mắt tròn
        light = QColor("#EFE7D5")
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(light)
        for cx in (42.2, 50.8):
            p.drawEllipse(QPointF(cx, 24.5), 2.2, 0.85)

        marks(p)


# ═══════════════════════════════════════════════════════════════ hồ sơ
PROFILE = Profile(
    name="Sandman",
    vi_name="Người Cát",
    real_name="William Baker",

    tagline="Một tên vượt ngục trốn nhầm vào bãi thử hạt nhân, và đứng dậy "
            "khi không còn hoàn toàn là người nữa.",

    summary=(
        "William Baker — ngoài đời hắn dùng cái tên Flint Marko — là một tên "
        "tội phạm vừa vượt ngục. Hắn trốn xuống bãi biển nằm trong khu thử hạt "
        "nhân, và có mặt đúng lúc người ta cho nổ. Cát nhiễm xạ trộn vào cơ "
        "thể hắn, và từ đó Baker là cát. Mà cát thì không đấm vỡ được.",

        "Xuất hiện trong The Amazing Spider-Man #4 (09/1963), Sandman là bài "
        "toán đầu tiên Spider-Man không giải được bằng nắm đấm. Đấm vào thì "
        "tay xuyên qua, trói thì hắn chảy ra. Cách Peter hạ hắn trong số báo "
        "đó là một cái máy hút bụi — rất đúng chất giai đoạn Ditko: thắng "
        "bằng cái đầu chứ không bằng cơ bắp.",

        "Hắn nắn cơ thể thành búa, thành chuỳ, nén cát cứng như đá hoặc tơi "
        "ra cho đòn đi xuyên qua, và hút thêm cát vào để phình to. Nước và "
        "nhiệt độ cao là hai thứ hạ được hắn. Sandman cũng là một trong sáu "
        "cái tên sáng lập Sinister Six (ASM Annual #1, 1964) — nhưng khác "
        "phần lớn danh sách này, đã có một quãng dài hắn cố làm người tử tế, "
        "đứng cùng phía với Spider-Man, trước khi bị kéo ngược về vai ác.",
    ),

    powers=(
        "Biến toàn thân thành cát: đấm xuyên qua, trói không được",
        "Nắn tay thành búa, thành chuỳ, thành lưỡi dao",
        "Nén cát cứng như đá, hoặc tơi ra để đòn đi xuyên qua",
        "Hút thêm cát vào người để phình to ra",
        "Sợ nước; gặp nhiệt độ đủ cao thì hoá thuỷ tinh",
    ),

    facts=(
        ("Tên thật", "William Baker"),
        ("Biệt danh", "Flint Marko"),
        ("Xuất hiện đầu", "ASM #4  ·  09/1963"),
        ("Tác giả", "Stan Lee & Steve Ditko"),
        ("Băng nhóm", "Sinister Six — thành viên sáng lập"),
        ("Trên màn ảnh", "Thomas Haden Church, Spider-Man 3 (2007)"),
    ),

    blurb="Rất ít cái tên trong danh sách này từng thử làm người tử tế. "
          "Sandman thử thật, và trong một quãng dài, hắn làm được.",

    art=draw_sandman,
    caption="Chân dung dựng lại bằng code",

    links=(
        ("Wikipedia", "https://en.wikipedia.org/wiki/Sandman_(Marvel_Comics)"),
        ("Marvel Fandom",
         "https://marvel.fandom.com/wiki/William_Baker_(Earth-616)"),
    ),
)
