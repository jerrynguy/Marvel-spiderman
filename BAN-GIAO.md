# Marvel-spiderman — bàn giao sang phiên mới

## Project là gì

App PySide6 (`python3 spiderman.py`) hiện dòng thời gian 91 ác nhân
Spider-Man theo phong cách truyện Silver Age: giấy pulp, lưới halftone, mực
in lệch trục. Click một nhân vật đã có hồ sơ thì mở tấm hồ sơ ngay trong app.

Repo: `jerrynguy/Marvel-spiderman`. Mới nhất là hồ sơ Absolute của Living
Brain, Electro, Mysterio và Green Goblin, trên nhánh
`claude/villain-evolution-profiles-aavzr8`.

## ĐỌC CÁI NÀY TRƯỚC: việc còn dang dở là gì

**Mới 13 trên 91 nhân vật có hồ sơ trong app. 78 người còn lại click vào là
mở trình duyệt ra Wikipedia** — xem `on_click()` trong `spiderman.py`:

```python
profile = characters.get(name)
if profile is None:
    self.open_web(url_for(name, self.source.currentText()))   # 78 người rơi vào đây
    return
self.open_profile(profile, self.sender())                      # chỉ 13 người
```

Đó là khoảng trống chính của project, và cũng là việc đang chạy: **viết hồ sơ
gốc cho những nhân vật chưa có**, đi tuần tự theo dòng thời gian. Mười ba người
đã xong là mười ba cái tên đầu danh sách; người kế tiếp là **Scorpion**
(ASM #20, 01/1965), rồi Molten Man, Crime Master...

Hệ "dạng tiến hoá Absolute" bên dưới **đã xong và không cần làm thêm gì**.
Đừng đề xuất gắn Absolute cho ai đó chưa có hồ sơ gốc: Absolute treo dưới
`evolution=` của một `PROFILE` đã tồn tại, không có hồ sơ gốc thì không có
chỗ mà treo. Trình tự bắt buộc là **hồ sơ gốc trước, Absolute sau (nếu
muốn)**.

## Mười ba hồ sơ đã có

Mười trong mười ba người đã có dạng Absolute; ba người còn lại mới chỉ
có hồ sơ gốc.

| # | Nhân vật | Số báo | Chân dung dựng quanh cái gì | Absolute |
|---|---|---|---|---|
| 1 | Chameleon | ASM #1 | mặt nạ trắng trơn không có nét mặt | có |
| 2 | Vulture | ASM #2 | đôi cánh dang hết cỡ | có |
| 3 | Tinkerer | ASM #2 | ông già dưới quầng đèn xưởng | có |
| 4 | Doctor Octopus | ASM #3 | bốn càng máy | có |
| 5 | Sandman | ASM #4 | nửa người rã thành cát | có |
| 6 | Lizard | ASM #6 | áo blouse rách trên mình bò sát | có |
| 7 | Living Brain | ASM #8 | cỗ máy đối xứng, băng giấy đục lỗ | có |
| 8 | Electro | ASM #9 | mặt nạ hình sao giữa vụ phóng điện | có |
| 9 | Big Man | ASM #10 | người thật bé tí dưới cái bóng khổng lồ | chưa |
| 10 | Mysterio | ASM #13 | quả cầu thuỷ tinh không có mặt bên trong | có |
| 11 | Green Goblin | ASM #14 | nhìn từ dưới lên: bom bí ngô đang rơi xuống ta | có |
| 12 | Kraven the Hunter | ASM #15 | mặt nhìn qua khe rách giữa tán lá | chưa |
| 13 | Beetle | Strange Tales #123 | bản vẽ chế tạo, bộ giáp tháo rời và rỗng | chưa |

## Nguyên tắc vẽ chân dung — quan trọng nhất

**Mỗi chân dung phải khác hẳn mười hai cái kia.** Không chỉ khác nội dung mà khác
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

Bốn hồ sơ mới nhất bẻ tiếp bốn trục khác:

- **Mysterio** cho một quả cầu thuỷ tinh mà bên trong không có gì ngoài
  sương — không giấu mặt như Chameleon, mà là không có mặt để giấu.
- **Green Goblin** đổi **góc nhìn**: nhìn từ dưới đất ngước lên, quả bom rơi
  về phía người xem nên to gần kín nửa khung. Và nguồn sáng nằm *trong* vật,
  thoát ra qua mấy lỗ khoét.
- **Kraven** chèn thêm một tầng: mực (tán lá) → giấy (khe rách) → mực (chính
  hắn, lọt trong khe). Cùng một màu mực cho tầng ngoài cùng và trong cùng.
- **Beetle** bỏ hẳn mảng đặc: toàn bộ là nét — đường bao, gạch bóng, đường
  dóng, số khoanh tròn trên giấy kẻ ô. Không phải chân dung mà là bản vẽ chế
  tạo, vì Jenkins là thợ máy; và bộ giáp tháo rời thì rỗng, vì cuối cùng hắn
  cởi ra thật.

Khi làm người kế tiếp, hãy hỏi trước: hình này có thể là hình của ai khác
trong danh sách không? Nếu có thì nghĩ lại.

Và một cái đã thử rồi mà hỏng, đừng thử lại: **để nhân vật là khoảng giấy
âm**, tức bỏ hẳn mực trên người và chỉ vẽ nền quanh. Kraven đi bốn vòng theo
lối đó đều ra một bức tượng nhợt nhạt — khoảng âm không tô bóng vào trong
được, mà nhân vật nào cũng nằm ở khuôn mặt.

## Cách làm việc bắt buộc: vẽ xong phải nhìn ảnh

Đừng tin code đúng chỉ vì nó chạy. Mọi lỗi nặng của mười ba chân dung này đều
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
  Hiện là 86 mục cho mười ba nhân vật (2 mục mỗi hồ sơ, thêm 6 mục cho mỗi
  dạng Absolute), phải xanh hết trước khi commit.

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
- **Thêm một `evolve_fx` là phải sờ đúng bốn chỗ** trong `ui/character_modal.py`:
  bảng tra ở `_make_cracks`, bảng tra ở `_make_shards`, một nhánh trong
  `_paint_boom`, và chiều quét trong `_paint_rebuild` (cả khúc tính `band` lẫn
  khúc vẽ nét sáng ở mép). Thiếu chỗ nào cũng chỉ lộ ra lúc chạy.
- **Dữ liệu của mảnh vỡ luôn nằm ở `self._shards`**, kể cả khi nó không phải
  mảnh vỡ. Kiểu `scan` cất các dòng quét ở đó; viết `self._rows` cho dễ đọc thì
  `paintEvent` ném `AttributeError` mỗi khung hình rồi **sập cả app** — cùng
  loại bẫy với `_make_shards` trả về `None` ngày trước.
- **Phá tờ giấy theo thứ tự thì mới ra chuyện, phá rải rác thì chỉ ra hoa văn.**
  Kiểu `scan` lúc đầu cho mỗi dòng tắt vào một lúc bốc ngẫu nhiên: kết quả là
  một tấm mành sáo, không ai đọc ra là cái gì. Sửa thành dòng chỉ mất đồng bộ
  **sau khi đầu đọc chạy qua** thì đọc ra ngay là một trang đang bị đọc dở.
  Cùng lý do, độ trượt ngang phải giữ dưới ~13% bề ngang tờ giấy; rộng hơn thì
  mấy chục dải giấy văng ra kín cả cửa sổ, trông như thanh cuộn.
- **Cắt tờ giấy thành nhiều dải thì chụp sẵn tờ giấy vào `QImage`.** Gọi
  `paint_sheet()` bốn sáu lần mỗi khung hình là không kịp; `_sheet_image()` trong
  `ui/character_modal.py` lo chỗ này.
- **Chữ nhỏ trong chân dung: đừng vẽ cả nghìn ký tự mỗi khung.** Trường ký tự
  của Living Brain có ~1.900 ô, dựng sẵn hết vào ảnh rồi mỗi khung chỉ xoá và
  viết lại 30 ô — 3,7 ms mỗi khung. Muốn xoá được một ô thì nền dưới nó phải là
  **màu phẳng**; để nền chuyển sắc thì mỗi chỗ xoá thành một vệt vuông thấy rõ.
- **Đục lỗ trên giấy thì tô bằng màu màn phủ, đừng tô bằng màu giấy của tấm
  mới.** Sau lưng tờ giấy là màn phủ chứ không phải tấm sắp tới. Kiểu `strike`
  lúc đầu tô lỗ cháy bằng `self._to.paper`, mà dạng tới đây lại có tờ giấy
  sáng, nên cả trận cháy ra một đám bong bóng xà phòng. Đây là cái bẫy chỉ lộ
  ra khi dạng mới dùng bộ da **sáng** — sáu dạng trước đều tối nên không ai
  vấp.
- **Nhánh rẽ vuông góc thì ra cái cây, không ra tia sét.** Bản đầu của chân
  dung Electro cho nhánh rẽ 40–86°: kết quả là một tế bào thần kinh rất đẹp mà
  không phải người. Rẽ hẹp lại (20–50°) và luôn chếch về phía trước theo hướng
  dòng chạy thì mới ra chất phóng điện.
- **Nét đều bề dày thì tia sét thành ống neon.** Phải thuôn dần từ gốc ra
  ngọn, vẽ từng đoạn một. Đắt, nhưng chỉ đắt lúc dựng ảnh sẵn, không đắt mỗi
  khung hình.
- **Muốn một đám nhánh đọc ra dáng người thì cần năm điểm neo.** Mặt nạ ở đầu
  cộng bốn nút sáng ở hai tay hai chân. Bỏ bốn nút đi là hình lập tức quay về
  làm một vụ phóng điện vô danh — đã thử.
- **`str.replace` trong script sửa file thì thay *mọi* chỗ khớp.** Chèn một
  nhánh mới vào `_paint_rebuild` bằng cách thay `elif raster:` đã đụng luôn
  cái `elif raster:` thứ hai ở khúc vẽ nét sáng, và file gãy cú pháp ngay.
  Sửa nhiều chỗ giống nhau thì kẹp thêm dòng trên dưới cho khớp đúng một chỗ.
- **Bóng người mà hợp hết mọi mảng vào một path thì mất luôn nhân dạng.**
  Mysterio hợp cả cổ áo dựng vào áo choàng: kết quả là một cái chụp đèn có
  quả cầu trên đỉnh. Tách cổ áo ra vẽ đè lên, cho nó tông riêng và viền
  riêng, thì nhận ra Beck ngay.
- **Thứ tự vẽ các lớp sân khấu chính là nội dung.** Chùm đèn chân phải nằm
  *sau* tấm phông; vẽ sau thì ánh sáng phủ lên mặt phông và cả người hoá ra
  trong suốt. Cạnh ván cũng phải sáng hơn nền mới đọc ra là bề dày.
- **Dấu sao markdown trong chữ hồ sơ: đã dính lần thứ ba.** Mysterio và
  Green Goblin đều lọt `*nhấn mạnh*` vào `intro=` và chỉ lộ ra khi chụp tấm
  hồ sơ. Đừng tin mắt mình nữa, chạy hẳn phép thử này trước mỗi lần commit:

  ```bash
  python3 - <<'PY'
  import pathlib
  for p in pathlib.Path("characters").glob("*.py"):
      s = p.read_text()
      if "Profile(" not in s: continue
      for line in s[s.index("= Profile("):].splitlines():
          if "*" in line and not line.strip().startswith("#"):
              print(p.name, line.strip())
  PY
  ```
- Qt nuốt phím `Tab` cho việc chuyển tiêu điểm, nên phím tắt đổi tai hồ sơ
  dùng mũi tên trái/phải.
- **Chữ trong hồ sơ không phải Markdown.** Viết `*nhấn mạnh*` thì tấm hồ sơ
  in ra nguyên hai dấu sao. Đã dính hai lần (Mysterio, Kraven). Muốn nhấn thì
  đổi cách đặt câu; `_bullets()` có dùng rich text nhưng đó là HTML nó tự
  bọc, còn `summary` thì cứ coi như chữ trơn.
- **Chữ trong chân dung thì dùng `QFont.setPixelSize`, đừng vẽ tay từng nét.**
  Beetle cần mấy số chú thích cỡ hai đơn vị; vẽ bằng `drawLine` cho khỏi phụ
  thuộc font thì ra nét nguệch ngoạc chứ không ra con số. `setPixelSize` tính
  theo đơn vị khung 100×120 nên chữ đúng cỡ ở mọi độ phóng và mọi DPI —
  `setPointSizeF` thì không, nó đi theo DPI.
- **`misprint()` chỉ hợp với hình cỡ vừa.** Nó đẻ ra hai bản lệch 2–3 đơn vị;
  áp lên một bóng người thì ra chất pulp, áp lên mảng phủ gần kín tờ giấy
  (nền, tán lá, bầu trời) thì mọi đường biên hoá dải đỏ-lam dày cộp, cả khung
  loè loẹt. Mảng lớn thì tô mực trơn, để dành mực lệch cho chi tiết nhỏ.

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
| Living Brain | `signal` đen trung tính, mực trắng | `scan` đầu đọc chạy dọc, dòng mất đồng bộ | ghi từng dòng từ đầu trang |
| Electro | `arc` giấy loà trên màn phủ đen kịt | `strike` sét đánh thủng, cháy dọc nhánh | loang ra dọc chính nhánh sét |
| Mysterio | `stage` nhung rượu + vàng kim | `mirage` giấy nhân bản rồi tráo chỗ | lật cả tờ như lật quân bài |
| Green Goblin | `smog` khói hoá chất, nền trung tính giữa | `press` khuôn dập thành lưới phôi bí ngô | dập lại từng ô theo thứ tự đọc |

Mười cái trên đã chiếm hết các hướng dễ thấy; làm dạng thứ mười một thì phải
nghĩ ra bộ da và cú chuyển cảnh mới. Nhưng nhắc lại: đó không phải việc đang
cần.

Bộ da `signal` và hiệu ứng `scan` của Living Brain là bộ mới nhất, và nó bẻ
hai trục mà sáu dạng kia đều chung:

- **Không có màu.** Sáu bộ da kia đều ám một sắc; `signal` đen trung tính, mực
  trắng, và là bộ duy nhất khai **ba** lớp `ghosts` thay vì hai — R · G · B
  của một màn hình bị xé, chứ không phải bản in chồng sai. `paint_sheet()` vốn
  chỉ lặp qua `skin.ghosts` nên thêm lớp thứ ba không phải sửa gì.
- **Chân dung không có một mảng mực nào**, toàn bộ dựng bằng ký tự trên lưới
  ô 2,5 × 3,3. Cái bóng đọc ra được là nhờ ba thứ cùng lúc: ô trong bóng thì ô
  nào cũng có chữ và sáng, ô ngoài chỉ 22% có chữ và mờ hẳn, cộng một mảng nền
  phẳng cùng một nét viền mảnh. Bỏ mảng nền và nét viền đi thì thử rồi: ra một
  đám nhiễu, không ra hình cỗ máy.

Bộ da `arc` và hiệu ứng `strike` của Electro thì bẻ hai trục khác nữa:

- **Giấy sáng đặt trên nền tối nhất.** `dust` cũng sáng nhưng màn phủ sáng
  theo; `arc` thì ngược — trang giấy loà trắng nổi trên một màn phủ đen kịt,
  đúng cảm giác nhìn một cú phóng hồ quang giữa đêm.
- **Chân dung đảo lại tương quan sáng tối của chính hồ sơ gốc.** Ở ASM #9,
  mặt nạ hình sao là chỗ *sáng nhất* tờ giấy. Ở bản Absolute cả trang đã cháy
  trắng vì chính hắn, nên hắn phải là thứ *tối nhất* khung — sáng hơn giấy
  thì không còn chỗ mà sáng nữa.

Bộ `stage` và hiệu ứng `mirage` của Mysterio bẻ thêm hai trục nữa:

- **Nền đỏ.** Chín bộ kia đều nền trung tính, lạnh, hoặc xanh; đây là bộ duy
  nhất lấy nhung rượu làm nền, vàng kim làm viền. Hai lớp mực lệch trục cũng
  trượt xa nhất cả dàn (±16 thay vì ±3…11) — không phải in sai, mà là hai
  diễn viên đóng thế đứng sau tờ giấy.
- **Tấm mới không bị che bớt mà bị *bóp ngang*.** Tám hướng dựng kia đều là
  một vùng cắt lớn dần; `mirage` thì không cắt gì cả, nó nén cả tờ giấy quanh
  trục dọc rồi mở ra, đúng động tác lật một quân bài. Muốn làm kiểu này thì
  phải biến hình cái painter chứ đừng tìm cách cắt.

Bộ `smog` của Green Goblin bẻ nốt cái trục cuối còn lại:

- **Nền trung tính giữa.** Mười bộ kia bộ nào cũng hoặc gần đen hoặc gần
  trắng; bộ này ở đúng khoảng giữa — giấy ám khói hoá chất, ố vàng ôliu — và
  màn phủ cũng là hơi độc chứ không phải bóng tối hay ánh sáng. Sau bộ này
  thì thang sáng–tối coi như hết chỗ: dạng thứ mười một phải tìm trục khác
  (chất liệu, độ nhám, số lớp mực), đừng tìm thêm sắc độ.

## Vị trí file

```
spiderman.py                khung app: danh sách, bộ lọc, tìm kiếm, dòng thời gian
theme.py                    Skin + 11 bảng màu (thêm SIGNAL, ARC, STAGE, SMOG)
ui/character_modal.py       tấm hồ sơ, nút EVOLVE, tai hồ sơ, toàn bộ 10 hiệu ứng
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
