# QUY TRÌNH NHẬP KHO HÀNG HÓA
> **Mã hiệu:** QT-NK-05  
> **Phiên bản:** 1.0 (Áp dụng từ năm 2026)  
> **Tóm tắt nội dung:** Quy trình kiểm tra số lượng, chất lượng, đối chiếu PO và nhập kho thực tế trên Odoo ERP.  

---

## I. MỤC ĐÍCH
Kiểm soát chặt chẽ số lượng, phẩm chất hàng hóa nhập từ các Nhà phân phối (Synnex FPT, Digiworld, Viễn Sơn...) vào kho công ty.

## II. CÁC BƯỚC THỰC HIỆN
### Bước 1: Tiếp nhận hàng và chứng từ
- Thủ kho tiếp nhận biên bản giao hàng, phiếu xuất kho của nhà cung cấp và đối chiếu với Đơn mua hàng (PO) trên Odoo.
- Kiểm tra tính nguyên vẹn của kiện hàng (niêm phong, thùng carton, tem vỡ).

### Bước 2: Kiểm đếm số lượng và quy cách
- Mở thùng kiểm đếm 100% số lượng thực tế so với phiếu giao hàng.
- Quét mã vạch (Barcode/Serial) để ghi nhận chi tiết số serial của từng sản phẩm có giá trị cao.

### Bước 3: Xác nhận Phiếu nhập kho (Receipt) trên Odoo ERP
- Thủ kho mở Phiếu nhập kho (Receipt `WH/IN/...`) tương ứng trên Odoo.
- Nhập số lượng thực nhận. Nếu đủ, nhấn nút 'Xác nhận' (Validate).
- Số lượng tồn kho khả dụng lập tức được cộng dồn vào CSDL.
