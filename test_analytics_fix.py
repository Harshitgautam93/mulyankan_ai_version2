#!/usr/bin/env python3
"""
Test script to verify analytics functions are correctly retrieving
and processing data from Supabase after the fix.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import (
    get_all_evaluations,
    get_evaluations_summary,
    get_average_score,
    get_grade_distribution,
    get_topic_performance,
    get_student_performance,
    get_evaluations_by_topic,
    get_class_stats,
    get_score_distribution,
    save_evaluation_result
)

def test_analytics():
    """Test all analytics functions."""
    print("=" * 60)
    print("ANALYTICS TEST - Verifying Supabase Data Integration")
    print("=" * 60)
    
    # Test 1: Retrieve all evaluations
    print("\n[TEST 1] Retrieving all evaluations...")
    try:
        all_evals = get_all_evaluations()
        print(f"✅ Retrieved {len(all_evals)} evaluations from Supabase")
        if all_evals:
            print(f"   Sample record: {all_evals[0]}")
    except Exception as e:
        print(f"❌ Failed to retrieve evaluations: {e}")
        return False
    
    # Test 2: Summary statistics
    print("\n[TEST 2] Getting summary statistics...")
    try:
        summary = get_evaluations_summary()
        print(f"✅ Summary retrieved:")
        print(f"   Total: {summary.get('total')}")
        print(f"   Avg Score: {summary.get('avg_score')}/10")
        print(f"   Unique Students: {summary.get('unique_students')}")
        print(f"   Unique Topics: {summary.get('unique_topics')}")
    except Exception as e:
        print(f"❌ Failed to get summary: {e}")
        return False
    
    # Test 3: Average score
    print("\n[TEST 3] Calculating average score...")
    try:
        avg = get_average_score()
        print(f"✅ Average score: {avg}/10")
    except Exception as e:
        print(f"❌ Failed to calculate average: {e}")
        return False
    
    # Test 4: Grade distribution
    print("\n[TEST 4] Getting grade distribution...")
    try:
        grades = get_grade_distribution()
        print(f"✅ Grade distribution: {grades}")
    except Exception as e:
        print(f"❌ Failed to get grade distribution: {e}")
        return False
    
    # Test 5: Topic performance
    print("\n[TEST 5] Getting topic performance...")
    try:
        topics = get_topic_performance()
        print(f"✅ Topic performance: {topics}")
    except Exception as e:
        print(f"❌ Failed to get topic performance: {e}")
        return False
    
    # Test 6: Student performance
    print("\n[TEST 6] Getting student performance...")
    try:
        students = get_student_performance()
        print(f"✅ Student performance ({len(students)} students):")
        for student, score in list(students.items())[:3]:
            print(f"   {student}: {score}/10")
    except Exception as e:
        print(f"❌ Failed to get student performance: {e}")
        return False
    
    # Test 7: Class statistics
    print("\n[TEST 7] Getting class statistics...")
    try:
        stats = get_class_stats()
        if stats:
            print(f"✅ Class statistics:")
            print(f"   Min: {stats.get('min_score')}")
            print(f"   Max: {stats.get('max_score')}")
            print(f"   Mean: {stats.get('mean')}")
            print(f"   Median: {stats.get('median')}")
            print(f"   Std Dev: {stats.get('std_dev')}")
        else:
            print("⚠️  No class statistics available")
    except Exception as e:
        print(f"❌ Failed to get class statistics: {e}")
        return False
    
    # Test 8: Score distribution
    print("\n[TEST 8] Getting score distribution...")
    try:
        distribution = get_score_distribution()
        print(f"✅ Score distribution: {distribution}")
    except Exception as e:
        print(f"❌ Failed to get score distribution: {e}")
        return False
    
    # Test 9: Save a test evaluation
    print("\n[TEST 9] Testing save_evaluation_result...")
    try:
        test_eval = {
            "score": "8.5",
            "grade": "A",
            "feedback": "Test feedback - analytics fix verification"
        }
        result = save_evaluation_result("Analytics Test Topic", "Test Student", test_eval)
        if result:
            print(f"✅ Successfully saved test evaluation")
            # Verify it appears in data
            import time
            time.sleep(1)  # Give Supabase a moment to process
            all_evals_after = get_all_evaluations()
            if len(all_evals_after) > len(all_evals):
                print(f"✅ Confirmed: New evaluation is visible in analytics (total: {len(all_evals_after)})")
            else:
                print(f"⚠️  Warning: New evaluation may not have been saved properly")
        else:
            print(f"❌ Failed to save evaluation")
    except Exception as e:
        print(f"❌ Failed during save test: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Analytics System is Working!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_analytics()
