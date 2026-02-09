# 🚀 STARTUP CHECKLIST - DO THIS NOW

## Step 1: Run Supabase SQL Setup

Go to: https://supabase.com → Your Project → SQL Editor → New Query

Copy/Paste **ENTIRE** SQL from `COMPLETE_SETUP_GUIDE.md` (Lines: Create users table → Vector search function)

Click **RUN** and wait for success ✅

---

## Step 2: Verify Configuration Files

### ✅ Check .streamlit/secrets.toml
File: `c:\Users\LENOVO\mulyankan_ai_version_2\.streamlit\secrets.toml`

Must have:
- SUPABASE_URL = "your-supabase-url"
- SUPABASE_KEY = "your-supabase-anon-key"
- GROQ_API_KEY = "your-groq-api-key"
- GROQ_MODEL = "llama-3.3-70b-versatile"

### ✅ Check backend/.env
File: `c:\Users\LENOVO\mulyankan_ai_version_2\backend\.env`

Must have SAME values as secrets.toml

---

## Step 3: Install All Dependencies

Run in terminal:

```powershell
cd C:\Users\LENOVO\mulyankan_ai_version_2
pip install -r requirements.txt --upgrade
```

Wait for completion ✅

---

## Step 4: Start the App

```powershell
streamlit run frontend/app.py
```

Browser will open at: `http://localhost:8501`

---

## Step 5: Test the Flow

1. **See login form** → ✅ OK
2. **Click "Sign Up"** → Create test account (user@test.com / password123)
3. **Should auto-login** → ✅ If you see DASHBOARD, success!
4. **Dashboard appears** → ✅ Login works!

---

## 🚨 TROUBLESHOOTING

| Error | Solution |
|-------|----------|
| "Table not found" | Run SQL setup in Supabase SQL Editor |
| "RLS policy error" | Run the complete SQL (all 5 tables + policies) |
| "Module not found" | Run `pip install -r requirements.txt` |
| "Auth error" | Check `.streamlit/secrets.toml` has correct URL/KEY |
| "No redirect to dashboard" | Check `login_form()` is at line 93 in app.py |
| "Import error for st_login_form" | Already installed, but run `pip install st-login-form` again |

---

## ✅ IF ALL ABOVE IS DONE

Run this final check:

```powershell
cd C:\Users\LENOVO\mulyankan_ai_version_2
python -c "from st_login_form import login_form; print('✅ All imports working')"
streamlit run frontend/app.py
```

You should be able to **sign up, auto-login, and see the dashboard**.

Good luck! 🎉
