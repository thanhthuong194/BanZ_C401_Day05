# SPEC — AI Product Hackathon

**Nhóm:** Bàn Z-C401  
**Track:** VinFast  
**Problem statement (1 câu):** Khách hàng muốn mua xe VinFast thường mất nhiều giờ đọc review rời rạc và khó kiểm chứng; chatbot AI giúp tổng hợp thông tin theo nhu cầu cá nhân, có dẫn nguồn rõ ràng, để rút ngắn thời gian ra quyết định.

---

## 1. AI Product Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi** | User nào? Pain gì? AI giải gì? | Khi AI sai thì sao? User sửa bằng cách nào? | Cost/latency bao nhiêu? Risk chính? |
| **Trả lời** | **Người dùng:** người đang cân nhắc mua xe VinFast lần đầu hoặc đổi xe.  <br>**Nỗi đau:** mất khoảng 2-5 giờ để đọc nhiều nguồn, thông tin hay mâu thuẫn, khó so sánh theo nhu cầu thực tế (đi phố, gia đình, ngân sách).  <br>**Giá trị AI:** tóm tắt ưu/nhược điểm theo từng mẫu xe (VF3, VF5, VF8...), gợi ý xe phù hợp và nêu lý do dễ hiểu. | **Rủi ro chính:** AI nêu sai thông số, sai giá, hoặc trích sai nguồn.  <br>**Cách giảm rủi ro:** chỉ trả lời dựa trên dữ liệu đã lập chỉ mục; bắt buộc hiển thị nguồn cho các thông tin quan trọng (giá, pin, an toàn).  <br>**Khi AI sai:** người dùng bấm “Sai/Thiếu nguồn”, chọn loại lỗi và gửi chỉnh sửa ngắn; hệ thống ghi log để cải thiện dữ liệu và prompt. | **Kỹ thuật:** RAG (truy xuất tài liệu rồi mới sinh câu trả lời), có bước xếp hạng lại kết quả truy xuất.  <br>**Mục tiêu tốc độ:** P95 < 4 giây/câu trả lời.  <br>**Mục tiêu chi phí:** <= $0.02/câu hỏi.  <br>**Rủi ro vận hành:** dữ liệu cũ, thiên lệch nguồn, thiếu dữ liệu cho phiên bản xe mới. |

**Automation hay augmentation?** Augmentation  
Justify: AI hỗ trợ tư vấn ban đầu; quyết định mua, lái thử và chốt sale vẫn do khách hàng và tư vấn viên showroom.

**Learning signal:**

1. Dữ liệu chỉnh sửa của người dùng đi vào đâu? Vào bảng correction log (loại lỗi, câu hỏi, câu trả lời, nguồn, mẫu xe), sau đó vào hàng chờ để rà soát và cập nhật dữ liệu định kỳ.
2. Sản phẩm đo gì để biết đang tốt lên hay tệ đi? Tỷ lệ “Hữu ích”, tỷ lệ “Sai/Thiếu nguồn”, tỷ lệ người dùng hỏi sâu (>= 3 câu/phiên), và tỷ lệ đồng ý để lại thông tin liên hệ.
3. Dữ liệu thuộc loại nào? Domain-specific, Human-judgment, Real-time (một phần cho giá/khuyến mãi), User-specific (mức nhẹ theo ngữ cảnh phiên chat).  
   Có marginal value không? Có. Dữ liệu review tiếng Việt theo ngữ cảnh sử dụng thật và dữ liệu correction nội bộ có giá trị tăng dần theo thời gian.

---

## 2. User Stories — 4 paths

### Feature: Tư vấn chọn xe theo nhu cầu

