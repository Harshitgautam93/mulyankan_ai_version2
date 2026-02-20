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

# Load environment variables from root .env file
load_dotenv(os.path.join(ROOT_DIR, ".env"))

# PDF parsing dependency
try:
    import PyPDF2
    _HAS_PYPDF2 = True
except Exception:
    _HAS_PYPDF2 = False

# Analytics & Visualization
try:
    import plotly.graph_objects as go
    import plotly.express as px
    _HAS_PLOTLY = True
except Exception:
    _HAS_PLOTLY = False

from datetime import datetime

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
    # Import database module directly to avoid name-binding races in Streamlit
    import backend.database as db_service
    
    # Map functions for easier access
    get_all_evaluations = db_service.get_all_evaluations
    get_average_score = db_service.get_average_score
    get_grade_distribution = db_service.get_grade_distribution
    get_topic_performance = db_service.get_topic_performance
    get_student_performance = db_service.get_student_performance
    get_evaluations_by_topic = db_service.get_evaluations_by_topic
    get_evaluations_over_time = db_service.get_evaluations_over_time
    get_top_students = db_service.get_top_students
    get_evaluations_summary = db_service.get_evaluations_summary
    get_score_distribution = db_service.get_score_distribution
    get_topic_evaluation_count = db_service.get_topic_evaluation_count
    get_student_evaluation_count = db_service.get_student_evaluation_count
    get_weak_students = db_service.get_weak_students
    get_strong_students = db_service.get_strong_students
    get_class_stats = db_service.get_class_stats
    get_performance_by_grade = db_service.get_performance_by_grade
    get_topic_difficulty = db_service.get_topic_difficulty
    get_assignments_per_student = db_service.get_assignments_per_student
    get_recent_evaluations = db_service.get_recent_evaluations
    get_evaluation_stats_by_date = db_service.get_evaluation_stats_by_date
    insert_test_data = db_service.insert_test_data
    save_evaluation_result = db_service.save_evaluation_result
    store_guideline = db_service.store_guideline
    
    # Optional Data Management functions (handled gracefully)
    delete_all_evaluations = getattr(db_service, 'delete_all_evaluations', None)
    delete_mock_data = getattr(db_service, 'delete_mock_data', None)

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
# 4. Analytics Data Fetching (Direct)
# ===============================
def cached_get_summary():
    # Caching removed for automatic reloading
    return get_evaluations_summary()

