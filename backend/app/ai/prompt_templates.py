"""Prompt templates for Vietnamese legal AI assistant."""

SYSTEM_PROMPT = """Bạn là trợ lý pháp lý AI chuyên về luật Việt Nam. Nhiệm vụ của bạn:
1. Trả lời câu hỏi pháp lý dựa HOÀN TOÀN trên ngữ cảnh được cung cấp.
2. Luôn trích dẫn điều khoản, văn bản cụ thể trong câu trả lời.
3. Nếu ngữ cảnh không đủ thông tin, hãy nói rõ: "Tôi không tìm thấy thông tin liên quan trong cơ sở dữ liệu."
4. KHÔNG bịa đặt hay suy diễn thông tin ngoài ngữ cảnh.
5. Trả lời bằng tiếng Việt, rõ ràng, dễ hiểu cho người dân phổ thông.
6. Nếu có mâu thuẫn giữa các văn bản, ưu tiên văn bản có hiệu lực mới nhất."""

RAG_PROMPT_TEMPLATE = """Dựa trên các ngữ cảnh pháp lý sau đây, hãy trả lời câu hỏi của người dùng.

=== NGỮCẢNH PHÁP LÝ ===
{context}
=== HẾT NGỮCẢNH ===

Câu hỏi: {question}

Hướng dẫn trả lời:
- Trả lời chính xác dựa trên ngữ cảnh. Trích dẫn số điều, tên văn bản.
- Nếu có nhiều văn bản liên quan, ưu tiên văn bản mới nhất còn hiệu lực.
- Kết thúc bằng phần "Nguồn tham khảo:" liệt kê các văn bản đã sử dụng."""

SUMMARY_PROMPT_TEMPLATE = """Hãy tóm tắt nội dung chính của văn bản pháp lý sau đây bằng tiếng Việt.

Văn bản:
{text}

Yêu cầu tóm tắt:
- Nêu tên, số hiệu văn bản (nếu có)
- Phạm vi điều chỉnh và đối tượng áp dụng
- Các điểm chính, nội dung quan trọng
- Ngày có hiệu lực (nếu có)
- Độ dài tóm tắt: {summary_length} (ngắn/trung bình/chi tiết)"""

CONFIDENCE_PROMPT = """Dựa trên câu trả lời bạn vừa đưa ra và ngữ cảnh pháp lý được cung cấp,
hãy đánh giá mức độ tin cậy của câu trả lời trên thang 0.0 - 1.0:
- 0.9-1.0: Trả lời chắc chắn, có trích dẫn điều khoản rõ ràng
- 0.7-0.8: Trả lời khá chắc chắn, có cơ sở
- 0.5-0.6: Trả lời dựa trên suy luận, không hoàn toàn rõ ràng
- <0.5: Không đủ thông tin để trả lời chắc chắn

Chỉ trả về một số thập phân, không thêm giải thích."""

IMAGE_DESCRIPTION_PROMPT = """Mô tả nội dung của hình ảnh/sơ đồ này trong ngữ cảnh tài liệu pháp lý Việt Nam.
Tập trung vào:
- Nội dung chữ trong hình (nếu có)
- Cấu trúc sơ đồ/quy trình
- Mối quan hệ giữa các thành phần
Trả lời bằng tiếng Việt."""
