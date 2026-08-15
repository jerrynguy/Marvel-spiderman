# Ảnh nhân vật

Thả file ảnh vào đúng thư mục này, rồi khai báo tên file trong hồ sơ nhân vật:

```python
PROFILE = Profile(
    name="Chameleon",
    image="chameleon.jpg",     # trỏ tới assets/characters/chameleon.jpg
    ...
)
```

Quy tắc:

- Định dạng nào Qt đọc được đều dùng được: `.png`, `.jpg`, `.webp`, `.bmp`.
- Ảnh được phóng để **phủ kín** khung rồi cắt phần thừa, nên ảnh dọc
  (khoảng 3:4) và mặt nằm giữa khung sẽ lên hình đẹp nhất. Cỡ 600×760 px
  trở lên là đủ nét.
- Ảnh thật luôn được ưu tiên hơn hình vẽ bằng code (`art=`). Muốn quay lại
  hình vẽ thì xoá dòng `image=` hoặc đổi tên file đi.
- Chưa có ảnh mà cũng không có `art=` thì khung sẽ in chữ cái đầu thật to —
  app vẫn chạy bình thường, không lỗi.

Ảnh nhân vật Marvel hầu hết có bản quyền. Thư mục này để trống trong repo;
tự thêm ảnh mà bạn có quyền dùng.
