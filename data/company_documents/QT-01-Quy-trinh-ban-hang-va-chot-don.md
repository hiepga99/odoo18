# QUY TRÌNH BÁN HÀNG VÀ CHỐT ĐƠN B2B & B2C
> **Mã hiệu:** QT-BH-01  
> **Phiên bản:** 1.0 (Áp dụng từ năm 2026)  
> **Tóm tắt nội dung:** Quy định các bước tiếp nhận nhu cầu, tư vấn sản phẩm, báo giá và xác nhận đơn hàng bán trên hệ thống ERP.  

---

## I. MỤC ĐÍCH
Quy trình này quy định trình tự các bước thực hiện hoạt động bán hàng từ khâu tiếp nhận thông tin khách hàng, tư vấn sản phẩm, gửi báo giá cho đến khi chốt đơn hàng và chuyển giao thông tin sang bộ phận kho vận, kế toán trên hệ thống Odoo ERP.

## II. PHẠM VI ÁP DỤNG
Áp dụng cho toàn bộ nhân viên kinh doanh (Sales), chăm sóc khách hàng và các bộ phận liên quan trực thuộc Công ty.

## III. NỘI DUNG QUY TRÌNH
### Bước 1: Tiếp nhận nhu cầu khách hàng
- Kênh tiếp nhận: Hotline, Zalo OA, Website, Email công ty hoặc nhắn tin trực tiếp qua AI Chatbot.
- Ghi nhận thông tin cơ bản: Tên khách hàng, số điện thoại, địa chỉ, nhu cầu mặt hàng và thời gian mong muốn nhận hàng.

### Bước 2: Kiểm tra tồn kho và lập Báo giá (Quotation)
- Nhân viên kinh doanh (hoặc AI Agent) kiểm tra số lượng tồn kho khả dụng trên module Tồn kho (Inventory) của Odoo ERP.
- Tạo Báo giá (Quotation) trên Odoo: Chọn đúng khách hàng, sản phẩm, số lượng, áp dụng chính sách giá và chiết khấu tương ứng.
- Thời hạn hiệu lực của Báo giá: Mặc định 07 ngày làm việc kể từ ngày gửi.

### Bước 3: Đàm phán và Xác nhận đơn hàng (Sales Order)
- Sau khi khách hàng đồng ý với báo giá, nhân viên thực hiện thao tác 'Xác nhận' (Confirm) trên Odoo.
- Hệ thống tự động chuyển trạng thái từ Báo giá sang 'Đơn bán hàng' (Sales Order) và tự động sinh Lệnh giao hàng (Delivery Order) gửi sang bộ phận Kho.

### Bước 4: Chuyển giao thông tin giao hàng & thanh toán
- Đơn hàng trả trước: Kế toán xác nhận đã nhận tiền đặt cọc hoặc thanh toán 100% trước khi kho xuất hàng.
- Đơn hàng công nợ (B2B): Thực hiện kiểm tra hạn mức tín dụng theo Quy chế quản lý công nợ QT-07.
