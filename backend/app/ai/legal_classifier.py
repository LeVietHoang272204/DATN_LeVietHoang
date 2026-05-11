"""Legal document classifier.

Dùng keyword matching + Gemini để:
1. Tự động phân loại văn bản pháp luật (lĩnh vực pháp lý)
2. Trích xuất metadata: số hiệu, ngày ban hành, cơ quan, trạng thái hiệu lực
3. Lưu nội dung đã xử lý ra file .md chuẩn hóa
4. Tự động đặt tên tài liệu theo nội dung
"""

import re
import os
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# ── Regex nhận dạng tiêu đề văn bản pháp luật VN ────────────────────────────
# Ví dụ: "LUẬT ĐẤT ĐAI", "NGHỊ ĐỊNH số 91/2019/NĐ-CP", "THÔNG TƯ số 12/2021/TT-BTC"
_LEGAL_TITLE_PATTERNS = [
    # BỘ LUẬT / LUẬT + tên + số hiệu (tùy chọn)
    re.compile(
        r"(BỘ LUẬT|LUẬT)\s+([A-ZĐÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂẮẶẤẦẨẪẢẠẶẼẺẸỀ"
        r"ẾỆỈỊỌỘỔỖỞỚỜỌỦỨỪỰỮỰỲỴỶỸÝ\s]+?)(?:\s+số\s+[\w/\-]+)?(?:\n|$)",
        re.IGNORECASE,
    ),
    # NGHỊ ĐỊNH / THÔNG TƯ / QUYẾT ĐỊNH / PHÁP LỆNH / NGHỊ QUYẾT số ...
    re.compile(
        r"(NGHỊ ĐỊNH|THÔNG TƯ|QUYẾT ĐỊNH|PHÁP LỆNH|NGHỊ QUYẾT|CHỈ THỊ|"
        r"THÔNG TƯ LIÊN TỊCH|NGHỊ ĐỊNH LIÊN BỘ)"
        r"\s+(?:số\s+)?([\w/\-]+(?:/[\w\-]+)*)",
        re.IGNORECASE,
    ),
    # HIẾN PHÁP
    re.compile(r"(HIẾN PHÁP)\s+(?:NƯỚC\s+)?[\w\s]+?(\d{4})", re.IGNORECASE),
]

# Tên file "vô nghĩa" — chỉ số, UUID, hoặc quá ngắn
_MEANINGLESS_TITLE_RE = re.compile(
    r"^[\d\s\-_\.]+$"                    # toàn số/dấu
    r"|^[a-f0-9]{8,}$"                   # UUID hex
    r"|^(document|file|upload|scan|img|image|doc|pdf|untitled)[\s\d\-_]*$",
    re.IGNORECASE,
)

FIELD_KEYWORDS: dict[str, list[str]] = {
    "giao-thong": [
        "giao thông", "phương tiện", "lái xe", "đường bộ", "đường thủy",
        "hàng không", "đăng kiểm", "biển số", "tốc độ", "vận tải",
        "luật giao thông", "vi phạm giao thông",
    ],
    "dat-dai": [
        "đất đai", "quyền sử dụng đất", "giấy chứng nhận", "sổ đỏ", "sổ hồng",
        "thu hồi đất", "bồi thường", "quy hoạch", "địa chính", "thửa đất",
        "luật đất đai", "chuyển nhượng đất",
    ],
    "lao-dong": [
        "lao động", "hợp đồng lao động", "tiền lương", "bảo hiểm xã hội",
        "nghỉ phép", "sa thải", "kỷ luật lao động", "người sử dụng lao động",
        "người lao động", "thử việc", "bộ luật lao động",
    ],
    "dan-su": [
        "dân sự", "hợp đồng", "bồi thường thiệt hại", "thừa kế", "di chúc",
        "tài sản", "sở hữu", "bộ luật dân sự", "quyền dân sự",
        "nghĩa vụ dân sự", "năng lực pháp luật",
    ],
    "hinh-su": [
        "hình sự", "tội phạm", "hình phạt", "tù", "phạt tiền", "bộ luật hình sự",
        "điều tra", "truy tố", "xét xử", "cải tạo không giam giữ",
        "tội danh", "khởi tố",
    ],
    "hanh-chinh": [
        "hành chính", "vi phạm hành chính", "xử phạt hành chính", "thủ tục hành chính",
        "cơ quan nhà nước", "công chức", "viên chức", "quyết định hành chính",
        "khiếu nại", "tố cáo",
    ],
    "doanh-nghiep": [
        "doanh nghiệp", "công ty", "luật doanh nghiệp", "cổ phần", "trách nhiệm hữu hạn",
        "vốn điều lệ", "đăng ký kinh doanh", "giải thể", "phá sản",
        "hội đồng quản trị", "cổ đông",
    ],
    "nha-o": [
        "nhà ở", "chung cư", "nhà chung cư", "sở hữu nhà", "thuê nhà",
        "luật nhà ở", "ban quản trị", "diện tích", "xây dựng",
    ],
    "hon-nhan-gia-dinh": [
        "hôn nhân", "gia đình", "kết hôn", "ly hôn", "cấp dưỡng", "con cái",
        "giám hộ", "nhận nuôi", "luật hôn nhân",
    ],
    "to-tung": [
        "tố tụng", "dân sự", "hình sự", "hành chính", "tòa án", "viện kiểm sát",
        "bộ luật tố tụng", "đương sự", "nguyên đơn", "bị đơn", "phiên tòa",
        "kháng cáo", "kháng nghị",
    ],
}

