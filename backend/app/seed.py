"""
Seed data script - chạy 1 lần để tạo dữ liệu mẫu
Usage: cd backend && python -m app.seed
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, init_db
import app.models  # noqa - ensure all models loaded
from app.models.template import Template
from app.models.event import Event, EventQuestion
from app.core.security import hash_password
from app.models.user import User
from datetime import datetime, timedelta


def seed():
    init_db()
    db = SessionLocal()

    try:
        # --- Admin user ---
        existing_admin = db.query(User).filter(User.email == "admin@legal-rag.vn").first()
        if not existing_admin:
            admin = User(
                email="admin@legal-rag.vn",
                full_name="Quản trị viên",
                hashed_password=hash_password("admin123456"),
                role="admin",
            )
            db.add(admin)
            db.flush()
            print("[+] Tạo tài khoản admin: admin@legal-rag.vn / admin123456")

        # --- Templates ---
        existing_templates = db.query(Template).count()
        if existing_templates == 0:
            templates = [
                Template(
                    name="Hợp đồng lao động",
                    description="Mẫu hợp đồng lao động theo Bộ luật Lao động 2019",
                    category="hop-dong",
                    fields=[
                        {"name": "employer_name", "label": "Tên công ty", "type": "text", "required": True},
                        {"name": "employer_address", "label": "Địa chỉ công ty", "type": "text", "required": True},
                        {"name": "employer_representative", "label": "Người đại diện", "type": "text", "required": True},
                        {"name": "employer_position", "label": "Chức vụ người đại diện", "type": "text", "required": True},
                        {"name": "employee_name", "label": "Họ tên người lao động", "type": "text", "required": True},
                        {"name": "employee_dob", "label": "Ngày sinh", "type": "text", "required": True},
                        {"name": "employee_id_number", "label": "Số CCCD", "type": "text", "required": True},
                        {"name": "employee_address", "label": "Địa chỉ thường trú", "type": "text", "required": True},
                        {"name": "job_title", "label": "Vị trí công việc", "type": "text", "required": True},
                        {"name": "workplace", "label": "Địa điểm làm việc", "type": "text", "required": True},
                        {"name": "salary", "label": "Mức lương (VNĐ)", "type": "text", "required": True},
                        {"name": "contract_duration", "label": "Thời hạn hợp đồng", "type": "text", "required": True},
                        {"name": "start_date", "label": "Ngày bắt đầu", "type": "text", "required": True},
                    ],
                    content_template="""CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
---

HỢP ĐỒNG LAO ĐỘNG

Hôm nay, ngày ... tháng ... năm ..., tại {{workplace}}

Chúng tôi gồm:

BÊN A (Người sử dụng lao động):
- Tên công ty: {{employer_name}}
- Địa chỉ: {{employer_address}}
- Đại diện bởi: {{employer_representative}} - Chức vụ: {{employer_position}}

BÊN B (Người lao động):
- Họ và tên: {{employee_name}}
- Ngày sinh: {{employee_dob}}
- Số CCCD: {{employee_id_number}}
- Địa chỉ thường trú: {{employee_address}}

Hai bên thỏa thuận ký kết hợp đồng lao động với các điều khoản sau:

Điều 1. Công việc và địa điểm làm việc
- Vị trí: {{job_title}}
- Địa điểm: {{workplace}}

Điều 2. Thời hạn hợp đồng
- Loại hợp đồng: Có thời hạn {{contract_duration}}
- Từ ngày: {{start_date}}

Điều 3. Tiền lương
- Mức lương: {{salary}} VNĐ/tháng
- Hình thức trả: Chuyển khoản ngân hàng, trả vào ngày cuối mỗi tháng

Điều 4. Thời giờ làm việc, nghỉ ngơi
- Thời gian làm việc: 8 giờ/ngày, 48 giờ/tuần
- Nghỉ phép năm: 12 ngày/năm

Điều 5. Bảo hiểm xã hội, bảo hiểm y tế
- Bên A có trách nhiệm đóng BHXH, BHYT, BHTN cho Bên B theo quy định pháp luật.

Hợp đồng được lập thành 02 bản, mỗi bên giữ 01 bản có giá trị pháp lý như nhau.

BÊN A                                    BÊN B
(Ký, ghi rõ họ tên)                      (Ký, ghi rõ họ tên)
""",
                ),
                Template(
                    name="Đơn khiếu nại",
                    description="Mẫu đơn khiếu nại hành chính theo Luật Khiếu nại 2011",
                    category="don-tu",
                    fields=[
                        {"name": "recipient", "label": "Nơi gửi (cơ quan)", "type": "text", "required": True},
                        {"name": "sender_name", "label": "Họ tên người khiếu nại", "type": "text", "required": True},
                        {"name": "sender_address", "label": "Địa chỉ", "type": "text", "required": True},
                        {"name": "sender_phone", "label": "Số điện thoại", "type": "text", "required": True},
                        {"name": "sender_id_number", "label": "Số CCCD", "type": "text", "required": True},
                        {"name": "decision_info", "label": "Quyết định bị khiếu nại (số, ngày, cơ quan ban hành)", "type": "textarea", "required": True},
                        {"name": "complaint_content", "label": "Nội dung khiếu nại", "type": "textarea", "required": True},
                        {"name": "request", "label": "Yêu cầu giải quyết", "type": "textarea", "required": True},
                    ],
                    content_template="""CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
---

ĐƠN KHIẾU NẠI