**Trigger:** Người dùng nhập nhu cầu (ngân sách, số chỗ, quãng đường/ngày, ưu tiên tiết kiệm hay tiện nghi) -> AI đề xuất 1-2 mẫu xe phù hợp, kèm lý do và nguồn.

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | Người dùng thấy gì? Kết thúc ra sao? | AI gợi ý “VF5 phù hợp đi phố 30-50 km/ngày trong ngân sách X”, nêu 3 lý do, có nguồn rõ ràng; người dùng bấm “Hữu ích” và chuyển sang bước so sánh chi tiết. |
| Low-confidence — AI không chắc | Hệ thống báo “không chắc” thế nào? | Khi dữ liệu thiếu hoặc mâu thuẫn, AI hiển thị “Độ chắc chắn thấp”, đưa 2 phương án và hỏi thêm 1-2 câu để làm rõ nhu cầu. |
| Failure — AI sai | Người dùng phát hiện sai bằng cách nào? | AI gợi ý xe vượt ngân sách; người dùng bấm “Sai”; hệ thống xin lỗi, hỏi lại điều kiện bắt buộc, rồi trả lời lại bằng bộ lọc chặt hơn. |
| Correction — người dùng sửa | Người dùng sửa bằng cách nào? Dữ liệu đi đâu? | Người dùng chỉnh lại ngân sách/tiêu chí và bấm “Lưu phản hồi”; dữ liệu vào correction log để cải thiện bước hiểu nhu cầu và xếp hạng kết quả. |

### Feature: Hỏi đáp thông số và review có dẫn nguồn

**Trigger:** Người dùng hỏi về thông số, giá, hoặc trải nghiệm thực tế của một mẫu xe cụ thể -> AI trả lời ngắn gọn, có dẫn nguồn.

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | Người dùng thấy gì? Kết thúc ra sao? | AI trả lời đúng trọng tâm, kèm 2-3 nguồn liên quan; người dùng tiếp tục hỏi sâu hoặc bấm để nhận tư vấn từ showroom. |
| Low-confidence — AI không chắc | Hệ thống báo “không chắc” thế nào? | Nếu dữ liệu cũ hoặc thiếu nguồn tin cậy, AI không khẳng định chắc chắn; hiển thị cảnh báo “Cần xác minh tại showroom”. |
| Failure — AI sai | Người dùng phát hiện sai bằng cách nào? | AI nêu sai giá theo phiên bản; người dùng bấm “Thiếu chính xác” và chọn “Sai giá”; hệ thống buộc truy xuất lại từ nguồn giá mới nhất trước khi trả lời lại. |
| Correction — người dùng sửa | Người dùng sửa bằng cách nào? Dữ liệu đi đâu? | Người dùng gửi thông tin bổ sung; dữ liệu vào hàng chờ kiểm duyệt trước khi cập nhật kho tri thức để tránh nhiễu. |

---

## 3. Eval metrics + threshold

**Optimize precision hay recall?** Precision  
Tại sao? Bài toán tư vấn mua xe cần độ đúng cao; sai thông tin giá/an toàn làm mất niềm tin ngay từ lần đầu.  
Nếu chọn sai hướng thì sao? Nếu thiên về recall quá mức, chatbot có thể trả lời dài nhưng kém chắc chắn, làm tăng lỗi và giảm ý định để lại thông tin liên hệ.

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| Độ chính xác của thông tin có dẫn nguồn | >= 90% | < 80% trong 1 tuần |
| Tỷ lệ bịa thông tin ở nhóm giá/an toàn | = 0% | > 1 lỗi xác nhận sai/ngày |
| Tỷ lệ câu trả lời có dẫn nguồn khi có số liệu | >= 95% | < 85% trong 3 ngày liên tiếp |
| Tỷ lệ người dùng bấm “Hữu ích” | >= 70% | < 50% trong 2 tuần |
| P95 latency | < 4 giây | > 6 giây trong giờ cao điểm, 3 ngày liên tiếp |
| Tỷ lệ để lại thông tin liên hệ hợp lệ | >= 5% | < 2% trong 4 tuần |

---

## 4. Top 3 failure modes

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | Câu hỏi mơ hồ, có từ lóng/châm biếm, hệ thống hiểu sai ý định | Tư vấn sai nhu cầu nhưng trả lời rất tự tin | Bắt buộc hỏi làm rõ khi độ chắc chắn hiểu ý định thấp |
| 2 | Dữ liệu giá/khuyến mãi bị cũ hoặc lẫn phiên bản | Người dùng nhận sai thông tin giá, mất niềm tin | Đặt thời hạn hiệu lực dữ liệu giá; nếu quá hạn thì hiển thị “Cần xác minh” |
| 3 | Truy xuất nhầm nguồn (khác hãng hoặc nhầm mẫu xe gần tên) | AI trích sai nguồn và đề xuất sai | Lọc cứng theo hãng/mẫu xe trước khi sinh câu trả lời; kiểm tra chéo nội dung và metadata nguồn |

