from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output" / "pdf"
RAG_DIR = PROJECT_ROOT / "data" / "raw" / "coolmate_demo"

FONT_REGULAR = Path(r"C:\Windows\Fonts\arial.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")

ACCESSED_DATE = "09/10/2026"


@dataclass(frozen=True)
class Section:
    heading: str
    paragraphs: tuple[str, ...] = ()
    bullets: tuple[str, ...] = ()


@dataclass(frozen=True)
class DocumentSpec:
    filename: str
    document_id: str
    title: str
    source_title: str
    source_url: str
    summary: str
    sections: tuple[Section, ...]


DOCUMENTS: tuple[DocumentSpec, ...] = (
    DocumentSpec(
        filename="01_coolmate_chinh_sach_doi_tra_tom_tat.pdf",
        document_id="CM-DEMO-RETURN-01",
        title="Chính sách đổi trả - Bản tóm tắt cho RAG",
        source_title="Chính sách đổi trả - Coolmate",
        source_url="https://www.coolmate.me/page/chinh-sach-doi-tra",
        summary=(
            "Tài liệu chuẩn hóa các mốc thời gian, điều kiện, ngoại lệ và quy trình đổi trả "
            "được công khai trên trang Coolmate. Nội dung dùng để thử nghiệm truy vấn tiếng Việt "
            "và trích dẫn nguồn trong hệ thống RAG."
        ),
        sections=(
            Section(
                "1. Phạm vi và thời hạn",
                bullets=(
                    "Khách hàng có thể yêu cầu đổi hoặc trả sản phẩm trong vòng 60 ngày kể từ ngày nhận hàng.",
                    "Chính sách nêu việc hỗ trợ đối với cả sản phẩm đã giặt hoặc đã cắt mác, ngoại trừ các nhóm sản phẩm bị loại trừ.",
                    "Các sản phẩm Outlet, sản phẩm Săn deal, sản phẩm đặt riêng và một số sản phẩm Pre-order giới hạn không thuộc phạm vi áp dụng chung.",
                    "Đơn mua qua sàn thương mại điện tử trước hết áp dụng quy định trả hàng của sàn. Khi đã quá thời hạn của sàn, trang nguồn cho biết chính sách Coolmate có thể được xem xét áp dụng.",
                ),
            ),
            Section(
                "2. Quy trình yêu cầu đổi hoặc trả",
                bullets=(
                    "Bước 1: Khách hàng gửi thông tin yêu cầu qua biểu mẫu đổi trả hoặc liên hệ hotline chăm sóc khách hàng.",
                    "Bước 2: Bộ phận chăm sóc khách hàng xác nhận sản phẩm, yêu cầu và thời gian nhận hàng.",
                    "Bước 3: Sau khi xác nhận, đơn vị bán gửi sản phẩm thay thế hoặc tổ chức nhận lại sản phẩm cần trả.",
                    "Đối với đổi hàng hai chiều, khách hàng có thể nhận sản phẩm mới đồng thời bàn giao sản phẩm đổi cho nhân viên giao nhận.",
                ),
            ),
            Section(
                "3. Hoàn tiền",
                bullets=(
                    "Khoản hoàn được chuyển vào tài khoản ngân hàng do khách hàng cung cấp sau khi yêu cầu được xác nhận.",
                    "Mốc thời gian công khai là tối đa 24 giờ làm việc, không tính thứ Bảy, Chủ nhật và ngày lễ.",
                    "Yêu cầu gửi sau thời điểm tổng hợp trong ngày có thể được chuyển sang ngày làm việc tiếp theo.",
                ),
            ),
            Section(
                "4. Giới hạn và trường hợp cần xác minh",
                bullets=(
                    "Trang chính sách công khai giới hạn số lần đổi và cho phép dừng hỗ trợ nếu phát hiện dấu hiệu lợi dụng chính sách.",
                    "Thông tin công khai hiện có cách diễn đạt khác nhau về phí vận chuyển khi trả hàng: có đoạn mô tả nhận hàng miễn phí, đồng thời có đoạn nêu khoản phí vận chuyển 25.000 đồng được khấu trừ khi hoàn tiền.",
                    "Khi xử lý nghiệp vụ thực tế, nhân viên phải kiểm tra phiên bản chính sách hiện hành và xác nhận với bộ phận chăm sóc khách hàng, không tự suy luận từ bản tóm tắt này.",
                ),
            ),
            Section(
                "5. Gợi ý metadata cho hệ thống",
                bullets=(
                    "Loại tài liệu: chính sách khách hàng.",
                    "Chủ đề: đổi hàng, trả hàng, hoàn tiền, phí vận chuyển, sàn thương mại điện tử.",
                    "Đối tượng sử dụng: chăm sóc khách hàng, bán hàng và khách hàng.",
                ),
            ),
        ),
    ),
    DocumentSpec(
        filename="02_coolmate_faq_giao_hang_va_don_hang_tom_tat.pdf",
        document_id="CM-DEMO-ORDER-02",
        title="FAQ giao hàng và xử lý đơn - Bản tóm tắt cho RAG",
        source_title="FAQs - Câu hỏi thường gặp khi mua sắm tại Coolmate",
        source_url="https://www.coolmate.me/en/page/faqs",
        summary=(
            "Tài liệu chuẩn hóa các câu trả lời công khai liên quan đến thời gian giao hàng, theo dõi đơn, "
            "thay đổi thông tin, đổi hàng hai chiều và hoàn tiền."
        ),
        sections=(
            Section(
                "1. Thời gian giao hàng dự kiến",
                bullets=(
                    "Đơn giao tại nội thành Hà Nội hoặc Thành phố Hồ Chí Minh được mô tả là có thể nhận trong vòng 24 giờ sau khi đơn được xác nhận.",
                    "Nếu kho tại địa phương không đủ hàng và đơn phải chuyển từ kho ở tỉnh khác, thời gian dự kiến là 2 đến 3 ngày.",
                    "Đơn giao đến các tỉnh khác có thời gian dự kiến 2 đến 3 ngày.",
                    "Đơn Pre-order tuân theo lịch giao được công bố riêng cho từng chương trình.",
                    "Các mốc trên là thông tin tham khảo từ FAQ, không phải cam kết tuyệt đối trong mọi tình huống vận chuyển.",
                ),
            ),
            Section(
                "2. Theo dõi và điều chỉnh đơn hàng",
                bullets=(
                    "Khách hàng có thể cung cấp mã đơn hoặc số điện thoại đặt hàng cho kênh chăm sóc khách hàng để nhận mã vận đơn.",
                    "Nếu cần đổi số điện thoại, địa chỉ hoặc hình thức thanh toán, khách hàng cần liên hệ fanpage hoặc hotline để được hỗ trợ trước khi đơn đi quá xa trong quy trình xử lý.",
                    "Với yêu cầu đổi từ thanh toán khi nhận hàng sang thanh toán trước, bộ phận chăm sóc khách hàng cung cấp hướng dẫn và cập nhật trạng thái sau khi xác nhận giao dịch.",
                ),
            ),
            Section(
                "3. Giao hàng và giờ phục vụ",
                bullets=(
                    "FAQ nêu giao hàng chủ yếu trong giờ hành chính; một số khu vực có thể được hỗ trợ giao buổi tối nhưng không được bảo đảm trong mọi trường hợp.",
                    "Các trung tâm vận hành tiếp nhận theo khung giờ được công bố trên trang nguồn và nghỉ Chủ nhật, ngày lễ.",
                    "Khách hàng nên xác nhận lại giờ nhận hàng khi có yêu cầu đặc biệt.",
                ),
            ),
            Section(
                "4. Đổi hàng hai chiều và trả hàng",
                bullets=(
                    "Đổi hàng hai chiều là quy trình giao sản phẩm mới và nhận lại sản phẩm đổi trong cùng lượt giao nhận.",
                    "Khách hàng đổi trực tiếp tại trung tâm vận hành cần báo trước để hàng thay thế được chuẩn bị.",
                    "Sau khi yêu cầu trả hàng được xác nhận, khoản hoàn được xử lý theo chính sách hoàn tiền; việc thu hồi hàng có thể do đơn vị bán đến nhận hoặc do khách tự gửi.",
                ),
            ),
            Section(
                "5. Hủy đơn đã thanh toán trước",
                bullets=(
                    "Khách hàng cần gửi thông tin qua biểu mẫu hoặc liên hệ kênh chăm sóc khách hàng.",
                    "FAQ nêu thời gian hoàn lại tiền trong vòng 24 giờ sau khi nhận đủ thông tin, tùy thời điểm tiếp nhận và ngày làm việc.",
                ),
            ),
        ),
    ),
    DocumentSpec(
        filename="03_coolmate_chinh_sach_bao_mat_du_lieu_tom_tat.pdf",
        document_id="CM-DEMO-PRIVACY-03",
        title="Chính sách bảo mật dữ liệu - Bản tóm tắt cho RAG",
        source_title="Chính sách bảo mật thông tin cá nhân - Coolmate",
        source_url="https://www.coolmate.me/en/page/chinh-sach-bao-mat-thong-tin-ca-nhan",
        summary=(
            "Tài liệu mô tả ngắn gọn loại dữ liệu được thu thập, mục đích sử dụng, chia sẻ, lưu giữ, "
            "bảo vệ và quyền của người dùng theo nội dung công khai trên trang nguồn."
        ),
        sections=(
            Section(
                "1. Phạm vi và dữ liệu có thể được thu thập",
                bullets=(
                    "Chính sách áp dụng cho website, tên miền phụ liên quan và ứng dụng Coolmate.",
                    "Dữ liệu có thể được cung cấp khi người dùng truy cập website, đăng ký tài khoản, đặt hàng, đăng ký nhận tin, tham gia khảo sát hoặc điền biểu mẫu.",
                    "Các trường thông tin được liệt kê gồm họ tên hoặc tên đăng nhập, số điện thoại, email, địa chỉ thanh toán, tuổi và mật khẩu.",
                    "Một số dữ liệu có thể được nhận từ bên thứ ba hoặc từ thông tin người dùng đã công khai trên mạng xã hội.",
                ),
            ),
            Section(
                "2. Mục đích sử dụng",
                bullets=(
                    "Cá nhân hóa trải nghiệm và cải thiện website.",
                    "Xử lý giao dịch, vận hành đơn hàng và hỗ trợ khách hàng.",
                    "Quản lý chương trình khuyến mại, khảo sát hoặc tính năng trên website.",
                    "Gửi thông tin định kỳ khi người dùng đã đồng ý; người nhận có thể sử dụng liên kết hủy đăng ký.",
                ),
            ),
            Section(
                "3. Chia sẻ và xử lý bởi bên thứ ba",
                bullets=(
                    "Dữ liệu có thể được chia sẻ với nhà cung cấp dịch vụ phục vụ lưu trữ, email, thanh toán, chăm sóc khách hàng và vận hành đơn hàng.",
                    "Các đối tác tiếp thị, phân tích, quảng cáo hoặc công ty liên kết có thể tham gia xử lý theo phạm vi được mô tả trong chính sách.",
                    "Thông tin có thể được cung cấp cho cơ quan có thẩm quyền hoặc chuyển giao trong trường hợp tái cấu trúc doanh nghiệp khi có căn cứ phù hợp.",
                ),
            ),
            Section(
                "4. Lưu giữ và bảo vệ dữ liệu",
                bullets=(
                    "Dữ liệu được lưu trong thời gian cần thiết để cung cấp dịch vụ và đáp ứng nghĩa vụ liên quan; khi không còn cần thiết, dữ liệu có thể được xóa hoặc ẩn danh.",
                    "Một phần chính sách nêu thời gian lưu tối đa 6 năm và xóa dữ liệu trong vòng 60 ngày sau khi tài khoản bị xóa, trừ trường hợp cần lưu theo yêu cầu khác.",
                    "Thông tin nhạy cảm được truyền qua kết nối bảo mật và chỉ người được ủy quyền được truy cập.",
                    "Thông tin thẻ không được Coolmate lưu trực tiếp sau giao dịch; dữ liệu thanh toán được xử lý qua đối tác cổng thanh toán.",
                    "Không hệ thống nào được bảo đảm an toàn tuyệt đối; vì vậy người dùng vẫn cần bảo vệ thông tin đăng nhập của mình.",
                ),
            ),
            Section(
                "5. Quyền của người dùng và công nghệ theo dõi",
                bullets=(
                    "Khách hàng có thể yêu cầu cập nhật, chỉnh sửa, hạn chế hoặc xóa dữ liệu sau khi xác minh danh tính.",
                    "Một số bản sao lưu có thể chưa được xóa ngay lập tức.",
                    "Website sử dụng cookie, local storage, session và công nghệ đo lường để ghi nhớ lựa chọn và phân tích hành vi sử dụng.",
                    "Người dùng có thể tắt cookie trong trình duyệt, nhưng một số chức năng có thể hoạt động không đầy đủ.",
                ),
            ),
            Section(
                "6. Sự cố và thay đổi chính sách",
                bullets=(
                    "Trang nguồn mô tả quy trình đánh giá sự cố, thông báo cho cá nhân bị ảnh hưởng và áp dụng biện pháp khắc phục khi xảy ra vi phạm dữ liệu.",
                    "Chính sách có thể được cập nhật khi dịch vụ hoặc yêu cầu pháp lý thay đổi; người dùng nên kiểm tra phiên bản mới nhất trên trang nguồn.",
                ),
            ),
        ),
    ),
    DocumentSpec(
        filename="04_coolmate_dieu_kien_han_che_giao_dich_tom_tat.pdf",
        document_id="CM-DEMO-LIMIT-04",
        title="Điều kiện hạn chế giao dịch - Bản tóm tắt cho RAG",
        source_title="Điều kiện hạn chế - Coolmate",
        source_url="https://www.coolmate.me/page/dieu-kien-han-che",
        summary=(
            "Tài liệu chuẩn hóa các giới hạn về thời gian, địa lý, tồn kho và trường hợp đơn hàng "
            "có thể bị từ chối, tạm dừng hoặc hủy."
        ),
        sections=(
            Section(
                "1. Thời gian cung cấp dịch vụ",
                bullets=(
                    "Website tiếp nhận đơn hàng 24 giờ mỗi ngày, trừ thời gian bảo trì được thông báo.",
                    "Chương trình khuyến mại, đợt mở bán hoặc sản phẩm giới hạn có thể chỉ mở trong khoảng thời gian được công bố riêng.",
                    "Yêu cầu gửi ngoài khung giờ của bộ phận chăm sóc khách hàng được xử lý trong ngày làm việc tiếp theo.",
                ),
            ),
            Section(
                "2. Phạm vi địa lý",
                bullets=(
                    "Hoạt động bán hàng trực tuyến được mô tả là phục vụ trong lãnh thổ Việt Nam, tùy khả năng của đối tác vận chuyển.",
                    "Hải đảo, biên giới, vùng sâu hoặc khu vực chưa có dịch vụ giao nhận có thể nằm ngoài phạm vi phục vụ.",
                    "Một số chương trình hoặc sản phẩm giới hạn có thể chỉ áp dụng tại tỉnh, thành phố được công bố.",
                    "Trang nguồn nêu chưa hỗ trợ giao hàng ra ngoài lãnh thổ Việt Nam tại thời điểm công bố.",
                ),
            ),
            Section(
                "3. Điều kiện đối với khách hàng",
                bullets=(
                    "Người đặt hàng cần có năng lực phù hợp để thực hiện giao dịch; trường hợp chưa đủ năng lực cần có người đại diện hợp pháp.",
                    "Thông tin người nhận, liên hệ và giao hàng phải chính xác, trung thực.",
                    "Đơn có thông tin không chính xác hoặc dấu hiệu gian lận có thể bị từ chối hoặc tạm dừng để xác minh.",
                ),
            ),
            Section(
                "4. Số lượng và tồn kho",
                bullets=(
                    "Khả năng cung cấp phụ thuộc tồn kho thực tế tại thời điểm xử lý đơn.",
                    "Số lượng mua có thể bị giới hạn với hàng khuyến mại, hàng giới hạn hoặc chương trình đặc biệt.",
                    "Nếu phát sinh chênh lệch tồn kho sau khi đặt hàng, bộ phận bán hàng có thể đề xuất sản phẩm thay thế hoặc hủy phần đơn liên quan và hoàn tiền tương ứng.",
                ),
            ),
            Section(
                "5. Trường hợp đơn hàng có thể bị từ chối hoặc hủy",
                bullets=(
                    "Có dấu hiệu gian lận hoặc lợi dụng khuyến mại, đổi trả hay hoàn tiền.",
                    "Địa chỉ nằm ngoài phạm vi giao nhận của đối tác tại thời điểm xử lý.",
                    "Không thể liên hệ khách hàng sau nhiều lần hoặc thông tin đặt hàng không chính xác.",
                    "Có sự cố về giá, dữ liệu tồn kho, tình huống bất khả kháng hoặc yêu cầu của cơ quan có thẩm quyền.",
                ),
            ),
            Section(
                "6. Nguyên tắc sử dụng trong RAG",
                bullets=(
                    "Kết quả truy vấn phải trả về điều kiện áp dụng cùng ngoại lệ liên quan, không chỉ trả lời có hoặc không.",
                    "Khi câu hỏi liên quan đơn hàng cụ thể, agent cần gọi dữ liệu ERP để kiểm tra trạng thái và tồn kho; RAG chỉ cung cấp chính sách nền.",
                    "Nếu nội dung bản tóm tắt khác phiên bản website mới nhất, ưu tiên chính sách chính thức đang được công bố.",
                ),
            ),
        ),
    ),
)


