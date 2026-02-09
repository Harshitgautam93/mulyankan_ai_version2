# 🎓 Mulyankan AI - Intelligent Assignment Evaluation System

**A comprehensive AI-powered system for evaluating student assignments with detailed feedback, scoring, and personalized learning recommendations.**

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [System Architecture](#system-architecture)
4. [Prerequisites](#prerequisites)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [Usage](#usage)
8. [Project Structure](#project-structure)
9. [API & Database Schema](#api--database-schema)
10. [Troubleshooting](#troubleshooting)

---

## 🌟 Overview

Mulyankan AI is an intelligent assignment evaluation platform that leverages:
- **Groq LLM** (Mixtral/Llama 3.3) for expert-level grading
- **Supabase** for database and vector storage
- **Streamlit** for professional UI/UX
- **Advanced evaluation** with gap analysis and personalized resources

The system provides:
- ✅ Automated grading with detailed rubric breakdowns
- ✅ Gap analysis highlighting missing concepts
- ✅ Personalized learning resources and recommendations
- ✅ Student roll number tracking for unique identification
- ✅ Professional PDF reports with 7-section evaluation
- ✅ Real-time analytics dashboard with performance insights
- ✅ Vector database knowledge base for improved accuracy

---

## ✨ Features

### 1. **Intelligent Evaluation Engine**
- **7-Section Report Structure:**
  1. Assignment Topic summary
  2. Evaluation Summary (Score, Grade, Feedback)
  3. Detailed Scoring Breakdown (rubric-based)
  4. Concepts Needing Improvement (gap analysis)
  5. How to Improve (bridge guidance)
  6. Recommended Resources (learning materials)
  7. Assessment Details (complexity, confidence, uniqueness)

### 2. **Student-Centric Tracking**
- Roll number as unique identifier
- Name, topic, and submission tracking
- Historical evaluation records
- Student performance analytics

### 3. **Professional Dashboard (Streamlit)**
- **Tab 1: Student Evaluation**
  - Upload student PDF answers
  - Define grading rubric
  - Run AI evaluation
  - Download PDF report
  
- **Tab 2: Knowledge Base**
  - Upload sample solutions/guidelines
  - Vector database indexing for context retrieval
  - Automatic knowledge retrieval during evaluation
  
- **Tab 3: Analytics**
  - Score distributions
  - Grade performance breakdown
  - Topic difficulty analysis
  - Student performance ranking
  - Trend analysis over time
  - Recent evaluations table with roll numbers

### 4. **Persistent Results**
- Session state management prevents result loss
- Evaluation data saved to database
- Download reports with roll number identification

---

## 🏗️ System Architecture

### Data Flow
```
Student Submission (PDF + Metadata)
         ↓
PDF Text Extraction (PyPDF2)
         ↓
Retrieve Similar Guidelines (Vector DB)
         ↓
LLM Evaluation (Groq - Mixtral)
         ↓
Parse to EvaluationSchema (Pydantic)
         ↓
Save to Database (Supabase)
         ↓
Generate PDF Report (FPDF2)
         ↓
Display Results + Download
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Streamlit 1.28+ | UI/UX Dashboard |
| LLM | Groq (Mixtral/Llama) | Evaluation Engine |
| Database | Supabase | Persistent Storage |
| Vector DB | Supabase Vectors | Knowledge Retrieval |
| PDF Processing | PyPDF2 + FPDF2 | Text Extract & Report Gen |
| ML/NLP | HuggingFace Embeddings | Semantic Search |
| API Framework | LangChain | LLM Orchestration |

---

## 📦 Prerequisites

### System Requirements
- **Python**: 3.10 or higher
- **OS**: Windows, macOS, or Linux
- **RAM**: 4GB minimum (8GB recommended)
- **Internet**: Required for Groq API and Supabase

### External Accounts
1. **Groq API Key** - [Get free API key](https://console.groq.com)
2. **Supabase Account** - [Create account](https://supabase.com)
3. **Git** (for version control)

### Optional
- **Tesseract OCR** (for scanned PDFs - Windows installation provided)

---

## 🚀 Installation & Setup

### Step 1: Clone Repository
```bash
git clone git@github.com:Harshitgautam93/mulyankan_ai_version2.git
cd mulyankan_ai_version2
```

### Step 2: Create Virtual Environment
```powershell
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create Configuration Files
Create `backend/.env`:
```env
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-service-key
```

Create `.streamlit/secrets.toml`:
```toml
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-anon-key"
GROQ_API_KEY = "your-groq-api-key"
GROQ_MODEL = "llama-3.3-70b-versatile"
```

### Step 5: Set Up Supabase Database
1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Create a new project
3. Run the following SQL in SQL Editor:

```sql
-- Create evaluations table
CREATE TABLE evaluations (
    id BIGSERIAL PRIMARY KEY,
    student_name VARCHAR(255) NOT NULL,
    student_roll VARCHAR(50) UNIQUE NOT NULL,
    topic VARCHAR(255) NOT NULL,
    score VARCHAR(10),
    grade VARCHAR(2),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create assignments table (for vector storage)
CREATE TABLE assignments (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(384),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_roll_number ON evaluations(student_roll);
CREATE INDEX idx_topic ON evaluations(topic);
CREATE INDEX idx_created_at ON evaluations(created_at DESC);
CREATE INDEX ON assignments USING ivfflat (embedding vector_cosine_ops);

-- Enable Vector extension
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## ⚙️ Configuration

### Groq LLM Models
Available models:
- `llama-3.3-70b-versatile` ✓ Recommended
- `mixtral-8x7b-32768`
- `llama-2-70b-4096`

Change in `.env` or `secrets.toml`

### Evaluation Temperature
Currently set to `0` (deterministic). Modify in `backend/main.py`:
```python
ChatGroq(
    model=os.getenv("GROQ_MODEL"),
    temperature=0  # Change this for more creative responses
)
```

---

## 📖 Usage

### Start the Application
```bash
streamlit run frontend/app.py
```

Opens dashboard at: `http://localhost:8501`

### Login Credentials (Default)
| Username | Password |
|----------|----------|
| admin | admin123 |
| teacher | teacher123 |

### Workflow

#### 1️⃣ **Evaluate Assignment (Tab 1)**
1. Enter student name and **roll number** (unique identifier)
2. Enter assignment topic (e.g., "Photosynthesis")
3. Define grading rubric with evaluation criteria
4. Upload student's PDF answer
5. Click "Evaluate" and wait for AI analysis
6. Review results (Score, Grade, Feedback)
7. **Download PDF Report** (filename includes roll number)

#### 2️⃣ **Upload Guidelines (Tab 2)**
1. Upload sample solution or model answer PDF
2. System automatically indexes content in vector database
3. This improves evaluation accuracy for similar topics

#### 3️⃣ **View Analytics (Tab 3)**
1. **Summary Metrics**: Total evaluations, average score, unique students, topics covered
2. **Score Distributions**: Bar chart of score frequencies
3. **Grade Breakdown**: Performance by grade level
4. **Topic Analysis**: Difficulty level per topic
5. **Student Ranking**: Top and struggling students
6. **Recent Evaluations**: Table with roll numbers (newest first)
7. **Trends**: Line chart showing evaluation progress over time

---

## 📁 Project Structure

```
mulyankan_ai_version2/
├── backend/
│   ├── __init__.py
│   ├── .env                    # Configuration (add your keys here)
│   ├── main.py                 # Core evaluation engine
│   ├── database.py             # Supabase integration & analytics
│   ├── pdf_utils.py            # PDF text extraction utilities
│   └── logs/                   # Extracted text logs
│
├── frontend/
│   ├── __init__.py
│   ├── app.py                  # Streamlit dashboard
│   ├── pdf_generator.py        # PDF report generation
│   └── logo.png                # UI logo
│
├── scripts/
│   └── set_tesseract_cmd.ps1   # Tesseract OCR setup (Windows)
│
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
└── .streamlit/
    └── secrets.toml            # Streamlit secrets (local only)
```

---

## 🔌 API & Database Schema

### EvaluationSchema (Output Format)

```python
{
  "score": "7",                  # 0-10
  "grade": "B",                  # A, B, C, D, F
  "feedback": "Strong understanding...",
  
  "rubric_breakdown": [
    {
      "criteria": "Concept Understanding",
      "score": "7",
      "max_score": "10",
      "feedback": "Good grasp of basic concepts..."
    }
  ],
  
  "missing_concepts": [
    {
      "concept": "Advanced Theory",
      "importance": "HIGH",
      "explanation": "This concept is crucial for..."
    }
  ],
  
  "bridge_guidance": "To improve, focus on...",
  
  "suggested_resources": [
    {
      "title": "Khan Academy - Topic",
      "description": "Learn advanced concepts",
      "action_item": "Complete 3 videos on..."
    }
  ],
  
  "metadata": {
    "complexity_level": "Intermediate",
    "ai_confidence": "92",
    "plagiarism_similarity": "5"
  }
}
```

### Database Tables

#### `evaluations` Table
| Column | Type | Purpose |
|--------|------|---------|
| id | BIGSERIAL | Primary key |
| student_name | VARCHAR(255) | Student name |
| student_roll | VARCHAR(50) | **Unique identifier** |
| topic | VARCHAR(255) | Assignment topic |
| score | VARCHAR(10) | Numeric score (e.g., "7") |
| grade | VARCHAR(2) | Letter grade (A-F) |
| feedback | TEXT | Evaluation feedback |
| created_at | TIMESTAMP | Submission timestamp |

#### `assignments` Table (Vector DB)
| Column | Type | Purpose |
|--------|------|---------|
| id | BIGSERIAL | Primary key |
| content | TEXT | Sample solution text |
| metadata | JSONB | Optional metadata |
| embedding | VECTOR(384) | Semantic embeddings |
| created_at | TIMESTAMP | Upload timestamp |

---

## 🐛 Troubleshooting

### Issue: "Groq API Key not found"
**Solution:**
1. Check `.env` file has `GROQ_API_KEY`
2. Check `secrets.toml` has `GROQ_API_KEY`
3. Restart Streamlit: `Ctrl+C` then `streamlit run frontend/app.py`

### Issue: "Supabase connection failed"
**Solution:**
1. Verify `SUPABASE_URL` and `SUPABASE_KEY`
2. Check internet connection
3. Verify Supabase tables exist (run SQL setup from Step 5)
4. Ensure `SUPABASE_KEY` is the **anon key**, not service role key

### Issue: "PDF evaluation returns error"
**Solution:**
1. Ensure PDF is text-based (not image-scanned)
2. Verify all form fields are filled (including Roll Number)
3. Check PDF file size (max 50MB recommended)
4. View error message in terminal for details

### Issue: "Analytics page shows no data"
**Solution:**
1. Complete at least one evaluation first
2. Check Supabase database has records in `evaluations` table
3. Click "Refresh Data" button in analytics tab
4. Check browser console (F12) for JavaScript errors

### Issue: "Results disappear after evaluation"
**Solution:**
This has been fixed with session state persistence. If still experiencing:
1. Check browser console for errors
2. Clear browser cache: `Ctrl+Shift+Delete`
3. Restart Streamlit

### Issue: "Roll number not visible in analytics"
**Solution:**
1. Ensure Supabase table has `student_roll` column
2. Re-run SQL setup with ALTER TABLE if missing
3. Restart app and re-evaluate with roll number

---

## 🔐 Security Best Practices

### Never commit secrets!
✅ **DO:**
- Keep API keys in `.env` (local file)
- Keep keys in `.streamlit/secrets.toml` (local file)
- Add `.env` and `secrets.toml` to `.gitignore`

❌ **DON'T:**
- Commit API keys to GitHub
- Share `.env` files
- Use demo keys in production

### Credentials Rotation
1. Regularly rotate Groq API keys
2. Regenerate Supabase keys monthly
3. Update `.env` and restart application

---

## 📊 Performance Metrics

### Typical Performance
| Operation | Time | Notes |
|-----------|------|-------|
| PDF Evaluation | 15-30 sec | Depends on LLM response |
| PDF Report Generation | 1-2 sec | FPDF processing |
| Analytics Dashboard Load | 2-5 sec | Supabase queries |
| Vector Search | 500ms | Knowledge base lookup |

### Optimization Tips
1. Use shorter rubrics for faster evaluation
2. Limit analytics time range for large datasets
3. Cache vector embeddings for repeated topics
4. Batch process multiple PDFs offline

---

## 🤝 Contributing

To contribute improvements:
1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Push to GitHub
5. Create a pull request

---

## 📝 License

This project is for educational purposes. Modify as needed for your institution.

---

## 📞 Support & Questions

For issues or questions:
1. Check the Troubleshooting section above
2. Review logs in `backend/logs/`
3. Check Supabase dashboard for database issues
4. Review Groq API documentation

---

## 🎯 Roadmap

**Future Enhancements:**
- [ ] Batch evaluation of multiple PDFs
- [ ] Custom evaluation rubric templates
- [ ] Plagiarism detection integration
- [ ] Export analytics reports to Excel
- [ ] Multi-language support
- [ ] Mobile app for offline evaluation

---

**Last Updated:** February 9, 2026  
**Version:** 2.0 (Roll Number Support & Enhanced PDF Reports)  
**Status:** Production Ready ✅