**Failure nguy hiểm nhất:** AI trả lời nghe hợp lý nhưng sai thực tế, và người dùng không phát hiện ngay.

---

## 5. ROI 3 kịch bản

**Định nghĩa chung:** “Thông tin liên hệ hợp lệ” là có ít nhất số điện thoại hoặc email + nhu cầu mua xe cơ bản để đội tư vấn có thể liên hệ lại.

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | 120 người dùng/ngày, 55% thấy hữu ích, 3% để lại thông tin liên hệ hợp lệ | 400 người dùng/ngày, 70% thấy hữu ích, 6% để lại thông tin liên hệ hợp lệ | 1200 người dùng/ngày, 80% thấy hữu ích, 9% để lại thông tin liên hệ hợp lệ |
| **Cost** | $45/ngày (LLM + embedding + hạ tầng) | $140/ngày | $360/ngày |
| **Benefit** | Tiết kiệm 3 giờ tư vấn viên/ngày + 3.6 khách để lại thông tin liên hệ hợp lệ/ngày | Tiết kiệm 10 giờ/ngày + 24 khách để lại thông tin liên hệ hợp lệ/ngày | Tiết kiệm 28 giờ/ngày + 108 khách để lại thông tin liên hệ hợp lệ/ngày |
| **Net** | Dương nhẹ nếu mỗi khách để lại thông tin hợp lệ tạo giá trị >= $15 | Dương rõ rệt, có thể hoàn vốn vận hành theo ngày | Dương mạnh, phù hợp mở rộng đa kênh (web, app, kiosk showroom) |

**Kill criteria:** Dừng hoặc đổi hướng nếu trong 8 tuần liên tiếp có một trong các điều kiện: (1) tỷ lệ “Hữu ích” < 50%, (2) chưa đưa lỗi sai giá/an toàn về 0, hoặc (3) chi phí vận hành lớn hơn lợi ích định lượng trong 2 tháng liên tục.

---

## 6. Mini AI spec (1 trang)

Chatbot này tập trung vào giai đoạn người dùng đang tìm hiểu trước khi mua xe VinFast. Mục tiêu chính là giúp người dùng bớt mất thời gian đọc review rời rạc, có cái nhìn nhanh nhưng vẫn đáng tin, và đi đến quyết định tiếp theo như so sánh xe, đăng ký lái thử, hoặc để lại thông tin liên hệ để showroom tư vấn.

Hệ thống dùng RAG: trước tiên truy xuất dữ liệu liên quan, sau đó mới tạo câu trả lời. Với các thông tin nhạy cảm như giá và an toàn, chatbot chỉ trả lời khi có nguồn rõ ràng. Nếu dữ liệu chưa chắc chắn, chatbot phải báo mức độ chắc chắn thấp và hướng người dùng sang bước xác minh tại showroom.

Sản phẩm ưu tiên độ chính xác (precision) hơn độ bao phủ (recall), vì chỉ cần một vài câu trả lời sai ở thông tin quan trọng cũng đủ làm người dùng mất niềm tin. Các chỉ số theo dõi gồm độ chính xác thông tin có nguồn, tỷ lệ bịa thông tin bằng 0 cho nhóm giá/an toàn, tốc độ phản hồi P95 dưới 4 giây, tỷ lệ “Hữu ích”, và tỷ lệ để lại thông tin liên hệ hợp lệ.

Vòng lặp cải thiện được thiết kế ngay từ đầu: mọi phản hồi “Sai/Thiếu nguồn” và chỉnh sửa của người dùng được ghi lại để cập nhật dữ liệu, cải thiện prompt và logic truy xuất theo chu kỳ. Nhờ đó, chatbot càng chạy càng phù hợp với nhu cầu người dùng thực tế.
