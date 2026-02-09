import os
from dotenv import load_dotenv

from supabase import create_client
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore

# ===============================
# Environment Setup
# ===============================
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY not set in environment variables")

# ===============================
# Client & Embedding Model Initialization
# ===============================
# Use anon key for client-side, service role key for backend
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", SUPABASE_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Initializing embeddings (MiniLM is great for speed/memory)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ===============================
# Store Guideline Logic
# ===============================
def store_guideline(question_text: str, solution_text: str):
    """
    Stores the Question as searchable content and Solution in metadata.
    This allows us to find the right assignment based on the question.
    """
    try:
        SupabaseVectorStore.from_texts(
            texts=[question_text], 
            embedding=embeddings,
            client=supabase,
            table_name="assignments",
            query_name="match_assignments",
            metadatas=[{"solution": solution_text}], # Store the actual answer here
        )
        return "✅ Question & Solution Indexed Successfully"
    except Exception as e:
        raise RuntimeError(f"Supabase insert failed: {e}")

# ===============================
# Retrieve Relevant Guideline
# ===============================
def retrieve_relevant_guideline(query_text: str):
    try:
        print(f"--- DEBUG: Searching for Topic: '{query_text}' ---")
        
        # Ensure the vector store is initialized with the client
        vector_store = SupabaseVectorStore(
            client=supabase,
            embedding=embeddings,
            table_name="assignments",
            query_name="match_assignments"
        )
        
        # FIX: Use a lower-level search or ensure the match_assignments 
        # RPC is returning the correct JSON structure.
        results = vector_store.similarity_search(
            query=query_text,
            k=1
        )

        # Try to extract solution from vector search result
        if results:
            try:
                solution = None
                if hasattr(results[0], "metadata"):
                    solution = results[0].metadata.get("solution")
                # fallback if metadata is stored differently
                if not solution and hasattr(results[0], "metadata") and isinstance(results[0].metadata, dict):
                    # try common alternate keys
                    for key in ("answer", "solution_text", "sol"):
                        if key in results[0].metadata:
                            solution = results[0].metadata[key]
                            break

                if solution:
                    print(f"--- DEBUG: Match Found via vector search ---")
                    return solution
            except Exception as e:
                print(f"--- DEBUG: Failed extracting metadata from vector result: {e}")

        # FALLBACK: If vector search returned nothing useful, query Supabase rows directly
        print("--- DEBUG: Vector search returned no usable result, attempting SQL fallback... ---")
        try:
            resp = supabase.table("assignments").select("*").limit(50).execute()
            # resp may be an object with .data or a dict
            rows = getattr(resp, "data", None) or (resp.get("data") if isinstance(resp, dict) else None)

            def _extract_solution_from_row(row: dict):
                if not isinstance(row, dict):
                    return None
                # common metadata keys used by vectorstores
                for meta_key in ("metadatas", "metadata", "meta", "metadata"):
                    md = row.get(meta_key)
                    if isinstance(md, dict):
                        for key in ("solution", "answer", "solution_text"):
                            if key in md:
                                return md.get(key)
                    if isinstance(md, str):
                        try:
                            import json
                            mdj = json.loads(md)
                            for key in ("solution", "answer"):
                                if key in mdj:
                                    return mdj.get(key)
                        except Exception:
                            pass
                # top-level fallbacks
                for key in ("solution", "answer", "solution_text"):
                    if key in row:
                        return row.get(key)
                return None

            if rows:
                for r in rows:
                    s = _extract_solution_from_row(r)
                    if s:
                        print("--- DEBUG: Match Found via SQL fallback ---")
                        return s
            else:
                print("--- DEBUG: No rows returned from assignments table ---")

            return None
        except Exception as e:
            print(f"--- DEBUG: SQL fallback search failed: {e}")
            return None

    except AttributeError as e:
        if "params" in str(e):
            print("--- ERROR: Supabase SDK version mismatch. ---")
            print("Check that your match_assignments RPC is correctly defined in Supabase.")
        # Attempt SQL fallback when vectorstore RPC or SDK doesn't match
        try:
            resp = supabase.table("assignments").select("*").limit(50).execute()
            rows = getattr(resp, "data", None) or (resp.get("data") if isinstance(resp, dict) else None)
            if rows:
                for r in rows:
                    # try to extract solution from common locations
                    md = None
                    if isinstance(r, dict):
                        md = r.get("metadata") or r.get("metadatas") or r.get("meta")
                    if isinstance(md, dict) and md.get("solution"):
                        print("--- DEBUG: Match Found via SQL fallback (AttributeError path) ---")
                        return md.get("solution")
                    if isinstance(r, dict) and r.get("solution"):
                        print("--- DEBUG: Match Found via SQL fallback (AttributeError path) ---")
                        return r.get("solution")
            print("--- DEBUG: SQL fallback (AttributeError path) found nothing ---")
            return None
        except Exception as ex:
            print(f"--- DEBUG: SQL fallback after AttributeError failed: {ex}")
            return None
    except Exception as e:
        print(f"--- DEBUG: Search failed: {e} ---")
        return None


