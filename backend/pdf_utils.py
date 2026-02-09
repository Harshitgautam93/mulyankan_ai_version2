import io
import os
import shutil
import logging
import io
import os
import shutil
import logging

try:
    import PyPDF2
    _HAS_PYPDF2 = True
except Exception:
    _HAS_PYPDF2 = False

try:
    import pdfplumber
    _HAS_PDFPLUMBER = True
except Exception:
    _HAS_PDFPLUMBER = False

try:
    import pytesseract
    _HAS_PYTESSERACT = True
except Exception:
    pytesseract = None
    _HAS_PYTESSERACT = False

logger = logging.getLogger(__name__)


def _configure_tesseract_cmd() -> bool:
    """Attempt to locate a tesseract executable and configure pytesseract.

    Returns True if an executable was found and configured, False otherwise.
    Checks environment overrides, PATH (shutil.which), and common Windows install locations.
    """
    global _HAS_PYTESSERACT
    if not _HAS_PYTESSERACT or pytesseract is None:
        return False

    # Allow explicit override from environment
    env_paths = [os.environ.get("TESSERACT_CMD"), os.environ.get("TESSERACT_PATH")]
    for p in env_paths:
        if p:
            if os.path.isfile(p):
                pytesseract.pytesseract.tesseract_cmd = p
                logger.info("Using TESSERACT from env: %s", p)
                return True
            # If directory given, append exe name
            candidate = os.path.join(p, "tesseract.exe")
            if os.path.isfile(candidate):
                pytesseract.pytesseract.tesseract_cmd = candidate
                logger.info("Using TESSERACT from env path: %s", candidate)
                return True

    # Check if tesseract is on PATH
    which_path = shutil.which("tesseract")
    if which_path:
        pytesseract.pytesseract.tesseract_cmd = which_path
        logger.info("Found tesseract on PATH: %s", which_path)
        return True

    # Common Windows install locations
    common = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\ProgramData\chocolatey\lib\tesseract\tools\Tesseract-OCR\tesseract.exe",
        r"C:\ProgramData\chocolatey\bin\tesseract.exe",
        os.path.expanduser(r"~\scoop\shims\tesseract.EXE"),
        os.path.expanduser(r"~\scoop\apps\tesseract\current\tesseract.exe"),
    ]
    for p in common:
        if os.path.isfile(p):
            pytesseract.pytesseract.tesseract_cmd = p
            logger.info("Found tesseract at: %s", p)
            return True

    # Not found; disable pytesseract usage to avoid runtime errors later
    logger.warning("Tesseract executable not found. OCR fallback will be disabled until tesseract is installed or TESSERACT_CMD is set.")
    _HAS_PYTESSERACT = False
    return False


# Configure at import time if pytesseract is present
if _HAS_PYTESSERACT:
    try:
        _configure_tesseract_cmd()
    except Exception:
        logger.exception("Error while configuring tesseract executable")


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extracts and returns text from PDF bytes. Returns empty string on failure.

    Uses PyPDF2 if available, falls back to pdfplumber, and finally to OCR (pdfplumber+pytesseract) if available.
    """
    if not pdf_bytes:
        return ""

    # Primary: PyPDF2
    if _HAS_PYPDF2:
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            pages = [p.extract_text() or "" for p in reader.pages]
            combined = "\n".join(pages).strip()
            if combined:
                return combined
        except Exception:
            logger.debug("PyPDF2 extraction failed, falling back", exc_info=True)

    # Fallback: pdfplumber text extraction
    if _HAS_PDFPLUMBER:
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                texts = [p.extract_text() or "" for p in pdf.pages]
            combined = "\n".join(texts).strip()
            if combined:
                return combined
        except Exception:
            logger.debug("pdfplumber extraction failed", exc_info=True)

    # Final fallback: OCR using pdfplumber to render pages + pytesseract
    if _HAS_PDFPLUMBER and _HAS_PYTESSERACT:
        try:
            ocr_texts = []
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    try:
                        img = page.to_image(resolution=150)
                        pil = img.original
                        text = pytesseract.image_to_string(pil)
                        ocr_texts.append(text or "")
                    except Exception:
                        logger.debug("OCR failed on a page", exc_info=True)
                        ocr_texts.append("")
            combined_ocr = "\n".join(ocr_texts).strip()
            return combined_ocr
        except Exception:
            logger.exception("OCR extraction failed")

    return ""


def _ensure_logs_dir():
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir


def parse_guideline_text(full_text: str) -> dict:
    """Attempt to extract a title/question and a solution from guideline text.

    Heuristics:
    - Look for common markers like 'Question:', 'Q:', 'Problem:' for question start.
    - Look for 'Solution:', 'Answer:', 'Official Solution' for solution start.
    - Otherwise use first non-empty line as title and remainder as solution.
    Returns dict with keys: title, solution, full_text
    """
    import re

    if not full_text:
        return {"title": "", "solution": "", "full_text": full_text}

    text = full_text.strip()

    # Try to find explicit solution marker
    sol_match = re.search(r"(?mi)^(solution[:\-\s].*$|answer[:\-\s].*$|official solution[:\-\s].*$)", text)
    if sol_match:
        idx = sol_match.start()
        # question area is before idx
        title_area = text[:idx].strip()
        solution_area = text[idx:].strip()
        # Trim markers from solution_area if present
        solution_area = re.sub(r"(?mi)^(solution[:\-\s]*|answer[:\-\s]*|official solution[:\-\s]*)", "", solution_area).strip()
        # title heuristic: take first non-empty line
        title = ""
        for line in title_area.splitlines():
            if line.strip():
                title = line.strip()
                break
        if not title:
            title = title_area[:200]
        return {"title": title, "solution": solution_area, "full_text": text}

    # Fallback: look for a question marker
    q_match = re.search(r"(?mi)^(question[:\-\s].*$|q[:\-\s].*$|problem[:\-\s].*$)", text)
    if q_match:
        idx = q_match.start()
        # find next blank line to separate question from rest
        lines = text[idx:].splitlines()
        if len(lines) > 1:
            title = lines[0].strip()
            solution = "\n".join(lines[1:]).strip()
            return {"title": title, "solution": solution, "full_text": text}

    # Default: first non-empty line is title, rest is solution
    lines = text.splitlines()
    title = ""
    rest = []
    found = False
    for ln in lines:
        if not found and ln.strip():
            title = ln.strip()
            found = True
        elif found:
            rest.append(ln)
    solution = "\n".join(rest).strip()
    return {"title": title, "solution": solution, "full_text": text}


def extract_and_parse_pdf(pdf_bytes: bytes) -> dict:
    """Extract text from PDF bytes and parse into title/solution; also log the extracted text.

    Returns dict: {title, solution, full_text, log_path}
    """
    full = extract_text_from_pdf_bytes(pdf_bytes)
    parsed = parse_guideline_text(full)

    # write log
    try:
        logs_dir = _ensure_logs_dir()
        import datetime
        ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        safe_name = f"pdf_extracted_{ts}.txt"
        path = os.path.join(logs_dir, safe_name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(parsed.get("full_text", ""))
        parsed["log_path"] = path
    except Exception:
        parsed["log_path"] = None

    return parsed
