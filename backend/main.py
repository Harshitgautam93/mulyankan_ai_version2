import os
from pydantic import BaseModel, Field
from typing import List, Dict
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Import your custom database and PDF utilities
from backend.database import retrieve_relevant_guideline, save_evaluation_result
from backend.database import store_guideline as _store_guideline
from backend.pdf_utils import extract_text_from_pdf_bytes, extract_and_parse_pdf

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
    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "mixtral-8x7b-32768"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0
    )
    parser = JsonOutputParser(pydantic_object=EvaluationSchema)
    
    sample_solution = retrieve_relevant_guideline(question) or "Use the rubric as reference."

    prompt = ChatPromptTemplate.from_template("""
    You are an expert AI grader providing comprehensive, pedagogically-sound feedback.
    
    Your task: Evaluate the student's answer and provide not just a grade, but actionable insights for improvement.
    
    CONTEXT:
    --------
    Question: {question}
    Sample Solution/Guideline: {sample_solution}
    Student Answer: {student_answer}
    Grading Rubric: {rubric}
    
    EVALUATION INSTRUCTIONS:
    -----------------------
    
    1. EXECUTIVE SUMMARY (score, grade, feedback):
       - Assign a score (0-10) and corresponding letter grade (A=9-10, B=7-8, C=5-6, D=3-4, F=0-2)
       - Provide a concise executive summary of the answer's strengths and overall assessment
    
    2. TOPIC SWAP DIAGNOSTIC (if applicable):
       - If the score is 3 or lower, check if the student answered the WRONG question
       - Use language like: "Your submission accurately describes X and Y. However, the assignment specifically asked for Z. While these are both [domain] concepts, they serve different purposes."
       - This helps students understand they didn't fail at the technique—they misunderstood the assignment
       - Leave blank/empty if the score is above 3 or the answer is on-topic
    
    3. RUBRIC BREAKDOWN:
       - Break down the evaluation into specific criteria from the rubric
       - For each criterion, assign individual scores with specific feedback
       - Format: criteria name, score/max_score, and targeted feedback for improvement
       - Be specific: explain WHAT was done well or WHAT was missing
       - Show both strengths AND gaps (e.g., "Constructors were well-defined, BUT you missed Polymorphism")
    
    4. GAP ANALYSIS (What was Missing):
       - Identify key concepts, facts, or techniques that should have been included
       - For each missing element:
         * List the concept name
         * Rate its importance (HIGH/MEDIUM/LOW)
         * Explain why it was important for this answer (e.g., "Method Overriding: Necessary for creating flexible, interchangeable code")
       - This helps students understand the "expected vs actual" gap
    
    5. THE BRIDGE (Corrective Guidance):
       - Compare what the student wrote to what the correct answer should contain
       - Show the relationship between their effort and the expected answer
       - Use language like: "It seems you focused on X. However, Y is what the question asked for."
       - Help them see their work wasn't wasted—just misdirected
       - Provide the conceptual link between what they did right and what to do next time
       - Example: "To improve, try rewriting your code so that different classes (like 'Cat' and 'Dog') can both use a 'speak()' method, but produce different results."
    
    6. SUGGESTED RESOURCES & NEXT STEPS:
       - Provide 2-3 actionable learning resources
       - For each resource:
         * Title of the reading/concept
         * What the student should learn from it (in the context of their mistake)
         * Specific action to take (e.g., "Review method overriding in Python documentation")
    
    7. METADATA FOR TRACKING:
       - Complexity Level: What level is this problem? (Beginner/Intermediate/Advanced)
       - AI Confidence: How confident are you in this grading? (0-100%)
       - Plagiarism Similarity: Estimate % similarity to standard solutions (0-100%)
    
    {format_instructions}
    """)

    chain = prompt | llm | parser

    try:
        result = chain.invoke({
            "question": question,
            "sample_solution": sample_solution,
            "student_answer": student_answer,
            "rubric": rubric,
            "format_instructions": parser.get_format_instructions()
        })
        
        if save_to_db and student_name:
            save_evaluation_result(question, student_name, result, student_roll=student_roll)
        
        return result
    except Exception as e:
        return {"error": f"Evaluation failed: {str(e)}"}


def evaluate_pdf(question: str, student_pdf_bytes: bytes, rubric: str, student_name: str = None, student_roll: str = None, save_to_db: bool = True):
    """Extract student answer text from PDF bytes and run evaluation pipeline."""
    student_text = extract_text_from_pdf_bytes(student_pdf_bytes)
    if not student_text:
        raise RuntimeError("Failed to extract student text from PDF or PDF is empty.")
    return process_assignment_evaluation(question, student_text, rubric, student_name=student_name, student_roll=student_roll, save_to_db=save_to_db)


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
