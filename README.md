# Marvel-spiderman

Dòng thời gian ác nhân của Spider-Man, dựng bằng PySide6 theo phong cách
Silver Age: giấy pulp ố vàng, lưới halftone, mực in lệch trục.

Click vào một nhân vật đã có hồ sơ để mở tấm hồ sơ ngay trong app — chân dung,
mô tả, năng lực, lý lịch — với hiệu ứng chuyển cảnh mượt kiểu PowerPoint.
Nhân vật chưa có hồ sơ thì vẫn mở trang web như trước.

Hồ sơ nào có dạng tiến hoá thì mọc thêm nút **EVOLVE** ở chân trang: bấm vào,
tờ giấy cũ vỡ ra và dạng mới hiện lên ở một tai hồ sơ riêng, với chân dung tự
chạy theo thời gian. Sáu nhân vật đang có dạng tiến hoá, và chúng cố tình
không giống nhau chỗ nào:

| | Bảng màu | Phá tờ giấy | Dựng tấm mới | Chân dung |
|---|---|---|---|---|
| **Chameleon** | `void` — tím than, đỏ và lam | `shatter` — nứt từ giữa rồi nổ | mở từ giữa ra hai phía | mặt nạ vỡ thành dải trượt |
| **Vulture** | `sky` — thép lạnh và đèn natri | `shred` — vuốt xé, gió cuốn đi | quét ngang một lượt | ngược sáng mặt trời mọc, chân trời nghiêng |
| **Tinkerer** | `mesh` — graphite, đỏ tía và xanh axit | `dissolve` — ăn từ mép, xoắn thành lốc ô | khép từ ngoài vào tâm | đứng trên lưới của chính mình, nửa dưới rã thành ô |
| **Doctor Octopus** | `forge` — sắt ám khói, gang chảy và đồng thau | `crush` — bốn càng bấu, nén oằn, bẻ thành tảng | hai cánh cửa thép trượt vào nhau | tám càng tự uốn theo sóng, từng đốt một |
| **Sandman** | `dust` — cát bệch, sắt gỉ và obsidian | `erode` — mài mòn sau một đường biên răng cưa | cát bồi lên từ đáy thành đụn | bóng người dựng lại từ nhiễu, mép luôn đang lở |
| **Lizard** | `swamp` — xanh rêu, lưu huỳnh và tím nọc | `bloom` — rễ bò vào, bào tử phình thành ổ phủ kín | nở tròn ra từ một hạt ở giữa | dáng bò rình nằm ngang, sóng chạy dọc đuôi |

Mức độ "sống" của chân dung cũng tăng dần: ba dạng đầu có bóng người đứng yên
và chỉ chi tiết nhỏ động đậy; Otto và Marko thì chính nhân vật cử động — Otto
uốn tám càng, Marko thì đến cái hình cũng không cố định, mỗi khung hình một
đường viền khác.

Hai bộ da đi ra khỏi khuôn: `dust` là bộ **sáng** duy nhất — mở ra không tối
sầm mà loà lên, màn phủ là một trận cát trắng xoá; còn `swamp` là bộ duy nhất
lấy nền là một **màu** thay vì sắc trung tính.

## Chạy

```bash
pip install PySide6
python3 spiderman.py
```

## Cấu trúc