# Nhãn hiển thị
FIELD_LABELS: dict[str, str] = {
    "giao-thong": "Giao thông",
    "dat-dai": "Đất đai",
    "lao-dong": "Lao động",
    "dan-su": "Dân sự",
    "hinh-su": "Hình sự",
    "hanh-chinh": "Hành chính",
    "doanh-nghiep": "Doanh nghiệp",
    "nha-o": "Nhà ở",
    "hon-nhan-gia-dinh": "Hôn nhân - Gia đình",
    "to-tung": "Tố tụng",
    "khac": "Khác",
}

# Regex trích xuất metadata từ tiêu đề / đầu văn bản
_DOC_NUMBER_RE = re.compile(
    r"(số|so)\s*[:\.]?\s*(\d+[\w/-]+)", re.IGNORECASE
)
_DATE_RE = re.compile(
    r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})", re.IGNORECASE
)
_EFFECTIVE_RE = re.compile(
    r"(có hiệu lực|hiệu lực thi hành)\s+(?:từ\s+)?ngày\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}|\d{1,2}\s+tháng\s+\d{1,2}\s+năm\s+\d{4})",
    re.IGNORECASE,
)
_ISSUING_BODY_RE = re.compile(
    r"^(quốc hội|chính phủ|bộ [^\n,]+|ủy ban nhân dân|hội đồng nhân dân|thủ tướng|bộ trưởng)",
    re.IGNORECASE | re.MULTILINE,
)


def classify_legal_field(text: str, title: str = "") -> str:
    """Phân loại lĩnh vực pháp lý dựa trên từ khóa.

    Returns slug như 'lao-dong', 'dat-dai', ...
    """
    combined = (title + " " + text[:3000]).lower()

    scores: dict[str, int] = {}
    for field, keywords in FIELD_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in combined)
        if score:
            scores[field] = score

    if not scores:
        return "khac"

    return max(scores, key=lambda k: scores[k])


def extract_metadata_from_text(text: str, title: str = "") -> dict:
    """Trích xuất metadata từ nội dung văn bản."""
    snippet = text[:2000]

    # Số hiệu văn bản
    doc_num_match = _DOC_NUMBER_RE.search(snippet)
    document_number = doc_num_match.group(2) if doc_num_match else None

    # Ngày ban hành
    date_match = _DATE_RE.search(snippet)
    issued_date = None
    if date_match:
        try:
            issued_date = datetime(
                int(date_match.group(3)),
                int(date_match.group(2)),
                int(date_match.group(1)),
            ).date().isoformat()
        except ValueError:
            pass

    # Ngày có hiệu lực
    effective_match = _EFFECTIVE_RE.search(snippet)
    effective_date_str = effective_match.group(2) if effective_match else None

    # Cơ quan ban hành
    body_match = _ISSUING_BODY_RE.search(snippet)
    issuing_body = body_match.group(0).strip().title() if body_match else None

    # Kiểm tra còn hiệu lực dựa trên từ khóa
    expired_keywords = ["hết hiệu lực", "bị bãi bỏ", "đã bị thay thế", "không còn hiệu lực"]
    is_expired = any(kw in text[:1000].lower() for kw in expired_keywords)

    return {
        "document_number": document_number,
        "issued_date": issued_date,
        "effective_date_str": effective_date_str,
        "issuing_body": issuing_body,
        "is_expired": is_expired,
    }


