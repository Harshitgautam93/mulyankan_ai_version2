import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate  # Use core for stability
from langchain_core.output_parsers import JsonOutputParser # Use core
from pydantic import BaseModel, Field

# 1. Structured Output Schema
class EvaluationResult(BaseModel):
    score: str = Field(description="Score out of 10, e.g. 7/10")
    grade: str = Field(description="Grade: A, B, C, or F")
    feedback: str = Field(description="Specific improvement feedback")

# 2. Initialize Components
parser = JsonOutputParser(pydantic_object=EvaluationResult)

llm = ChatGroq(
    model_name="llama3-70b-8192", 
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# 3. Evaluation Function
def evaluate_answer(
    question: str,
    sample_solution: str,
    student_answer: str,
    rubric: str
):
    # Ensure system-level instruction is included for better JSON adherence
    prompt = ChatPromptTemplate.from_template("""
    You are an expert academic evaluator. 
    Grade the Student Answer strictly using the context provided.
    
    Question: {question}
    Sample Solution: {sample_solution}
    Grading Rubric: {rubric}
    Student Answer: {student_answer}

    {format_instructions}
    """)

    # The 'Pipe' operator correctly handles the internal 'create' calls
    chain = prompt | llm | parser

    try:
        # Pass variables as a dictionary to invoke()
        result = chain.invoke({
            "question": question,
            "sample_solution": sample_solution,
            "student_answer": student_answer,
            "rubric": rubric,
            "format_instructions": parser.get_format_instructions()
        })
        return result

    except Exception as e:
        # Prevent UI crashes with a clean JSON fallback
        return {
            "score": "0/10",
            "grade": "F",
            "feedback": f"Evaluation failed: {str(e)}"
        }