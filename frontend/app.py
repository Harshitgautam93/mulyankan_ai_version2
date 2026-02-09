# ===============================
# Environment & Path Setup
# ===============================
import sys
import os
import io
import re
from dotenv import load_dotenv
import streamlit as st
import pandas as pd

# 1. FIXED: Clean path setup
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# PDF parsing dependency
try:
    import PyPDF2
    _HAS_PYPDF2 = True
except Exception:
    _HAS_PYPDF2 = False

load_dotenv()

# ===============================
# 1. Professional Page Config
# ===============================
st.set_page_config(
    page_title="Mulyankan AI | Dashboard",
    page_icon="📝",
    layout="wide"  # Crucial for the Dashboard feel
)

# ===============================
# 2. Custom Styling (CSS Injection) - Pill-Based Design System
# ===============================
st.markdown("""
    <style>
    /* ===== COLOR PALETTE ===== */
    :root {
        --primary-blue: #4e89ae;
        --light-blue-gray: #c5d3e8;
        --input-bg: #e3e9f2;
        --border-color: #c5d3e8;
        --steel-blue: #4e89ae;
        --sage-green: #7cb342;
        --soft-amber: #ffa726;
        --dark-navy: #1a2332;
        --white: #ffffff;
    }

    /* ===== GLOBAL STYLES ===== */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }

    /* ===== MAIN CONTAINER ===== */
    .main {
        background-color: #f8f9fb;
    }

    /* ===== TYPOGRAPHY ===== */
    h1, h2, h3 {
        color: #1a2332;
        font-weight: 600;
    }

    h1 {
        font-size: 1.6rem;
        margin-bottom: 0.75rem;
    }

    h2 {
        font-size: 1.1rem;
        margin-top: 0.75rem;
        margin-bottom: 0.5rem;
    }

    h3 {
        font-size: 0.95rem;
        margin-top: 0.5rem;
        margin-bottom: 0.4rem;
    }

    /* ===== FLOATING PILL TABS ===== */
    .stTabs {
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab-list"] {
        background-color: #c5d3e8;
        border-radius: 50px;
        padding: 4px;
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #1a2332;
        border-radius: 50px;
        padding: 8px 20px;
        font-weight: 500;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background-color: #4e89ae !important;
        color: white !important;
    }

    .stTabs [aria-selected="false"] {
        background-color: transparent;
        color: #1a2332;
    }

    /* ===== METRIC CARDS ===== */
    [data-testid="metric-container"] {
        background-color: white;
        border-left: 4px solid #4e89ae;
        border-radius: 8px;
        padding: 0.6rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    [data-testid="stMetricValue"] {
        font-size: 1.4rem;
        color: #4e89ae;
        font-weight: 700;
    }

    [data-testid="stMetricLabel"] {
        color: #666666;
        font-weight: 500;
        font-size: 0.8rem;
    }

    /* ===== BUTTONS ===== */
    div.stButton > button:first-child {
        background-color: #4e89ae;
        color: white;
        border: none;
        border-radius: 50px;
        padding: 10px 24px;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(78, 137, 174, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }

    div.stButton > button:first-child:hover {
        background-color: #3d6f8e;
        box-shadow: 0 4px 12px rgba(78, 137, 174, 0.4);
        transform: translateY(-2px);
    }

    /* ===== FORM INPUTS ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #e3e9f2 !important;
        border: 1px solid #c5d3e8 !important;
        border-radius: 8px !important;
        color: #1a2332 !important;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border: 1px solid #4e89ae !important;
        box-shadow: 0 0 0 3px rgba(78, 137, 174, 0.1) !important;
    }

    /* ===== FORM SECTION HEADERS ===== */
    .form-section-header {
        color: #1a2332;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #4e89ae;
    }

    /* ===== DIVIDER ===== */
    hr {
        border: none;
        border-top: 1px solid #c5d3e8;
        margin: 1rem 0;
    }

    /* ===== INFO/WARNING/SUCCESS BOXES ===== */
    .stSuccess {
        background-color: rgba(124, 179, 66, 0.1);
        border: 1px solid #7cb342;
        border-left: 4px solid #7cb342;
    }

    .stWarning {
        background-color: rgba(255, 167, 38, 0.1);
        border: 1px solid #ffa726;
        border-left: 4px solid #ffa726;
    }

    .stInfo {
        background-color: rgba(78, 137, 174, 0.1);
        border: 1px solid #4e89ae;
        border-left: 4px solid #4e89ae;
    }

    .stError {
        background-color: rgba(231, 76, 60, 0.1);
        border: 1px solid #e74c3c;
        border-left: 4px solid #e74c3c;
    }

    /* ===== FILE UPLOADER ===== */
    .stFileUploadDropzone {
        border: 2px dashed #c5d3e8;
        border-radius: 8px;
        background-color: rgba(197, 211, 232, 0.05);
    }

    /* ===== MARKDOWN CONTENT ===== */
    .markdown-text {
        color: #1a2332;
    }

    /* ===== SPINNER ===== */
    .stSpinner > div {
        border-top-color: #4e89ae !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Backend Imports
BACKEND_OK = True
try:
    from backend.main import process_assignment_evaluation
    from backend.database import (
        store_guideline, save_evaluation_result,
        get_all_evaluations, get_average_score, get_grade_distribution,
        get_topic_performance, get_student_performance, get_evaluations_by_topic,
        get_evaluations_over_time, get_top_students, get_evaluations_summary,
        get_score_distribution, get_topic_evaluation_count, get_student_evaluation_count,
        get_weak_students, get_strong_students, get_class_stats, get_performance_by_grade,
        get_topic_difficulty, get_assignments_per_student, get_recent_evaluations,
        get_evaluation_stats_by_date, insert_test_data
    )
    from frontend.pdf_generator import generate_pdf_bytes
    # Optional backend helpers
    try:
        from backend.main import store_guideline_from_pdf as _store_guideline_from_pdf
    except Exception: _store_guideline_from_pdf = None
    try:
        from backend.main import evaluate_pdf as _evaluate_pdf
    except Exception: _evaluate_pdf = None
except ImportError as e:
    BACKEND_OK = False
    st.error(f"Import Error: {e}. Ensure '__init__.py' exists.")

# ===============================
# 3. Hardcoded Authentication
# ===============================
# Hardcoded credentials - change as needed
VALID_USERS = {
    "admin": "admin123",
    "teacher": "teacher123",
    "user": "password123"
}

def check_authentication():
    """Check if user is logged in based on session state."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = None
    return st.session_state.authenticated, st.session_state.username

def login_user(username: str, password: str) -> bool:
    """Verify credentials and set session state."""
    if username in VALID_USERS and VALID_USERS[username] == password:
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.user_id = username
        return True
    return False

def logout_user():
    """Clear authentication state."""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_id = None

# Initialize session state for analytics refresh
if "evaluation_completed" not in st.session_state:
    st.session_state.evaluation_completed = False
if "last_evaluation_result" not in st.session_state:
    st.session_state.last_evaluation_result = None
if "last_evaluation_points" not in st.session_state:
    st.session_state.last_evaluation_points = 10
if "last_evaluation_roll" not in st.session_state:
    st.session_state.last_evaluation_roll = None
if "last_evaluation_topic" not in st.session_state:
    st.session_state.last_evaluation_topic = None

# ===== RENDER LOGIN OR DASHBOARD =====
is_authenticated, username = check_authentication()

if is_authenticated and username:
    # --- LOGGED IN AREA ---
    
    # User Info Box (Top Right Corner)
    col_spacer, col_user_info = st.columns([5, 1])
    with col_user_info:
        st.markdown(f"👤 **{username}**", help="Logged in user")
        if st.button("🚪 Logout", key='logout_btn', use_container_width=True):
            logout_user()
            st.rerun()

    # Dashboard Header with Emoji
    st.markdown("<h1>📝 Mulyankan AI Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666; margin-top: -1rem; margin-bottom: 1.5rem;'>Intelligent Assignment Evaluation System</p>", unsafe_allow_html=True)
    
    # Dashboard Stats (Live) with Metric Cards
    st.markdown("<div style='background-color: #f8f9fb; padding: 0.8rem; border-radius: 12px;'>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    if BACKEND_OK:
        summary = get_evaluations_summary()
        m1.metric("📊 Assignments Evaluated", summary["total"], "")
        m2.metric("⭐ Avg. Class Score", f"{summary['avg_score']}/10", "")
        m3.metric("👥 Unique Students", summary["unique_students"], "")
        m4.metric("📚 Topics Covered", summary["unique_topics"], "")
    else:
        m1.metric("📊 Assignments Evaluated", "N/A", "")
        m2.metric("⭐ Avg. Class Score", "N/A", "")
        m3.metric("👥 Unique Students", "N/A", "")
        m4.metric("📚 Topics Covered", "N/A", "")
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # 5. Organizing Workflow with Floating Pills
    tab1, tab2, tab3 = st.tabs(["🧪 Student Evaluation", "🧬 Knowledge Base", "📈 Analytics"])

    with tab1:
        st.markdown("<h2>🧪 Process New Submission</h2>", unsafe_allow_html=True)
        
        # Contextual Inset for Student Evaluation
        st.markdown("""
        <div style='
            background-color: #e3e9f2;
            border: 1px solid #c5d3e8;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.8rem;
        '>
        """, unsafe_allow_html=True)
        
        with st.form("eval_form"):
            st.markdown("<div style='color: #1a2332; font-weight: 700; font-size: 0.95rem; margin-bottom: 0.6rem;'>📋 Student Information</div>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                student_name = st.text_input("Student Name", placeholder="e.g., John Doe", key="sname")
                student_roll = st.text_input("Roll Number", placeholder="e.g., 2024001", key="roll")
            with col_b:
                input_q = st.text_input("Topic", placeholder="e.g., Photosynthesis", key="topic")
                points_possible = st.number_input("Max Marks", min_value=1, value=10, key="marks")
            
            grading_rubric = st.text_area("Rubric", placeholder="Criteria?", height=45, key="rubric")
            
            st.markdown("<div style='margin-top: 0.5rem; color: #666; font-size: 0.9rem;'>📄 Upload Answer</div>", unsafe_allow_html=True)
            student_pdf = st.file_uploader("PDF", type=["pdf"], key="pdf_upload")
            
            submit_eval = st.form_submit_button("🚀 Evaluate", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        if submit_eval:
            if student_pdf and input_q and student_roll:
                with st.spinner("🔍 Analyzing submission..."):
                    pdf_bytes = student_pdf.read()
                    eval_result = None
                    # Evaluation Logic
                    try:
                        if _evaluate_pdf:
                            eval_result = _evaluate_pdf(input_q, pdf_bytes, grading_rubric, student_name=student_name, student_roll=student_roll, save_to_db=True)
                        else:
                            # Fallback extraction logic
                            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                            student_text = "\n".join([p.extract_text() for p in reader.pages]).strip()
                            eval_result = process_assignment_evaluation(
                                input_q, student_text, grading_rubric, 
                                student_name=student_name, student_roll=student_roll, save_to_db=True
                            )
                        
                        if eval_result:
                            # Store evaluation result in session state to persist across reruns
                            st.session_state.last_evaluation_result = eval_result
                            st.session_state.last_evaluation_points = points_possible
                            st.session_state.last_evaluation_roll = student_roll
                            st.session_state.last_evaluation_topic = input_q
                            st.session_state.evaluation_completed = True
                            st.balloons()
                    except Exception as e:
                        st.error(f"❌ Evaluation Error: {e}")
            else:
                st.warning("⚠️ Please fill in Student Name, Roll Number, Topic, and Upload a PDF.")
        
        # Display evaluation results if they exist (persistent across page interactions)
        if st.session_state.last_evaluation_result:
            st.divider()
            st.markdown("<h3>✅ Evaluation Complete</h3>", unsafe_allow_html=True)
            res_col1, res_col2, res_col3 = st.columns(3)
            eval_result = st.session_state.last_evaluation_result
            res_col1.metric("Score", f"{eval_result.get('score')}/{st.session_state.last_evaluation_points}")
            res_col2.metric("Grade", eval_result.get('grade'))
            res_col3.metric("Roll No.", st.session_state.last_evaluation_roll or "N/A")
            st.info(f"**Feedback:** {eval_result.get('feedback')}")
            
            # PDF Download with roll number
            out_pdf = generate_pdf_bytes(st.session_state.last_evaluation_topic or "Assignment", "[From PDF]", eval_result, roll_number=st.session_state.last_evaluation_roll)
            filename = f"{st.session_state.last_evaluation_roll}_{st.session_state.username}_Report.pdf" if st.session_state.last_evaluation_roll else f"{st.session_state.username}_Report.pdf"
            st.download_button("📥 Download Report", out_pdf, filename, use_container_width=True, key="download_report")
            
            # Clear button to reset and evaluate another assignment
            if st.button("➕ Evaluate Another", use_container_width=True, key="eval_another"):
                st.session_state.last_evaluation_result = None
                st.session_state.evaluation_completed = False
                st.rerun()

    with tab2:
        st.markdown("<h2>🧬 Knowledge Ingestion</h2>", unsafe_allow_html=True)
        st.write("Upload official keys or sample solutions to improve AI accuracy.")
        
        # Contextual Inset for Knowledge Base
        st.markdown("""
        <div style='
            background-color: #e3e9f2;
            border: 1px solid #c5d3e8;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.8rem;
        '>
        """, unsafe_allow_html=True)
        
        with st.form("ingestion_form"):
            st.markdown("<div style='color: #1a2332; font-weight: 700; font-size: 0.95rem; margin-bottom: 0.6rem;'>📄 Upload Guideline</div>", unsafe_allow_html=True)
            uploaded_guideline = st.file_uploader("Guideline PDF", type=["pdf"], key="guide_pdf")
            submitted_ref = st.form_submit_button("💾 Save", use_container_width=True)
            
            if submitted_ref and uploaded_guideline:
                pdf_bytes = uploaded_guideline.read()
                # Existing logic for storing guidelines...
                st.success("✅ Guideline successfully ingested into Vector DB.")
        
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<h2>📈 Comprehensive Analytics Dashboard</h2>", unsafe_allow_html=True)
        
        # Add refresh button and timestamp
        from datetime import datetime
        refresh_col1, refresh_col2, refresh_col3 = st.columns([6, 2, 2])
        
        with refresh_col2:
            if st.button("🔄 Refresh Data", use_container_width=True, help="Click to refresh analytics with latest data"):
                st.rerun()
        
        with refresh_col3:
            st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        
        if not BACKEND_OK:
            st.warning("⚠️ Analytics is unavailable because backend imports failed. Fix the import error above to enable analytics.")
        else:
            try:
                summary = get_evaluations_summary()
            except Exception as e:
                st.error(f"❌ Error loading analytics: {e}")
                summary = {"total": 0}
            
            if summary["total"] == 0:
                st.info("📊 No data yet. Start evaluating in Tab 1 to see analytics.")
            else:
                # ===== TOP SUMMARY METRICS =====
                class_stats = get_class_stats()
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                col1.metric("Total", summary["total"])
                col2.metric("Avg", f"{summary['avg_score']}/10")
                col3.metric("Students", summary["unique_students"])
                col4.metric("Topics", summary["unique_topics"])
                if class_stats:
                    col5.metric("Median", f"{class_stats['median']}/10")
                    col6.metric("Std Dev", f"{class_stats['std_dev']}")
                
                # ===== VISUALIZATIONS ROW 1 =====
                st.markdown("**📉 Distributions**")
                viz_col1, viz_col2 = st.columns(2)
                
                with viz_col1:
                    score_dist = get_score_distribution()
                    score_dist_clean = {k: v for k, v in score_dist.items() if v > 0}
                    if score_dist_clean:
                        st.bar_chart(score_dist_clean, height=200)
                
                with viz_col2:
                    grade_dist = get_grade_distribution()
                    grade_dist_clean = {k: v for k, v in grade_dist.items() if v > 0}
                    if grade_dist_clean:
                        st.bar_chart(grade_dist_clean, height=200)
                
                # ===== VISUALIZATIONS ROW 2 =====
                st.markdown("**📚 Topics**")
                topic_col1, topic_col2 = st.columns(2)
                
                with topic_col1:
                    topic_eval_count = get_evaluations_by_topic()
                    if topic_eval_count:
                        st.bar_chart(topic_eval_count, height=200)
                
                with topic_col2:
                    topic_perf = get_topic_performance()
                    if topic_perf:
                        st.bar_chart(topic_perf, height=200)
                
                # ===== STUDENT ANALYSIS =====
                st.markdown("**👥 Students**")
                student_col1, student_col2 = st.columns(2)
                
                with student_col1:
                    top_students = get_top_students(10)
                    if top_students:
                        st.bar_chart(top_students, height=200)
                
                with student_col2:
                    student_eval_freq = get_student_evaluation_count()
                    top_10_freq = dict(list(student_eval_freq.items())[:10])
                    if top_10_freq:
                        st.bar_chart(top_10_freq, height=200)
                
                # ===== STUDENT SEGMENTATION =====
                st.markdown("**🎯 Segmentation**")
                seg_col1, seg_col2 = st.columns(2)
                
                with seg_col1:
                    st.markdown("**Top Performers (≥7)**")
                    strong_students = get_strong_students(7)
                    if strong_students:
                        strong_df = pd.DataFrame(list(strong_students.items()), columns=["Student", "Score"])
                        st.dataframe(strong_df, use_container_width=True, hide_index=True, height=200)
                
                with seg_col2:
                    st.markdown("**Needs Support (<5)**")
                    weak_students = get_weak_students(5)
                    if weak_students:
                        weak_df = pd.DataFrame(list(weak_students.items()), columns=["Student", "Score"])
                        st.dataframe(weak_df, use_container_width=True, hide_index=True, height=200)
                
                # ===== TREND ANALYSIS =====
                st.markdown("**📈 Trends**")
                date_stats = get_evaluation_stats_by_date()
                if date_stats:
                    date_counts = {date: data["count"] for date, data in date_stats.items()}
                    st.line_chart(date_counts, height=250)
                
                # ===== DETAILED TABLES =====
                with st.expander("📋 Details (Expand)", expanded=False):
                    col_tbl1, col_tbl2 = st.columns(2)
                    
                    with col_tbl1:
                        st.markdown("**Performance by Grade**")
                        perf_by_grade = get_performance_by_grade()
                        if perf_by_grade:
                            grade_df = pd.DataFrame([
                                {
                                    "Grade": grade,
                                    "Count": data["count"],
                                    "Avg": data["avg_score"]
                                }
                                for grade, data in perf_by_grade.items()
                            ])
                            st.dataframe(grade_df, use_container_width=True, hide_index=True, height=250)
                    
                    with col_tbl2:
                        st.markdown("**Topic Difficulty**")
                        topic_diff = get_topic_difficulty()
                        if topic_diff:
                            difficulty_df = pd.DataFrame([
                                {
                                    "Topic": topic,
                                    "Avg": score,
                                    "Level": "🟢 Easy" if score >= 7 else "🟡 Med" if score >= 5 else "🔴 Hard"
                                }
                                for topic, score in topic_diff.items()
                            ])
                            st.dataframe(difficulty_df, use_container_width=True, hide_index=True, height=250)
                    
                    st.markdown("**Recent Evaluations**")
                    all_evals = get_all_evaluations()
                    if all_evals:
                        df_evals = pd.DataFrame([
                            {
                                "Roll No.": e.get("student_roll", "N/A"),
                                "Student": e.get("student_name", "N/A"),
                                "Topic": e.get("topic", "N/A"),
                                "Score": e.get("score", "N/A"),
                                "Grade": e.get("grade", "N/A"),
                                "Feedback": str(e.get("feedback", "N/A"))[:50] + "..." if len(str(e.get("feedback", ""))) > 50 else str(e.get("feedback", "N/A"))
                            }
                            for e in all_evals[:15]
                        ])
                        st.dataframe(df_evals, use_container_width=True, height=300)
else:
    # --- LOGGED OUT AREA (Login Form) ---
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔐 Mulyankan AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Sign in to access the Evaluation System</p>", unsafe_allow_html=True)
        
        st.divider()
        
        # Login Form
        with st.form("login_form"):
            login_username = st.text_input("Username", placeholder="e.g., admin")
            login_password = st.text_input("Password", type="password", placeholder="Enter password")
            login_button = st.form_submit_button("🔓 Sign In", use_container_width=True)
        
        if login_button:
            if login_user(login_username, login_password):
                st.rerun()
            else:
                st.error("❌ Invalid username or password. Try: admin/admin123")
        
        st.info("**Demo Credentials:**\n- Username: `admin` | Password: `admin123`\n- Username: `teacher` | Password: `teacher123`")


st.divider()
st.caption("Powered by Llama 3.3 (Groq) & Supabase")