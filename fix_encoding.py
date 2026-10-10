# -*- coding: utf-8 -*-
import json
import odoo

CUSTOMERS = [
    # Doanh nghiệp
    {"name": "Công ty TNHH Công nghệ Alpha Việt Nam", "is_company": True, "street": "Tầng 5, Tòa Keangnam Landmark 72, Nam Từ Liêm", "city": "Hà Nội", "phone": "02437891234", "email": "contact@alphatech.vn"},
    {"name": "Công ty Cổ phần Thương mại & Dịch vụ Sao Mai", "is_company": True, "street": "Số 45 Lê Duẩn, Quận 1", "city": "TP. Hồ Chí Minh", "phone": "02838221100", "email": "info@saomaicorp.vn"},
    {"name": "Công ty TNHH Giải pháp Phần mềm F-Tech", "is_company": True, "street": "Tòa nhà FPT, Phố Duy Tân, Cầu Giấy", "city": "Hà Nội", "phone": "02473008888", "email": "sales@ftech.vn"},
    {"name": "Công ty CP Đầu tư & Phát triển Bất động sản An Bình", "is_company": True, "street": "120 Nguyễn Thị Minh Khai, Quận 3", "city": "TP. Hồ Chí Minh", "phone": "02839302211", "email": "purchasing@anbinhland.vn"},
    {"name": "Công ty TNHH LogiTech Solution Đà Nẵng", "is_company": True, "street": "Số 15 Quang Trung, Hải Châu", "city": "Đà Nẵng", "phone": "02363889977", "email": "admin@logitechdanang.vn"},
    {"name": "Công ty CP Phân phối Thiết bị Thông minh SmartHome", "is_company": True, "street": "Tòa nhà Landmark 81, Bình Thạnh", "city": "TP. Hồ Chí Minh", "phone": "02839115544", "email": "support@smarthomevn.com"},
    {"name": "Công ty TNHH Thương mại Quốc tế Hòa Phát Tech", "is_company": True, "street": "Số 88 Trần Hưng Đạo, Hoàn Kiếm", "city": "Hà Nội", "phone": "02439426688", "email": "contact@hoaphattech.com"},
    {"name": "Công ty CP Bán lẻ Kỹ thuật số Nam Á", "is_company": True, "street": "64 Võ Văn Tần, Quận 3", "city": "TP. Hồ Chí Minh", "phone": "02838332211", "email": "sales@namadigital.vn"},
    {"name": "Công ty TNHH Dịch vụ Truyền thông & Quảng cáo Sen Vàng", "is_company": True, "street": "10 Mai Chí Thọ, TP. Thủ Đức", "city": "TP. Hồ Chí Minh", "phone": "02837409988", "email": "ketoan@senvangmedia.vn"},
    {"name": "Công ty CP Thiết bị Văn phòng Hiện Đại M-Office", "is_company": True, "street": "Số 204 Hoàng Quốc Việt, Cầu Giấy", "city": "Hà Nội", "phone": "02437554433", "email": "order@moffice.vn"},
    {"name": "Viện Nghiên cứu & Ứng dụng Công nghệ Mới", "is_company": True, "street": "1 Đại Cồ Việt, Hai Bà Trưng", "city": "Hà Nội", "phone": "02438692222", "email": "tech@viennghiencuu.gov.vn"},
    {"name": "Công ty TNHH Chuỗi Cung ứng Toàn Cầu V-Logistics", "is_company": True, "street": "Đường 2A, KCN Biên Hòa 2", "city": "Đồng Nai", "phone": "02513836123", "email": "procurement@vlogistics.vn"},
    {"name": "Công ty CP Xây dựng & Nội thất Vinadesign", "is_company": True, "street": "18 Võ Thị Sáu, Ngô Quyền", "city": "Hải Phòng", "phone": "02253821100", "email": "design@vinadesign.vn"},
    {"name": "Trung tâm Đào tạo Tin học & Ngoại ngữ Tân Tiến", "is_company": True, "street": "254 Nguyễn Văn Linh, Thanh Khê", "city": "Đà Nẵng", "phone": "02363651122", "email": "daotao@tantienedu.vn"},
    {"name": "Công ty TNHH Sản xuất & Thương mại Gia dụng Sunhouse Mart", "is_company": True, "street": "Khu công nghiệp Tiên Sơn", "city": "Bắc Ninh", "phone": "02223714888", "email": "sunhouse@sunhousemart.vn"},
    # Cá nhân
    {"name": "Nguyễn Văn An", "is_company": False, "street": "Số 12 Ngõ 88 Trung Kính, Cầu Giấy", "city": "Hà Nội", "phone": "0912345678", "email": "an.nguyen@gmail.com"},
    {"name": "Trần Thị Minh Tâm", "is_company": False, "street": "15 Lê Lợi, Phường Bến Nghé, Quận 1", "city": "TP. Hồ Chí Minh", "phone": "0988776655", "email": "tam.tran@gmail.com"},
    {"name": "Lê Hoàng Long", "is_company": False, "street": "45 Nguyễn Tri Phương, Hải Châu", "city": "Đà Nẵng", "phone": "0905123456", "email": "long.le@gmail.com"},
    {"name": "Phạm Thị Thu Hương", "is_company": False, "street": "88 Đinh Tiên Hoàng, Hoàn Kiếm", "city": "Hà Nội", "phone": "0934567890", "email": "huong.pham@yahoo.com"},
    {"name": "Vũ Minh Tuấn", "is_company": False, "street": "23 Nguyễn Thị Diệu, Quận 3", "city": "TP. Hồ Chí Minh", "phone": "0971234567", "email": "tuan.vu@outlook.com"},
    {"name": "Đỗ Hoàng Bách", "is_company": False, "street": "76 Lạch Tray, Ngô Quyền", "city": "Hải Phòng", "phone": "0918765432", "email": "bach.do@gmail.com"},
    {"name": "Hoàng Thị Mai", "is_company": False, "street": "30 Nguyễn Văn Cừ, Ninh Kiều", "city": "Cần Thơ", "phone": "0909876543", "email": "mai.hoang@gmail.com"},
    {"name": "Đặng Quốc Việt", "is_company": False, "street": "150 Nguyễn Trãi, Thanh Xuân", "city": "Hà Nội", "phone": "0945678901", "email": "viet.dang@gmail.com"},
    {"name": "Bùi Thúy Kiều", "is_company": False, "street": "55 Phan Đăng Lưu, Phú Nhuận", "city": "TP. Hồ Chí Minh", "phone": "0938112233", "email": "kieu.bui@gmail.com"},
    {"name": "Ngô Tiến Dũng", "is_company": False, "street": "19 Hùng Vương, Nha Trang", "city": "Khánh Hòa", "phone": "0967889900", "email": "dung.ngo@gmail.com"},
]

