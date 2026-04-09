# SPEC — AI Product Hackathon

**Nhóm:** Bàn Z-C401
**Track:** VinFast
**Problem statement (1 câu):** Khách hàng muốn mua xe VinFast phải mất nhiều giờ đọc review rời rạc và dễ nhiễu, trong khi AI chatbot có thể tổng hợp ưu/nhược điểm theo nhu cầu cá nhân, dẫn nguồn minh bạch và rút ngắn thời gian ra quyết định.

---

## 1. AI Product Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi** | User nào? Pain gì? AI giải gì? | Khi AI sai thì sao? User sửa bằng cách nào? | Cost/latency bao nhiêu? Risk chính? |
| **Trả lời** | **User:** người đang cân nhắc mua xe VinFast lần đầu hoặc đổi xe.<br>**Pain:** mất 2-5 giờ để đọc review phân tán, thông tin mâu thuẫn, khó so sánh theo nhu cầu thực tế (đi phố, gia đình, ngân sách).<br>**AI giải:** chatbot tóm tắt ưu/nhược điểm theo từng model (VF3, VF5, VF8...), trả lời theo use-case và gợi ý shortlist. | **Rủi ro chính:** AI bịa thông số, nhầm giá, hoặc trích sai nguồn.<br>**Kiểm soát:** chỉ trả lời từ dữ liệu đã index; bắt buộc hiển thị nguồn/citation cho claim quan trọng (giá, pin, an toàn).<br>**Khi sai:** user bấm “Sai/Thiếu nguồn”, chọn loại lỗi, nhập sửa nhanh; hệ thống ghi correction log để cập nhật prompt + dữ liệu. | **Tech:** RAG pipeline (retriever + re-ranker + grounded generation), dataset review đã làm sạch theo model.<br>**Latency mục tiêu:** P95 < 4 giây/câu trả lời.<br>**Cost mục tiêu:** <= $0.02/câu hỏi.<br>**Risk:** dữ liệu review lỗi thời, thiên lệch nguồn, thiếu coverage theo phiên bản xe. |

**Automation hay augmentation?** Augmentation
Justify: AI đóng vai trò tư vấn ban đầu và tổng hợp thông tin minh bạch; quyết định mua, lái thử, và chốt sale vẫn do khách hàng và tư vấn viên.

**Learning signal:**

1. User correction đi vào đâu? Correction log trong analytics (loại lỗi, câu hỏi, câu trả lời, nguồn, model xe) -> queue re-label và cập nhật index định kỳ.
2. Product thu signal gì để biết tốt lên hay tệ đi? Tỷ lệ “Hữu ích”, tỷ lệ “Sai/Thiếu nguồn”, tỷ lệ người dùng tiếp tục hỏi sâu (>=3 câu/session), tỷ lệ click/đồng ý nhận hotline showroom.
3. Data thuộc loại nào? Domain-specific, Human-judgment, Real-time (một phần về giá/chương trình), User-specific (mức nhẹ qua intent/session).
	Có marginal value không? Có. Dữ liệu review tiếng Việt theo ngữ cảnh sử dụng thực tế và correction nội bộ là tín hiệu mà model nền chưa nắm đủ và thay đổi theo thời gian.

---

## 2. User Stories — 4 paths

### Feature: Tư vấn chọn xe theo nhu cầu

**Trigger:** User nhập nhu cầu (ngân sách, số chỗ, quãng đường/ngày, ưu tiên tiết kiệm hay tiện nghi) -> AI đề xuất 1-2 model phù hợp, kèm lý do và nguồn.

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | AI đề xuất “VF5 phù hợp đi phố 30-50km/ngày trong tầm ngân sách X”, nêu 3 lý do, dẫn nguồn rõ; user bấm “Hữu ích” và xem thêm so sánh chi tiết. |
| Low-confidence — AI không chắc | System báo “không chắc” bằng cách nào? User quyết thế nào? | Khi nguồn mâu thuẫn hoặc thiếu dữ liệu, AI hiển thị nhãn “Độ chắc chắn thấp”, đưa 2 phương án + câu hỏi làm rõ (ưu tiên cốp, số người đi, sạc tại nhà). |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | AI gợi ý model không khớp ngân sách; user nhận ra sai và bấm “Sai”, hệ thống xin lỗi, hỏi lại ràng buộc bắt buộc, trả lời lại với bộ lọc chặt hơn. |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | User sửa giá trần/ngân sách hoặc tiêu chí và chọn “Lưu phản hồi”; phản hồi lưu vào correction log để cải thiện intent parsing và ranking. |

### Feature: Hỏi đáp thông số và review có dẫn nguồn

**Trigger:** User hỏi thông số/giá/đánh giá thực tế của model cụ thể -> AI trả lời dạng ngắn gọn + citation.

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | AI trả lời đúng thông tin, trích 2-3 nguồn liên quan, user tiếp tục hỏi sâu về chi phí sử dụng hoặc đặt lịch tư vấn. |
| Low-confidence — AI không chắc | System báo “không chắc” bằng cách nào? User quyết thế nào? | Nếu thiếu nguồn đáng tin hoặc dữ liệu cũ, AI không khẳng định tuyệt đối; hiển thị cảnh báo “Cần xác minh tại showroom” và đề xuất hotline gần nhất. |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | AI trả giá không khớp phiên bản; user bấm “Thiếu chính xác”, chọn “Sai giá”; hệ thống buộc re-query chỉ từ nguồn giá mới nhất trước khi trả lời lại. |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | User gửi mức giá cập nhật hoặc nguồn mới; dữ liệu vào hàng chờ kiểm duyệt trước khi cập nhật knowledge base để tránh nhiễu. |