def register_fonts() -> None:
    if not FONT_REGULAR.exists() or not FONT_BOLD.exists():
        raise FileNotFoundError("Không tìm thấy font Arial hỗ trợ tiếng Việt.")
    pdfmetrics.registerFont(TTFont("ArialVN", str(FONT_REGULAR)))
    pdfmetrics.registerFont(TTFont("ArialVN-Bold", str(FONT_BOLD)))


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "eyebrow": ParagraphStyle(
            "Eyebrow",
            parent=base["Normal"],
            fontName="ArialVN-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#0B6E4F"),
            spaceAfter=4 * mm,
            alignment=TA_LEFT,
        ),
        "title": ParagraphStyle(
            "TitleVN",
            parent=base["Title"],
            fontName="ArialVN-Bold",
            fontSize=22,
            leading=27,
            textColor=colors.HexColor("#17324D"),
            alignment=TA_LEFT,
            spaceAfter=5 * mm,
        ),
        "lead": ParagraphStyle(
            "Lead",
            parent=base["BodyText"],
            fontName="ArialVN",
            fontSize=11,
            leading=16,
            textColor=colors.HexColor("#34495E"),
            spaceAfter=6 * mm,
        ),
        "h2": ParagraphStyle(
            "Heading2VN",
            parent=base["Heading2"],
            fontName="ArialVN-Bold",
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#17324D"),
            spaceBefore=3 * mm,
            spaceAfter=2.5 * mm,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "BodyVN",
            parent=base["BodyText"],
            fontName="ArialVN",
            fontSize=9.8,
            leading=14.2,
            textColor=colors.HexColor("#263746"),
            spaceAfter=2.5 * mm,
            alignment=TA_LEFT,
        ),
        "bullet": ParagraphStyle(
            "BulletVN",
            parent=base["BodyText"],
            fontName="ArialVN",
            fontSize=9.8,
            leading=14.2,
            textColor=colors.HexColor("#263746"),
            leftIndent=5 * mm,
            firstLineIndent=-3.5 * mm,
            spaceAfter=2.2 * mm,
            bulletIndent=1 * mm,
        ),
        "meta_label": ParagraphStyle(
            "MetaLabel",
            parent=base["Normal"],
            fontName="ArialVN-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#64748B"),
        ),
        "meta_value": ParagraphStyle(
            "MetaValue",
            parent=base["Normal"],
            fontName="ArialVN",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#263746"),
            wordWrap="CJK",
        ),
        "note": ParagraphStyle(
            "NoteVN",
            parent=base["BodyText"],
            fontName="ArialVN",
            fontSize=8.6,
            leading=12.5,
            textColor=colors.HexColor("#475569"),
        ),
    }


