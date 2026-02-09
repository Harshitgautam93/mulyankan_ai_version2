#!/usr/bin/env python3
"""
Utility script to manage test data in Supabase
Allows clearing test data and keeping only real evaluations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import supabase

def view_all_evaluations():
    """View all evaluations in the database."""
    print("=" * 80)
    print("ALL EVALUATIONS IN DATABASE")
    print("=" * 80)
    try:
        resp = supabase.table("evaluations").select("*").order("created_at", desc=True).execute()
        rows = getattr(resp, "data", None) or (resp.get("data") if isinstance(resp, dict) else None)
        
        if not rows:
            print("No evaluations found")
            return
        
        for i, row in enumerate(rows, 1):
            print(f"\n{i}. ID: {row.get('id')}")
            print(f"   Student: {row.get('student_name')}")
            print(f"   Topic: {row.get('topic')}")
            print(f"   Score: {row.get('score')}/10")
            print(f"   Grade: {row.get('grade')}")
            print(f"   Created: {row.get('created_at')}")
            print(f"   Feedback: {row.get('feedback')[:60]}..." if len(str(row.get('feedback', ''))) > 60 else f"   Feedback: {row.get('feedback')}")
    except Exception as e:
        print(f"Error: {e}")

def clear_all_evaluations():
    """Clear ALL evaluations from the database."""
    try:
        resp = supabase.table("evaluations").delete().neq("id", 0).execute()
        print("✅ All evaluations cleared from database")
        return True
    except Exception as e:
        print(f"❌ Error clearing evaluations: {e}")
        return False

def clear_test_data():
    """Clear only test/mock data, keeping real evaluations."""
    test_topics = [
        "Photosynthesis",
        "Mitochondria Function", 
        "DNA Replication",
        "Cell Division",
        "Genetics",
        "Analytics Test Topic"
    ]
    
    test_students = [
        "Alice Johnson",
        "Bob Smith", 
        "Charlie Brown",
        "Diana Prince",
        "Eve Wilson",
        "Frank Miller",
        "Grace Lee",
        "Henry Davis",
        "Test Student"
    ]
    
    try:
        # Get all evaluations
        resp = supabase.table("evaluations").select("id, student_name, topic").execute()
        rows = getattr(resp, "data", None) or (resp.get("data") if isinstance(resp, dict) else None)
        
        if not rows:
            print("No evaluations to check")
            return True
        
        # Identify test records
        test_ids = []
        for row in rows:
            topic = row.get("topic", "")
            student = row.get("student_name", "")
            
            # Mark for deletion if it matches test data
            if topic in test_topics or student in test_students:
                test_ids.append(row.get("id"))
        
        if not test_ids:
            print("✅ No test data found to delete")
            return True
        
        # Delete test records
        deleted_count = 0
        for id_val in test_ids:
            try:
                supabase.table("evaluations").delete().eq("id", id_val).execute()
                deleted_count += 1
            except:
                pass
        
        print(f"✅ Deleted {deleted_count} test records from database")
        return True
    except Exception as e:
        print(f"❌ Error clearing test data: {e}")
        return False

def get_stats_summary():
    """Show current database statistics."""
    try:
        resp = supabase.table("evaluations").select("id, student_name, topic").execute()
        rows = getattr(resp, "data", None) or (resp.get("data") if isinstance(resp, dict) else None)
        
        if not rows:
            print("No evaluations in database")
            return
        
        unique_students = len(set(row.get("student_name", "") for row in rows))
        unique_topics = len(set(row.get("topic", "") for row in rows))
        
        print("\n📊 DATABASE STATISTICS")
        print(f"Total Evaluations: {len(rows)}")
        print(f"Unique Students: {unique_students}")
        print(f"Unique Topics: {unique_topics}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage test data in Supabase")
    parser.add_argument("--view", action="store_true", help="View all evaluations")
    parser.add_argument("--clear-test", action="store_true", help="Clear only test data")
    parser.add_argument("--clear-all", action="store_true", help="Clear all evaluations")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    
    args = parser.parse_args()
    
    if args.view:
        view_all_evaluations()
    elif args.clear_test:
        confirm = input("⚠️  Are you sure you want to delete test data? (yes/no): ")
        if confirm.lower() == "yes":
            clear_test_data()
    elif args.clear_all:
        confirm = input("⚠️  Are you sure you want to delete ALL evaluations? (yes/no): ")
        if confirm.lower() == "yes":
            clear_all_evaluations()
    elif args.stats:
        view_all_evaluations()
        get_stats_summary()
    else:
        print("Usage:")
        print("  python manage_test_data.py --view      # View all evaluations")
        print("  python manage_test_data.py --stats     # Show statistics")
        print("  python manage_test_data.py --clear-test # Delete only test data")
        print("  python manage_test_data.py --clear-all  # Delete all evaluations")
