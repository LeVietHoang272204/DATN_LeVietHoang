"""Quiz Generator — AI tự sinh câu hỏi trắc nghiệm pháp luật.

Dùng Gemini để:
1. Sinh câu hỏi từ nội dung tài liệu pháp luật đã có trong ChromaDB
2. Đảm bảo 4 đáp án (A/B/C/D), 1 đáp án đúng, có giải thích
3. Phân theo lĩnh vực pháp luật và mức độ khó (dễ/trung bình/khó)
"""

import json
import logging
import re
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

from app.config import settings
from app.ai.vectorstore import search_similar

logger = logging.getLogger(__name__)

QUIZ_SYSTEM_PROMPT = """Bạn là chuyên gia pháp luật Việt Nam. Nhiệm vụ của bạn là tạo câu hỏi trắc nghiệm 
chất lượng cao từ nội dung văn bản pháp luật được cung cấp.

Quy tắc BẮT BUỘC:
1. Câu hỏi phải dựa HOÀN TOÀN trên nội dung được cung cấp, không bịa đặt.
2. Mỗi câu hỏi có đúng 4 đáp án (A, B, C, D), chỉ 1 đáp án đúng.
3. Các đáp án sai phải hợp lý, không quá lộ liễu.
4. Phần giải thích phải trích dẫn điều khoản cụ thể.
5. Trả về JSON hợp lệ theo đúng format yêu cầu."""

QUIZ_GENERATION_PROMPT = """Dựa trên nội dung pháp luật sau đây, hãy tạo {count} câu hỏi trắc nghiệm 
với mức độ {difficulty}.

=== NỘI DUNG PHÁP LUẬT ===
{context}
=== HẾT NỘI DUNG ===

Lĩnh vực: {legal_field}
Mức độ: {difficulty} (dễ=kiến thức cơ bản / trung-bình=hiểu sâu / khó=áp dụng thực tế)

Trả về JSON theo đúng format sau (không thêm bất kỳ text nào ngoài JSON):
{{
  "questions": [
    {{
      "question_text": "Câu hỏi đầy đủ?",
      "options": {{
        "A": "Đáp án A",
        "B": "Đáp án B", 
        "C": "Đáp án C",
        "D": "Đáp án D"
      }},
      "correct_answer": "A",
      "explanation": "Theo Điều X, khoản Y: ... (giải thích chi tiết)",
      "difficulty": "{difficulty}",
      "points": {points}
    }}
  ]
}}"""

DIFFICULTY_POINTS = {"dễ": 5, "trung-bình": 10, "khó": 20}


def generate_quiz_from_field(
    legal_field: str,
    count: int = 5,
    difficulty: str = "trung-bình",
    collection_name: Optional[str] = None,
) -> list[dict]:
    """Sinh câu hỏi quiz từ tài liệu của một lĩnh vực pháp luật.

    Args:
        legal_field: slug lĩnh vực ('lao-dong', 'dat-dai', ...)
        count: số câu hỏi cần sinh (tối đa 10)
        difficulty: 'dễ' | 'trung-bình' | 'khó'
        collection_name: ChromaDB collection (None = public)

    Returns:
        List[dict] mỗi dict có: question_text, options, correct_answer,
                                explanation, difficulty, points
    """
    count = min(count, 10)
    
    # Lấy nội dung từ ChromaDB theo lĩnh vực
    query = f"quy định pháp luật {legal_field.replace('-', ' ')}"
    filter_dict = {"legal_field": legal_field} if legal_field != "khac" else None
    results = search_similar(
        query=query,
        collection_name=collection_name,
        top_k=8,
        filter_dict=filter_dict,
    )

    if not results:
        # Thử tìm không có filter
        results = search_similar(query=query, collection_name=collection_name, top_k=8)

    if not results:
        logger.warning(f"No documents found for field: {legal_field}")
        return []

    context = "\n\n---\n\n".join(
        r["text"] for r in results if r.get("text")
    )[:6000]

    return _call_gemini_generate(
        context=context,
        legal_field=legal_field,
        count=count,
        difficulty=difficulty,
    )


def generate_quiz_from_document(
    document_text: str,
    legal_field: str = "khac",
    count: int = 5,
    difficulty: str = "trung-bình",
) -> list[dict]:
    """Sinh câu hỏi trực tiếp từ nội dung văn bản (dùng khi vừa upload xong)."""
    count = min(count, 10)
    context = document_text[:6000]
    return _call_gemini_generate(
        context=context,
        legal_field=legal_field,
        count=count,
        difficulty=difficulty,
    )


def _call_gemini_generate(
    context: str,
    legal_field: str,
    count: int,
    difficulty: str,
) -> list[dict]:
    """Gọi Gemini để sinh quiz, parse JSON trả về."""
    if not settings.GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY not configured")
        return []

    points = DIFFICULTY_POINTS.get(difficulty, 10)

    prompt = QUIZ_GENERATION_PROMPT.format(
        count=count,
        difficulty=difficulty,
        context=context,
        legal_field=legal_field,
        points=points,
    )

    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.3,
        )
        messages = [
            SystemMessage(content=QUIZ_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
        response = llm.invoke(messages)
        raw = response.content.strip()

        # Bóc tách JSON từ response (Gemini đôi khi thêm markdown code block)
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_match:
            logger.error(f"No JSON in Gemini response: {raw[:200]}")
            return []

        data = json.loads(json_match.group(0))
        questions = data.get("questions", [])

        # Validate từng câu hỏi
        valid = []
        for q in questions:
            if _validate_question(q):
                # Chuẩn hóa options thành list ["A. ...", "B. ...", ...]
                opts = q.get("options", {})
                if isinstance(opts, dict):
                    q["options"] = [f"{k}. {v}" for k, v in opts.items()]
                valid.append(q)

        logger.info(f"Generated {len(valid)}/{count} valid questions for {legal_field}")
        return valid

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error from Gemini: {e}")
        return []
    except Exception as e:
        logger.error(f"Gemini quiz generation error: {e}")
        return []


def _validate_question(q: dict) -> bool:
    """Kiểm tra câu hỏi hợp lệ."""
    return (
        q.get("question_text")
        and q.get("options")
        and q.get("correct_answer")
        and q.get("explanation")
    )