@st.cache_data(ttl=600)
def cached_get_all_evaluations():
    return get_all_evaluations()

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
                            # Debug: Check if result contains expected fields
                            if not eval_result.get('score') and not eval_result.get('feedback'):
                                st.warning(f"⚠️ Backend returned incomplete data. Response: {eval_result}")
                            
                            # Store evaluation result in session state to persist across reruns
                            st.session_state.last_evaluation_result = eval_result
                            st.session_state.last_evaluation_points = points_possible
                            st.session_state.last_evaluation_roll = student_roll
                            st.session_state.last_evaluation_topic = input_q
                            st.session_state.evaluation_completed = True
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Evaluation returned no result.")
                    except Exception as e:
                        st.error(f"❌ Evaluation Error: {e}")
                        import traceback
                        st.code(traceback.format_exc(), language="python")
            else:
                st.warning("⚠️ Please fill in Student Name, Roll Number, Topic, and Upload a PDF.")
        
        # Display evaluation results if they exist (persistent across page interactions)
        if st.session_state.last_evaluation_result:
            st.divider()
            eval_result = st.session_state.last_evaluation_result
            
            # Check for errors in the result
            if eval_result.get('feedback') and 'Evaluation error' in eval_result.get('feedback', ''):
                st.error(f"❌ {eval_result.get('feedback')}")
            else:
                st.markdown("<h3>✅ Evaluation Complete</h3>", unsafe_allow_html=True)
                
                # Quick metrics
                res_col1, res_col2, res_col3 = st.columns(3)
                res_col1.metric("Score", f"{eval_result.get('score', 'N/A')}/{st.session_state.last_evaluation_points}")
                res_col2.metric("Grade", eval_result.get('grade', 'N/A'))
                res_col3.metric("Roll No.", st.session_state.last_evaluation_roll or "N/A")
                
                # Main feedback
                st.subheader("📋 Feedback")
                st.info(eval_result.get('feedback', 'No feedback available'))
                
                # Topic Diagnostic (if applicable)
                if eval_result.get('topic_diagnostic'):
                    st.subheader("⚠️ Topic Assessment")
                    st.warning(eval_result.get('topic_diagnostic'))
                
                # Rubric Breakdown
                if eval_result.get('rubric_breakdown') and len(eval_result['rubric_breakdown']) > 0:
                    st.subheader("📊 Rubric Breakdown")
                    for item in eval_result['rubric_breakdown']:
                        if isinstance(item, dict):
                            col1, col2 = st.columns([3, 1])
                            criteria = item.get('criteria', 'N/A')
                            score = item.get('score', 'N/A')
                            max_score = item.get('max_score', '10')
                            feedback = item.get('feedback', '')
                            
                            with col1:
                                st.write(f"**{criteria}**")
                                st.caption(feedback)
                            with col2:
                                st.metric("", f"{score}/{max_score}")
                
                # Missing Concepts
                if eval_result.get('missing_concepts') and len(eval_result['missing_concepts']) > 0:
                    st.subheader("🔍 Missing Concepts")
                    for concept in eval_result['missing_concepts']:
                        if isinstance(concept, dict):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**{concept.get('concept', 'N/A')}**")
                                st.caption(concept.get('explanation', ''))
                            with col2:
                                importance = concept.get('importance', 'MEDIUM')
                                if importance == 'HIGH':
                                    st.error(importance)
                                elif importance == 'MEDIUM':
                                    st.warning(importance)
                                else:
                                    st.info(importance)
                
                # Bridge Guidance
                if eval_result.get('bridge_guidance'):
                    st.subheader("🌉 How to Improve")
                    st.write(eval_result['bridge_guidance'])
                
                # Suggested Resources
                if eval_result.get('suggested_resources') and len(eval_result['suggested_resources']) > 0:
                    st.subheader("📚 Suggested Resources")
                    for resource in eval_result['suggested_resources']:
                        if isinstance(resource, dict):
                            with st.expander(f"{resource.get('title', 'Resource')}"):
                                st.write(f"**Learn:** {resource.get('description', '')}")
                                st.write(f"**Action:** {resource.get('action_item', '')}")
                
                # Metadata
                if eval_result.get('metadata'):
                    with st.expander("📌 Evaluation Metadata"):
                        meta = eval_result['metadata']
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Complexity", meta.get('complexity_level', 'N/A'))
                        with col2:
                            st.metric("AI Confidence", f"{meta.get('ai_confidence', '0')}%")
                        with col3:
                            st.metric("Plagiarism Check", f"{meta.get('plagiarism_similarity', '0')}%")
                
                # PDF Download with roll number
                st.divider()
                st.subheader("💾 Download Report")
                try:
                    out_pdf = generate_pdf_bytes(st.session_state.last_evaluation_topic or "Assignment", "[From PDF]", eval_result, roll_number=st.session_state.last_evaluation_roll)
                    filename = f"{st.session_state.last_evaluation_roll}_{st.session_state.username}_Report.pdf" if st.session_state.last_evaluation_roll else f"{st.session_state.username}_Report.pdf"
                    st.download_button("📥 Download Full Report (PDF)", out_pdf, filename, use_container_width=True, key="download_report")
                except Exception as e:
                    st.error(f"❌ Could not generate PDF: {e}")
                    import traceback
                    st.code(traceback.format_exc(), language="python")
            
            # Clear button to reset and evaluate another assignment
            if st.button("➕ Evaluate Another", use_container_width=True, key="eval_another"):
                st.session_state.last_evaluation_result = None
                st.session_state.evaluation_completed = False
                st.rerun()
        
        # --- NEW: PERSISTENT HISTORY VIEW ---
        st.markdown("---")
        with st.expander("📜 Your Evaluation History", expanded=False):
            all_evals = get_all_evaluations()
            if all_evals:
                # Filter for non-mock data if possible, or just show all
                history_data = []
                for e in all_evals[:20]:
                    history_data.append({
                        "Time": e.get("created_at", "")[11:16] if e.get("created_at") else "N/A",
                        "Roll": e.get("student_roll", "N/A"),
                        "Student": e.get("student_name", "N/A"),
                        "Topic": e.get("topic", "N/A"),
                        "Score": e.get("score", "N/A"),
                        "Grade": e.get("grade", "N/A")
                    })
                st.table(pd.DataFrame(history_data))
                st.caption("Check the 'Analytics' tab for full ranking and statistics.")
            else:
                st.info("No evaluations in history yet.")

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
                with st.spinner("📌 Processing and storing guideline..."):
                    try:
                        if _store_guideline_from_pdf:
                            result = _store_guideline_from_pdf(pdf_bytes)
                            st.success(f"✅ {result}")
                        else:
                            st.error("❌ Knowledge ingestion service not available. Check backend imports.")
                    except Exception as e:
                        st.error(f"❌ Error storing guideline: {e}")
                        import traceback
                        st.code(traceback.format_exc(), language="python")
        
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<h2>📈 Performance Analytics</h2>", unsafe_allow_html=True)
        st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        
        if not BACKEND_OK:
            st.warning("⚠️ Analytics is unavailable because backend imports failed.")
        else:
            try:
                summary = get_evaluations_summary()
                all_evals_for_tab3 = get_all_evaluations()
            except Exception as e:
                st.error(f"❌ Error loading analytics: {e}")
                summary = {"total": 0}
                all_evals_for_tab3 = []
            
            if not all_evals_for_tab3:
                st.info("📊 No student evaluations found yet. Go to 'Student Evaluation' to process your first submission.")
            else:
                # ===== TOP SUMMARY METRICS =====
                class_stats = get_class_stats()
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                col1.metric("📊 Total", summary["total"])
                col2.metric("⭐ Avg", f"{summary['avg_score']}/10")
                col3.metric("👥 Students", summary["unique_students"])
                col4.metric("📚 Topics", summary["unique_topics"])
                if class_stats:
                    col5.metric("📈 Median", f"{class_stats['median']}/10")
                    col6.metric("📉 Std Dev", f"{class_stats['std_dev']}")
                
                st.divider()
                
                # ===== VISUALIZATION ROW 1: SCORE AND GRADE DISTRIBUTIONS =====
                st.markdown("### 📊 Performance Overview")
                dist_col1, dist_col2 = st.columns(2)
                
                with dist_col1:
                    score_dist = get_score_distribution()
                    score_labels = list(score_dist.keys())
                    score_values = list(score_dist.values())
                    
                    fig_score = go.Figure(data=[
                        go.Pie(
                            labels=score_labels,
                            values=score_values,
                            hole=0,
                            marker=dict(colors=['#d32f2f', '#f57c00', '#fac858', '#97be32', '#34c368'])
                        )
                    ])
                    fig_score.update_layout(
                        title="Score Distribution",
                        height=300,
                        showlegend=True,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    st.plotly_chart(fig_score, use_container_width=True)
                
                with dist_col2:
                    grade_dist = get_grade_distribution()
                    grade_labels = [k for k, v in grade_dist.items() if v > 0]
                    grade_values = [v for k, v in grade_dist.items() if v > 0]
                    grade_colors = {'A': '#34c368', 'B': '#97be32', 'C': '#fac858', 'D': '#f57c00', 'F': '#d32f2f'}
                    grade_color_list = [grade_colors.get(g, '#808080') for g in grade_labels]
                    
                    fig_grade = go.Figure(data=[
                        go.Bar(
                            x=grade_labels,
                            y=grade_values,
                            marker=dict(color=grade_color_list),
                            text=grade_values,
                            textposition='auto',
                        )
                    ])
                    fig_grade.update_layout(
                        title="Grade Distribution",
                        xaxis_title="Grade",
                        yaxis_title="Count",
                        height=300,
                        showlegend=False,
                        margin=dict(l=40, r=20, t=30, b=40)
                    )
                    st.plotly_chart(fig_grade, use_container_width=True)
                
                st.divider()
                
                # ===== VISUALIZATION ROW 2: TOPICS =====
                st.markdown("### 📚 Topic Performance")
                topic_col1, topic_col2 = st.columns(2)
                
                with topic_col1:
                    topic_eval_count = get_evaluations_by_topic()
                    if topic_eval_count:
                        topics = list(topic_eval_count.keys())
                        counts = list(topic_eval_count.values())
                        
                        fig_topic_count = go.Figure(data=[
                            go.Bar(
                                x=topics,
                                y=counts,
                                marker=dict(color=counts, colorscale='Blues', showscale=False),
                                text=counts,
                                textposition='auto',
                            )
                        ])
                        fig_topic_count.update_layout(
                            title="Evaluations per Topic",
                            xaxis_title="Topic",
                            yaxis_title="Count",
                            height=300,
                            showlegend=False,
                            margin=dict(l=40, r=20, t=30, b=80),
                            xaxis_tickangle=-45
                        )
                        st.plotly_chart(fig_topic_count, use_container_width=True)
                
                with topic_col2:
                    topic_perf = get_topic_performance()
                    if topic_perf:
                        topics = list(topic_perf.keys())
                        scores = list(topic_perf.values())
                        
                        fig_topic_perf = go.Figure(data=[
                            go.Bar(
                                x=topics,
                                y=scores,
                                marker=dict(
                                    color=scores,
                                    colorscale=['#d32f2f', '#f57c00', '#fac858', '#97be32', '#34c368'],
                                    cmin=0,
                                    cmax=10
                                ),
                                text=[f"{s:.1f}" for s in scores],
                                textposition='auto',
                            )
                        ])
                        fig_topic_perf.update_layout(
                            title="Average Score by Topic",
                            xaxis_title="Topic",
                            yaxis_title="Average Score",
                            height=300,
                            showlegend=False,
                            yaxis=dict(range=[0, 10]),
                            margin=dict(l=40, r=20, t=30, b=80),
                            xaxis_tickangle=-45
                        )
                        st.plotly_chart(fig_topic_perf, use_container_width=True)
                
                st.divider()
                
                # ===== VISUALIZATION ROW 3: STUDENT ANALYSIS =====
                st.markdown("### 👥 Student Performance")
                student_col1, student_col2 = st.columns(2)
                
                with student_col1:
                    top_students = get_top_students(10)
                    if top_students:
                        students = list(top_students.keys())
                        scores = list(top_students.values())
                        
                        fig_top_students = go.Figure(data=[
                            go.Bar(
                                y=students,
                                x=scores,
                                orientation='h',
                                marker=dict(
                                    color=scores,
                                    colorscale='Viridis',
                                    showscale=True,
                                    colorbar=dict(title="Score")
                                ),
                                text=[f"{s:.1f}" for s in scores],
                                textposition='auto',
                            )
                        ])
                        fig_top_students.update_layout(
                            title="Top 10 Students",
                            xaxis_title="Average Score",
                            height=300,
                            showlegend=False,
                            xaxis=dict(range=[0, 10]),
                            margin=dict(l=150, r=20, t=30, b=40)
                        )
                        st.plotly_chart(fig_top_students, use_container_width=True)
                
                with student_col2:
                    student_eval_freq = get_student_evaluation_count()
                    if student_eval_freq:
                        top_10_students = dict(list(student_eval_freq.items())[:10])
                        students = list(top_10_students.keys())
                        freq = list(top_10_students.values())
                        
                        fig_eval_freq = go.Figure(data=[
                            go.Bar(
                                y=students,
                                x=freq,
                                orientation='h',
                                marker=dict(color='#4e89ae'),
                                text=freq,
                                textposition='auto',
                            )
                        ])
                        fig_eval_freq.update_layout(
                            title="Top 10 Students by Evaluation Count",
                            xaxis_title="Number of Evaluations",
                            height=300,
                            showlegend=False,
                            margin=dict(l=150, r=20, t=30, b=40)
                        )
                        st.plotly_chart(fig_eval_freq, use_container_width=True)
                
                st.divider()
                
                # ===== STUDENT SEGMENTATION =====
                st.markdown("### 🎯 Student Segmentation")
                seg_col1, seg_col2 = st.columns(2)
                
                with seg_col1:
                    st.markdown("**🏆 Top Performers (≥7)**")
                    strong_students = get_strong_students(7)
                    if strong_students:
                        strong_data = [{"Student": s, "Score": score} for s, score in strong_students.items()]
                        strong_df = pd.DataFrame(strong_data).head(10)
                        st.dataframe(strong_df, use_container_width=True, hide_index=True, height=250)
                    else:
                        st.info("No top performers yet")
                
                with seg_col2:
                    st.markdown("**⚠️ Needs Support (<5)**")
                    weak_students = get_weak_students(5)
                    if weak_students:
                        weak_data = [{"Student": s, "Score": score} for s, score in weak_students.items()]
                        weak_df = pd.DataFrame(weak_data).head(10)
                        st.dataframe(weak_df, use_container_width=True, hide_index=True, height=250)
                    else:
                        st.info("No students need support")
                
                st.divider()
                
                # ===== TREND ANALYSIS =====
                st.markdown("### 📈 Evaluation Trends")
                date_stats = get_evaluation_stats_by_date()
                if date_stats:
                    dates = list(date_stats.keys())
                    counts = [date_stats[d]["count"] for d in dates]
                    avg_scores = [date_stats[d]["avg_score"] for d in dates]
                    
                    fig_trends = go.Figure()
                    fig_trends.add_trace(go.Scatter(
                        x=dates, y=counts,
                        mode='lines+markers',
                        name='Evaluation Count',
                        yaxis='y1',
                        line=dict(color='#4e89ae', width=2),
                        marker=dict(size=8)
                    ))
                    fig_trends.add_trace(go.Scatter(
                        x=dates, y=avg_scores,
                        mode='lines+markers',
                        name='Avg Score',
                        yaxis='y2',
                        line=dict(color='#fac858', width=2),
                        marker=dict(size=8)
                    ))
                    fig_trends.update_layout(
                        title="Evaluation Trends Over Time",
                        xaxis_title="Date",
                        yaxis=dict(
                            title=dict(text="Evaluation Count", font=dict(color='#4e89ae')),
                            tickfont=dict(color='#4e89ae')
                        ),
                        yaxis2=dict(
                            title=dict(text="Average Score", font=dict(color='#fac858')),
                            tickfont=dict(color='#fac858'),
                            overlaying='y',
                            side='right',
                            range=[0, 10]
                        ),
                        height=350,
                        hovermode='x unified',
                        margin=dict(l=60, r=60, t=40, b=60),
                        legend=dict(x=0.01, y=0.99)
                    )
                    st.plotly_chart(fig_trends, use_container_width=True)
                
                st.divider()
                
                # ===== DETAILED TABLES =====
                with st.expander("📋 Detailed Analysis (Expand)", expanded=False):
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.markdown("**Performance by Grade**")
                        perf_by_grade = get_performance_by_grade()
                        if perf_by_grade:
                            grade_data = []
                            for grade, data in sorted(perf_by_grade.items(), key=lambda x: {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'F': 4}.get(x[0], 5)):
                                grade_data.append({
                                    "Grade": grade,
                                    "Count": data["count"],
                                    "Avg Score": f"{data['avg_score']:.2f}"
                                })
                            grade_df = pd.DataFrame(grade_data)
                            st.dataframe(grade_df, use_container_width=True, hide_index=True)
                    
                    with detail_col2:
                        st.markdown("**Topic Difficulty Ranking**")
                        topic_diff = get_topic_difficulty()
                        if topic_diff:
                            difficulty_data = []
                            for i, (topic, score) in enumerate(topic_diff.items(), 1):
                                if score >= 7:
                                    level = "🟢 Easy"
                                elif score >= 5:
                                    level = "🟡 Medium"
                                else:
                                    level = "🔴 Hard"
                                difficulty_data.append({
                                    "Rank": i,
                                    "Topic": topic,
                                    "Avg Score": f"{score:.2f}",
                                    "Level": level
                                })
                            diff_df = pd.DataFrame(difficulty_data)
                            st.dataframe(diff_df, use_container_width=True, hide_index=True)
                    
                    st.markdown("**Leaderboard: Top Ranked Students (Top Score)**")
                    all_evals = get_all_evaluations()
                    if all_evals:
                        eval_data = []
                        # Convert scores to float for proper sorting
                        for record in all_evals:
                            record['_score_numeric'] = 0.0
                            try:
                                record['_score_numeric'] = float(record.get('score', 0))
                            except: pass
                        
                        # Sort by score descending (Highest score @ #1)
                        sorted_evals = sorted(all_evals, key=lambda x: x['_score_numeric'], reverse=True)
                        
                        for e in sorted_evals[:100]:
                            feedback_text = str(e.get("feedback", "N/A"))[:60]
                            if len(str(e.get("feedback", ""))) > 60:
                                feedback_text += "..."
                            eval_data.append({
                                "Rank": sorted_evals.index(e) + 1,
                                "Roll": e.get("student_roll", "N/A"),
                                "Student": e.get("student_name", "N/A")[:25],
                                "Score": f"{e.get('score', '0')}/10",
                                "Grade": e.get("grade", "N/A"),
                                "Topic": e.get("topic", "N/A")[:20],
                                "Date": e.get("created_at", "N/A")[:10] if e.get("created_at") else "N/A",
                            })
                        df_evals = pd.DataFrame(eval_data)
                        st.dataframe(df_evals, use_container_width=True, height=500, hide_index=True)
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