# NGUYÊN TẮC THIẾT KẾ VÀ PHÁT TRIỂN MÃ NGUỒN (CODING PRINCIPLES & PONYTAIL)

Mọi tác vụ lập trình trong dự án phải tuân thủ nghiêm ngặt 5 nguyên tắc cốt lõi và phong cách **Ponytail (Lazy Senior Dev Mode)**:

---

## 1. Analyze Before Coding
* Đọc kỹ cấu trúc dự án và mã nguồn hiện có trước khi thực hiện bất kỳ chỉnh sửa nào.
* Xác định rõ phạm vi ảnh hưởng (callers, tests, cấu hình, dữ liệu) trước khi bắt tay vào code.

## 2. Reuse Before Create
* Luôn tái sử dụng các components, services, tools, helper utilities và patterns đã có sẵn trong dự án.
* Tuyệt đối không viết mới nếu codebase hoặc thư viện chuẩn (Standard Library) đã hỗ trợ.

## 3. Minimal Changes
* Chỉ chỉnh sửa đúng phần cần thiết để giải quyết triệt để yêu cầu.
* Không tự ý viết lại toàn bộ module (rewrite) hoặc thêm các tính năng không được yêu cầu ("for later" code).
* Ưu tiên diff ngắn nhất và an toàn nhất (The shortest working diff wins).

## 4. Clean Architecture & Pragmatism
* Tổ chức code hợp lý, gọn gàng theo domain nghiệp vụ.
* Tránh chia quá nhiều file vụn vặt hoặc tạo các lớp abstraction / wrapper không cần thiết.
* Giữ cấu trúc dự án tinh gọn: tách biệt rõ ràng giữa Code thực thi và Dữ liệu mẫu (Data/Scripts).

## 5. Review Before Finish
* Trước khi hoàn thành, bắt buộc rà soát:
  - Loại bỏ code trùng lặp (duplication) và các file dư thừa/rác.
  - Đảm bảo không làm gãy các chức năng và test suite hiện có.
  - Kiểm tra xem có bất kỳ thay đổi nào làm phình to repository không cần thiết.

---

## 6. Triết lý Ponytail Integration
* **Khẩu hiệu:** *"The best code is the code you never wrote."*
* **Thang quyết định khi code:**
  1. Cái này có thực sự cần tồn tại không? (YAGNI)
  2. Đã có trong codebase chưa? (Tái sử dụng)
  3. Thư viện chuẩn / nền tảng có làm được không?
  4. Dependency hiện có giải quyết được không? (Không cài thêm package mới cho vài dòng code)
  5. Có thể làm thành một giải pháp trực diện, đơn giản không?
* **Bảo toàn:** Luôn giữ tính đúng đắn, xác thực dữ liệu, bảo mật và xử lý ngoại lệ an toàn.
