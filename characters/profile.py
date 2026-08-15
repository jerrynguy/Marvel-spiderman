"""
Khuôn dữ liệu cho một hồ sơ nhân vật.

Mỗi nhân vật là một file riêng trong thư mục này, khai báo đúng một biến
`PROFILE = Profile(...)`. Không cần đăng ký ở đâu khác — thêm file là xong.

Ảnh nhân vật:
    · Thả file ảnh vào  assets/characters/  rồi ghi tên file vào `image`.
    · Hoặc bỏ trống `image` và vẽ tay bằng `art` (một hàm nhận QPainter và
      QRectF). Nếu cả hai đều có, ảnh thật được ưu tiên, `art` là dự phòng.
    · `art` nhận thêm tham số thứ ba (số giây) thì chân dung tự động chạy —
      khung hình được vẽ lại liên tục và `t` tăng dần.

Dạng tiến hoá:
    Điền `evolution=` bằng một Profile khác thì tấm hồ sơ mọc thêm nút
    tiến hoá; bấm vào, tờ giấy vỡ ra và dạng mới hiện ra ở một tai hồ sơ
    riêng. Dạng mới lại có thể có `evolution` của nó — nối bao nhiêu tầng
    cũng được.

    Mỗi dạng Absolute nên khác nhau cả ba tầng: `skin` chọn bảng màu riêng,
    `evolve_fx` chọn kiểu phá tờ giấy cũ, và hàm `art` vẽ chân dung với ngôn
    ngữ chuyển động riêng của nhân vật đó.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets" / "characters"


@dataclass(frozen=True)
class Section:
    """Một mục dài trong cột đọc: tiêu đề, một đoạn dẫn, rồi các gạch đầu dòng.

    Mỗi gạch đầu dòng là cặp (tên đòn, mô tả) — tên in đậm dẫn dòng.
    """

    title: str
    intro: str = ""
    items: Tuple[Tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Tier:
    """Một bậc trên thang tàn phá: nhãn, tên bậc, mô tả và tốc độ gây hại."""

    label: str
    title: str
    text: str
    speed: str = ""


@dataclass(frozen=True)
class Profile:
    # ---- định danh: `name` phải trùng đúng tên trong danh sách VILLAINS
    name: str
    vi_name: str = ""            # tên gọi tiếng Việt, in dưới masthead
    real_name: str = ""          # tên thật của nhân vật
    keys: Tuple[str, ...] = ()   # tên gọi khác để tra cứu

    # ---- nội dung
    tagline: str = ""            # một câu mở, in nghiêng cạnh chân dung
    summary: Tuple[str, ...] = ()   # các đoạn mô tả
    powers: Tuple[str, ...] = ()    # gạch đầu dòng năng lực
    sections: Tuple[Section, ...] = ()   # các mục dài, mỗi mục một khối
    tiers: Tuple[Tier, ...] = ()         # thang bậc tàn phá, vẽ thành nấc
    facts: Tuple[Tuple[str, str], ...] = ()   # bảng (nhãn, giá trị)
    blurb: str = ""              # câu kết in trong khung, giọng biên tập

    # ---- cách trình bày tấm hồ sơ
    kicker: str = ""             # chữ đỏ nhỏ ở góc trên, mặc định "Hồ sơ ác nhân"
    stamp: str = ""              # dòng đóng dấu bên phải header
    note: str = ""               # nhãn nhỏ cạnh kicker
    note_kind: str = "new"       # màu nhãn: edge | new | fix
    tab: str = ""                # chữ trên tai hồ sơ, mặc định là `name`
    skin: str = ""               # tên bộ da: pulp (mặc định) | void | sky

    # ---- dạng tiến hoá
    evolution: Optional["Profile"] = None   # dạng mở ra bằng nút tiến hoá
    evolve_label: str = ""       # chữ trên nút, mặc định "EVOLVE"
    evolve_fx: str = "shatter"   # kiểu phá tờ giấy cũ: shatter | shred

    # ---- hình ảnh
    image: str = ""              # tên file trong assets/characters
    art: Optional[Callable] = None   # painter(QPainter, QRectF) vẽ thay ảnh
    caption: str = ""            # chú thích dưới khung chân dung

    # ---- liên kết ngoài: ((nhãn, url), ...)
    links: Tuple[Tuple[str, str], ...] = field(default=())

    def image_path(self) -> Optional[Path]:
        """Đường dẫn ảnh nếu file có thật, ngược lại None."""
        if not self.image:
            return None
        p = Path(self.image)
        if not p.is_absolute():
            p = ASSETS / p
        return p if p.is_file() else None

    def lookup_keys(self) -> Tuple[str, ...]:
        return (self.name,) + tuple(self.keys)