PRODUCTS = [
    # 1. Thiết bị điện tử & Tin học (30 sản phẩm)
    ("Laptop Dell XPS 13 Plus 9320 (i7-1360P/16GB/512GB)", 34500000, 29000000, "Thiết bị điện tử & Tin học"),
    ("Laptop Dell Latitude 3440 (i5-1335U/8GB/256GB)", 15900000, 13200000, "Thiết bị điện tử & Tin học"),
    ("Laptop Dell Inspiron 15 3520 (i3-1215U/8GB/256GB)", 10500000, 8900000, "Thiết bị điện tử & Tin học"),
    ("Laptop Asus Zenbook 14 OLED UX3405 (Ultra 7/16GB/1TB)", 28900000, 24500000, "Thiết bị điện tử & Tin học"),
    ("Laptop Asus Vivobook 15 X1504ZA (i5-1235U/16GB/512GB)", 14200000, 11900000, "Thiết bị điện tử & Tin học"),
    ("Laptop Lenovo ThinkPad E14 Gen 5 (i5-1335U/16GB/512GB)", 18500000, 15600000, "Thiết bị điện tử & Tin học"),
    ("Laptop Lenovo IdeaPad Slim 3 14IAH8 (i5-12450H/16GB/512GB)", 13900000, 11800000, "Thiết bị điện tử & Tin học"),
    ("Laptop HP ProBook 450 G10 (i5-1335U/16GB/512GB)", 17800000, 15100000, "Thiết bị điện tử & Tin học"),
    ("Laptop HP Victus 15 Gaming (i5-12450H/RTX 2050/16GB)", 17500000, 14900000, "Thiết bị điện tử & Tin học"),
    ("Laptop Acer Swift Go 14 SFG14 OLED (Ultra 5/16GB/512GB)", 21900000, 18500000, "Thiết bị điện tử & Tin học"),
    ("Laptop Apple MacBook Air 13 inch M2 (8GB/256GB)", 24900000, 21500000, "Thiết bị điện tử & Tin học"),
    ("Laptop Apple MacBook Air 15 inch M3 (16GB/512GB)", 37900000, 32800000, "Thiết bị điện tử & Tin học"),
    ("Laptop Apple MacBook Pro 14 inch M3 Pro (18GB/512GB)", 49900000, 43500000, "Thiết bị điện tử & Tin học"),
    ("Màn hình Dell UltraSharp 27 inch 4K U2723QE", 13200000, 11000000, "Thiết bị điện tử & Tin học"),
    ("Màn hình Dell P2422H 23.8 inch FHD IPS", 3990000, 3300000, "Thiết bị điện tử & Tin học"),
    ("Màn hình LG 27UP850N-W 27 inch 4K Type-C", 8900000, 7500000, "Thiết bị điện tử & Tin học"),
    ("Màn hình LG UltraGear 24GN65R 144Hz Gaming", 3450000, 2850000, "Thiết bị điện tử & Tin học"),
    ("Màn hình Asus ProArt PA278CV 27 inch 2K IPS", 8500000, 7200000, "Thiết bị điện tử & Tin học"),
    ("Màn hình Samsung ViewFinity S9 27 inch 5K", 23900000, 20200000, "Thiết bị điện tử & Tin học"),
    ("Màn hình ViewSonic VG2440V Tích hợp Webcam & Mic", 4200000, 3500000, "Thiết bị điện tử & Tin học"),
    ("Máy tính bảng iPad Air 6 M2 11 inch Wi-Fi 128GB", 16900000, 14500000, "Thiết bị điện tử & Tin học"),
    ("Máy tính bảng iPad 10.2 inch Gen 9 64GB", 7490000, 6400000, "Thiết bị điện tử & Tin học"),
    ("Máy tính bảng Samsung Galaxy Tab S9 FE 128GB", 9990000, 8300000, "Thiết bị điện tử & Tin học"),
    ("Máy tính để bàn PC HP Pro SFF 280 G9 (i5-12400/8GB/256GB)", 12500000, 10500000, "Thiết bị điện tử & Tin học"),
    ("Máy tính để bàn PC Dell OptiPlex 7010 Micro (i5-13500T/16GB/512GB)", 16200000, 13800000, "Thiết bị điện tử & Tin học"),
    ("Máy tính Mini PC ASUS NUC 13 Pro (i7-1360P/Barebone)", 14800000, 12600000, "Thiết bị điện tử & Tin học"),
    ("Ổ cứng SSD Samsung 990 Pro 1TB M.2 PCIe 4.0", 2850000, 2350000, "Thiết bị điện tử & Tin học"),
    ("Ổ cứng SSD Kingston NV2 500GB PCIe 4.0", 990000, 790000, "Thiết bị điện tử & Tin học"),
    ("Ổ cứng di động HDD WD My Passport 2TB USB 3.2", 2150000, 1750000, "Thiết bị điện tử & Tin học"),
    ("Ổ cứng di động SSD SanDisk Extreme E61 1TB Chống nước", 2950000, 2450000, "Thiết bị điện tử & Tin học"),

    # 2. Phụ kiện & Âm thanh (25 sản phẩm)
    ("Chuột không dây Logitech MX Master 3S", 2350000, 1950000, "Phụ kiện & Âm thanh"),
    ("Chuột công thái học Logitech Lift Vertical Ergonomic", 1390000, 1150000, "Phụ kiện & Âm thanh"),
    ("Chuột văn phòng không dây Logitech M331 Silent", 340000, 260000, "Phụ kiện & Âm thanh"),
    ("Chuột gaming Razer DeathAdder Essential", 450000, 340000, "Phụ kiện & Âm thanh"),
    ("Bàn phím cơ không dây Keychron K2 Pro QMK/VIA", 2190000, 1790000, "Phụ kiện & Âm thanh"),
    ("Bàn phím cơ FL-Esports OG98 Retro Dual Mode", 2650000, 2200000, "Phụ kiện & Âm thanh"),
    ("Bàn phím không dây Logitech MX Keys Mini", 2150000, 1780000, "Phụ kiện & Âm thanh"),
    ("Bàn phím văn phòng có dây Dell KB216", 190000, 135000, "Phụ kiện & Âm thanh"),
    ("Bộ bàn phím chuột không dây Logitech MK295 Silent", 590000, 460000, "Phụ kiện & Âm thanh"),
    ("Tai nghe chụp tai chống ồn Sony WH-1000XM5", 7990000, 6800000, "Phụ kiện & Âm thanh"),
    ("Tai nghe True Wireless Apple AirPods Pro 2 USB-C", 5690000, 4900000, "Phụ kiện & Âm thanh"),
    ("Tai nghe Sony WF-C500 True Wireless Pin 20h", 1490000, 1150000, "Phụ kiện & Âm thanh"),
    ("Tai nghe chụp tai văn phòng Jabra Evolve2 40 USB-C", 2990000, 2450000, "Phụ kiện & Âm thanh"),
    ("Tai nghe gaming Corsair HS55 Stereo 3.5mm", 990000, 780000, "Phụ kiện & Âm thanh"),
    ("Loa hội nghị trực tuyến Jabra Speak 510 MS", 3450000, 2850000, "Phụ kiện & Âm thanh"),
    ("Loa máy tính Bluetooth Edifier R1700BT 66W", 2490000, 2050000, "Phụ kiện & Âm thanh"),
    ("Loa di động Marshall Emberton II Chống nước IP67", 3990000, 3350000, "Phụ kiện & Âm thanh"),
    ("Webcam Logitech C920 Pro HD 1080p", 1650000, 1350000, "Phụ kiện & Âm thanh"),
    ("Webcam Logitech Brio 4K Ultra HD Ultra Pro", 4290000, 3550000, "Phụ kiện & Âm thanh"),
    ("Hub chuyển đổi Type-C HyperDrive 8-in-1 4K60Hz", 1850000, 1450000, "Phụ kiện & Âm thanh"),
    ("Cáp sạc USB-C to USB-C Anker 543 Dù 140W 1.8m", 280000, 195000, "Phụ kiện & Âm thanh"),
    ("Củ sạc nhanh Anker GaNPrime 65W 3 cổng A2668", 950000, 720000, "Phụ kiện & Âm thanh"),
    ("Pin sạc dự phòng Baseus Blade 100W 20000mAh Siêu mỏng", 1250000, 980000, "Phụ kiện & Âm thanh"),
    ("Giá đỡ laptop nhôm tản nhiệt Rain Design mStand", 1250000, 950000, "Phụ kiện & Âm thanh"),
    ("Đèn treo màn hình bảo vệ mắt Yeelight Screen Light Bar", 990000, 750000, "Phụ kiện & Âm thanh"),

    # 3. Thiết bị mạng & Viễn thông (20 sản phẩm)
    ("Router Wifi 6 TP-Link Archer AX73 AX5400", 2250000, 1850000, "Thiết bị mạng & Viễn thông"),
    ("Router Wifi 6 ASUS RT-AX53U Băng tần kép AX1800", 1150000, 920000, "Thiết bị mạng & Viễn thông"),
    ("Hệ thống Mesh Wifi TP-Link Deco X50 (Bộ 3 thiết bị)", 4890000, 4050000, "Thiết bị mạng & Viễn thông"),
    ("Bộ định tuyến cân bằng tải DrayTek Vigor2927 Dual-WAN", 4650000, 3950000, "Thiết bị mạng & Viễn thông"),
    ("Bộ định tuyến Router Mikrotik RB750Gr3 (hEX)", 1490000, 1220000, "Thiết bị mạng & Viễn thông"),
    ("Bộ phát Wifi chuyên dụng Ruijie Reyee RG-RAP2200(E) AC1300", 1750000, 1420000, "Thiết bị mạng & Viễn thông"),
    ("Switch mạng 8 cổng TP-Link TL-SG108 Gigabit Vỏ kim loại", 590000, 450000, "Thiết bị mạng & Viễn thông"),
    ("Switch mạng PoE 16 cổng D-Link DGS-1016D Gigabit", 1890000, 1550000, "Thiết bị mạng & Viễn thông"),
    ("Switch mạng quản trị Cisco CBS110-24T-EU 24 Port Gigabit", 3950000, 3350000, "Thiết bị mạng & Viễn thông"),
    ("Thiết bị lưu trữ NAS Synology DS224+ 2-Bay", 8990000, 7750000, "Thiết bị mạng & Viễn thông"),
    ("Ổ cứng chuyên dụng NAS WD Red Plus 4TB 5400RPM", 2950000, 2450000, "Thiết bị mạng & Viễn thông"),
    ("Camera IP Dome Hikvision DS-2CD2123G0-I 2MP Chuẩn nén H265+", 1250000, 980000, "Thiết bị mạng & Viễn thông"),
    ("Đầu ghi hình camera IP 8 kênh Hikvision DS-7608NI-Q1", 1650000, 1320000, "Thiết bị mạng & Viễn thông"),
    ("Bộ lưu điện UPS APC Back-UPS 650VA/390W BX650LI-MS", 1390000, 1120000, "Thiết bị mạng & Viễn thông"),
    ("Bộ lưu điện Online Santak C1K 1KVA/800W", 7450000, 6300000, "Thiết bị mạng & Viễn thông"),
    ("Tủ rack mạng 10U-D600 Cửa lưới màu đen", 1650000, 1280000, "Thiết bị mạng & Viễn thông"),
    ("Cuộn dây cáp mạng Cat6 UTP Commscope 305m Thùng", 2650000, 2150000, "Thiết bị mạng & Viễn thông"),
    ("Hạt mạng RJ45 Cat6 Commscope (Hộp 100 hạt)", 450000, 330000, "Thiết bị mạng & Viễn thông"),
    ("Kìm bấm mạng đa năng Dintek RJ45/RJ11", 380000, 280000, "Thiết bị mạng & Viễn thông"),
    ("Bộ kích sóng Wifi 6 TP-Link RE705X AX3000", 1290000, 1020000, "Thiết bị mạng & Viễn thông"),

    # 4. Thiết bị gia dụng thông minh (25 sản phẩm)
    ("Robot hút bụi lau nhà Dreame L20 Ultra Tự giặt giẻ sấy khô", 18900000, 15800000, "Thiết bị gia dụng thông minh"),
    ("Robot hút bụi Ecovacs Deebot T20 OMNI Lực hút 6000Pa", 14500000, 12200000, "Thiết bị gia dụng thông minh"),
    ("Máy lọc không khí Xiaomi Smart Air Purifier 4 Pro", 4890000, 3950000, "Thiết bị gia dụng thông minh"),
    ("Máy lọc không khí Coway AP-1008DH Khử mùi diệt khuẩn", 7990000, 6600000, "Thiết bị gia dụng thông minh"),
    ("Nồi chiên không dầu Philips HD9650/91 dung tích XXL 1.4kg", 5490000, 4500000, "Thiết bị gia dụng thông minh"),
    ("Nồi chiên không dầu Lock&Lock EJF357BLK 5.2L Điện tử", 2150000, 1720000, "Thiết bị gia dụng thông minh"),
    ("Nồi cơm điện tử cao tần Cuckoo CRP-LHTR1010FB 1.8L", 11900000, 10100000, "Thiết bị gia dụng thông minh"),
    ("Máy ép chậm Hurom H400 Thế hệ mới Động cơ êm ái", 10800000, 9200000, "Thiết bị gia dụng thông minh"),
    ("Máy làm sữa hạt đa năng Tefal BL967B66 1300W", 2850000, 2300000, "Thiết bị gia dụng thông minh"),
    ("Máy hút bụi cầm tay Dyson V12 Detect Slim Fluffy", 16900000, 14200000, "Thiết bị gia dụng thông minh"),
    ("Máy sấy tóc siêu tốc Dyson Supersonic HD15 Flyaway", 12500000, 10600000, "Thiết bị gia dụng thông minh"),
    ("Bàn là cây hơi nước đứng Philips GC524/60 1600W", 1990000, 1580000, "Thiết bị gia dụng thông minh"),
    ("Quạt không cánh lọc không khí Xiaomi Mijia Smart Tower Fan", 2450000, 1950000, "Thiết bị gia dụng thông minh"),
    ("Máy rửa bát âm tủ Bosch SMS4ECI26E Serie 4 Inox", 17900000, 15300000, "Thiết bị gia dụng thông minh"),
    ("Bếp từ đôi Bosch PPI82560MS Mặt kính Schott Ceran", 11500000, 9800000, "Thiết bị gia dụng thông minh"),
    ("Ấm siêu tốc giữ nhiệt thông minh Xiaomi Smart Kettle Pro", 890000, 690000, "Thiết bị gia dụng thông minh"),
    ("Máy đo độ ẩm và nhiệt độ thông minh SwitchBot Meter Plus", 450000, 330000, "Thiết bị gia dụng thông minh"),
    ("Khóa cửa thông minh vân tay Kaadas K9 Nhận diện nhanh", 7800000, 6400000, "Thiết bị gia dụng thông minh"),
    ("Máy khử khuẩn đũa dao thìa tia UV Morphy Richards", 1150000, 890000, "Thiết bị gia dụng thông minh"),
    ("Máy tạo độ ẩm phun sương siêu âm Deerma F628S", 490000, 370000, "Thiết bị gia dụng thông minh"),
    ("Bình giữ nhiệt Lock&Lock LHC4131B 450ml Thép 316", 320000, 230000, "Thiết bị gia dụng thông minh"),
    ("Máy làm sạch bằng hơi nước nóng Karcher SC 2 EasyFix", 3650000, 3050000, "Thiết bị gia dụng thông minh"),
    ("Cân sức khỏe điện tử thông minh Xiaomi Mi Body Scale 2", 390000, 280000, "Thiết bị gia dụng thông minh"),
    ("Ổ cắm điện thông minh Tuya Wifi 16A Đo điện năng", 185000, 130000, "Thiết bị gia dụng thông minh"),
    ("Công tắc thông minh cảm ứng Lumi Zigbee 2 nút kính phẳng", 1350000, 1100000, "Thiết bị gia dụng thông minh"),

    # 5. Thiết bị văn phòng & Nội thất (20 sản phẩm)
    ("Ghế công thái học Ergonomic Sihoo M57 Lưới thoáng khí", 3850000, 3150000, "Thiết bị văn phòng & Nội thất"),
    ("Ghế công thái học GTChair Dvary Butterfly Cao cấp", 15500000, 13200000, "Thiết bị văn phòng & Nội thất"),
    ("Ghế văn phòng xoay lưng lưới Hòa Phát GL119", 950000, 750000, "Thiết bị văn phòng & Nội thất"),
    ("Bàn nâng hạ thông minh tự động điều chỉnh độ cao 2 motor", 6900000, 5600000, "Thiết bị văn phòng & Nội thất"),
    ("Bàn làm việc văn phòng chân sắt chữ K 120x60cm", 850000, 620000, "Thiết bị văn phòng & Nội thất"),
    ("Tủ tài liệu văn phòng 2 cánh gỗ công nghiệp MFC Melamine", 1450000, 1100000, "Thiết bị văn phòng & Nội thất"),
    ("Máy in Laser đa năng HP LaserJet MFP M141w (In/Scan/Copy/Wifi)", 3950000, 3350000, "Thiết bị văn phòng & Nội thất"),
    ("Máy in Canon LBP2900 Trắng đen Huyền thoại A4", 4200000, 3600000, "Thiết bị văn phòng & Nội thất"),
    ("Máy in phun màu Epson L3210 Đa năng Hệ thống mực ngoài", 3850000, 3250000, "Thiết bị văn phòng & Nội thất"),
    ("Máy hủy tài liệu Bonsaii 4C16 Hủy vụn bảo mật cao", 1950000, 1550000, "Thiết bị văn phòng & Nội thất"),
    ("Máy chấm công vân tay khuôn mặt Ronald Jack FA210", 3150000, 2550000, "Thiết bị văn phòng & Nội thất"),
    ("Máy đóng sách gáy xoắn lò xo Deli 3870", 1250000, 950000, "Thiết bị văn phòng & Nội thất"),
    ("Máy ép plastic văn phòng khổ A3 DSB SO-GOOD 330S", 1550000, 1200000, "Thiết bị văn phòng & Nội thất"),
    ("Thùng 5 ram giấy in Double A A4 70gsm (500 tờ/ram)", 345000, 275000, "Thiết bị văn phòng & Nội thất"),
    ("Thùng 5 ram giấy in IK Plus A4 80gsm Định lượng chuẩn", 380000, 310000, "Thiết bị văn phòng & Nội thất"),
    ("Bút ký cao cấp Parker IM Black GT Ngòi Mực Dạ Bi", 780000, 580000, "Thiết bị văn phòng & Nội thất"),
    ("Hộp 12 bút bi Pilot G2 ngòi 0.5mm Màu đen", 310000, 230000, "Thiết bị văn phòng & Nội thất"),
    ("Bảng từ trắng văn phòng viết bút lông Hàn Quốc 120x80cm", 680000, 490000, "Thiết bị văn phòng & Nội thất"),
    ("Máy chiếu mini thông minh Wanbo T6 Max Full HD 1080P", 5490000, 4500000, "Thiết bị văn phòng & Nội thất"),
    ("Màn chiếu treo tường điều khiển điện 100 inch Dalite", 1850000, 1450000, "Thiết bị văn phòng & Nội thất"),
]

