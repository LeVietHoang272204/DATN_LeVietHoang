"""Table extraction from PDF documents using pdfplumber."""

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


def extract_tables_from_pdf(pdf_path: str) -> List[dict]:
    """Extract all tables from a PDF file.

    Returns list of {"page": int, "table_index": int, "text": str} dicts.
    """
    import pdfplumber

    tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_tables = page.extract_tables()
                for t_idx, table in enumerate(page_tables):
                    table_text = _table_to_text(table)
                    if table_text.strip():
                        tables.append({
                            "page": page_num,
                            "table_index": t_idx,
                            "text": table_text,
                        })
    except Exception as e:
        logger.error(f"Table extraction failed for {pdf_path}: {e}")

    return tables


def _table_to_text(table: list) -> str:
    """Convert a pdfplumber table (list of lists) to readable text."""
    if not table:
        return ""

    rows = []
    for row in table:
        cells = [str(cell).strip() if cell else "" for cell in row]
        rows.append(" | ".join(cells))

    return "\n".join(rows)
