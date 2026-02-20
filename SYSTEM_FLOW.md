# Mulyankan AI - System Flow Documentation

## Complete Evaluation Pipeline

### 1. KNOWLEDGE INGESTION (Tab 2: "🧬 Knowledge Base")
**Flow:**
- User uploads a **Guideline PDF** (e.g., official answer key)
- `store_guideline_from_pdf()` extracts text from PDF
- Text is converted to embeddings using HuggingFace (sentence-transformers/all-MiniLM-L6-v2)
- Embeddings stored in **Supabase Vector Database** (table: "assignments")
- This guideline is used as reference during evaluation

**Code:** `frontend/app.py` lines 459-483 → `backend/main.py` function `store_guideline_from_pdf()`

---

### 2. STUDENT EVALUATION (Tab 1: "🧪 Student Evaluation")
**Flow:**
1. User fills form with:
   - Student Name
   - Roll Number
   - Topic (e.g., "Photosynthesis")
   - Rubric (evaluation criteria)
   - Student Answer PDF

2. When "🚀 Evaluate" is clicked:
   - PDF is extracted to text using `extract_text_from_pdf_bytes()`
   - `process_assignment_evaluation()` is called with:
     - question (Topic)
     - student_answer (extracted text)
     - rubric (provided criteria)

3. Inside evaluation:
   - **Retrieve guideline:** `retrieve_relevant_guideline(topic)` searches Vector DB
   - **Compare:** Groq LLM compares student answer with guideline using rubric
   - **Generate score:** Returns structured evaluation with:
     - Score (0-10)
     - Grade (A-F)
     - Feedback (executive summary)
     - Rubric breakdown (per-criteria scores)
     - Missing concepts (with importance)
     - Bridge guidance (how to improve)
     - Suggested resources (with actions)
     - Metadata (difficulty, confidence, plagiarism %)

4. **Save to Database:**
   - Results saved to Supabase "evaluations" table
   - Includes: topic, student_name, student_roll, score, grade, feedback

**Code:** `frontend/app.py` lines 382-419 → `backend/main.py` function `process_assignment_evaluation()`

---

### 3. RESULT DISPLAY
**On Screen (Real-time):**
- Score/Grade/Roll Number metrics
- Feedback box
- Rubric breakdown (collapsible per criterion)
- Missing concepts (with importance flags)
- Bridge guidance section
- Suggested resources (expandable)
- Metadata (difficulty, confidence, plagiarism check)

**Download:**
- PDF report with all sections
- Filename: `{roll_number}_{username}_Report.pdf`

**Code:** `frontend/app.py` lines 420-515 → `frontend/pdf_generator.py` function `generate_pdf_bytes()`

---

### 4. ANALYTICS (Tab 3: "📈 Analytics")
**Data Visualized:**
- Total evaluations, average score, unique students, topics covered
- Score distributions
- Student performance rankings
- Topic difficulty rankings
- Grade distributions
- Evaluation trends over time

**Code:** `backend/database.py` analytics functions (get_all_evaluations, get_average_score, etc.)

---

## Key Components

### Environment Variables (.env file at project root)
```
SUPABASE_URL=https://...
SUPABASE_KEY=...
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile
```

### Database Schema (Supabase)
- **assignments table**: Stores guidelines with embeddings
  - Columns: text, metadata (solution)
  - RPC: match_assignments (vector similarity search)

- **evaluations table**: Stores grading results
  - Columns: topic, student_name, student_roll, score, grade, feedback, created_at

### LLM Integration (Groq)
- Model: `llama-3.3-70b-versatile` or `mixtral-8x7b-32768`
- Purpose: Compare student answers with guidelines
- Structured output: Uses Pydantic schemas for consistent JSON responses

---

## Troubleshooting Checklist

✅ **Knowledge Ingestion Not Working?**
- Check Supabase credentials in .env
- Verify "assignments" table exists with RPC "match_assignments"
- Upload a PDF with clear text (not scanned images)

✅ **Evaluation Not Generating?**
- Check GROQ_API_KEY is valid in .env
- Verify student PDF has extractable text
- Check terminal for [EVAL_ERROR] messages

✅ **PDF Report Not Downloading?**
- Ensure pdf_generator.py has no syntax errors
- Check that evaluation result includes all required fields

✅ **Analytics Showing No Data?**
- Run evaluations first (analytics need data)
- Check "evaluations" table in Supabase has records

---

## Recent Fixes (Current Session)

1. ✅ Fixed environment variable loading - now loads from project root .env with override
2. ✅ Fixed knowledge ingestion section - now actually calls store_guideline_from_pdf()
3. ✅ Enhanced evaluation results display - shows all details (rubric, concepts, resources)
4. ✅ Added error handling throughout - better debugging capability
5. ✅ Added PDF report error handling - shows what went wrong if generation fails

---

## Next Steps

1. Upload a guideline PDF in "Knowledge Base" tab
2. Upload a student answer PDF in "Student Evaluation" tab
3. Fill in Topic and Rubric
4. Click "🚀 Evaluate"
5. View results on screen or download as PDF
6. Check "Analytics" tab for class-wide insights
