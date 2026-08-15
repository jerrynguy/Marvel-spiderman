# Marvel-spiderman

Dòng thời gian ác nhân của Spider-Man, dựng bằng PySide6 theo phong cách
Silver Age: giấy pulp ố vàng, lưới halftone, mực in lệch trục.

Click vào một nhân vật đã có hồ sơ để mở tấm hồ sơ ngay trong app — chân dung,
mô tả, năng lực, lý lịch — với hiệu ứng chuyển cảnh mượt kiểu PowerPoint.
Nhân vật chưa có hồ sơ thì vẫn mở trang web như trước.

Hồ sơ nào có dạng tiến hoá thì mọc thêm nút **EVOLVE** ở chân trang: bấm vào,
tờ giấy nứt ra rồi nổ tung, và dạng mới được quét lại trên nền đen ở một tai
hồ sơ riêng. Chameleon là nhân vật đầu tiên có dạng đó — **Absolute
Chameleon**, mối đe doạ cấp quốc gia, với chân dung tự chạy theo thời gian.

## Chạy

```bash
pip install PySide6
python3 spiderman.py
```

## Cấu trúc

```
spiderman.py            khung app: danh sách, bộ lọc, tìm kiếm, dòng thời gian
theme.py                bảng màu, mặt chữ, lưới halftone, hai bộ da PULP/VOID
ui/character_modal.py   tấm hồ sơ + toàn bộ hiệu ứng chuyển cảnh và tiến hoá
characters/
    profile.py          khuôn dữ liệu Profile, Section, Tier
    art.py              đồ nghề vẽ chân dung dùng chung
    __init__.py         tự quét thư mục, không cần đăng ký tay
    chameleon.py        ASM #1 — mặt nạ trắng trơn
    chameleon_absolute.py  dạng tiến hoá của Chameleon, chân dung tự chạy
    vulture.py          ASM #2 — dang cánh
    tinkerer.py         ASM #2 — ngọn đèn xưởng
    doctor_octopus.py   ASM #3 — bốn càng máy
    sandman.py          ASM #4 — nửa người rã thành cát
    lizard.py           ASM #6 — áo blouse rách trên mình bò sát
assets/characters/      nơi thả ảnh nhân vật
```

## Thêm một nhân vật

1. Chép `characters/chameleon.py` thành `characters/<tên>.py`.
2. Sửa nội dung, giữ nguyên tên biến `PROFILE`.
3. `Profile.name` phải trùng đúng tên trong danh sách `VILLAINS` ở
   `spiderman.py`. Tên khác thì thêm vào `keys=(...)`.
4. Chạy lại app. Không cần khai báo thêm ở đâu cả.

Chip của nhân vật đã có hồ sơ sẽ hiện một **góc gấp** ở mép trên bên phải.

### Ảnh nhân vật

Thả ảnh vào `assets/characters/` rồi ghi `image="tên_file.jpg"` trong hồ sơ.
Không có ảnh thì vẽ tay bằng code qua tham số `art=` — như chiếc mặt nạ trắng
trơn của Chameleon hay đôi cánh của Vulture. Chi tiết xem
`assets/characters/README.md`.

### Vẽ chân dung bằng code

`characters/art.py` lo sẵn phần khung và chất liệu in, chỉ việc vẽ theo khung
quy ước 100 × 120:

```python
from .art import design, fan, marks, mirrored, misprint, ribbon

def draw_ai_do(p, rect):
    with design(p, rect):        # co giãn, căn giữa vào khung thật
        misprint(p, than_nguoi)  # mảng đen + hai lớp mực in lệch trục
        canh = fan(goc, [...])   # xoè lông từ một gốc
        canh = canh.united(mirrored(canh))
        marks(p)                 # dấu canh trục bốn góc
```

