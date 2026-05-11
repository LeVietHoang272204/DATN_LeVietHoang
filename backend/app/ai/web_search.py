"""Web search fallback for legal queries.

Khi ChromaDB không có tài liệu liên quan, tìm kiếm DuckDuckGo 
và lọc kết quả từ các nguồn pháp luật uy tín của Việt Nam.

Không cần API key — dùng DuckDuckGo Instant Answer API (miễn phí).
"""

import logging
import re
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

# ── Nguồn pháp luật uy tín Việt Nam ──────────────────────────────────────────
TRUSTED_LEGAL_DOMAINS = [
    "vbpl.vn",          # Cổng Thông tin Pháp luật Quốc gia (Bộ Tư pháp)
    "thuvienphapluat.vn",
    "luatvietnam.vn",
    "moj.gov.vn",       # Bộ Tư pháp
    "chinhphu.vn",      # Cổng TTÐT Chính phủ
    "quochoi.vn",       # Quốc hội
    "toaan.gov.vn",     # Tòa án nhân dân tối cao
    "vksndtc.gov.vn",   # Viện Kiểm sát nhân dân tối cao
    "molisa.gov.vn",    # Bộ Lao động
    "monre.gov.vn",     # Bộ Tài nguyên Môi trường
]

# Giới hạn tìm kiếm
_MAX_RESULTS = 5
_TIMEOUT_SECONDS = 8


async def web_search_legal(query: str) -> list[dict]:
    """Tìm kiếm DuckDuckGo, ưu tiên kết quả từ nguồn pháp luật uy tín.

    Returns:
        List[{"title": str, "url": str, "snippet": str, "is_trusted": bool}]
    """
    # Thêm từ khóa tăng độ chính xác
    search_query = f"{query} luật Việt Nam site:vbpl.vn OR site:thuvienphapluat.vn OR site:luatvietnam.vn"

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            resp = await client.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": search_query,
                    "format": "json",
                    "no_html": "1",
                    "skip_disambig": "1",
                    "kl": "vn-vi",
                },
                headers={"User-Agent": "LegalAI-Bot/1.0"},
                follow_redirects=True,
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}")
        return []

    results = []

    # Instant Answer
    if data.get("AbstractText"):
        results.append({
            "title": data.get("Heading", ""),
            "url": data.get("AbstractURL", ""),
            "snippet": data["AbstractText"][:500],
            "is_trusted": _is_trusted(data.get("AbstractURL", "")),
        })

    # Related Topics
    for topic in data.get("RelatedTopics", []):
        if len(results) >= _MAX_RESULTS:
            break
        if isinstance(topic, dict) and topic.get("Text"):
            url = topic.get("FirstURL", "")
            results.append({
                "title": topic.get("Text", "")[:100],
                "url": url,
                "snippet": topic.get("Text", "")[:400],
                "is_trusted": _is_trusted(url),
            })

    # Sắp xếp: nguồn uy tín lên trước
    results.sort(key=lambda x: (not x["is_trusted"], 0))
    return results[:_MAX_RESULTS]


def _is_trusted(url: str) -> bool:
    return any(domain in url for domain in TRUSTED_LEGAL_DOMAINS)


def format_search_results_for_prompt(results: list[dict]) -> str:
    """Chuyển kết quả tìm kiếm thành context cho LLM prompt."""
    if not results:
        return ""

    lines = ["=== KẾT QUẢ TÌM KIẾM WEB ==="]
    for i, r in enumerate(results, 1):
        trusted = "✓ Nguồn uy tín" if r["is_trusted"] else "⚠ Nguồn chưa xác minh"
        lines.append(
            f"\n[{i}] {r['title']}\n"
            f"    URL: {r['url']} ({trusted})\n"
            f"    {r['snippet']}"
        )
    lines.append("\n=== HẾT KẾT QUẢ ===")
    return "\n".join(lines)
