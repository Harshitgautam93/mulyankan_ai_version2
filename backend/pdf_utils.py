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
    import pypdfium2 as pdfium
    _HAS_PYPDFIUM2 = True
except Exception:
    _HAS_PYPDFIUM2 = False

try:
    import pytesseract
    from PIL import Image, ImageOps, ImageEnhance
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

    print(f"[DEBUG] Starting PDF text extraction ({len(pdf_bytes)} bytes)")

    # Primary: PyPDF2
    if _HAS_PYPDF2:
        try:
            print("[DEBUG] Attempting PyPDF2 extraction...")
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            pages = [p.extract_text() or "" for p in reader.pages]
            combined = "\n".join(pages).strip()
            # If we got actual alphanumeric text, return it. Otherwise try fallback.
            if any(c.isalnum() for c in combined):
                print(f"[DEBUG] PyPDF2 success: extracted {len(combined)} chars")
                return combined
            print("[DEBUG] PyPDF2 returned no alphanumeric text.")
        except Exception as e:
            print(f"[DEBUG] PyPDF2 failed: {e}")
            logger.debug("PyPDF2 extraction failed, falling back", exc_info=True)

    # Fallback: pdfplumber text extraction
    if _HAS_PDFPLUMBER:
        try:
            print("[DEBUG] Attempting pdfplumber extraction...")
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                texts = [p.extract_text() or "" for p in pdf.pages]
            combined = "\n".join(texts).strip()
            if any(c.isalnum() for c in combined):
                print(f"[DEBUG] pdfplumber success: extracted {len(combined)} chars")
                return combined
            print("[DEBUG] pdfplumber returned no alphanumeric text.")
        except Exception as e:
            print(f"[DEBUG] pdfplumber failed: {e}")
            logger.debug("pdfplumber extraction failed", exc_info=True)

    # Final fallback: OCR using pypdfium2 (preferred) or pdfplumber to render pages + pytesseract
    if _HAS_PYTESSERACT:
        print("[DEBUG] Attempting OCR fallback...")
        ocr_texts = []
        
        # Method A: pypdfium2 (Higher quality rendering)
        if _HAS_PYPDFIUM2:
            try:
                print("[DEBUG] Rendering pages with pypdfium2 for OCR...")
                pdf = pdfium.PdfDocument(pdf_bytes)
                for i in range(len(pdf)):
                    print(f"[DEBUG] Processing page {i+1}/{len(pdf)}...")
                    page = pdf[i]
                    # Render at 300 DPI for better OCR
                    bitmap = page.render(scale=300/72)
                    pil = bitmap.to_pil()
                    
                    # Ensure white background (fix for transparent PDFs)
                    if pil.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', pil.size, (255, 255, 255))
                        background.paste(pil, mask=pil.split()[-1])
                        pil = background
                    
                    # Preprocess for handwriting
                    pil = pil.convert('L') # Grayscale
                    pil = ImageOps.autocontrast(pil) # Improve contrast
                    
                    # Optional: Enhance sharpness for clearer handwriting
                    enhancer = ImageEnhance.Sharpness(pil)
                    pil = enhancer.enhance(2.0)
                    
                    # Use PSM 3 (Auto) which is usually better for mixed handwriting
                    text = pytesseract.image_to_string(pil, config='--psm 3')
                    ocr_texts.append(text or "")
                pdf.close()
                combined_ocr = "\n".join(ocr_texts).strip()
                if any(c.isalnum() for c in combined_ocr):
                    print(f"[DEBUG] OCR success (pypdfium2): extracted {len(combined_ocr)} chars")
                    return combined_ocr
                print("[DEBUG] OCR (pypdfium2) returned no alphanumeric text.")
            except Exception as e:
                print(f"[DEBUG] pypdfium2 OCR failed: {e}")
                logger.debug("pypdfium2 OCR fallback failed: %s", e)

        # Method B: pdfplumber (Legacy fallback)
        if _HAS_PDFPLUMBER:
            try:
                print("[DEBUG] Rendering pages with pdfplumber for OCR...")
                with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                    for i, page in enumerate(pdf.pages):
                        try:
                            print(f"[DEBUG] Processing page {i+1}/{len(pdf.pages)}...")
                            # Higher resolution for better OCR
                            img = page.to_image(resolution=300)
                            pil = img.original
                            
                            # Preprocess
                            pil = pil.convert('L')
                            pil = ImageOps.autocontrast(pil)
                            
                            # Enhance sharpness
                            enhancer = ImageEnhance.Sharpness(pil)
                            pil = enhancer.enhance(2.0)
                            
                            text = pytesseract.image_to_string(pil, config='--psm 3')
                            ocr_texts.append(text or "")
                        except Exception as e:
                            print(f"[DEBUG] OCR failed on page {i+1} with pdfplumber: {e}")
                            logger.debug("OCR failed on matching page with pdfplumber", exc_info=True)
                combined_ocr = "\n".join(ocr_texts).strip()
                if any(c.isalnum() for c in combined_ocr):
                    print(f"[DEBUG] OCR success (pdfplumber): extracted {len(combined_ocr)} chars")
                    return combined_ocr
                print("[DEBUG] OCR (pdfplumber) returned no alphanumeric text.")
            except Exception as e:
                print(f"[DEBUG] pdfplumber OCR failed: {e}")
                logger.exception("OCR extraction via pdfplumber failed")

    print("[DEBUG] All text extraction methods failed.")
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
    """Extract text from PDF bytes and parse into title/solution.
    
    Returns dict: {title, solution, full_text}
    """
    full = extract_text_from_pdf_bytes(pdf_bytes)
    parsed = parse_guideline_text(full)
    return parsed
