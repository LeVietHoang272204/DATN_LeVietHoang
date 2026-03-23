# Hệ thống Phân tích và Tóm tắt Văn bản Pháp lý
## Ứng dụng Multimodal RAG với LLM

### Giới thiệu

Hệ thống hỗ trợ phân tích, tóm tắt và tra cứu văn bản pháp lý Việt Nam sử dụng kỹ thuật Multimodal Retrieval-Augmented Generation (RAG) kết hợp Large Language Model (Google Gemini 1.5 Flash).

### Tính năng chính

- **Chat RAG**: Hỏi đáp dựa trên nội dung văn bản pháp lý đã tải lên, có trích dẫn nguồn và điểm tin cậy
- **Tóm tắt văn bản**: Tóm tắt tự động nội dung văn bản pháp lý
- **Multimodal**: Hỗ trợ PDF (text + scan/OCR + bảng + hình ảnh), DOCX
- **Smart Chunking**: Phân đoạn thông minh theo cấu trúc pháp lý (Chương/Mục/Điều/Khoản/Điểm)
- **Thư viện cá nhân**: Quản lý tài liệu cá nhân với RAG riêng biệt
- **Sự kiện & Quiz**: Tổ chức sự kiện thi trắc nghiệm pháp luật
- **Mẫu văn bản**: Tạo văn bản từ mẫu có sẵn (hợp đồng, đơn khiếu nại...)
- **Versioning**: Quản lý phiên bản văn bản, ưu tiên văn bản mới hơn

---

### Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Backend | Python 3.11, FastAPI 0.115 |
| Frontend | Next.js 14, TailwindCSS, TypeScript |
| AI/LLM | Google Gemini 1.5 Flash (free tier) |
| Embeddings | BAAI/bge-m3 (hỗ trợ tiếng Việt) |
| Vector DB | ChromaDB 0.5 |
| Database | SQLite (dev) / PostgreSQL 16 (prod) |
| OCR | EasyOCR + Tesseract (fallback) |
| Storage | Cloudinary |
| Orchestration | Docker Compose |

---

### Cấu trúc dự án

```
DATN/
├── backend/
│   ├── app/
│   │   ├── ai/              # AI pipeline (embeddings, chunking, OCR, RAG...)
│   │   ├── api/              # REST API routes
│   │   ├── core/             # Security, dependencies, rate limiter
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic services
│   │   ├── config.py         # App configuration
│   │   ├── database.py       # Database setup
│   │   └── main.py           # FastAPI entrypoint
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── components/       # Shared components
│   │   ├── lib/              # API client, auth store
│   │   └── types/            # TypeScript interfaces
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

---

### Yêu cầu hệ thống

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (tùy chọn)
- Google Gemini API Key (miễn phí): https://aistudio.google.com/app/apikey
- Cloudinary account (miễn phí): https://cloudinary.com

---

### Cài đặt & Chạy

#### 1. Clone & cấu hình

```bash
# Copy file cấu hình
cp .env.example .env

# Chỉnh sửa .env với thông tin của bạn
# BẮT BUỘC: GOOGLE_API_KEY, CLOUDINARY_*
```

#### 2a. Chạy với Docker Compose (khuyến nghị)

```bash
docker-compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs (Swagger): http://localhost:8000/docs

#### 2b. Chạy thủ công (development)

**Backend:**

```bash
cd backend

# Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy server
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend

# Cài đặt dependencies
npm install

# Chạy dev server
npm run dev
```

---

### Biến môi trường (.env)

| Biến | Mô tả | Bắt buộc |
|---|---|---|
| `DATABASE_URL` | Connection string DB | Có (mặc định SQLite) |
| `JWT_SECRET_KEY` | Secret key cho JWT | Có |
| `GOOGLE_API_KEY` | Google Gemini API key | **Có** |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | **Có** |
| `CLOUDINARY_API_KEY` | Cloudinary API key | **Có** |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | **Có** |
| `CHROMA_PERSIST_DIR` | Thư mục lưu ChromaDB | Không (mặc định `./chroma_data`) |
| `CHUNK_SIZE` | Kích thước chunk | Không (mặc định 512) |
| `CONFIDENCE_THRESHOLD` | Ngưỡng tin cậy | Không (mặc định 0.65) |

---

### API Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/api/auth/register` | Đăng ký |
| POST | `/api/auth/login` | Đăng nhập |
| GET | `/api/auth/me` | Thông tin user |
| POST | `/api/documents/upload` | Tải lên văn bản |
| GET | `/api/documents/` | Danh sách văn bản |
| POST | `/api/documents/{id}/summarize` | Tóm tắt văn bản |
| POST | `/api/documents/{id}/ask` | Hỏi đáp về văn bản |
| POST | `/api/chat/sessions` | Tạo phiên chat mới |
| POST | `/api/chat/sessions/{id}/send` | Gửi tin nhắn |
| GET | `/api/chat/sessions/{id}/stream` | Chat streaming (SSE) |
| GET | `/api/events/` | Danh sách sự kiện |
| POST | `/api/events/{id}/submit` | Nộp bài thi |
| GET | `/api/templates/` | Danh sách mẫu |
| POST | `/api/templates/{id}/generate` | Tạo văn bản từ mẫu |
| POST | `/api/media/upload` | Tải lên tài liệu cá nhân |

Xem đầy đủ tại: http://localhost:8000/docs

---

### Các cải tiến so với thiết kế ban đầu

1. **Confidence Scoring** – LLM tự đánh giá độ tin cậy của câu trả lời (0.0–1.0), cảnh báo khi < 0.65
2. **Smart Legal Chunking** – Phân đoạn theo Điều/Khoản thay vì cắt cố định 500 token
3. **Document Versioning** – Theo dõi ngày hiệu lực/hết hạn, ưu tiên văn bản mới
4. **Personal RAG Isolation** – Mỗi user có ChromaDB collection riêng
5. **OCR Fallback** – EasyOCR → Tesseract, có tiền xử lý ảnh (grayscale, contrast, binarize)
6. **Rate Limiting** – Token bucket cho Gemini API (per-minute + per-day)
7. **Conflict Resolution** – Prompt hướng dẫn LLM ưu tiên văn bản mới hơn khi có mâu thuẫn

---

### Tác giả

- **Họ tên**: Lê Việt Hoàng
- **MSSV**: 64130729
- **Trường**: Đại học Công nghiệp TP.HCM

---

### License

Dự án được phát triển phục vụ mục đích học tập (Đồ án tốt nghiệp).