---

## 3. Eval metrics + threshold

**Optimize precision hay recall?** Precision
Tại sao? Bài toán tư vấn mua xe ưu tiên “đúng và đáng tin” hơn “bao phủ mọi ý”; sai thông tin về giá/an toàn làm mất niềm tin ngay.
Nếu sai ngược lại thì chuyện gì xảy ra? Nếu thiên về recall, chatbot có thể trả lời dài nhưng chứa claim không chắc chắn, làm tăng tỷ lệ sai và giảm chuyển đổi sang bước tư vấn thật.

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| Precision của factual claims có citation | >= 90% | < 80% trong 1 tuần |
| Hallucination rate cho giá và tính năng an toàn | = 0% | > 1 trường hợp xác nhận sai/ngày |
| Citation coverage cho câu trả lời có thông tin định lượng | >= 95% | < 85% trong 3 ngày liên tiếp |
| Tỷ lệ phản hồi “Hữu ích” | >= 70% | < 50% trong 2 tuần |
| P95 latency | < 4 giây | > 6 giây trong giờ cao điểm 3 ngày liên tiếp |

---

## 4. Top 3 failure modes

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | Query mơ hồ hoặc dùng từ lóng/châm biếm, intent parser hiểu sai | AI tư vấn sai nhu cầu nhưng vẫn tự tin | Thêm bước clarifying question bắt buộc khi intent confidence thấp; tách intent “hỏi vui” và “hỏi mua thật” |
| 2 | Dữ liệu giá/chương trình ưu đãi bị cũ hoặc không theo phiên bản | User nhận thông tin giá sai, mất niềm tin | Gắn TTL cho dữ liệu giá; ưu tiên nguồn mới nhất; nếu dữ liệu quá hạn thì trả về trạng thái “cần xác minh” |
| 3 | Retriever kéo nhầm review xe hãng khác hoặc model gần tên | AI trích sai nguồn, recommendation lệch | Áp bộ lọc brand/model cứng trước khi sinh; kiểm tra consistency giữa câu trả lời và metadata nguồn |

Failure nguy hiểm nhất: trường hợp AI trả lời “đúng cú pháp nhưng sai thực tế” với độ tự tin cao và user không phát hiện ngay (silent failure).

---

## 5. ROI 3 kịch bản

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | 120 user/ngày, 55% thấy hữu ích, 3% để lại lead | 400 user/ngày, 70% thấy hữu ích, 6% để lại lead | 1200 user/ngày, 80% thấy hữu ích, 9% để lại lead |
| **Cost** | $45/ngày (LLM + embedding + hạ tầng) | $140/ngày | $360/ngày |
| **Benefit** | Tiết kiệm 3 giờ tư vấn viên/ngày + 3.6 lead/ngày | Tiết kiệm 10 giờ/ngày + 24 lead/ngày | Tiết kiệm 28 giờ/ngày + 108 lead/ngày |
| **Net** | Dương nhẹ nếu 1 lead tạo giá trị >= $15 | Dương rõ rệt, hoàn vốn vận hành theo ngày | Dương mạnh, có thể mở rộng đa kênh (web, app, showroom kiosk) |

**Kill criteria:** Dừng/pivot nếu trong 8 tuần liên tiếp có 1 trong các điều kiện: (1) Helpful rate < 50%, (2) Hallucination giá/an toàn không đưa về 0%, hoặc (3) chi phí vận hành > lợi ích định lượng trong 2 tháng liên tục.

---

## 6. Mini AI spec (1 trang)

Sản phẩm là chatbot tư vấn mua xe VinFast cho giai đoạn “research trước mua”, giúp người dùng giảm thời gian đọc review phân tán và ra quyết định nhanh hơn. Đối tượng chính là khách hàng phổ thông đang cân nhắc giữa các dòng VF3/VF5/VF8 theo ngân sách và nhu cầu sử dụng thực tế. Chatbot hoạt động theo hướng augmentation: AI tổng hợp và gợi ý, còn quyết định cuối cùng vẫn thuộc về người dùng và tư vấn viên showroom.

Về kỹ thuật, hệ thống dùng RAG để đảm bảo grounded answers từ knowledge base review đã làm sạch theo model xe, kèm cơ chế citation bắt buộc cho claim quan trọng. Chất lượng ưu tiên precision vì domain mua xe nhạy cảm với sai lệch thông tin, đặc biệt là giá và tính năng an toàn. Mục tiêu chất lượng gồm precision factual claims >= 90%, citation coverage >= 95%, latency P95 < 4 giây và hallucination bằng 0 cho trường thông tin nhạy cảm.

Rủi ro lớn nhất là silent failure: câu trả lời nghe hợp lý nhưng sai thực tế. Để giảm rủi ro, hệ thống áp dụng kiểm soát theo nhiều lớp: lọc brand/model trước retrieval, cờ low-confidence khi thiếu dữ liệu, TTL cho dữ liệu giá, và fallback sang “cần xác minh tại showroom” khi không đủ bằng chứng.

Data flywheel được thiết kế ngay từ đầu: mọi tín hiệu “Hữu ích/Sai”, loại lỗi, và chỉnh sửa của người dùng được ghi vào correction log để cải thiện parser, ranking và dữ liệu nền theo vòng lặp tuần. Thành công kinh doanh được đo bằng tỷ lệ người dùng hữu ích, tỷ lệ để lại lead, và số giờ tư vấn viên tiết kiệm được mỗi ngày.
