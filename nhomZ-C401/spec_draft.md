# SPEC draft — NhomXX-Room

## Track: Track A - VinFast (AI chatbot hỗ trợ mua xe, phân tích review)

## Problem statement
Khách hàng tìm hiểu mua xe VinFast tốn hàng giờ đồng hồ lướt đọc, xem các video review xe. AI Chatbot sẽ đóng vai trò tư vấn viên ảo.

## Canvas draft

| | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Trả lời** | **Pain:** User mất nhiều thời gian để nghiên cứu, xem review để có được một cái nhìn tổng quan về sản phẩm.<br>**Value:** Trích xuất nhanh ưu/nhược điểm thực tế của xe từ database và đưa ra góc nhìn tổng quan. | **Rủi ro:** AI bịa thông số (hallucinate) hoặc đưa sai giá xe.<br>**Giải pháp:** Mọi câu trả lời phải trích nguồn (vd: "Theo review trên Otofun..."). | **Tech:** Dùng RAG pipeline truy xuất data review đã làm sạch. API cost rẻ.<br>**Risk:** Cần crawl/làm sạch đủ lượng review thực tế, tránh data seeding ảo. |

**Auto hay Aug?** Augmentation (Tăng cường) — AI đóng vai trò gợi ý dựa trên nhu cầu và cung cấp thông tin ban đầu minh bạch. Quyết định mua và chốt sale vẫn do con người (khách hàng + tư vấn viên).

**Learning signal:** Tỷ lệ khách hàng nhấn "Hữu ích" (Thumbs up) sau câu trả lời, và tỷ lệ khách hàng hỏi số hotline của showroom, hoặc đồng ý đề xuất nhận số hotline. Nếu khách bấm "Không đúng trọng tâm" (Thumbs down), AI lưu log lại để chỉnh prompt.

## Hướng đi chính
- **Prototype:** Một giao diện chatbot đơn giản tích hợp luồng RAG, nạp sẵn bộ dữ liệu: Thông số kỹ thuật xe VinFast (VF3, VF5, VF8...).
- **Eval metrics:** Precision của việc trích xuất review ≥ 85% (không ghép râu ông nọ cắm cằm bà kia). Tỷ lệ Hallucination = 0% đối với **giá cả** và **tính năng an toàn**.
- **Main failure mode:** Khách hàng hỏi mỉa mai, dùng từ lóng, hoặc AI đọc nhầm data review của xe hãng đối thủ thành xe VinFast.

## Phân công nhóm
- **Tùng:** Phát triển Prototype (Xây dựng luồng RAG, thiết kế prompt, xử lý logic truy xuất dữ liệu).
- **Thưởng:** Lên chi tiết User Stories theo 4 paths (Đúng/Sai/Không chắc/Sửa) và phân tích các Failure modes.
- **Sĩ:** Xây dựng chi tiết bảng Canvas & Phụ trách thu thập, làm sạch bộ dữ liệu review xe.
- **Tuấn:** Xây dựng bộ Eval metrics, tính toán ROI và chuẩn bị nội dung trình bày cho Demo Day.
