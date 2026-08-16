# Marvel-spiderman — bàn giao sang phiên mới

## Project là gì

App PySide6 (`python3 spiderman.py`) hiện dòng thời gian 91 ác nhân
Spider-Man theo phong cách truyện Silver Age: giấy pulp, lưới halftone, mực
in lệch trục. Click một nhân vật đã có hồ sơ thì mở tấm hồ sơ ngay trong app.

Repo: `jerrynguy/Marvel-spiderman`, nhánh `main`, mới nhất `961ab32`.
Mọi thứ đã push xong, không còn gì lơ lửng.

## ĐỌC CÁI NÀY TRƯỚC: việc còn dang dở là gì

**Mới 11 trên 91 nhân vật có hồ sơ trong app. 80 người còn lại click vào là
mở trình duyệt ra Wikipedia** — xem `on_click()` trong `spiderman.py`:

```python
profile = characters.get(name)
if profile is None:
    self.open_web(url_for(name, self.source.currentText()))   # 80 người rơi vào đây
    return
self.open_profile(profile, self.sender())                      # chỉ 11 người
```

Đó là khoảng trống chính của project, và cũng là việc đang chạy: **viết hồ sơ
gốc cho những nhân vật chưa có**, đi tuần tự theo dòng thời gian. Mười một người
đã xong là mười một cái tên đầu danh sách; người kế tiếp là **Kraven the
Hunter** (ASM #15, 08/1964), rồi Beetle, Scorpion...

Hệ "dạng tiến hoá Absolute" bên dưới **đã xong và không cần làm thêm gì**.
Đừng đề xuất gắn Absolute cho ai đó chưa có hồ sơ gốc: Absolute treo dưới
`evolution=` của một `PROFILE` đã tồn tại, không có hồ sơ gốc thì không có
chỗ mà treo. Trình tự bắt buộc là **hồ sơ gốc trước, Absolute sau (nếu
muốn)**.

## Mười một hồ sơ đã có

Sáu người đầu có thêm dạng Absolute; năm người sau mới chỉ có hồ sơ gốc.

| # | Nhân vật | Số báo | Chân dung dựng quanh cái gì | Absolute |
|---|---|---|---|---|
| 1 | Chameleon | ASM #1 | mặt nạ trắng trơn không có nét mặt | có |
| 2 | Vulture | ASM #2 | đôi cánh dang hết cỡ | có |
| 3 | Tinkerer | ASM #2 | ông già dưới quầng đèn xưởng | có |
| 4 | Doctor Octopus | ASM #3 | bốn càng máy | có |
| 5 | Sandman | ASM #4 | nửa người rã thành cát | có |
| 6 | Lizard | ASM #6 | áo blouse rách trên mình bò sát | có |
| 7 | Living Brain | ASM #8 | cỗ máy đối xứng, băng giấy đục lỗ | chưa |
| 8 | Electro | ASM #9 | mặt nạ hình sao giữa vụ phóng điện | chưa |
| 9 | Big Man | ASM #10 | người thật bé tí dưới cái bóng khổng lồ | chưa |
| 10 | Mysterio | ASM #13 | quả cầu thuỷ tinh không có mặt bên trong | chưa |
| 11 | Green Goblin | ASM #14 | nhìn từ dưới lên: bom bí ngô đang rơi xuống ta | chưa |

## Nguyên tắc vẽ chân dung — quan trọng nhất

**Mỗi chân dung phải khác hẳn mười cái kia.** Không chỉ khác nội dung mà khác
cả cách dựng hình. Sáu hồ sơ đầu đều theo một lối: bóng đen đặc trên nền
giấy, `misprint()` lo phần mực lệch trục. Ba hồ sơ sau cố tình bẻ lối đó:

- **Living Brain** đảo vai trò của chi tiết: khối máy là mực đen, còn mọi chi
  tiết là mặt đồng hồ sáng nổi lên trên nền đen.
- **Electro** đảo hẳn sắc độ: bộ đồ chỉ tối vừa phải (`SUIT`), mặt nạ và găng
  là chỗ sáng nhất tờ giấy. Hắn làm bằng ánh sáng nên vẽ thành mảng đen thì
  sai bản chất.
- **Big Man** dùng hai sắc độ cho hai lớp: cái bóng tô mực nhạt và **không**
  kèm bóng in lệch trục (nó vốn không có thật), người thật tô đen đặc kèm đủ
  hai lớp mực lệch.

Khi làm người kế tiếp, hãy hỏi trước: hình này có thể là hình của ai khác
trong danh sách không? Nếu có thì nghĩ lại.

## Cách làm việc bắt buộc: vẽ xong phải nhìn ảnh

Đừng tin code đúng chỉ vì nó chạy. Mọi lỗi nặng của mười một chân dung này đều
chỉ lộ ra khi render ra PNG rồi mở lên nhìn. Vòng lặp là: viết code → render
offscreen → **mở ảnh ra xem** → sửa. Thường mất ba bốn vòng.

```bash
QT_QPA_PLATFORM=offscreen python3 <script>
```

Ba phép thử hay dùng (viết trong scratchpad, không commit):

- **Chụp tấm chân dung**: dựng `PortraitPlate(profile, QSize(300, 360), SKINS["pulp"])`,
  `plate.render(painter, QPoint(0, 0))` vào một `QImage` rồi lưu ra PNG.
  Lưu ý `render()` cần tham số `QPoint` thứ hai, thiếu là sập.
- **Chụp cả tấm hồ sơ**: dựng `spiderman.Window()`, `QTest.mouseClick` vào
  chip, `QTest.qWait(1400)`, rồi render cả cửa sổ. Xem chữ có tràn dòng
  không, hàng lý lịch có gãy làm hai không.
- **Vòng đời**: mở từng nhân vật, bấm `EvolveButton`, kiểm `stage.index`,
  `stage.card.s.name`, `stage._fx_style`, `stage.tabs.count()`, rồi đóng.
  Hiện là 81 mục cho chín nhân vật, phải xanh hết trước khi commit.

Khi chưa nhìn ra hình bị gì, **render riêng cái bóng người** (chỉ `_figure()`,
tô một màu, không nền không hiệu ứng). Nhiều lần tưởng thiếu cánh tay mà thật
ra tay vẫn đó, chỉ là bị lớp khác nuốt mất.

## Mấy cái bẫy đã gặp

- **Hợp path thì mất luôn đường nối bên trong.** `body.united(arm)` cho ra
  một bóng liền, nên chỗ tay giáp thân không còn nét nào — cánh tay chìm vào
  thân. Cách chữa: vẽ viền riêng cho từng cánh tay đè lên (xem `electro.py`),
  chứ không phải nới rộng khoảng cách.
- **Đừng chồng path rời thay vì hợp lại.** Chồng rời thì mỗi chi được viền
  riêng, nhân vật trông như hình que neon. Hợp lại rồi mới vẽ viền bổ sung.
- **Chi tiết sáng trên đồ thì đừng cho thêm bóng in lệch trục.** Cả bóng
  người đã lệch một lần rồi; lệch chồng nữa thì viền sét hoá thành dải ba màu
  loè loẹt. Chỉ mực sáng và nét mảnh là đủ.
- **Tô chi tiết thì cắt theo bóng người** (`setClipPath(figure, IntersectClip)`).
  Vẽ rộng tay cũng không tràn, khỏi phải căn từng toạ độ.
- **`setClipRect`/`setClipPath` thay hẳn vùng cắt chứ không giao thêm.** Luôn
  truyền `Qt.ClipOperation.IntersectClip`.
- **Đừng chèn hàm mới vào giữa `_make_shards` / `_make_cracks`** trong
  `ui/character_modal.py`. Đã mắc hai lần: nhánh mặc định thành code chết sau
  `return`, kiểu `shatter` nhận `None` rồi **sập trong paintEvent**. Nay hai
  hàm đó đã đổi sang tra bảng nên không còn chỗ chen.
- Qt nuốt phím `Tab` cho việc chuyển tiêu điểm, nên phím tắt đổi tai hồ sơ
  dùng mũi tên trái/phải.

## Hiệu năng chân dung

Khung hồ sơ **vẽ lại tấm chân dung hơn hai chục lần trong lúc mở** (đếm được
bằng cách đè `PortraitPlate.paintEvent`). Ngân sách khoảng 4–10 ms mỗi lần vẽ.

- Chân dung **động** (`art` có tham số `t`): lớp nào không đổi theo `t` thì
  dựng sẵn vào `QImage` rồi dán — xem `_still()` trong các file `*_absolute.py`.
- Chân dung **tĩnh mà nặng** thì cũng đáng dựng sẵn cả tấm: `electro.py` cache
  nguyên bức theo đúng cỡ điểm ảnh thật, **16,7 ms xuống còn 0,18 ms**. Nhớ
  lấy `scale` từ `p.transform().m11()` để ảnh không bị nhoè trên màn HiDPI, và
  giới hạn số bản trong cache kẻo kéo cửa sổ là phình bộ nhớ.
- Hợp path (`united`, `subtracted`) là phép đắt. Hàm nào không có tham số đổi
  thì bọc `@lru_cache` là xong.
- Đổi cọ hàng trăm lần mỗi khung là thứ đắt nhất — gom theo bậc màu rồi
  `drawRects`.

Sau khi cache, luôn **đối chiếu từng điểm ảnh** giữa bản dán và bản vẽ thẳng
ở cả 1x và 2x. Lệch quá 2/255 là cache sai chứ không phải khử răng cưa.

## Thêm một hồ sơ gốc (việc chính đang cần)

1. Chép `characters/big_man.py` thành `characters/<tên>.py`
2. Sửa nội dung, giữ nguyên tên biến `PROFILE`
3. `Profile.name` phải trùng đúng tên trong danh sách `VILLAINS` ở
   `spiderman.py`; tên khác thì thêm vào `keys=(...)`
4. Vẽ chân dung bằng code qua `art=` (khung quy ước 100 × 120, đồ nghề ở
   `characters/art.py`), hoặc thả ảnh vào `assets/characters/` rồi khai
   `image="tên.jpg"`
5. Thêm một dòng vào cây thư mục trong `README.md`

Không cần đăng ký ở đâu khác — `characters/__init__.py` tự quét thư mục.
Chip của nhân vật đã có hồ sơ sẽ hiện một góc gấp ở mép trên bên phải.

Các trường của hồ sơ: `tagline`, `summary` (3–4 đoạn), `powers` (5 gạch đầu
dòng), `facts` (6 hàng), `blurb`, và nếu cần thì `sections=(Section(...),)`
cùng `tiers=(Tier(...),)`. `kicker` đổi được chữ đỏ góc trên — Living Brain
dùng `"Hồ sơ khí tài"` vì nó là máy chứ không phải người.

**Giá trị trong `facts` nên dưới 40 ký tự**, dài hơn là hàng gãy làm hai
dòng. Đã phải cắt ngắn dòng "Trên màn ảnh" của Electro vì lý do này.

## Dữ liệu phải tra, đừng viết theo trí nhớ

Mỗi hồ sơ đều tra lại bằng `WebSearch` trước khi viết. `en.wikipedia.org` bị
chặn ở tầng proxy nên `WebFetch` thẳng vào đó sẽ hỏng; dùng `WebSearch` rồi
đọc kết quả từ marvel.fandom.com, spiderfan.org, marvel.com.

Mấy chi tiết chỉ tra mới ra, mà lại là thứ làm nên cả bức chân dung:

- Bảng điều khiển của Living Brain nằm **giữa ngực** — đúng chỗ người thợ bị
  đẩy ngã vào làm nó phát điên. Chi tiết đó thành tâm điểm của hình.
- Bộ đồ Electro là **xanh lá viền sét vàng**, găng hình tia chớp. Không tra
  thì đã vẽ bộ đồ trơn.
- Foswell cao **1m65**, và hắn độn giày với độn vai. Con số đó chính là bố
  cục của bức hình.

## Phần đã xong: hệ "dạng tiến hoá Absolute"

Hồ sơ nào khai `evolution=` thì mọc thêm nút **EVOLVE** ở chân trang. Bấm
vào: tờ giấy cũ bị phá theo một kiểu riêng, tấm mới hiện ra ở một tai hồ sơ
bên cạnh. Đổi qua lại bằng chuột hoặc mũi tên trái/phải.

Ba trục tạo khác biệt, khai trong `Profile`:

| Trục | Việc |
|---|---|
| `skin="..."` | Bảng màu cả tấm hồ sơ. Định nghĩa ở `theme.py` |
| `evolve_fx="..."` | Cách phá tờ giấy cũ **và** chiều quét dựng tấm mới |
| `art=fn(p, rect, t)` | Chân dung; có tham số `t` thì tự chạy 25 hình/giây |

| Nhân vật | skin | evolve_fx | dựng tấm mới |
|---|---|---|---|
| Chameleon | `void` tím than | `shatter` nứt rồi nổ | mở từ giữa |
| Vulture | `sky` thép + natri | `shred` vuốt xé, gió cuốn | quét ngang |
| Tinkerer | `mesh` graphite + axit | `dissolve` ăn từ mép, lốc ô | khép từ ngoài vào |
| Doctor Octopus | `forge` gang chảy + đồng thau | `crush` càng bấu, bẻ thành tảng | cửa thép trượt lại |
| Sandman | `dust` cát bệch (**sáng**) | `erode` mài mòn | cát bồi từ đáy |
| Lizard | `swamp` xanh rêu + lưu huỳnh | `bloom` bào tử phủ kín | nở tròn từ một hạt |

Sáu cái trên đã chiếm hết các hướng dễ thấy; làm dạng thứ bảy thì phải nghĩ
ra bộ da và cú chuyển cảnh mới. Nhưng nhắc lại: đó không phải việc đang cần.

## Vị trí file

```
spiderman.py                khung app: danh sách, bộ lọc, tìm kiếm, dòng thời gian
theme.py                    Skin + 7 bảng màu (PULP, VOID, SKY, MESH, FORGE, DUST, SWAMP)
ui/character_modal.py       tấm hồ sơ, nút EVOLVE, tai hồ sơ, toàn bộ 6 hiệu ứng
characters/profile.py       Profile, Section, Tier
characters/art.py           đồ nghề vẽ dùng chung (design, ribbon, fan, glow, Rolls...)
characters/<tên>.py         hồ sơ gốc
characters/<tên>_absolute.py  dạng tiến hoá (không khai PROFILE, treo qua evolution=)
```

## Quy trình push — quan trọng

Session không có quyền ghi GitHub (Claude GitHub App chưa được kết nối cho
tổ chức). `git push` trả 403 từ chính GitHub. Cách làm đã chốt:

1. Claude commit trong container
2. Claude chạy `git format-patch origin/main --stdout > x.patch` rồi gửi file
3. Người dùng tải về, chạy trên máy mình (Windows PowerShell):
   ```powershell
   git am $HOME\Downloads\x.patch
   git push
   ```
4. Phiên sau `git fetch origin main` rồi `git diff --stat HEAD origin/main`
   để chắc cây file khớp, sau đó `git reset --hard origin/main`

Đừng mất thời gian thử push lại — đã thử hết: git thẳng, GIT_ASKPASS, GitHub
MCP, `add_repo` access:push. Tất cả đều 403.

Trước khi cắt patch, **luôn `git fetch origin main` rồi kiểm lại** — người
dùng có thể đã push commit trước xen vào giữa, và gửi patch chứa cả commit đã
có trên remote thì `git am` sẽ xung đột. Chỉ gửi phần `origin/main..HEAD`.