| Hàm | Việc |
|---|---|
| `design(p, rect, h=...)` | Đưa khung vẽ 100 × 120 vào khung thật. `h` nhỏ hơn 120 thì hình to ra và tràn mép dưới |
| `misprint(p, path)` | Mảng đen kèm hai lớp mực đỏ/xanh trượt lệch |
| `marks(p)` | Dấu canh trục bản in ở bốn góc |
| `feather(...)` / `fan(...)` | Một chiếc lông, hoặc cả nắm xoè từ một gốc — cũng dùng làm ngạnh kẹp |
| `ribbon(p0, p1, p2, w0, w1)` | Dải thuôn chạy dọc đường cong — càng máy, vòi, roi, tia điện |
| `mirrored(path)` | Lật đối xứng qua trục dọc, đỡ phải vẽ hai bên |
| `glow(p, tâm, bán kính, màu)` | Quầng sáng toả tròn, đặc ở giữa và tắt dần ra rìa |
| `scanlines(p, rect, bước, màu)` | Vạch quét ngang kiểu mặt kính CRT |
| `Rolls(hạt giống)` | Dãy số ngẫu nhiên cố định — rắc chấm, xé mảnh mà hình không rung |

## Chân dung biết cử động

`art` nhận hai tham số `(painter, rect)` thì vẽ một lần rồi thôi. Khai thêm
tham số thứ ba — số giây kể từ lúc mở hồ sơ — thì khung chân dung tự chạy
lại 25 hình mỗi giây:

```python
def draw_ai_do(p, rect, t=0.0):
    with design(p, rect):
        ...
```

Những lớp không đổi theo `t` nên dựng sẵn một lần rồi dán vào, như
`chameleon_absolute.py` làm với thành phố và bóng người: vẽ thẳng cả tám lớp
mỗi khung hình tốn 23 ms, dán lớp tĩnh xuống còn 9 ms.

## Dạng tiến hoá

Điền `evolution=` bằng một `Profile` khác thì hồ sơ mọc thêm nút **EVOLVE**:

```python
PROFILE = Profile(
    name="Chameleon",
    ...
    evolution=ABSOLUTE,      # một Profile khác, có thể lại có evolution của nó
    evolve_label="Evolve",
)
```

Dạng mới khai `dark=True` thì cả tấm hồ sơ đổi da: nền đen, mực huỳnh quang,
mực lệch trục kiểu tín hiệu số hỏng thay cho bản in chồng màu sai. Ngoài
`summary`/`powers` quen thuộc, hồ sơ dài còn có:

| Trường | Việc |
|---|---|
| `sections=(Section(...),)` | Mục dài: tiêu đề, đoạn dẫn, rồi các gạch đầu dòng `(tên đòn, mô tả)` |
| `tiers=(Tier(...),)` | Thang bậc tàn phá, vẽ thành nấc — càng lên cao mực càng đỏ |
| `kicker` `stamp` `note` `tab` | Chữ ở góc trên, dòng đóng dấu, nhãn nhỏ, tên trên tai hồ sơ |

Bấm nút lần đầu: tờ giấy rung lên, nứt từ giữa ra, nổ thành mảnh, rồi tấm mới
được quét lại và tự dựng lấy bố cục. Xong xuôi, hai dạng nằm ở hai tai hồ sơ
nhô trên mép giấy — bấm tai hoặc gõ mũi tên trái/phải để đổi qua lại, lần này
chỉ một nhát quét chứ không nổ nữa.

## Hiệu ứng mở hồ sơ

1. Màn phủ tối dần lên kèm lưới halftone.
2. Tờ giấy phóng ra từ đúng vị trí con chip vừa bấm, giữ nguyên tỉ lệ
   (nhịp vào chậm — giữa nhanh — ra chậm, giống Morph của PowerPoint).
3. Tờ giấy đứng yên, từng khối nội dung trượt lên và hiện dần, lệch nhau
   vài phần trăm giây.
4. Đóng lại thì đảo ngược đúng thứ tự đó.

Đóng bằng phím `Esc`, nút **ĐÓNG**, dấu ✕, hoặc bấm ra ngoài tờ giấy.

Dữ liệu đã đối chiếu với Wikipedia và các nguồn Marvel (8/2026).