odoo.tools.config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', 'odoo18'])
registry = odoo.registry('odoo18')

with registry.cursor() as cr:
    # 1. Update Partners (id 45 to 69)
    print("Updating Partners...")
    for idx, c in enumerate(CUSTOMERS):
        pid = 45 + idx
        cr.execute("""
            UPDATE res_partner 
            SET name = %s, street = %s, city = %s 
            WHERE id = %s
        """, (c['name'], c['street'], c['city'], pid))
    
    # 2. Update Products (default_code SP0001 to SP0120)
    print("Updating Products...")
    prod_name_map = {}
    for idx, (pname, price, cost, cat_name) in enumerate(PRODUCTS, start=1):
        code = f"SP{idx:04d}"
        prod_name_map[code] = pname
        name_json = json.dumps({"en_US": pname, "vi_VN": pname}, ensure_ascii=False)
        cr.execute("""
            UPDATE product_template 
            SET name = %s::jsonb 
            WHERE default_code = %s
        """, (name_json, code))

    # 3. Update Sale Order Lines name
    print("Updating Sale Order Lines...")
    cr.execute("""
        SELECT sol.id, pt.default_code 
        FROM sale_order_line sol
        JOIN product_product pp ON sol.product_id = pp.id
        JOIN product_template pt ON pp.product_tmpl_id = pt.id
        WHERE pt.default_code LIKE 'SP%'
    """)
    rows = cr.fetchall()
    for sol_id, code in rows:
        if code in prod_name_map:
            cr.execute("UPDATE sale_order_line SET name = %s WHERE id = %s", (prod_name_map[code], sol_id))

    # 4. Ensure all sale_order user_id = 2 (Mitchell Admin)
    print("Ensuring Mitchell Admin assignment...")
    cr.execute("UPDATE sale_order SET user_id = 2 WHERE user_id IS NULL OR user_id = 1")

    cr.commit()
    print("ALL DATA FIXED WITH PERFECT VIETNAMESE ACCENTS!")