def header_footer(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#D7E3EA"))
    canvas.setLineWidth(0.7)
    canvas.line(18 * mm, height - 13 * mm, width - 18 * mm, height - 13 * mm)
    canvas.setFont("ArialVN-Bold", 7.5)
    canvas.setFillColor(colors.HexColor("#0B6E4F"))
    canvas.drawString(18 * mm, height - 10 * mm, "COOLMATE - DỮ LIỆU DEMO RAG")
    canvas.setFont("ArialVN", 7.5)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawRightString(width - 18 * mm, 10 * mm, f"Trang {doc.page}")
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.restoreState()


def metadata_table(spec: DocumentSpec, st: dict[str, ParagraphStyle]) -> Table:
    rows = [
        [Paragraph("Mã tài liệu", st["meta_label"]), Paragraph(spec.document_id, st["meta_value"])],
        [Paragraph("Phiên bản", st["meta_label"]), Paragraph("1.0 - Bản demo học thuật", st["meta_value"])],
        [Paragraph("Ngày truy cập nguồn", st["meta_label"]), Paragraph(ACCESSED_DATE, st["meta_value"])],
        [Paragraph("Tổ chức tham chiếu", st["meta_label"]), Paragraph("Coolmate / Công ty TNHH FASTECH ASIA", st["meta_value"])],
        [Paragraph("Nguồn", st["meta_label"]), Paragraph(f'<link href="{spec.source_url}" color="#0B6E4F">{spec.source_url}</link>', st["meta_value"])],
    ]
    table = Table(rows, colWidths=[38 * mm, 126 * mm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4F8FA")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D7E3EA")),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#E6EEF2")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2.2 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2 * mm),
            ]
        )
    )
    return table