```
spiderman.py            khung app: danh sách, bộ lọc, tìm kiếm, dòng thời gian
theme.py                bảng màu, mặt chữ, lưới halftone, các bộ da của tấm hồ sơ
ui/character_modal.py   tấm hồ sơ + toàn bộ hiệu ứng chuyển cảnh và tiến hoá
characters/
    profile.py          khuôn dữ liệu Profile, Section, Tier
    art.py              đồ nghề vẽ chân dung dùng chung
    __init__.py         tự quét thư mục, không cần đăng ký tay
    chameleon.py        ASM #1 — mặt nạ trắng trơn
    chameleon_absolute.py  dạng tiến hoá của Chameleon, chân dung tự chạy
    vulture.py          ASM #2 — dang cánh
    vulture_absolute.py    dạng tiến hoá của Vulture, ngược sáng mặt trời
    tinkerer.py         ASM #2 — ngọn đèn xưởng
    tinkerer_absolute.py   dạng tiến hoá của Tinkerer, rã thành vật chất lập trình
    doctor_octopus.py   ASM #3 — bốn càng máy
    doctor_octopus_absolute.py  dạng tiến hoá của Ock, bốn càng thành tám
    sandman.py          ASM #4 — nửa người rã thành cát
    sandman_absolute.py    dạng tiến hoá của Sandman, bão sa mạc hoá
    lizard.py           ASM #6 — áo blouse rách trên mình bò sát
    lizard_absolute.py     dạng tiến hoá của Lizard, đầm lầy đồng hoá
    living_brain.py     ASM #8 — cỗ máy của Giáo sư Petty, băng giấy đục lỗ
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

**Nguyên tắc: mỗi dạng Absolute phải khác hẳn những dạng còn lại**, không chỉ
khác chữ. Ba chỗ để tạo khác biệt, khai ngay trong `Profile` của dạng mới:

```python
ABSOLUTE = Profile(
    ...
    skin="sky",              # pulp | void | sky | mesh | forge | dust | swamp
    evolve_fx="shred",       # shatter | shred | dissolve | crush | erode | bloom
    art=draw_absolute_vulture,   # nhận (p, rect, t) để chân dung tự chạy
)
```

`skin` đổi màu toàn bộ tấm hồ sơ — tên nhân vật, dải mép trên, thang bậc, nút
bấm, tai hồ sơ đều đi theo. `evolve_fx` đổi cả cách phá tờ giấy cũ lẫn chiều
quét dựng tấm mới (mở từ giữa · quét ngang · khép từ ngoài vào · cửa thép
trượt lại · cát bồi từ đáy · nở tròn từ một hạt). Còn `art` là chỗ để nhân
vật có ngôn ngữ chuyển động của riêng nó. Ngoài `summary`/`powers` quen thuộc, hồ sơ dài còn có:

| Trường | Việc |
|---|---|
| `sections=(Section(...),)` | Mục dài: tiêu đề, đoạn dẫn, rồi các gạch đầu dòng `(tên đòn, mô tả)` |
| `tiers=(Tier(...),)` | Thang bậc tàn phá, vẽ thành nấc — càng lên cao mực càng đỏ. Nhãn đánh số (`Tier 1`) hay đặt tên (`Tier Alpha`) đều được, cột trái tự nới theo chữ dài nhất |
| `kicker` `stamp` `note` `tab` | Chữ ở góc trên, dòng đóng dấu, nhãn nhỏ, tên trên tai hồ sơ |

Bấm nút lần đầu: tờ giấy cũ vỡ theo kiểu của dạng sắp tới, rồi tấm mới được
quét lại và tự dựng lấy bố cục. Xong xuôi, các dạng nằm ở những tai hồ sơ nhô
trên mép giấy — bấm tai hoặc gõ mũi tên trái/phải để đổi qua lại, lần này chỉ
một nhát quét chứ không phá lại.

## Hiệu ứng mở hồ sơ

1. Màn phủ tối dần lên kèm lưới halftone.
2. Tờ giấy phóng ra từ đúng vị trí con chip vừa bấm, giữ nguyên tỉ lệ
   (nhịp vào chậm — giữa nhanh — ra chậm, giống Morph của PowerPoint).
3. Tờ giấy đứng yên, từng khối nội dung trượt lên và hiện dần, lệch nhau
   vài phần trăm giây.
4. Đóng lại thì đảo ngược đúng thứ tự đó.

Đóng bằng phím `Esc`, nút **ĐÓNG**, dấu ✕, hoặc bấm ra ngoài tờ giấy.

Dữ liệu đã đối chiếu với Wikipedia và các nguồn Marvel (8/2026).
