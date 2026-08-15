"""
Sổ tra hồ sơ nhân vật.

Cách thêm một nhân vật mới:
    1. Chép `chameleon.py` thành `<tên_nhân_vật>.py` trong thư mục này.
    2. Sửa nội dung, giữ nguyên biến `PROFILE`.
    3. `Profile.name` phải trùng đúng tên trong danh sách VILLAINS ở
       spiderman.py (nếu muốn tên khác, thêm vào `keys`).
Không cần khai báo thêm ở bất kỳ đâu — module này tự quét thư mục.

Nhân vật chưa có file hồ sơ vẫn chạy bình thường: click vào sẽ mở trang web
như trước.
"""

import importlib
import pkgutil

# tái xuất cho các file nhân vật
from .profile import Profile, Section, Tier  # noqa: F401

_index = None


def _build():
    """Nạp mọi module nhân vật trong gói và lập chỉ mục theo tên."""
    found = {}
    for info in pkgutil.iter_modules(__path__):
        if info.name.startswith("_") or info.name in ("profile", "art"):
            continue
        module = importlib.import_module(f"{__name__}.{info.name}")
        profile = getattr(module, "PROFILE", None)
        if isinstance(profile, Profile):
            for key in profile.lookup_keys():
                found[key.casefold()] = profile
    return found


def _ensure():
    global _index
    if _index is None:
        _index = _build()
    return _index


def get(name):
    """Hồ sơ của `name`, hoặc None nếu chưa có file cho nhân vật đó."""
    return _ensure().get(name.casefold())


def has(name):
    return name.casefold() in _ensure()


def names():
    """Tên các nhân vật đã có hồ sơ, không trùng lặp."""
    seen = {}
    for profile in _ensure().values():
        seen[profile.name] = None
    return tuple(seen)


def reload():
    """Quét lại thư mục — tiện khi vừa thêm file mà không muốn tắt app."""
    global _index
    _index = None
    return _ensure()
