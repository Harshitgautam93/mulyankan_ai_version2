import os
from dotenv import load_dotenv
import sys
from supabase import create_client
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore

# ===============================
# Environment Setup
# ===============================
# Add parent directory to path to find .env in project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(project_root, ".env"))

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
# Store Guideline Logic (Direct Insert - Bypassing LangChain Vector Store)
# ===============================
def store_guideline(question_text: str, solution_text: str):
    """
    Stores the Question as searchable content and Solution in metadata.
    Direct insert method to avoid LangChain SupabaseVectorStore schema issues.
    """
    try:
        import json
        from datetime import datetime
        
        # Generate embeddings for the question text
        question_embedding = embeddings.embed_query(question_text)
        
        # Prepare the data for direct insert
        data = {
            "content": question_text,
            "metadata": json.dumps({"solution": solution_text, "type": "guideline"}),
            "embedding": question_embedding,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Direct insert into assignments table
        result = supabase.table("assignments").insert(data).execute()
        
        print(f"✅ Guideline stored successfully")
        return "✅ Question & Solution Indexed Successfully"
    except Exception as e:
        print(f"[ERROR] Supabase insert failed: {e}")
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"Supabase insert failed: {e}")

# ===============================
# Retrieve Relevant Guideline (Updated for Direct Insert Format)
# ===============================
def retrieve_relevant_guideline(query_text: str):
    try:
        print(f"--- DEBUG: Searching for Topic: '{query_text}' ---")
        
        # Generate embedding for the query
        query_embedding = embeddings.embed_query(query_text)
        
        # Use Supabase RPC for vector similarity search
        try:
            results = supabase.rpc(
                "match_assignments",
                {
                    "query_embedding": query_embedding,
                    "match_count": 1,
                    "similarity_threshold": 0.0
                }
            ).execute()
            
            rows = getattr(results, "data", None) or (results.get("data") if isinstance(results, dict) else None)
            
            if rows and isinstance(rows, list) and len(rows) > 0:
                row = rows[0]
                # Extract solution from metadata JSON
                try:
                    import json
                    metadata = row.get("metadata")
                    if isinstance(metadata, str):
                        metadata = json.loads(metadata)
                    if isinstance(metadata, dict):
                        solution = metadata.get("solution")
                        if solution:
                            print(f"--- DEBUG: Match Found via vector RPC ---")
                            return solution
                except Exception as e:
                    print(f"--- DEBUG: Failed extracting solution from RPC result: {e}")
        except Exception as e:
            print(f"--- DEBUG: Vector RPC call failed: {e}")
        
        # FALLBACK: Direct SQL query to assignments table
        print("--- DEBUG: Attempting SQL fallback...")
        try:
            resp = supabase.table("assignments").select("*").limit(10).execute()
            rows = getattr(resp, "data", None) or (resp.get("data") if isinstance(resp, dict) else None)
            
            if rows:
                for row in rows:
                    try:
                        import json
                        metadata = row.get("metadata")
                        if isinstance(metadata, str):
                            metadata = json.loads(metadata)
                        if isinstance(metadata, dict):
                            solution = metadata.get("solution")
                            if solution:
                                print(f"--- DEBUG: Match Found via SQL fallback ---")
                                return solution
                    except Exception as e:
                        pass
            
            print("--- DEBUG: SQL fallback found no solutions ---")
            return None
            
        except Exception as e:
            print(f"--- DEBUG: SQL fallback failed: {e}")
            return None
    
    except Exception as e:
        print(f"--- DEBUG: Guideline retrieval failed: {e}")
        import traceback
        traceback.print_exc()
        return None