def section_flowables(section: Section, st: dict[str, ParagraphStyle]) -> Iterable:
    yield Paragraph(section.heading, st["h2"])
    for paragraph in section.paragraphs:
        yield Paragraph(paragraph, st["body"])
    for bullet in section.bullets:
        yield Paragraph(f"• {bullet}", st["bullet"])


def build_pdf(spec: DocumentSpec, st: dict[str, ParagraphStyle]) -> Path:
    target = OUTPUT_DIR / spec.filename
    doc = SimpleDocTemplate(
        str(target),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=19 * mm,
        bottomMargin=19 * mm,
        title=spec.title,
        author="Bộ dữ liệu demo RAG - dự án Odoo AI Agent",
        subject="Bản tóm tắt từ nguồn công khai Coolmate",
    )

    story = [
        Spacer(1, 8 * mm),
        Paragraph("TÀI LIỆU DEMO CHO PIPELINE RAG", st["eyebrow"]),
        Paragraph(spec.title, st["title"]),
        Paragraph(spec.summary, st["lead"]),
        metadata_table(spec, st),
        Spacer(1, 5 * mm),
    ]

    for section in spec.sections:
        story.extend(section_flowables(section, st))

    story.extend(
        [
            Spacer(1, 5 * mm),
            KeepTogether(
                [
                    Paragraph("Lưu ý sử dụng", st["h2"]),
                    Table(
                        [[Paragraph(
                            "Đây là bản tóm tắt và chuẩn hóa do nhóm dự án tạo từ thông tin công khai, "
                            "không phải văn bản chính thức do Coolmate phát hành. Nội dung chỉ dùng cho "
                            "nghiên cứu, demo và đánh giá RAG. Khi áp dụng thực tế phải đối chiếu trang nguồn mới nhất.",
                            st["note"],
                        )]],
                        colWidths=[164 * mm],
                        style=TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF8E6")),
                                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#E8C96A")),
                                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                                ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
                            ]
                        ),
                    ),
                    Spacer(1, 3 * mm),
                    Paragraph(
                        f"Nguồn tham khảo: {spec.source_title}. Truy cập ngày {ACCESSED_DATE}.",
                        st["note"],
                    ),
                ]
            ),
        ]
    )

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return target


def validate_pdf(path: Path) -> tuple[int, int]:
    reader = PdfReader(str(path))
    if len(reader.pages) == 0:
        raise ValueError(f"PDF không có trang: {path}")
    extracted = "\n".join((page.extract_text() or "") for page in reader.pages)
    if len(extracted.strip()) < 500:
        raise ValueError(f"PDF có quá ít nội dung trích xuất được: {path}")
    if "Lưu ý sử dụng" not in extracted or "Nguồn tham khảo" not in extracted:
        raise ValueError(f"PDF thiếu ghi chú nguồn bắt buộc: {path}")
    return len(reader.pages), len(extracted)


def main() -> None:
    register_fonts()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAG_DIR.mkdir(parents=True, exist_ok=True)
    st = styles()

    for spec in DOCUMENTS:
        output_path = build_pdf(spec, st)
        pages, chars = validate_pdf(output_path)
        rag_path = RAG_DIR / spec.filename
        shutil.copy2(output_path, rag_path)
        print(f"CREATED {output_path} | pages={pages} | extracted_chars={chars}")
        print(f"COPIED  {rag_path}")


if __name__ == "__main__":
    main()