Kính gửi: {{recipient}}

Tôi tên là: {{sender_name}}
Địa chỉ: {{sender_address}}
Số điện thoại: {{sender_phone}}
Số CCCD: {{sender_id_number}}

Tôi làm đơn này khiếu nại về:
Quyết định: {{decision_info}}

NỘI DUNG KHIẾU NẠI:
{{complaint_content}}

YÊU CẦU GIẢI QUYẾT:
{{request}}

Tôi cam đoan nội dung khiếu nại trên là đúng sự thật và chịu trách nhiệm trước pháp luật.

..., ngày ... tháng ... năm ...

Người khiếu nại
(Ký, ghi rõ họ tên)
""",
                ),
                Template(
                    name="Giấy ủy quyền",
                    description="Mẫu giấy ủy quyền cá nhân theo Bộ luật Dân sự 2015",
                    category="giay-to",
                    fields=[
                        {"name": "authorizer_name", "label": "Họ tên người ủy quyền", "type": "text", "required": True},
                        {"name": "authorizer_dob", "label": "Ngày sinh người ủy quyền", "type": "text", "required": True},
                        {"name": "authorizer_id", "label": "Số CCCD người ủy quyền", "type": "text", "required": True},
                        {"name": "authorizer_address", "label": "Địa chỉ người ủy quyền", "type": "text", "required": True},
                        {"name": "authorized_name", "label": "Họ tên người được ủy quyền", "type": "text", "required": True},
                        {"name": "authorized_dob", "label": "Ngày sinh người được ủy quyền", "type": "text", "required": True},
                        {"name": "authorized_id", "label": "Số CCCD người được ủy quyền", "type": "text", "required": True},
                        {"name": "authorized_address", "label": "Địa chỉ người được ủy quyền", "type": "text", "required": True},
                        {"name": "scope", "label": "Nội dung ủy quyền", "type": "textarea", "required": True},
                        {"name": "duration", "label": "Thời hạn ủy quyền", "type": "text", "required": True},
                    ],
                    content_template="""CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
---

GIẤY ỦY QUYỀN

Bên ủy quyền (Bên A):
- Họ và tên: {{authorizer_name}}
- Ngày sinh: {{authorizer_dob}}
- Số CCCD: {{authorizer_id}}
- Địa chỉ: {{authorizer_address}}

Bên được ủy quyền (Bên B):
- Họ và tên: {{authorized_name}}
- Ngày sinh: {{authorized_dob}}
- Số CCCD: {{authorized_id}}
- Địa chỉ: {{authorized_address}}

NỘI DUNG ỦY QUYỀN:
{{scope}}

THỜI HẠN ỦY QUYỀN: {{duration}}

Tôi cam đoan những thông tin trên là đúng sự thật. Bên được ủy quyền không được ủy quyền lại cho bên thứ ba.

..., ngày ... tháng ... năm ...

BÊN ỦY QUYỀN                          BÊN ĐƯỢC ỦY QUYỀN
(Ký, ghi rõ họ tên)                    (Ký, ghi rõ họ tên)
""",
                ),
            ]
            db.add_all(templates)
            print(f"[+] Tạo {len(templates)} mẫu văn bản")

        # --- Sample Event ---
        existing_events = db.query(Event).count()
        if existing_events == 0:
            event = Event(
                title="Kiểm tra kiến thức Hiến pháp 2013",
                description="Bài kiểm tra trắc nghiệm về các nội dung cơ bản của Hiến pháp nước CHXHCN Việt Nam 2013",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow() + timedelta(days=30),
                is_active=True,
                created_by=1,
            )
            db.add(event)
            db.flush()

            questions = [
                EventQuestion(
                    event_id=event.id,
                    question_text="Hiến pháp nước CHXHCN Việt Nam 2013 được Quốc hội thông qua ngày nào?",
                    options=["28/11/2012", "28/11/2013", "02/01/2013", "01/01/2014"],
                    correct_answer="1",
                    points=10,
                ),
                EventQuestion(
                    event_id=event.id,
                    question_text="Theo Hiến pháp 2013, nước CHXHCN Việt Nam do ai làm chủ?",
                    options=["Đảng Cộng sản", "Nhân dân", "Quốc hội", "Chính phủ"],
                    correct_answer="1",
                    points=10,
                ),
                EventQuestion(
                    event_id=event.id,
                    question_text="Hiến pháp 2013 gồm bao nhiêu chương?",
                    options=["10 chương", "11 chương", "12 chương", "13 chương"],
                    correct_answer="1",
                    points=10,
                ),
                EventQuestion(
                    event_id=event.id,
                    question_text="Theo Điều 2 Hiến pháp 2013, quyền lực nhà nước thuộc về ai?",
                    options=["Đảng Cộng sản Việt Nam", "Nhân dân", "Chủ tịch nước", "Quốc hội"],
                    correct_answer="1",
                    points=10,
                ),
                EventQuestion(
                    event_id=event.id,
                    question_text="Nhiệm kỳ của Quốc hội theo Hiến pháp 2013 là bao nhiêu năm?",
                    options=["4 năm", "5 năm", "6 năm", "Không quy định"],
                    correct_answer="1",
                    points=10,
                ),
            ]
            db.add_all(questions)
            print(f"[+] Tạo sự kiện mẫu với {len(questions)} câu hỏi")

        db.commit()
        print("[✓] Seed data hoàn tất!")

    except Exception as e:
        db.rollback()
        print(f"[!] Lỗi: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