def save_as_markdown(
    text: str,
    title: str,
    metadata: dict,
    output_dir: str = "./md_cache",
    filename: Optional[str] = None,
) -> str:
    """Lưu nội dung đã xử lý ra file .md chuẩn hóa.

    Format:
        ---
        title: ...
        legal_field: ...
        document_number: ...
        issuing_body: ...
        issued_date: ...
        effective_date: ...
        is_expired: false
        created_at: ...
        ---

        # Tiêu đề

        Nội dung...

    Returns: đường dẫn file .md đã lưu
    """
    os.makedirs(output_dir, exist_ok=True)

    legal_field = metadata.get("legal_field", "khac")
    field_dir = os.path.join(output_dir, legal_field)
    os.makedirs(field_dir, exist_ok=True)

    if not filename:
        safe_title = re.sub(r"[^\w\s-]", "", title.lower())
        safe_title = re.sub(r"\s+", "_", safe_title.strip())[:60]
        filename = f"{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    filepath = os.path.join(field_dir, filename)

    # Build frontmatter
    frontmatter_lines = [
        "---",
        f"title: \"{title}\"",
        f"legal_field: \"{FIELD_LABELS.get(legal_field, legal_field)}\"",
        f"legal_field_slug: \"{legal_field}\"",
        f"document_number: \"{metadata.get('document_number', '')}\"",
        f"issuing_body: \"{metadata.get('issuing_body', '')}\"",
        f"issued_date: \"{metadata.get('issued_date', '')}\"",
        f"effective_date: \"{metadata.get('effective_date_str', '')}\"",
        f"is_expired: {str(metadata.get('is_expired', False)).lower()}",
        f"document_id: {metadata.get('document_id', '')}",
        f"created_at: \"{datetime.now().isoformat()}\"",
        "---",
        "",
        f"# {title}",
        "",
    ]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(frontmatter_lines))
        f.write(text)

    logger.info(f"Saved .md: {filepath}")
    return filepath


# ── Auto title generation ──────────────────────────────────────────────────────

def is_meaningless_title(title: str) -> bool:
    """Kiểm tra tên tài liệu có 'vô nghĩa' không (chỉ số, UUID, quá ngắn...)."""
    clean = os.path.splitext(title.strip())[0]  # bỏ đuôi .pdf/.docx
    if len(clean) < 4:
        return True
    return bool(_MEANINGLESS_TITLE_RE.match(clean))


def extract_title_from_text(text: str) -> Optional[str]:
    """Trích xuất tên văn bản pháp luật từ nội dung bằng regex.

    Ưu tiên dòng đầu văn bản — nơi tiêu đề thường xuất hiện.
    Trả về None nếu không nhận ra được.
    """
    # Lấy 1500 ký tự đầu, bỏ khoảng trắng thừa
    snippet = re.sub(r"\s{3,}", "\n", text[:1500]).strip()

    for pattern in _LEGAL_TITLE_PATTERNS:
        m = pattern.search(snippet)
        if m:
            # Ghép toàn bộ match lại, title-case, xén khoảng trắng
            raw = " ".join(m.groups()).strip()
            raw = re.sub(r"\s+", " ", raw)
            if len(raw) >= 8:
                return raw.strip()

    return None


def auto_generate_title(
    text: str,
    filename: str,
    google_api_key: Optional[str] = None,
    gemini_model: str = "gemini-1.5-flash",
) -> str:
    """Tự động đặt tên tài liệu theo nội dung.

    Luồng ưu tiên:
    1. Regex trích xuất từ đầu văn bản (nhanh, không tốn quota)
    2. Gemini sinh tên ngắn gọn (nếu regex thất bại và API key có sẵn)
    3. Fallback về tên file gốc (đã làm sạch)

    Returns: tên tài liệu tiếng Việt có nghĩa
    """
    # Bước 1: thử regex
    regex_title = extract_title_from_text(text)
    if regex_title:
        logger.info(f"Auto-title via regex: {regex_title!r}")
        return regex_title

    # Bước 2: thử Gemini
    if google_api_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain.schema import HumanMessage

            llm = ChatGoogleGenerativeAI(
                model=gemini_model,
                google_api_key=google_api_key,
                temperature=0.1,
            )
            snippet = text[:1200].strip()
            prompt = (
                "Đọc đoạn đầu văn bản pháp luật dưới đây và đặt tên ngắn gọn, chính xác "
                "bằng tiếng Việt (tối đa 15 từ). Chỉ trả về TÊN, không giải thích.\n\n"
                f"Nội dung:\n{snippet}"
            )
            response = llm.invoke([HumanMessage(content=prompt)])
            generated = response.content.strip().strip('"').strip("'")
            # Loại bỏ nếu Gemini trả về quá dài hoặc rỗng
            if 5 < len(generated) <= 150:
                logger.info(f"Auto-title via Gemini: {generated!r}")
                return generated
        except Exception as e:
            logger.warning(f"Gemini title generation failed: {e}")

    # Bước 3: làm sạch tên file gốc
    base = os.path.splitext(filename)[0]
    clean = re.sub(r"[_\-]+", " ", base).strip()
    logger.info(f"Auto-title fallback to filename: {clean!r}")
    return clean if len(clean) >= 3 else filename

