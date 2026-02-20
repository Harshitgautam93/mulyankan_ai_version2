import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Load environment variables from root .env file BEFORE processing
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(project_root, ".env")
print(f"\n{'='*60}")
print(f"[MAIN.PY INIT] Loading environment variables")
print(f"{'='*60}")
print(f"Project root: {project_root}")
print(f"Env file path: {env_path}")
print(f"Env file exists: {os.path.exists(env_path)}")

# Load env file with override to ensure fresh load
load_dotenv(env_path, override=True)

# IMPORTANT: Store API key as module-level variable so it persists
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")

# Verify all environment variables are loaded
print(f"\n[MAIN.PY INIT] Checking loaded environment variables:")
for key in ["GROQ_API_KEY", "GROQ_MODEL", "SUPABASE_URL", "SUPABASE_KEY"]:
    value = os.getenv(key)
    if value:
        if len(value) > 20:
            print(f"  LOADED {key}: {value[:20]}...({len(value)} chars)")
        else:
            print(f"  LOADED {key}: {value}")
    else:
        print(f"  MISSING {key}")

if not GROQ_API_KEY:
    print(f"\n[WARNING] GROQ_API_KEY is not set!")
    print(f"[WARNING] Checking if it exists in environment after explicit load:")
    print(f"  Value: {os.getenv('GROQ_API_KEY')}")
else:
    print(f"\n[SUCCESS] GROQ_API_KEY successfully loaded: {GROQ_API_KEY[:20]}...")

print(f"{'='*60}\n")

# Import your custom database and PDF utilities
from backend.database import retrieve_relevant_guideline, save_evaluation_result
from backend.database import store_guideline as _store_guideline
from backend.pdf_utils import extract_text_from_pdf_bytes, extract_and_parse_pdf, _HAS_PYTESSERACT

print(f"[MAIN.PY] OCR Enabled: {_HAS_PYTESSERACT}")

# --- SCHEMA DEFINITIONS ---
class RubricCriterion(BaseModel):
    criteria: str = Field(description="The evaluation criterion")
    score: str = Field(description="Score for this criterion")
    max_score: str = Field(description="Maximum possible score")
    feedback: str = Field(description="Specific feedback on this criterion")

class MissingConcept(BaseModel):
    concept: str = Field(description="Name of the missing concept")
    importance: str = Field(description="Why it's important (HIGH/MEDIUM/LOW)")
    explanation: str = Field(description="Brief explanation of what was missed")

class SuggestedResource(BaseModel):
    title: str = Field(description="Resource title")
    description: str = Field(description="What the student should learn")
    action_item: str = Field(description="Specific action to take")

class EvaluationMetadata(BaseModel):
    complexity_level: str = Field(description="Beginner/Intermediate/Advanced")
    ai_confidence: str = Field(description="Confidence percentage (0-100)")
    plagiarism_similarity: str = Field(description="Similarity percentage to standard solutions")

class EvaluationSchema(BaseModel):
    score: str = Field(description="Score out of 10")
    grade: str = Field(description="Letter grade: A, B, C, D, F")
    feedback: str = Field(description="Executive summary and general feedback")
    topic_diagnostic: str = Field(description="Diagnostic note when the submission addresses the wrong topic (for low scores)")
    rubric_breakdown: List[RubricCriterion] = Field(description="Detailed scoring for each criterion")
    missing_concepts: List[MissingConcept] = Field(description="Concepts that were missing from the answer")
    bridge_guidance: str = Field(description="Corrective guidance linking student work to expected answer")
    suggested_resources: List[SuggestedResource] = Field(description="Resources and next steps for improvement")
    metadata: EvaluationMetadata = Field(description="Complexity level, AI confidence, plagiarism check")

