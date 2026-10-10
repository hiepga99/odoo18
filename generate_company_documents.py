import os

os.makedirs('data/company_documents', exist_ok=True)

DOCS = [
    {
        "filename": "QT-01-Quy-trinh-ban-hang-va-chot-don.md",
        "title": "QUY TRÌNH BÁN HÀNG VÀ CHỐT ĐƠN B2B & B2C",
        "code": "QT-BH-01",
        "summary": "Quy định các bước tiếp nhận nhu cầu, tư vấn sản phẩm, báo giá và xác nhận đơn hàng bán trên hệ thống ERP.",
        "content": """## I. MỤC ĐÍCH
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
- Đơn hàng công nợ (B2B): Thực hiện kiểm tra hạn mức tín dụng theo Quy chế quản lý công nợ QT-07."""
    },
    {
        "filename": "QT-02-Chinh-sach-bao-hanh-san-pham.md",
        "title": "CHÍNH SÁCH BẢO HÀNH SẢN PHẨM & THIẾT BỊ",
        "code": "CS-BH-02",
        "summary": "Quy định chi tiết điều kiện, thời hạn và quy trình tiếp nhận bảo hành các thiết bị điện tử, gia dụng, thiết bị mạng.",
        "content": """## I. MỤC ĐÍCH
Đảm bảo quyền lợi khách hàng sau mua và tiêu chuẩn hóa quy trình tiếp nhận, xử lý bảo hành cho tất cả các thiết bị phân phối bởi công ty.

## II. THỜI HẠN BẢO HÀNH
1. **Laptop, Máy tính để bàn, Màn hình:** Bảo hành chính hãng 24 tháng theo tiêu chuẩn của nhà sản xuất (Dell, HP, Asus, LG...).
2. **Thiết bị mạng (Router, Switch, Wifi Mesh):** Bảo hành 24 tháng, 1 đổi 1 trong 30 ngày đầu nếu lỗi do nhà sản xuất.
3. **Thiết bị gia dụng thông minh (Robot hút bụi, Máy lọc không khí, Nồi chiên):** Bảo hành 12 tháng.
4. **Phụ kiện (Chuột, bàn phím, tai nghe, sạc cáp):** Bảo hành 12 tháng.

## III. ĐIỀU KIỆN ĐƯỢC BẢO HÀNH
- Sản phẩm còn trong thời hạn bảo hành tính từ ngày xuất hóa đơn GTGT hoặc kích hoạt bảo hành điện tử theo Serial/IMEI.
- Tem bảo hành và số Serial/Barcode còn nguyên vẹn, không có dấu hiệu tẩy xóa, rách nát.
- Lỗi kỹ thuật do nhà sản xuất phát sinh trong quá trình sử dụng bình thường.

## IV. CÁC TRƯỜNG HỢP TỪ CHỐI BẢO HÀNH
- Sản phẩm bị rơi vỡ, móp méo, biến dạng, trầy xước nặng do tác động ngoại lực.
- Sản phẩm bị vào nước, chập cháy nổ do nguồn điện không ổn định hoặc thiên tai, sét đánh.
- Đã bị can thiệp, tự ý tháo dỡ sửa chữa bởi bên thứ ba không được ủy quyền."""
    },
    {
        "filename": "QT-03-Quy-dinh-doi-tra-hang-hoa.md",
        "title": "QUY ĐỊNH ĐỔI TRẢ VÀ HOÀN TIỀN",
        "code": "QD-DT-03",
        "summary": "Quy định điều kiện, thời gian và thủ tục giải quyết đổi trả hàng cho khách hàng cá nhân và doanh nghiệp.",
        "content": """## I. PHẠM VI ÁP DỤNG
Áp dụng cho tất cả các khách hàng mua hàng hóa trực tiếp hoặc trực tuyến từ Công ty.

## II. ĐIỀU KIỆN ĐỔI TRẢ HÀNG
### 1. Đổi mới trong vòng 07 ngày đầu:
- Áp dụng khi sản phẩm gặp lỗi phần cứng do nhà sản xuất đã được bộ phận kỹ thuật xác nhận.
- Đổi mới sản phẩm cùng model hoặc đổi sang model khác có giá trị tương đương/cao hơn (bù chênh lệch).

### 2. Trả hàng hoàn tiền:
- Hàng giao không đúng chủng loại, model, thông số kỹ thuật như trong đơn đặt hàng.
- Hàng hóa bị bể vỡ, móp méo khi vận chuyển và khách hàng từ chối nhận tại thời điểm đồng kiểm.

## III. YÊU CẦU ĐỐI VỚI HÀNG ĐỔI TRẢ
- Còn nguyên hộp (box), xốp bảo vệ, phụ kiện, sách hướng dẫn, quà tặng kèm theo.
- Hàng hóa không có dấu hiệu trầy xước, dơ bẩn, móp méo do người dùng.
- Có đầy đủ hóa đơn mua hàng hoặc số điện thoại mua hàng lưu trên hệ thống Odoo ERP.

## IV. THỜI GIAN VÀ PHƯƠNG THỨC HOÀN TIỀN
- Sau khi kho nhận lại hàng và kiểm tra hợp lệ, phòng Kế toán thực hiện hoàn tiền trong vòng 24 - 48 giờ làm việc qua tài khoản ngân hàng chính chủ của khách."""
    },
    {
        "filename": "QT-04-Chinh-sach-chiet-khau-va-khuyen-mai.md",
        "title": "CHÍNH SÁCH CHIẾT KHẤU THƯƠNG MẠI VÀ KHUYẾN MẠI",
        "code": "CS-CK-04",
        "summary": "Quy định tỷ lệ chiết khấu thương mại theo giá trị đơn hàng, cấp bậc đại lý và chương trình khuyến mại định kỳ.",
        "content": """## I. MỤC ĐÍCH
Tạo động lực mua hàng số lượng lớn, giữ chân khách hàng thân thiết và chuẩn hóa mức phê duyệt giá của nhân viên kinh doanh.

## II. MỨC CHIẾT KHẤU THEO GIÁ TRỊ ĐƠN HÀNG (B2B)
1. **Đơn hàng từ 50.000.000 VNĐ đến dưới 100.000.000 VNĐ:** Chiết khấu trực tiếp 3% trên tổng giá trị trước thuế.
2. **Đơn hàng từ 100.000.000 VNĐ đến dưới 300.000.000 VNĐ:** Chiết khấu 5% trên tổng giá trị trước thuế.
3. **Đơn hàng từ 300.000.000 VNĐ trở lên:** Chiết khấu 7% - 10% (Cần Trưởng phòng kinh doanh hoặc Giám đốc duyệt trên ERP).

## III. CHÍNH SÁCH KHÁCH HÀNG THÂN THIẾT (VIP)
- Khách hàng VIP Bạc (Doanh số tích lũy > 100 triệu/năm): Giảm thêm 1% cho mọi đơn hàng.
- Khách hàng VIP Vàng (Doanh số tích lũy > 500 triệu/năm): Giảm thêm 2% và miễn phí giao hàng toàn quốc.
- Khách hàng Kim Cương (Doanh số tích lũy > 1 tỷ/năm): Giảm thêm 3%, ưu tiên công nợ 45 ngày."""
    },
    {
        "filename": "QT-05-Quy-trinh-nhap-kho-hang-hoa.md",
        "title": "QUY TRÌNH NHẬP KHO HÀNG HÓA",
        "code": "QT-NK-05",
        "summary": "Quy trình kiểm tra số lượng, chất lượng, đối chiếu PO và nhập kho thực tế trên Odoo ERP.",
        "content": """## I. MỤC ĐÍCH
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
- Số lượng tồn kho khả dụng lập tức được cộng dồn vào CSDL."""
    },
    {
        "filename": "QT-06-Quy-trinh-xuat-kho-va-giao-hang.md",
        "title": "QUY TRÌNH XUẤT KHO VÀ ĐIỀU PHỐI GIAO HÀNG",
        "code": "QT-XK-06",
        "summary": "Quy định quy trình soạn hàng, đóng gói, kiểm tra trước xuất kho và bàn giao cho đơn vị vận chuyển.",
        "content": """## I. NGUYÊN TẮC XUẤT KHO
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
- Bấm 'Xác nhận' (Validate) Lệnh giao hàng trên Odoo. Hệ thống tự động trừ kho và cập nhật trạng thái đơn hàng sang 'Đã xuất kho'."""
    },
    {
        "filename": "QT-07-Quy-che-quan-ly-cong-no-khach-hang.md",
        "title": "QUY CHẾ QUẢN LÝ CÔNG NỢ PHẢI THU KHÁCH HÀNG",
        "code": "QC-CN-07",
        "summary": "Quy định điều kiện xét duyệt hạn mức công nợ, thời hạn thanh toán và quy trình thu hồi công nợ quá hạn.",
        "content": """## I. ĐIỀU KIỆN ÁP DỤNG CÔNG NỢ
- Chỉ áp dụng công nợ đối với Khách hàng doanh nghiệp (B2B) đã ký Hợp đồng nguyên tắc và có lịch sử thanh toán tốt tối thiểu 03 đơn hàng trả trước.
- Không áp dụng bán hàng công nợ cho khách hàng cá nhân.

## II. HẠN MỨC VÀ THỜI HẠN TÍN DỤNG
1. **Nhóm A (Khách hàng chiến lược):** Hạn mức nợ tối đa 500.000.000 VNĐ, thời hạn thanh toán 45 ngày kể từ ngày xuất hóa đơn.
2. **Nhóm B (Khách hàng tiêu chuẩn):** Hạn mức nợ tối đa 150.000.000 VNĐ, thời hạn thanh toán 30 ngày.
3. **Nhóm C (Khách hàng mới được cấp nợ):** Hạn mức nợ tối đa 50.000.000 VNĐ, thời hạn thanh toán 15 ngày.

## III. CHẾ TÀI QUÁ HẠN
- Quá hạn từ 1 đến 5 ngày: Kế toán gửi email nhắc nợ tự động từ Odoo.
- Quá hạn trên 7 ngày: Hệ thống Odoo tự động khóa chức năng tạo đơn hàng mới cho khách hàng này.
- Quá hạn trên 30 ngày: Chuyển hồ sơ sang bộ phận pháp chế xử lý tranh chấp."""
    },
    {
        "filename": "QT-08-Quy-trinh-kiem-ke-tai-san-va-hang-ton-kho.md",
        "title": "QUY TRÌNH KIỂM KÊ HÀNG TỒN KHO ĐỊNH KỲ",
        "code": "QT-KK-08",
        "summary": "Quy định trình tự tổ chức kiểm kê hàng hóa định kỳ hàng tháng, quý và xử lý chênh lệch số lượng.",
        "content": """## I. MỤC ĐÍCH
Đảm bảo số liệu tồn kho thực tế khớp 100% với số liệu ghi nhận trên phần mềm Odoo ERP, kịp thời phát hiện thất thoát, hư hỏng.

## II. LỊCH KIỂM KÊ
- **Kiểm kê định kỳ tháng:** Thực hiện vào ngày 28 hàng tháng đối với các nhóm hàng giá trị cao (Laptop, Màn hình, CPU, Robot hút bụi).
- **Kiểm kê toàn diện quý:** Thực hiện vào ngày cuối cùng của mỗi Quý đối với toàn bộ 100% mã hàng trong kho.

## III. XỬ LÝ CHÊNH LỆCH
1. Nếu thực tế nhiều hơn sổ sách (Thừa): Tạo bút toán điều chỉnh tăng tồn kho với lý do cụ thể sau khi đã rà soát phiếu nhập sót.
2. Nếu thực tế ít hơn sổ sách (Thiếu): Lập biên bản quy trách nhiệm. Nếu do lỗi bảo quản, nhân viên chịu trách nhiệm bồi thường theo giá vốn."""
    },
    {
        "filename": "QT-09-Quy-dinh-quan-ly-nha-cung-cap-va-mua-hang.md",
        "title": "QUY ĐỊNH QUẢN LÝ NHÀ CUNG CẤP VÀ MUA HÀNG",
        "code": "QD-NCC-09",
        "summary": "Quy trình lựa chọn, đánh giá chất lượng nhà phân phối và tạo yêu cầu mua hàng trên ERP.",
        "content": """## I. TIÊU CHÍ LỰA CHỌN NHÀ CUNG CẤP
- Là nhà phân phối chính hãng có đầy đủ giấy phép CO/CQ (Chứng nhận xuất xứ, chất lượng).
- Có chính sách giá cạnh tranh, chiết khấu quý/năm rõ ràng.
- Khả năng cung ứng ổn định và cam kết giao hàng trong vòng 24 - 48 giờ.

## II. QUY TRÌNH ĐẶT HÀNG (PURCHASE ORDER)
1. Khi mức tồn kho của một sản phẩm chạm ngưỡng tồn kho an toàn (Min Stock), nhân viên Mua hàng lập Yêu cầu báo giá (RFQ) trên Odoo.
2. So sánh báo giá tối thiểu 2 nhà cung cấp cho cùng một chủng loại.
3. Trình Trưởng phòng duyệt PO và gửi đơn đặt hàng chính thức qua email."""
    },
    {
        "filename": "QT-10-Huong-dan-xu-ly-don-hang-tren-Odoo-ERP.md",
        "title": "HƯỚNG DẪN XỬ LÝ ĐƠN HÀNG TRÊN HỆ THỐNG ODOO ERP",
        "code": "HD-ERP-10",
        "summary": "Tài liệu đào tạo nhân viên cách tạo Báo giá, xác nhận Sales Order, in phiếu xuất kho trên giao diện Odoo 18.",
        "content": """## I. CÁC BƯỚC TẠO ĐƠN HÀNG TRÊN ODOO 18
1. Đăng nhập vào Odoo ➔ Vào phân hệ **Bán hàng (Sales)**.
2. Nhấn nút **Mới (New)** để mở form tạo Báo giá.
3. Chọn **Khách hàng** từ danh sách có sẵn (hoặc tạo mới nhanh).
4. Tại tab **Chi tiết đơn hàng**, nhấn **Thêm sản phẩm**: Chọn mã SP, nhập số lượng, kiểm tra đơn giá tự động nhảy.
5. Nhấn **Xác nhận (Confirm)** để chốt đơn thành Đơn bán hàng.
6. Khi kho giao hàng xong, nhấn nút **Tạo hóa đơn (Create Invoice)** để chuyển dữ liệu sang Kế toán."""
    },
    {
        "filename": "QT-11-Quy-trinh-tiep-nhan-va-giai-quyet-khieu-nai.md",
        "title": "QUY TRÌNH TIẾP NHẬN VÀ GIẢI QUYẾT KHIẾU NẠI KHÁCH HÀNG",
        "code": "QT-KN-11",
        "summary": "Tiêu chuẩn SLA phản hồi khách hàng khi phát sinh sự cố giao chậm, hàng lỗi hoặc sai sót hóa đơn.",
        "content": """## I. MỤC TIÊU DỊCH VỤ (SLA)
- Phản hồi khách hàng lần đầu trong vòng 30 phút kể từ khi nhận phản ánh.
- Giải quyết dứt điểm các khiếu nại thông thường trong vòng 24 giờ.
- Các sự cố phức tạp cần kiểm tra kỹ thuật: Tối đa 48 giờ làm việc.

## II. PHÂN LOẠI KHIẾU NẠI
1. Khiếu nại giao trễ / thiếu phụ kiện: Kho kiểm tra camera đóng gói và gửi bổ sung hỏa tốc trong ngày.
2. Khiếu nại sai thông tin hóa đơn: Kế toán hủy/điều chỉnh hóa đơn điện tử trong vòng 4 giờ."""
    },
    {
        "filename": "QT-12-Chinh-sach-van-chuyen-va-giao-hang-toan-quoc.md",
        "title": "CHÍNH SÁCH VẬN CHUYỂN VÀ GIAO NHẬN TOÀN QUỐC",
        "code": "CS-VC-12",
        "summary": "Biểu phí vận chuyển, chính sách miễn phí ship (Freeship) và thời gian giao hàng các tuyến.",
        "content": """## I. CHÍNH SÁCH MIỄN PHÍ VẬN CHUYỂN (FREESHIP)
- Miễn phí giao hàng hỏa tốc trong nội thành Hà Nội & TP. Hồ Chí Minh cho đơn hàng từ 2.000.000 VNĐ.
- Miễn phí giao hàng tiêu chuẩn toàn quốc cho tất cả đơn hàng từ 5.000.000 VNĐ.

## II. THỜI GIAN GIAO HÀNG TIÊU CHUẨN
- Nội thành: Giao trong vòng 2 - 4 giờ làm việc.
- Các tỉnh thành lân cận: 1 - 2 ngày làm việc.
- Các tỉnh vùng xa / huyện xã: 2 - 4 ngày làm việc."""
    },
    {
        "filename": "QT-13-Quy-dinh-xuat-hoa-don-dien-tu-GTGT.md",
        "title": "QUY ĐỊNH XUẤT HÓA ĐƠN ĐIỆN TỬ GIÁ TRỊ GIA TĂNG (GTGT)",
        "code": "QD-HD-13",
        "summary": "Quy định về thời điểm lập hóa đơn điện tử, thông tin bắt buộc và lưu trữ theo Nghị định 123/2020/NĐ-CP.",
        "content": """## I. NGUYÊN TẮC XUẤT HÓA ĐƠN
1. Mọi giao dịch bán hàng đều phải lập hóa đơn điện tử GTGT hợp pháp, xuất ngay trong ngày chuyển giao quyền sở hữu hàng hóa.
2. Thuế suất GTGT: Áp dụng 8% hoặc 10% theo đúng danh mục hàng hóa thuộc diện giảm thuế của Chính phủ.

## II. KIỂM TRA THÔNG TIN HÓA ĐƠN
- Bắt buộc kiểm tra Mã số thuế bên mua qua cổng thông tin Tổng cục Thuế để đảm bảo doanh nghiệp đang hoạt động bình thường.
- Gửi hóa đơn điện tử (file XML và PDF) qua email chính thức của khách hàng ngay sau khi ký số."""
    },
    {
        "filename": "QT-14-Quy-trinh-cham-soc-khach-hang-sau-ban.md",
        "title": "QUY TRÌNH CHĂM SÓC KHÁCH HÀNG SAU BÁN (POST-SALES)",
        "code": "QT-CSKH-14",
        "summary": "Kịch bản liên hệ khảo sát độ hài lòng (CSAT), hướng dẫn cài đặt và hỗ trợ kỹ thuật sau khi giao hàng.",
        "content": """## I. QUY TRÌNH THỰC HIỆN
- **Ngày 3 sau nhận hàng:** AI Bot hoặc nhân viên CSKH gửi tin nhắn/gọi điện hỏi thăm tình trạng sử dụng sản phẩm.
- **Ngày 30 sau mua hàng:** Gửi email hướng dẫn bảo dưỡng định kỳ (với robot hút bụi, máy lọc không khí) và mã giảm giá 5% cho lần mua tiếp theo.
- **Trước ngày hết hạn bảo hành 30 ngày:** Thông báo nhắc nhở khách hàng bảo dưỡng hoặc gia hạn bảo hành."""
    },
    {
        "filename": "QT-15-Quy-dinh-an-toan-va-phong-chong-chay-no-kho.md",
        "title": "QUY ĐỊNH AN TOÀN LAO ĐỘNG VÀ PHÒNG CHÁY CHỮA CHÁY KHO",
        "code": "QD-PCCC-15",
        "summary": "Các nguyên tắc đảm bảo an toàn kho hàng linh kiện điện tử, pin Lithium và hệ thống điện.",
        "content": """## I. YÊU CẦU BẢO QUẢN THIẾT BỊ ĐIỆN TỬ
- Nhiệt độ kho duy trì từ 20°C - 28°C, độ ẩm không khí dưới 65% để tránh ẩm mốc linh kiện.
- Các sản phẩm chứa pin Lithium (Laptop, Robot hút bụi, Pin dự phòng) phải xếp ở khu vực thông thoáng, cách xa nguồn nhiệt tối thiểu 3m.
- Nghiêm cấm hút thuốc, đun nấu trong phạm vi khuôn viên kho hàng."""
    },
    {
        "filename": "QT-16-Quy-che-bao-mat-thong-tin-va-du-lieu-ERP.md",
        "title": "QUY CHẾ BẢO MẬT THÔNG TIN VÀ AN TOÀN CSDL ERP",
        "code": "QC-BM-16",
        "summary": "Quy định phân quyền người dùng trên Odoo ERP, bảo vệ dữ liệu khách hàng và phòng chống rò rỉ dữ liệu.",
        "content": """## I. PHÂN QUYỀN TRUY CẬP
- Nhân viên Sales: Chỉ được xem danh sách khách hàng và đơn hàng do mình phụ trách.
- Nhân viên Kho: Chỉ có quyền đọc và thao tác trên phiếu nhập/xuất kho.
- Kế toán / Quản trị viên: Có quyền truy cập báo cáo tài chính và toàn bộ CSDL.

## II. BẢO VỆ DỮ LIỆU
- Nghiêm cấm trích xuất (Export) dữ liệu số điện thoại, doanh thu ra file Excel cá nhân nếu không có phê duyệt của Ban Giám đốc.
- Sao lưu CSDL Odoo tự động hàng ngày lúc 01:00 sáng sang máy chủ lưu trữ độc lập."""
    },
    {
        "filename": "QT-17-Huong-dan-lap-bao-gia-nhanh-cho-khach-hang.md",
        "title": "HƯỚNG DẪN LẬP BÁO GIÁ NHANH VÀ CHUẨN FORM DOANH NGHIỆP",
        "code": "HD-BG-17",
        "summary": "Quy định định dạng báo giá chuẩn, thời gian phản hồi và quy tắc làm tròn giá bán.",
        "content": """## I. NGUYÊN TẮC LẬP BÁO GIÁ
1. Mọi báo giá gửi khách phải được xuất trực tiếp từ Odoo ERP dưới định dạng PDF có đầy đủ logo, thông tin công ty và dấu mộc điện tử.
2. Báo giá phải ghi rõ: Tình trạng tồn kho, chính sách bảo hành, thời gian giao hàng và điều khoản thanh toán.
3. Không gửi báo giá viết tay hoặc gõ tin nhắn văn bản sơ sài cho khách hàng doanh nghiệp."""
    },
    {
        "filename": "QT-18-Quy-trinh-huy-don-va-hoan-tien.md",
        "title": "QUY TRÌNH HỦY ĐƠN HÀNG VÀ XỬ LÝ HÀNG TRẢ VỀ (RMA)",
        "code": "QT-HD-18",
        "summary": "Trình tự thao tác hủy đơn trên ERP, hoàn hàng về kho và hạch toán hoàn tiền trên sổ sách.",
        "content": """## I. CÁC TRƯỜNG HỢP HỦY ĐƠN
- Khách hàng hủy trước khi xuất kho: Bấm 'Hủy' (Cancel) trên Odoo Sales Order, tồn kho tự động được giải phóng khỏi trạng thái giữ chỗ (Reserved).
- Khách hàng từ chối nhận khi giao hàng: Shipper mang hàng về kho, thủ kho tạo Phiếu trả hàng (Return Picking) để nhập lại kho chính."""
    },
    {
        "filename": "QT-19-Chinh-sach-dai-ly-va-cong-tac-vien.md",
        "title": "CHÍNH SÁCH ĐẠI LÝ VÀ CỘNG TÁC VIÊN BÁN HÀNG",
        "code": "CS-DL-19",
        "summary": "Điều kiện tham gia mạng lưới đại lý phân phối cấp 1, cấp 2 và mức chiết khấu hoa hồng hàng tháng.",
        "content": """## I. PHÂN CẤP ĐẠI LÝ
- **Đại lý Cấp 1:** Cam kết doanh số tối thiểu 300.000.000 VNĐ/tháng. Hưởng mức giá ưu đãi cấp 1 (chiết khấu 12% - 15% so với giá bán lẻ niêm yết).
- **Đại lý Cấp 2:** Cam kết doanh số tối thiểu 100.000.000 VNĐ/tháng. Hưởng mức chiết khấu 8% - 10%.
- **Cộng tác viên:** Hưởng hoa hồng 3% - 5% trên mỗi đơn hàng thành công, thanh toán vào ngày 10 hàng tháng."""
    },
    {
        "filename": "QT-20-Quy-trinh-bao-cao-doanh-thu-va-hieu-suat-ban-hang.md",
        "title": "QUY TRÌNH BÁO CÁO DOANH THU VÀ HIỆU SUẤT BÁN HÀNG",
        "code": "QT-BC-20",
        "summary": "Quy định kỳ hạn báo cáo, số liệu KPI bán hàng hàng tuần, tháng và đối soát số liệu kế toán.",
        "content": """## I. LỊCH BÁO CÁO ĐỊNH KỲ
- **Báo cáo tuần (Thứ Hai hàng tuần):** Tổng kết doanh số tuần, tỷ lệ chốt đơn, số đơn tồn đọng chưa giao.
- **Báo cáo tháng (Ngày mùng 2 đầu tháng):** Doanh thu thực đạt, công nợ phát sinh, biên lợi nhuận theo từng nhóm ngành hàng và đánh giá KPI nhân viên.

## II. NGUỒN DỮ LIỆU ĐỐI SOÁT
Mọi số liệu báo cáo bắt buộc phải đối soát từ Dashboard và phân hệ Báo cáo (Reporting) của Odoo ERP, không sử dụng số liệu ngoài sổ sách."""
    }
]

for doc in DOCS:
    filepath = os.path.join('data/company_documents', doc['filename'])
    content = f"""# {doc['title']}
> **Mã hiệu:** {doc['code']}  
> **Phiên bản:** 1.0 (Áp dụng từ năm 2026)  
> **Tóm tắt nội dung:** {doc['summary']}  

---

{doc['content']}
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Generated {len(DOCS)} company documents successfully!")
