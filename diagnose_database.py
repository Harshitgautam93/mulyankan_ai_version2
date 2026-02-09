#!/usr/bin/env python3
"""
Investigate Supabase database structure and check for evaluation data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import supabase

def check_database_structure():
    """Check all tables and their structure in Supabase."""
    print("=" * 80)
    print("SUPABASE DATABASE STRUCTURE")
    print("=" * 80)
    
    try:
        # Try to get tables info - this may not work depending on Supabase permissions
        # Instead, let's just try to query known tables
        
        tables_to_check = [
            "evaluations",
            "assignments", 
            "student_submissions",
            "submissions",
            "results",
            "grades",
            "evaluation_results"
        ]
        
        for table_name in tables_to_check:
            try:
                resp = supabase.table(table_name).select("*").limit(1).execute()
                rows = getattr(resp, "data", None) or (resp.get("data") if isinstance(resp, dict) else None)
                if rows:
                    print(f"\n✅ Table '{table_name}' exists with data")
                    if rows and len(rows) > 0:
                        print(f"   Sample columns: {list(rows[0].keys())}")
                else:
                    print(f"\n⚠️  Table '{table_name}' exists (empty)")
            except Exception as e:
                if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                    print(f"\n❌ Table '{table_name}' does not exist")
                else:
                    print(f"\n⚠️  Table '{table_name}' - Error: {str(e)[:60]}")
        
    except Exception as e:
        print(f"Error checking database: {e}")

def check_evaluations_table_structure():
    """Get detailed info about evaluations table."""
    print("\n" + "=" * 80)
    print("EVALUATIONS TABLE STRUCTURE")
    print("=" * 80)
    
    try:
        resp = supabase.table("evaluations").select("*").limit(5).execute()
        rows = getattr(resp, "data", None) or (resp.get("data") if isinstance(resp, dict) else None)
        
        if not rows:
            print("✅ Evaluations table exists but is EMPTY (no data)")
            print("\nThis could mean:")
            print("  1. You haven't uploaded any assignments yet")
            print("  2. The save_evaluation_result() function is not working")
            print("  3. Evaluations are being saved to a different table")
            return
        
        print(f"✅ Evaluations table has {len(rows)} records")
        
        if rows:
            print(f"\nTable columns: {list(rows[0].keys())}")
            print(f"\nSample record:")
            sample = rows[0]
            for key, value in sample.items():
                print(f"  {key}: {str(value)[:80]}")
            
    except Exception as e:
        print(f"Error: {e}")

def check_save_function():
    """Test the save_evaluation_result function."""
    print("\n" + "=" * 80)
    print("TESTING SAVE FUNCTION")
    print("=" * 80)
    
    from backend.database import save_evaluation_result
    
    test_eval = {
        "score": "9",
        "grade": "A",
        "feedback": "Test evaluation to verify saving works",
        "rubric_breakdown": [{"criteria": "test", "score": "9"}],
        "missing_concepts": [],
        "bridge_guidance": "Test",
        "suggested_resources": [],
        "metadata": {"complexity_level": "Beginner", "ai_confidence": "100", "plagiarism_similarity": "0"}
    }
    
    print("Attempting to save test evaluation...")
    try:
        result = save_evaluation_result(
            topic="Test Topic - Save Function Verification",
            student_name="TestUser_SaveFunctionCheck",
            evaluation_data=test_eval
        )
        
        if result:
            print("✅ save_evaluation_result() returned True")
            
            # Verify it's in the database
            import time
            time.sleep(1)
            
            resp = supabase.table("evaluations").select("*").eq("student_name", "TestUser_SaveFunctionCheck").execute()
            saved_rows = getattr(resp, "data", None) or (resp.get("data") if isinstance(resp, dict) else None)
            
            if saved_rows and len(saved_rows) > 0:
                print("✅ Confirmed: Test evaluation was saved to database!")
                print(f"   Record ID: {saved_rows[0].get('id')}")
                print(f"   Topic: {saved_rows[0].get('topic')}")
                print(f"   Score: {saved_rows[0].get('score')}")
            else:
                print("⚠️  Function returned True but record not found in database!")
        else:
            print("❌ save_evaluation_result() returned False - something failed")
    except Exception as e:
        print(f"❌ Error during save: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database_structure()
    check_evaluations_table_structure()
    check_save_function()