# --- CORE LOGIC FUNCTIONS ---
def process_assignment_evaluation(question, student_answer, rubric, student_name=None, student_roll=None, save_to_db=True):
    """
    Core evaluation function - orchestrates LLM grading with detailed feedback
    """
    try:
        # 1. Retrieve the reference guideline from Database
        reference_guideline = retrieve_relevant_guideline(question)
        print(f"[PROCESS_EVAL] Guideline found for '{question}': {reference_guideline is not None}")

        # 2. System Instructions for Grading
        template = """
        You are an expert academic evaluator. Your task is to evaluate a student's answer based on a specific question, a set of rubric criteria, and a reference guideline.

        QUESTION/TOPIC: {question}

        REFERENCE GUIDELINE (Use this as the standard for accuracy):
        {reference_guideline}

        RUBRIC CRITERIA:
        {rubric}

        STUDENT ANSWER TO EVALUATE:
        {student_answer}

        Instructions:
        1. Compare the student answer against the reference guideline.
        2. Strictly follow the provided rubric criteria for scoring.
        3. Provide a score from 0 to 10 (as a string).
        4. Assign a letter grade (A, B, C, D, or F).
        5. If the student's answer is completely off-topic or addresses the wrong question, provide a diagnostic note in 'topic_diagnostic' and give a low score.
        6. Identify specific missing concepts or inaccuracies.
        7. Provide 'bridge guidance' that explains exactly how the student can transition from their current answer to the ideal answer.
        8. Suggest actionable resources or next steps for improvement.
        9. Ensure the response is in valid JSON format matching the schema.

        {format_instructions}
        """

        # 3. Setup LLM and Parser
        parser = JsonOutputParser(pydantic_object=EvaluationSchema)
        prompt = ChatPromptTemplate.from_template(template)
        
        # Use the configured model
        llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=GROQ_MODEL,
            temperature=0.1
        )

        # 4. Create and run Chain
        chain = prompt | llm | parser
        
        print(f"[PROCESS_EVAL] Invoking Groq LLM ({GROQ_MODEL}) for student: {student_name}")
        result_dict = chain.invoke({
            "question": question,
            "reference_guideline": reference_guideline or "No specific guideline found. Evaluate based on general academic standards and expert knowledge of the topic.",
            "rubric": rubric,
            "student_answer": student_answer,
            "format_instructions": parser.get_format_instructions()
        })

        if save_to_db and student_name:
            save_evaluation_result(question, student_name, result_dict, student_roll=student_roll, student_answer=student_answer)
        
        return result_dict
    except Exception as e:
        error_msg = str(e)
        print(f"[EVAL_ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        return {
            "score": "0",
            "grade": "F",
            "feedback": f"Evaluation error: {error_msg}",
            "topic_diagnostic": "",
            "rubric_breakdown": [],
            "missing_concepts": [],
            "bridge_guidance": f"An error occurred during evaluation: {error_msg}",
            "suggested_resources": [],
            "metadata": {
                "complexity_level": "Unknown",
                "ai_confidence": "0",
                "plagiarism_similarity": "0"
            }
        }


def evaluate_pdf(question: str, student_pdf_bytes: bytes, rubric: str, student_name: str = None, student_roll: str = None, save_to_db: bool = True):
    """Extract student answer text from PDF bytes and run evaluation pipeline."""
    try:
        student_text = extract_text_from_pdf_bytes(student_pdf_bytes)
        print(f"[EVALUATE_PDF] Extracted {len(student_text)} characters from PDF.")
        if not student_text:
            raise RuntimeError("Failed to extract student text from PDF or PDF is empty. For handwritten assignments, ensure the PDF is clear and Tesseract OCR is configured correctly.")
        return process_assignment_evaluation(question, student_text, rubric, student_name=student_name, student_roll=student_roll, save_to_db=save_to_db)
    except Exception as e:
        error_msg = str(e)
        print(f"[EVALUATE_PDF_ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        return {
            "score": "0",
            "grade": "F",
            "feedback": f"PDF Evaluation error: {error_msg}",
            "topic_diagnostic": "",
            "rubric_breakdown": [],
            "missing_concepts": [],
            "bridge_guidance": f"An error occurred: {error_msg}",
            "suggested_resources": [],
            "metadata": {
                "complexity_level": "Unknown",
                "ai_confidence": "0",
                "plagiarism_similarity": "0"
            }
        }


def store_guideline_from_pdf(pdf_bytes: bytes):
    """Extract text from guideline PDF using backend parser and store it."""
    parsed = extract_and_parse_pdf(pdf_bytes)
    title = parsed.get("title") or "Uploaded Guideline"
    solution = parsed.get("solution") or parsed.get("full_text") or ""
    status = _store_guideline(title, solution)
    log_path = parsed.get("log_path")
    if log_path:
        return f"{status} (extracted_text_log: {log_path})"
    return status