# ===============================
# Store Guideline with Metadata (Updated)
# ===============================
def store_guideline_with_metadata(extracted_text: str, question_title: str):
    """Stores PDF text and links the title in metadata."""
    try:
        SupabaseVectorStore.from_texts(
            texts=[extracted_text],
            embedding=embeddings,
            client=supabase,
            table_name="assignments",
            query_name="match_assignments",
            metadatas=[{"question": question_title, "solution": extracted_text}]
        )
        return True
    except Exception as e:
        print(f"Ingestion Error: {e}")
        return False


# ===============================
# Retrieve with Fallback (Enhanced)
# ===============================
def retrieve_with_fallback(query_topic: str):
    """Tries Vector Search; if no results, tries SQL Keyword Match."""
    # Use existing retrieve_relevant_guideline which already has fallback
    return retrieve_relevant_guideline(query_topic)


# ===============================
# Save Evaluation Result
# ===============================
def save_evaluation_result(topic: str, student_name: str, evaluation_data: dict, student_roll: str = None):
    """Saves the final LLM grade to the evaluations table in Supabase."""
    try:
        from datetime import datetime
        supabase.table("evaluations").insert({
            "topic": topic,
            "student_name": student_name,
            "student_roll": student_roll,
            "score": evaluation_data.get("score"),
            "grade": evaluation_data.get("grade"),
            "feedback": evaluation_data.get("feedback"),
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        print(f"✅ Evaluation saved for {student_name} (Roll: {student_roll}) on topic '{topic}'")
        return True
    except Exception as e:
        print(f"Error saving evaluation: {e}")
        return False


# ===============================
# Cache & Refresh Utilities
# ===============================
def clear_analytics_cache():
    """Clear Streamlit cache for analytics - called after new evaluation."""
    import streamlit as st
    if hasattr(st, 'cache_data'):
        st.cache_data.clear()


# ===============================
# Analytics Functions
# ===============================
def get_all_evaluations():
    """Retrieve all evaluation records from database."""
    try:
        # SELECT only necessary fields to improve performance
        resp = supabase.table("evaluations").select("id, created_at, topic, student_name, student_roll, score, grade, feedback").order("created_at", desc=True).execute()
        rows = getattr(resp, "data", None) or (resp.get("data") if isinstance(resp, dict) else None)
        if rows and not isinstance(rows, list):
            rows = [rows] if rows else []
        return rows if rows else []
    except Exception as e:
        print(f"Error retrieving evaluations: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_total_evaluations():
    """Get count of total evaluations."""
    evaluations = get_all_evaluations()
    return len(evaluations)


def get_average_score():
    """Calculate average score across all evaluations."""
    evaluations = get_all_evaluations()
    if not evaluations:
        return 0
    
    total_score = 0
    count = 0
    for eval_record in evaluations:
        try:
            score = float(eval_record.get("score", 0))
            total_score += score
            count += 1
        except (ValueError, TypeError):
            pass
    
    return round(total_score / count, 2) if count > 0 else 0


def get_grade_distribution():
    """Get distribution of grades (A, B, C, D, F)."""
    evaluations = get_all_evaluations()
    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    
    for eval_record in evaluations:
        grade = eval_record.get("grade", "").strip().upper()
        if grade in grade_counts:
            grade_counts[grade] += 1
    
    return grade_counts


def get_topic_performance():
    """Get average score by topic."""
    evaluations = get_all_evaluations()
    topic_data = {}
    
    for eval_record in evaluations:
        topic = eval_record.get("topic", "Unknown")
        try:
            score = float(eval_record.get("score", 0))
        except (ValueError, TypeError):
            score = 0
        
        if topic not in topic_data:
            topic_data[topic] = {"scores": [], "count": 0}
        
        topic_data[topic]["scores"].append(score)
        topic_data[topic]["count"] += 1
    
    # Calculate averages
    topic_avg = {}
    for topic, data in topic_data.items():
        avg = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
        topic_avg[topic] = round(avg, 2)
    
    return topic_avg


def get_student_performance():
    """Get average score by student."""
    evaluations = get_all_evaluations()
    student_data = {}
    
    for eval_record in evaluations:
        student = eval_record.get("student_name", "Unknown")
        try:
            score = float(eval_record.get("score", 0))
        except (ValueError, TypeError):
            score = 0
        
        if student not in student_data:
            student_data[student] = {"scores": [], "count": 0}
        
        student_data[student]["scores"].append(score)
        student_data[student]["count"] += 1
    
    # Calculate averages
    student_avg = {}
    for student, data in student_data.items():
        avg = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
        student_avg[student] = round(avg, 2)
    
    # Sort by score descending
    return dict(sorted(student_avg.items(), key=lambda x: x[1], reverse=True))


def get_evaluations_by_topic():
    """Get count of evaluations per topic."""
    evaluations = get_all_evaluations()
    topic_counts = {}
    
    for eval_record in evaluations:
        topic = eval_record.get("topic", "Unknown")
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    # Sort by count descending
    return dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True))


def get_evaluations_over_time():
    """Get evaluations count per day for trend analysis."""
    evaluations = get_all_evaluations()
    daily_counts = {}
    
    for eval_record in evaluations:
        created_at = eval_record.get("created_at", "")
        if created_at:
            # Extract date part (YYYY-MM-DD)
            date = created_at.split("T")[0] if "T" in created_at else created_at
            daily_counts[date] = daily_counts.get(date, 0) + 1
    
    # Sort by date
    return dict(sorted(daily_counts.items()))


def get_top_students(limit=10):
    """Get top performing students."""
    student_perf = get_student_performance()
    return dict(list(student_perf.items())[:limit])


def get_evaluations_summary():
    """Get summary statistics."""
    evaluations = get_all_evaluations()
    return {
        "total": len(evaluations),
        "avg_score": get_average_score(),
        "unique_students": len(set(e.get("student_name", "") for e in evaluations)),
        "unique_topics": len(set(e.get("topic", "") for e in evaluations))
    }


# ===============================
# Advanced Analytics Functions
# ===============================
def get_score_distribution():
    """Get distribution of scores in ranges."""
    evaluations = get_all_evaluations()
    ranges = {"0-2": 0, "2-4": 0, "4-6": 0, "6-8": 0, "8-10": 0}
    
    for eval_record in evaluations:
        try:
            score = float(eval_record.get("score", 0))
            if score < 2:
                ranges["0-2"] += 1
            elif score < 4:
                ranges["2-4"] += 1
            elif score < 6:
                ranges["4-6"] += 1
            elif score < 8:
                ranges["6-8"] += 1
            else:
                ranges["8-10"] += 1
        except (ValueError, TypeError):
            pass
    
    return ranges


def get_topic_evaluation_count():
    """Get total number of evaluations per topic with count."""
    evaluations = get_all_evaluations()
    topic_info = {}
    
    for eval_record in evaluations:
        topic = eval_record.get("topic", "Unknown")
        if topic not in topic_info:
            topic_info[topic] = {"count": 0, "scores": []}
        
        topic_info[topic]["count"] += 1
        try:
            score = float(eval_record.get("score", 0))
            topic_info[topic]["scores"].append(score)
        except (ValueError, TypeError):
            pass
    
    # Add average to each topic
    for topic in topic_info:
        scores = topic_info[topic]["scores"]
        avg = sum(scores) / len(scores) if scores else 0
        topic_info[topic]["avg_score"] = round(avg, 2)
    
    return topic_info


def get_student_evaluation_count():
    """Get evaluation counts per student."""
    evaluations = get_all_evaluations()
    student_counts = {}
    
    for eval_record in evaluations:
        student = eval_record.get("student_name", "Unknown")
        student_counts[student] = student_counts.get(student, 0) + 1
    
    # Sort by count descending
    return dict(sorted(student_counts.items(), key=lambda x: x[1], reverse=True))


def get_weak_students(threshold=5):
    """Get students with average score below threshold."""
    student_perf = get_student_performance()
    weak_students = {k: v for k, v in student_perf.items() if v < threshold}
    return dict(sorted(weak_students.items(), key=lambda x: x[1]))


def get_strong_students(threshold=7):
    """Get students with average score above threshold."""
    student_perf = get_student_performance()
    strong_students = {k: v for k, v in student_perf.items() if v >= threshold}
    return dict(sorted(strong_students.items(), key=lambda x: x[1], reverse=True))


def get_class_stats():
    """Get comprehensive class statistics."""
    evaluations = get_all_evaluations()
    if not evaluations:
        return None
    
    scores = []
    for eval_record in evaluations:
        try:
            score = float(eval_record.get("score", 0))
            scores.append(score)
        except (ValueError, TypeError):
            pass
    
    if not scores:
        return None
    
    scores.sort()
    n = len(scores)
    
    return {
        "min_score": min(scores),
        "max_score": max(scores),
        "mean": round(sum(scores) / n, 2),
        "median": scores[n // 2] if n % 2 == 1 else round((scores[n // 2 - 1] + scores[n // 2]) / 2, 2),
        "std_dev": round((sum((x - (sum(scores) / n)) ** 2 for x in scores) / n) ** 0.5, 2),
        "total_scores": n
    }


def get_performance_by_grade():
    """Get comprehensive stats grouped by grade."""
    evaluations = get_all_evaluations()
    grade_stats = {}
    
    for eval_record in evaluations:
        grade = eval_record.get("grade", "N/A").strip().upper()
        if grade not in grade_stats:
            grade_stats[grade] = {"count": 0, "scores": []}
        
        grade_stats[grade]["count"] += 1
        try:
            score = float(eval_record.get("score", 0))
            grade_stats[grade]["scores"].append(score)
        except (ValueError, TypeError):
            pass
    
    # Calculate averages and counts for each grade
    result = {}
    for grade, data in grade_stats.items():
        scores = data["scores"]
        result[grade] = {
            "count": data["count"],
            "avg_score": round(sum(scores) / len(scores), 2) if scores else 0
        }
    
    return result


def get_topic_difficulty():
    """Rank topics by difficulty (lower avg score = harder)."""
    topic_perf = get_topic_performance()
    return dict(sorted(topic_perf.items(), key=lambda x: x[1]))


def get_assignments_per_student():
    """Get evaluation frequency per student."""
    evaluations = get_all_evaluations()
    student_eval_count = {}
    
    for eval_record in evaluations:
        student = eval_record.get("student_name", "Unknown")
        student_eval_count[student] = student_eval_count.get(student, 0) + 1
    
    return dict(sorted(student_eval_count.items(), key=lambda x: x[1], reverse=True))


def get_recent_evaluations(limit=50):
    """Get most recent evaluations."""
    evaluations = get_all_evaluations()
    return evaluations[:limit]


def get_evaluation_stats_by_date():
    """Get evaluation count and average score per date."""
    evaluations = get_all_evaluations()
    date_stats = {}
    
    for eval_record in evaluations:
        created_at = eval_record.get("created_at", "")
        if created_at:
            date = created_at.split("T")[0] if "T" in created_at else created_at
            if date not in date_stats:
                date_stats[date] = {"count": 0, "scores": []}
            
            date_stats[date]["count"] += 1
            try:
                score = float(eval_record.get("score", 0))
                date_stats[date]["scores"].append(score)
            except (ValueError, TypeError):
                pass
    
    # Calculate averages
    result = {}
    for date, data in date_stats.items():
        scores = data["scores"]
        result[date] = {
            "count": data["count"],
            "avg_score": round(sum(scores) / len(scores), 2) if scores else 0
        }
    
    return dict(sorted(result.items()))


# ===============================
# Insert Test Data (Development)
# ===============================
def insert_test_data():
    """Insert sample evaluation data for testing analytics."""
    from datetime import datetime
    test_data = [
        {"topic": "Photosynthesis", "student_name": "Alice Johnson", "score": "8.5", "grade": "A", "feedback": "Great understanding of the process"},
        {"topic": "Photosynthesis", "student_name": "Bob Smith", "score": "7.2", "grade": "B", "feedback": "Good but missing some details"},
        {"topic": "Photosynthesis", "student_name": "Charlie Brown", "score": "6.1", "grade": "C", "feedback": "Basic understanding shown"},
        {"topic": "Photosynthesis", "student_name": "Diana Prince", "score": "9.0", "grade": "A", "feedback": "Excellent work!"},
        {"topic": "Photosynthesis", "student_name": "Eve Wilson", "score": "5.5", "grade": "C", "feedback": "Needs improvement"},
        
        {"topic": "Photosynthesis", "student_name": "Frank Miller", "score": "7.8", "grade": "B", "feedback": "Well explained"},
        {"topic": "Photosynthesis", "student_name": "Grace Lee", "score": "8.9", "grade": "A", "feedback": "Outstanding!"},
        {"topic": "Photosynthesis", "student_name": "Henry Davis", "score": "4.2", "grade": "D", "feedback": "Incomplete understanding"},
        
        {"topic": "Mitochondria Function", "student_name": "Alice Johnson", "score": "7.5", "grade": "B", "feedback": "Good explanation"},
        {"topic": "Mitochondria Function", "student_name": "Bob Smith", "score": "8.1", "grade": "A", "feedback": "Excellent knowledge"},
        {"topic": "Mitochondria Function", "student_name": "Charlie Brown", "score": "6.5", "grade": "C", "feedback": "Average work"},
        {"topic": "Mitochondria Function", "student_name": "Diana Prince", "score": "8.8", "grade": "A", "feedback": "Perfect!"},
        
        {"topic": "DNA Replication", "student_name": "Alice Johnson", "score": "9.2", "grade": "A", "feedback": "Perfect understanding"},
        {"topic": "DNA Replication", "student_name": "Eve Wilson", "score": "7.3", "grade": "B", "feedback": "Good work"},
        {"topic": "DNA Replication", "student_name": "Frank Miller", "score": "8.4", "grade": "A", "feedback": "Very good"},
        
        {"topic": "Cell Division", "student_name": "Charlie Brown", "score": "5.8", "grade": "C", "feedback": "Needs practice"},
        {"topic": "Cell Division", "student_name": "Diana Prince", "score": "9.1", "grade": "A", "feedback": "Excellent"},
        {"topic": "Cell Division", "student_name": "Grace Lee", "score": "8.7", "grade": "A", "feedback": "Great job"},
        
        {"topic": "Genetics", "student_name": "Henry Davis", "score": "4.9", "grade": "D", "feedback": "Needs improvement"},
        {"topic": "Genetics", "student_name": "Bob Smith", "score": "7.6", "grade": "B", "feedback": "Good understanding"},
    ]
    
    inserted_count = 0
    current_time = datetime.utcnow().isoformat()
    for data in test_data:
        try:
            supabase.table("evaluations").insert({
                "topic": data["topic"],
                "student_name": data["student_name"],
                "score": data["score"],
                "grade": data["grade"],
                "feedback": data["feedback"],
                "created_at": current_time
            }).execute()
            inserted_count += 1
        except Exception as e:
            print(f"Error inserting test data: {e}")
    
    return f"✅ Inserted {inserted_count} test records"


# ===============================
# Store Evaluation Result
# ===============================