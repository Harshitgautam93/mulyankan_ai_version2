# Enhanced Evaluation System - Architecture & Data Flow

## System Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                     MULYANKAN AI - ENHANCED EVALUATION SYSTEM               ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE (Streamlit)                         │
│                                                                              │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐      │
│  │  Tab 1: Eval     │    │  Tab 2: KB       │    │  Tab 3: Analytics│      │
│  │  ├─ Student Name │    │  ├─ Upload PDF  │    │  └─ Charts       │      │
│  │  ├─ Topic        │    │  └─ Save Guide  │    │                  │      │
│  │  ├─ Max Marks    │    │                 │    │                  │      │
│  │  ├─ Rubric       │    │                 │    │                  │      │
│  │  ├─ Upload PDF   │    │                 │    │                  │      │
│  │  └─ Evaluate BTN │    │                 │    │                  │      │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         BACKEND PROCESSING (Python)                         │
│                                                                              │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────────────┐  │
│  │  PDF Extract │  │   Retrieve       │  │   Prepare Evaluation Input   │  │
│  │              │  │   Guidelines     │  │                              │  │
│  │  Text from   │  │   from Vector DB │  │   - Question               │  │
│  │  Student PDF │  │                  │  │   - Student Answer         │  │
│  └──────────────┘  └──────────────────┘  │   - Rubric                 │  │
│        │                    │             │   - Sample Solution        │  │
│        └────────┬───────────┘             └──────────────────────────────┘  │
│                 │                                      │                     │
│                 └──────────────┬───────────────────────┘                     │
│                                ▼                                             │
│                 ┌─────────────────────────────────────┐                     │
│                 │   LLM EVALUATION ENGINE (Groq)     │                     │
│                 │   Model: Llama/Mixtral             │                     │
│                 │   Temperature: 0 (Deterministic)   │                     │
│                 │                                     │                     │
│                 │   Prompt Instructions:             │                     │
│                 │   1. Score & Grade                 │                     │
│                 │   2. Rubric Breakdown              │                     │
│                 │   3. Gap Analysis                  │                     │
│                 │   4. Bridge Guidance               │                     │
│                 │   5. Resources                     │                     │
│                 │   6. Metadata                      │                     │
│                 └─────────────────────────────────────┘                     │
│                                │                                             │
│                                ▼                                             │
│                 ┌─────────────────────────────────────┐                     │
│                 │  EVALUATION SCHEMA (6 Sections)    │                     │
│                 │                                     │                     │
│                 │  ┌─ EvaluationSchema               │                     │
│                 │  ├─ score: string                  │                     │
│                 │  ├─ grade: string                  │                     │
│                 │  ├─ feedback: string               │                     │
│                 │  ├─ rubric_breakdown: [            │                     │
│                 │  │  └─ RubricCriterion[]           │                     │
│                 │  ├─ missing_concepts: [            │                     │
│                 │  │  └─ MissingConcept[]            │                     │
│                 │  ├─ bridge_guidance: string        │                     │
│                 │  ├─ suggested_resources: [         │                     │
│                 │  │  └─ SuggestedResource[]         │                     │
│                 │  └─ metadata: {                    │                     │
│                 │     └─ EvaluationMetadata          │                     │
│                 └─────────────────────────────────────┘                     │
│                                │                                             │
│                ┌───────────────┼───────────────────┐                        │
│                │               │                   │                        │
│                ▼               ▼                   ▼                        │
│     ┌─────────────────┐  ┌─────────────┐  ┌──────────────────┐            │
│     │  Save to        │  │  Generate   │  │  Return to       │            │
│     │  Database       │  │  PDF Report │  │  Frontend        │            │
│     │  (evaluation    │  │  (with all  │  │  (as Bytes)      │            │
│     │   results)      │  │   6 sections)   │                 │            │
│     └─────────────────┘  └─────────────┘  └──────────────────┘            │
│                │                   │              │                        │
└────────────────┼───────────────────┼──────────────┼────────────────────────┘
                 │                   │              │
                 ▼                   ▼              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FRONTEND DISPLAY & OUTPUT (Streamlit)                  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Show Results on Screen:                                             │  │
│  │  • Score Badge: "6/10"                                              │  │
│  │  • Grade Badge: "C"                                                 │  │
│  │  • Summary Feedback (from executive_summary section)                │  │
│  │  • "Download Report" Button                                         │  │
│  │                                                                      │  │
│  │  [📥 Download Report]  ← PDF with all 6 sections                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                   │                                         │
└───────────────────────────────────┼─────────────────────────────────────────┘
                                    ▼
                    ┌──────────────────────────────────┐
                    │  STUDENT RECEIVES PDF REPORT     │
                    │                                  │
                    │  ┌─────────────────────────────┐ │
                    │  │ 1. Executive Summary        │ │
                    │  ├─────────────────────────────┤ │
                    │  │ 2. Rubric Breakdown         │ │
                    │  ├─────────────────────────────┤ │
                    │  │ 3. Gap Analysis             │ │
                    │  ├─────────────────────────────┤ │
                    │  │ 4. Bridge Guidance          │ │
                    │  ├─────────────────────────────┤ │
                    │  │ 5. Suggested Resources      │ │
                    │  ├─────────────────────────────┤ │
                    │  │ 6. Metadata                 │ │
                    │  └─────────────────────────────┘ │
                    │                                  │
                    └──────────────────────────────────┘
```

---

## Data Flow: Detailed Step-by-Step

### Phase 1: INPUT PREPARATION

```
Student Submission
├─ Topic: "Explain Polymorphism"
├─ Rubric: "Cover types, code examples, clarity"
└─ PDF File: student_answer.pdf
                    │
                    ▼
Extract Text from PDF
                    │
                    ▼
Query Vector DB for Sample Solution
                    │
                    ▼
Prepare LLM Context:
├─ Question: "..."
├─ Student Answer: "..."  
├─ Sample Solution: "..."  
├─ Rubric: "..."
└─ Format Instructions (JSON schema)
```

### Phase 2: LLM EVALUATION

```
LLM Receives Context
├─ Instructions: 6 explicit section requirements
├─ Temperature: 0 (consistent, deterministic)
└─ Model: Mixtral/Llama
                    │
                    ▼
LLM Generates Output:
├─ Section 1: score, grade, feedback
├─ Section 2: [{criteria, score, max_score, feedback}, ...]
├─ Section 3: [{concept, importance, explanation}, ...]
├─ Section 4: bridge_guidance (string)
├─ Section 5: [{title, description, action_item}, ...]
└─ Section 6: {complexity_level, ai_confidence, plagiarism_similarity}
                    │
                    ▼
JSON Response Parsing
                    │
                    ▼
Pydantic Validation (EvaluationSchema)
```

### Phase 3: STORAGE & GENERATION

```
Validated Evaluation Data
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   Save to DB    Return Dict   Generate PDF
    (Backup)    (In Memory)   (Bytes)
        │           │           │
        └───────────┼───────────┘
                    │
                    ▼
Return to Frontend
```

### Phase 4: FRONTEND DISPLAY

```
Frontend Receives Evaluation Results
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   Display      Display      Generate
   Score        Grade        Download
   (6/10)       (C)          Button
        │           │           │
        └───────────┼───────────┘
                    │
                    ▼
        User sees Results & 
        Downloads PDF Report
```

---

## Component Interaction Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                        COMPONENT DIAGRAM                            │
└─────────────────────────────────────────────────────────────────────┘

frontend/app.py (Streamlit UI)
    ├─ Input: Form collection
    ├─ Process: Call backend.main.evaluate_pdf()
    ├─ Display: Show results from EvaluationSchema
    └─ Output: PDF bytes via generate_pdf_bytes()
            │
            ▼
backend/main.py (Evaluation Engine)
    ├─ evaluate_pdf(): Extract text from PDF
    ├─ process_assignment_evaluation(): Run main evaluation
    │   ├─ Input: Question, Student answer, Rubric
    │   ├─ Call: LLM with detailed prompt
    │   ├─ Parse: JSON → EvaluationSchema
    │   └─ Save: To database if needed
    └─ EvaluationSchema: 6-section data structure
            │
            ▼
LLM API (Groq/Mixtral)
    ├─ Receives: Question, Answer, Rubric, Prompt Instructions
    ├─ Processes: Advanced reasoning with temperature=0
    └─ Returns: JSON with 6 sections
            │
            ▼
frontend/pdf_generator.py (PDF Creator)
    ├─ Input: EvaluationSchema dict
    ├─ Process: Render each of 6 sections
    │   ├─ Section 1: Header + Executive Summary
    │   ├─ Section 2: Rubric Breakdown table
    │   ├─ Section 3: Gap Analysis list
    │   ├─ Section 4: Bridge text
    │   ├─ Section 5: Resources list
    │   └─ Section 6: Metadata
    ├─ Styling: Colors, fonts, formatting
    └─ Output: PDF bytes
            │
            ▼
backend/database.py (Data Persistence)
    ├─ save_evaluation_result(): Store evaluation
    ├─ get_all_evaluations(): Retrieve for analytics
    └─ retrieve_relevant_guideline(): For context
```

---

## Data Structures

### Input Schema

```python
Input {
    question: str                    # Assignment topic
    student_answer: str              # Extracted from PDF
    rubric: str                      # Grading criteria
    student_name: str (optional)     # For database
    sample_solution: str (optional)  # From KB
}
```

### Output Schema (EvaluationSchema)

```python
EvaluationSchema {
    # Section 1: Executive Summary
    score: str                       # "6" (0-10)
    grade: str                       # "C" (A-F)
    feedback: str                    # Paragraph of feedback
    
    # Section 2: Rubric Breakdown
    rubric_breakdown: [
        {
            criteria: str            # Criterion name
            score: str               # Points earned
            max_score: str           # Max possible
            feedback: str            # Specific feedback
        },
        ...
    ]
    
    # Section 3: Gap Analysis
    missing_concepts: [
        {
            concept: str             # Missing concept name
            importance: str          # HIGH/MEDIUM/LOW
            explanation: str         # Why it matters
        },
        ...
    ]
    
    # Section 4: Bridge Guidance
    bridge_guidance: str             # Corrective guidance
    
    # Section 5: Suggested Resources
    suggested_resources: [
        {
            title: str               # Resource title
            description: str         # What to learn
            action_item: str         # Specific action
        },
        ...
    ]
    
    # Section 6: Metadata
    metadata: {
        complexity_level: str        # Beginner/Intermediate/Advanced
        ai_confidence: str           # 0-100%
        plagiarism_similarity: str   # 0-100%
    }
}
```

---

## Processing Pipeline

```
┌────────────────────────────────────────────────────────────────────┐
│                    EVALUATION PIPELINE                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  INPUT → EXTRACT → RETRIEVE → LLM → PARSE → VALIDATE → OUTPUT   │
│   PDF    TEXT      KB DATA    EVAL  JSON    SCHEMA     DICT      │
│   │       │        │          │     │       │         │          │
│   └───────┼────────┼──────────┼─────┼───────┼─────────┘          │
│           └────────┴──────────┼─────┴───────┘                     │
│                               ▼                                   │
│                     ┌──────────────────┐                         │
│                     │ EVALUATION RESULT │                         │
│                     │ (EvaluationSchema)│                         │
│                     └──────────────────┘                         │
│                               │                                   │
│             ┌─────────────────┼─────────────────┐                │
│             ▼                 ▼                 ▼                │
│        Database          Frontend          PDF Report            │
│        (Storage)         (Display)         (Download)            │
│                                                                   │
└────────────────────────────────────────────────────────────────────┘
```

---

## Error Handling & Fallbacks

```
PDF Processing
    │
    ├─ Success: Extract text
    │    ▼
    └─ Fail: Handle gracefully
         ▼
       Error Message

LLM Evaluation
    │
    ├─ Success: Valid JSON response
    │    ▼
    │ Parse to EvaluationSchema
    │    ▼
    └─ Fail: Return error dict
         ▼
       {"error": "Evaluation failed: ..."}

PDF Generation
    │
    ├─ Success: Render all sections
    │    ▼
    └─ Fail: Render available sections
         ▼
       Return partial PDF bytes

Frontend Display
    │
    ├─ Success: Show results
    │    ▼
    └─ Fail: Show error message
         ▼
       "Evaluation Error: ..."
```

---

## System Requirements

### Software
- Python 3.10+
- Streamlit 1.x
- LangChain + LangChain Groq
- Pydantic
- FPDF2
- PyPDF2

### APIs
- Groq API (LLM)
- Supabase (Database - optional)

### Performance
- LLM Response: 10-30 seconds
- PDF Generation: 1-2 seconds
- Total Time: < 1 minute per evaluation

---

## Scalability Considerations

### Current Capacity
- Handles multiple concurrent evaluations
- Database scales with Supabase
- LLM API handles rate limits

### Future Optimization
- Cache common guidelines
- Batch process multiple PDFs
- Implement evaluation templates
- Add async PDF generation

---

**Architecture Version:** 1.0  
**Last Updated:** February 5, 2026  
**Status:** Production Ready