# ===============================
# Store Guideline with Metadata (Updated to Direct Insert)
# ===============================
def store_guideline_with_metadata(extracted_text: str, question_title: str):
    """Stores PDF text and links the title in metadata using direct insert."""
    try:
        import json
        from datetime import datetime
        
        # Generate embeddings
        text_embedding = embeddings.embed_query(extracted_text)
        
        # Prepare data
        data = {
            "content": extracted_text,
            "metadata": json.dumps({
                "question": question_title,
                "solution": extracted_text,
                "type": "guideline"
            }),
            "embedding": text_embedding,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Direct insert
        supabase.table("assignments").insert(data).execute()
        
        print(f"✅ Guideline with metadata stored successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Ingestion Error: {e}")
        import traceback
        traceback.print_exc()
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
def save_evaluation_result(topic: str, student_name: str, evaluation_data: dict, student_roll: str = None, student_answer: str = None):
    """Saves the final LLM grade and all detailed feedback to Supabase."""
    try:
        from datetime import datetime
        import json
        
        # Prepare evaluation data with all available fields
        eval_record = {
            "topic": topic,
            "student_name": student_name,
            "score": evaluation_data.get("score"),
            "grade": evaluation_data.get("grade"),
            "feedback": evaluation_data.get("feedback"),
            "topic_diagnostic": evaluation_data.get("topic_diagnostic", ""),
            "bridge_guidance": evaluation_data.get("bridge_guidance", ""),
            "created_at": datetime.utcnow().isoformat(),
            # Complex JSON fields
            "rubric_breakdown": json.dumps(evaluation_data.get("rubric_breakdown", [])),
            "missing_concepts": json.dumps(evaluation_data.get("missing_concepts", [])),
            "suggested_resources": json.dumps(evaluation_data.get("suggested_resources", [])),
            "evaluation_metadata": json.dumps(evaluation_data.get("metadata", {}))
        }
        
        # Add roll number and student answer if provided
        if student_roll:
            eval_record["student_roll"] = student_roll
        if student_answer:
            eval_record["student_answer"] = student_answer
        
        # Insert into evaluations table
        try:
            result = supabase.table("evaluations").insert(eval_record).execute()
        except Exception as e:
            # FALLBACK: If new columns are missing, try saving only primary fields
            err_str = str(e)
            if any(col in err_str for col in ["student_roll", "student_answer", "rubric_breakdown"]):
                print("[DEBUG] Extra columns missing in DB, falling back to basic fields")
                basic_record = {
                    "topic": topic,
                    "student_name": student_name,
                    "score": evaluation_data.get("score"),
                    "grade": evaluation_data.get("grade"),
                    "feedback": evaluation_data.get("feedback"),
                    "created_at": eval_record["created_at"]
                }
                if student_roll and "student_roll" not in err_str:
                    basic_record["student_roll"] = student_roll
                result = supabase.table("evaluations").insert(basic_record).execute()
            else:
                raise e
        
        print(f"✅ Full Evaluation SAVED to Supabase: {student_name} | Topic: '{topic}'")
        clear_analytics_cache()
        return True
    except Exception as e:
        print(f"[ERROR] Error saving evaluation: {e}")
        import traceback
        traceback.print_exc()
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
# Data Management Functions
# ===============================
def delete_all_evaluations():
    """Wipes all records from the evaluations table."""
    try:
        # Using a filter that matches all (id > 0)
        supabase.table("evaluations").delete().gt("id", 0).execute()
        clear_analytics_cache()
        return True
    except Exception as e:
        print(f"[ERROR] Delete all failed: {e}")
        return False

def delete_mock_data():
    """Deletes the automatically inserted mock data (from Feb 4th)."""
    try:
        # Sample data was inserted with '2026-02-04'
        supabase.table("evaluations").delete().lt("created_at", "2026-02-10").execute()
        clear_analytics_cache()
        return True
    except Exception as e:
        print(f"[ERROR] Delete mock data failed: {e}")
        return False


# ===============================
# Analytics Functions
# ===============================
def get_all_evaluations():
    """Retrieve all evaluation records from database."""
    try:
        # Fetch everything (*) to ensure new columns are available in the result
        resp = supabase.table("evaluations").select("*").order("created_at", desc=True).execute()

        rows = getattr(resp, "data", None)
        if rows is None:
            # Try dictionary access if it's not an object
            rows = resp.get("data") if isinstance(resp, dict) else []
        
        # Ensure it's a list
        if rows is not None and not isinstance(rows, list):
            rows = [rows]

        actual_rows = rows if rows else []
        print(f"[DEBUG] get_all_evaluations: Retrieved {len(actual_rows)} records")
        return actual_rows
    except Exception as e:
        print(f"[ERROR] Error retrieving evaluations: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_total_evaluations():
    """Get count of total evaluations."""
    evaluations = get_all_evaluations()
    return len(evaluations)


def get_average_score():
    """Calculate average score across all evaluations."""
    try:
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
        
        result = round(total_score / count, 2) if count > 0 else 0
        print(f"[DEBUG] get_average_score: {result} ({count} scores)")
        return result
    except Exception as e:
        print(f"[ERROR] get_average_score failed: {e}")
        return 0


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
    """Get best (max) score by student."""
    evaluations = get_all_evaluations()
    student_data = {}
    
    for eval_record in evaluations:
        student = eval_record.get("student_name", "Unknown")
        try:
            score = float(eval_record.get("score", 0))
        except (ValueError, TypeError):
            score = 0
        
        if student not in student_data:
            student_data[student] = []
        
        student_data[student].append(score)
    
    # Calculate Best Score (Max)
    student_best = {}
    for student, scores in student_data.items():
        student_best[student] = max(scores) if scores else 0
    
    # Sort by score descending (Top Rank = Best Score)
    return dict(sorted(student_best.items(), key=lambda x: x[1], reverse=True))


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
    try:
        evaluations = get_all_evaluations()
        summary = {
            "total": len(evaluations),
            "avg_score": get_average_score(),
            "unique_students": len(set(e.get("student_name", "") for e in evaluations)) if evaluations else 0,
            "unique_topics": len(set(e.get("topic", "") for e in evaluations)) if evaluations else 0
        }
        print(f"[DEBUG] get_evaluations_summary: {summary}")
        return summary
    except Exception as e:
        print(f"[ERROR] get_evaluations_summary failed: {e}")
        import traceback
        traceback.print_exc()
        return {"total": 0, "avg_score": 0, "unique_students": 0, "unique_topics": 0}


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