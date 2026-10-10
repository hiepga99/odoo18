# TỔNG HỢP BỘ DỮ LIỆU & TÀI LIỆU DỰ ÁN (TUẦN 3 - DEADLINE 08/10)

> **Mã nhiệm vụ:** Khảo sát LLM, thu thập dữ liệu (Người phụ trách: Hiệp, Duy, Bình)  
> **Trạng thái:** HOÀN THÀNH 100% VƯỢT CHỈ TIÊU

---

## 1. KHẢO SÁT & ĐỐI CHUẨN LLM (BENCHMARK)
* **File tài liệu:** [`docs/llm_benchmark_report.md`](../docs/llm_benchmark_report.md)
* **Số lượng mô hình so sánh:** **4 mô hình** (Trọng tâm: **Hermes 3 - Nous Research** theo đề xuất của anh Hiệp; kết hợp Qwen-2.5-7B/14B, DeepSeek-V3, Llama-3.3-70B Groq).
* **Kết luận chọn mô hình cho Agent Core (Tuần 4 của Bình):**
  * **Chọn Hermes 3 (8B)** làm mô hình lõi cho Agent Core nhờ cơ chế Native Tool Calling và XML `<tool_call>` đỉnh cao, tỷ lệ gọi đúng tool $\ge 95\%$ (vượt xa KPI $\ge 80\%$).
  * Hỗ trợ chạy 100% FREE qua Ollama (`ollama run hermes3:8b`) dung lượng chỉ ~4.7 GB.

---

## 2. BỘ DỮ LIỆU HÓA ĐƠN ĐIỆN TỬ (INVOICES DATASET)
* **Thư mục:** [`data/invoices/`](invoices/)
* **Số lượng:** **100 file hóa đơn JSON độc lập** (`invoice_001.json` đến `invoice_100.json`) + **1 file tổng hợp** (`all_invoices_dataset.json`).
* **Cấu trúc dữ liệu:**
  * Mã số tra cứu, Ký hiệu mẫu hóa đơn (1C26TBB), Số hóa đơn.
  * Thông tin bên bán & bên mua (Tên, Mã số thuế, Địa chỉ, STK ngân hàng).
  * Chi tiết danh mục hàng hóa (Mã SP từ catalog Odoo, ĐVT, Số lượng, Đơn giá, Thành tiền).
  * Tiền thuế GTGT (8% & 10%), Tổng tiền thanh toán bằng số và bằng chữ.
* **Mục đích sử dụng:** Làm tập dữ liệu huấn luyện và kiểm thử cho module **PaddleOCR 3.7.0** ở Tuần 4 & Tuần 8 (Bình phụ trách).

---

## 3. BỘ TÀI LIỆU QUY TRÌNH NỘI BỘ (RAG KNOWLEDGE BASE)
* **Thư mục:** [`data/company_documents/`](company_documents/)
* **Số lượng:** **20 tài liệu quy trình chuẩn Markdown** (QT-01 đến QT-20).
* **Danh mục tài liệu:**
  1. `QT-01`: Quy trình bán hàng và chốt đơn B2B & B2C
  2. `QT-02`: Chính sách bảo hành sản phẩm & thiết bị (12-24 tháng)
  3. `QT-03`: Quy định đổi trả hàng hóa và hoàn tiền (7 ngày)
  4. `QT-04`: Chính sách chiết khấu thương mại và khuyến mại (3% - 10%)
  5. `QT-05`: Quy trình nhập kho hàng hóa từ Nhà phân phối
  6. `QT-06`: Quy trình xuất kho và điều phối giao hàng (FIFO)
  7. `QT-07`: Quy chế quản lý công nợ khách hàng B2B (15 - 45 ngày)
  8. `QT-08`: Quy trình kiểm kê hàng tồn kho định kỳ tháng/quý
  9. `QT-09`: Quy định quản lý nhà cung cấp và đặt hàng (PO)
  10. `QT-10`: Hướng dẫn xử lý đơn hàng trên Odoo 18 ERP
  11. `QT-11`: Quy trình tiếp nhận và giải quyết khiếu nại (SLA 24h)
  12. `QT-12`: Chính sách vận chuyển và giao nhận toàn quốc
  13. `QT-13`: Quy định xuất hóa đơn điện tử GTGT theo NĐ 123
  14. `QT-14`: Quy trình chăm sóc khách hàng sau bán (CSAT)
  15. `QT-15`: Quy định an toàn và PCCC kho linh kiện điện tử
  16. `QT-16`: Quy chế bảo mật thông tin và phân quyền Odoo ERP
  17. `QT-17`: Hướng dẫn lập báo giá nhanh chuẩn form doanh nghiệp
  18. `QT-18`: Quy trình hủy đơn hàng và xử lý hàng trả về (RMA)
  19. `QT-19`: Chính sách đại lý cấp 1, cấp 2 và cộng tác viên
  20. `QT-20`: Quy trình báo cáo doanh thu và hiệu suất bán hàng
* **Mục đích sử dụng:** Làm Knowledge Base để nạp vào Vector Database (**ChromaDB + bge-m3**) phục vụ tính năng **Hỏi đáp tài liệu nội bộ (RAG)** ở Tuần 6 & Tuần 11.
