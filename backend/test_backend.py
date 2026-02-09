from database import store_guideline, embeddings, supabase
from engine import evaluate_answer
from langchain_community.vectorstores import SupabaseVectorStore

# 1. MOCK DATA: Simulating an assignment setup
sample_question = "What is the capital of France and its significance?"
sample_solution = "The capital of France is Paris. It is a global hub for art, fashion, and culture."
rubric = "5 points for correct city, 5 points for significance. Total 10."

# 2. STORE: Save the solution to our Vector DB
print("Stashing sample solution in Supabase...")
store_guideline(sample_solution, {"question": sample_question})

# 3. RETRIEVE: Simulate a student submitting an answer
student_submission = "Paris is the capital. It's famous for the Eiffel Tower and art."

# Find the matching solution in the DB
vector_store = SupabaseVectorStore(
    client=supabase,
    embedding=embeddings,
    table_name="assignments",
    query_name="match_assignments"
)

matched_docs = vector_store.similarity_search(student_submission, k=1)
retrieved_context = matched_docs[0].page_content

# 4. EVALUATE: Ask the Judge (Groq) to grade it
print("Evaluating submission...")
result = evaluate_answer(
    question=sample_question,
    sample_solution=retrieved_context,
    student_answer=student_submission,
    rubric=rubric
)

print("\n--- EVALUATION RESULT ---")
print(result)