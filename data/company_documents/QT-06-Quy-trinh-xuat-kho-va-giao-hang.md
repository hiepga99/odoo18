# QUY TRÌNH XUẤT KHO VÀ ĐIỀU PHỐI GIAO HÀNG
> **Mã hiệu:** QT-XK-06  
> **Phiên bản:** 1.0 (Áp dụng từ năm 2026)  
> **Tóm tắt nội dung:** Quy định quy trình soạn hàng, đóng gói, kiểm tra trước xuất kho và bàn giao cho đơn vị vận chuyển.  

---

## I. NGUYÊN TẮC XUẤT KHO
1. Tuân thủ nghiêm ngặt nguyên tắc FIFO (First In First Out - Nhập trước xuất trước) hoặc FEFO đối với hàng hóa có hạn sử dụng.
2. Chỉ xuất kho khi có Lệnh giao hàng (Delivery Order) hợp lệ trên hệ thống Odoo ở trạng thái 'Sẵn sàng' (Assigned).

## II. QUY TRÌNH THỰC HIỆN
### Bước 1: Tiếp nhận lệnh xuất kho
Thủ kho in Danh sách soạn hàng (Picking List) từ Odoo ERP để lấy hàng từ các kệ theo sơ đồ kho.

### Bước 2: Soạn hàng và đóng gói
- Kiểm tra ngoại quan sản phẩm, dán tem bảo hành công ty.
- Đóng thùng carton, chèn xốp khí giảm chấn đối với đồ công nghệ điện tử và dán băng keo niêm phong.

### Bước 3: Bàn giao vận chuyển & Xác nhận xuất kho
- Quét mã vạch đơn hàng khi bàn giao cho nhân viên giao hàng hoặc bưu tá Viettel Post, GHTK.
- Bấm 'Xác nhận' (Validate) Lệnh giao hàng trên Odoo. Hệ thống tự động trừ kho và cập nhật trạng thái đơn hàng sang 'Đã xuất kho'.
