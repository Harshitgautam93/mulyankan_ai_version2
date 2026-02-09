# COMPLETE SETUP CHECKLIST - Mulyankan AI

## ✅ STEP 1: UPDATE requirements.txt

Make sure all dependencies are listed:

```
# Core Frameworks
langchain>=0.3.0
langchain-core>=1.0.0
langchain-community>=0.3.0
streamlit>=1.28.0

# Integration & Models
langchain-groq
langchain-huggingface
transformers>=5.0.0
huggingface-hub>=1.3.0

# Authentication & UI
st-login-form
st-supabase-connection

# Database & Logic
supabase
python-dotenv
pydantic>=2.0.0
langgraph
PyPDF2
```

Run in terminal:
```powershell
pip install -r requirements.txt
```

---

## ✅ STEP 2: VERIFY .streamlit/secrets.toml

File location: `c:\Users\LENOVO\mulyankan_ai_version_2\.streamlit\secrets.toml`

Content should be:
```toml
# Supabase Configuration
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-anon-key"

# Groq Configuration
GROQ_API_KEY = "your-groq-api-key"
GROQ_MODEL = "llama-3.3-70b-versatile"
```

---

## ✅ STEP 3: CREATE SUPABASE TABLES (CRITICAL!)

Go to: **Supabase Dashboard** → **SQL Editor** → **New Query**

Run this complete SQL setup:

```sql
-- ============================================
-- TABLE 1: Users (Authentication)
-- ============================================
DROP TABLE IF EXISTS public.users CASCADE;

CREATE TABLE public.users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_username ON public.users(username);

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Allow ANYONE to insert (signup)
CREATE POLICY "Allow signup - anyone can insert"
ON public.users FOR INSERT
WITH CHECK (true);

-- Allow users to read their own data
CREATE POLICY "Users can view their own data"
ON public.users FOR SELECT
USING (auth.uid() = id);

-- Allow users to update their own data
CREATE POLICY "Users can update their own data"
ON public.users FOR UPDATE
USING (auth.uid() = id);

-- ============================================
-- TABLE 2: Sessions (Track logged-in users)
-- ============================================
DROP TABLE IF EXISTS public.sessions CASCADE;

CREATE TABLE public.sessions (
  id BIGSERIAL PRIMARY KEY,
  username TEXT NOT NULL,
  user_id TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_sessions_user_id ON public.sessions(user_id);
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own session"
ON public.sessions FOR SELECT
USING (true);

CREATE POLICY "Users can insert their own session"
ON public.sessions FOR INSERT
WITH CHECK (true);

CREATE POLICY "Users can delete their own session"
ON public.sessions FOR DELETE
USING (true);

-- ============================================
-- TABLE 3: Assignments (Knowledge Base)
-- ============================================
DROP TABLE IF EXISTS public.assignments CASCADE;

CREATE TABLE public.assignments (
  id BIGSERIAL PRIMARY KEY,
  content TEXT,
  metadata JSONB,
  embedding vector(384),
  created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_assignments_embedding 
ON public.assignments USING ivfflat (embedding vector_cosine_ops);

ALTER TABLE public.assignments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read assignments"
ON public.assignments FOR SELECT
USING (true);

CREATE POLICY "Authenticated users can insert"
ON public.assignments FOR INSERT
WITH CHECK (true);

-- ============================================
-- TABLE 4: Evaluations (Results)
-- ============================================
DROP TABLE IF EXISTS public.evaluations CASCADE;

CREATE TABLE public.evaluations (
  id BIGSERIAL PRIMARY KEY,
  topic TEXT NOT NULL,
  student_name TEXT NOT NULL,
  score TEXT,
  grade TEXT,
  feedback TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_evaluations_student ON public.evaluations(student_name);
ALTER TABLE public.evaluations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read evaluations"
ON public.evaluations FOR SELECT
USING (true);

CREATE POLICY "Authenticated users can insert"
ON public.evaluations FOR INSERT
WITH CHECK (true);

-- ============================================
-- TABLE 5: Vector Search Function
-- ============================================
CREATE OR REPLACE FUNCTION match_assignments(
  query_embedding vector(384),
  match_count int DEFAULT 5,
  match_threshold float DEFAULT 0.6
)
RETURNS TABLE (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
LANGUAGE sql STABLE
AS $$
  SELECT
    assignments.id,
    assignments.content,
    assignments.metadata,
    1 - (assignments.embedding <=> query_embedding) AS similarity
  FROM assignments
  WHERE 1 - (assignments.embedding <=> query_embedding) > match_threshold
  ORDER BY assignments.embedding <=> query_embedding
  LIMIT match_count;
$$;
```

---

## ✅ STEP 4: VERIFY frontend/app.py

The app should already have proper auth flow. Key sections:

1. **Line ~90**: `login_form()` is called at top level (every rerun)
2. **Line ~96**: Checks `st.session_state.get("authenticated")`
3. **Line ~103**: Saves session to Supabase if authenticated
4. **Line ~115**: Renders dashboard if authenticated
5. **Line ~220**: Shows login form if NOT authenticated

---

## ✅ STEP 5: VERIFY backend/database.py

The `save_session()` and `delete_session()` functions exist:

- `save_session(username, user_id)` - Called after login
- `delete_session(user_id)` - Called after logout
- `get_session(user_id)` - For future session retrieval

---

## ✅ STEP 6: INSTALL ALL PACKAGES

Run this to ensure everything is installed:

```powershell
pip install -r requirements.txt --upgrade
```

---

## ✅ FINAL: START THE APP

```powershell
cd C:\Users\LENOVO\mulyankan_ai_version_2
streamlit run frontend/app.py
```

---

## 🔐 EXPECTED FLOW

1. **Browser opens** → Login form appears
2. **Click "Sign Up"** → Creates account in Supabase `users` table
3. **Auto-login** → Sets `st.session_state["authenticated"] = True`
4. **Session saved** → Saved to `sessions` table
5. **Redirect** → Dashboard appears automatically
6. **Dashboard features** → PDF upload, evaluation, knowledge base, analytics

---

## 🚨 If errors occur:

1. **"Module not found"** → Run `pip install -r requirements.txt`
2. **"Table not found"** → Run the SQL setup above
3. **"RLS policy error"** → Check RLS policies in Supabase SQL setup
4. **"Auth error"** → Verify `.streamlit/secrets.toml` has correct URLs and keys
5. **"Redirect not working"** → Check that `login_form()` is at top level in app.py

---

## 📋 CHECKLIST BEFORE STARTING

- [ ] requirements.txt updated
- [ ] .streamlit/secrets.toml verified
- [ ] All 5 tables created in Supabase
- [ ] RLS policies created correctly
- [ ] Vector function created
- [ ] pip install -r requirements.txt executed
- [ ] No import errors in terminal

Then run: `streamlit run frontend/app.py`
