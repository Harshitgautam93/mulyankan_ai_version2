"""
Quick test to verify PDF generation works with fixed Unicode characters and enhanced evaluation structure.
"""
import sys
import os

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from frontend.pdf_generator import generate_pdf_bytes

# Example 1: Topic Swap - Polymorphism vs Encapsulation
test_evaluation_topic_swap = {
    "score": "2",
    "grade": "F",
    "feedback": "The submission correctly defines OOP basics like constructors but completely misses the target topic of Polymorphism.",
    
    "topic_diagnostic": "Your submission accurately describes Encapsulation and Constructors. However, the assignment specifically asked for Polymorphism. While these are both OOP pillars, they serve different purposes. Encapsulation hides internal details, while Polymorphism allows different implementations of the same interface.",
    
    "rubric_breakdown": [
        {
            "criteria": "Domain Relevance",
            "score": "2",
            "max_score": "2",
            "feedback": "Recognized the question was about OOP."
        },
        {
            "criteria": "Topic Accuracy",
            "score": "0",
            "max_score": "8",
            "feedback": "Failed to address Polymorphism; discussed Encapsulation instead."
        }
    ],
    
    "missing_concepts": [
        {
            "concept": "Method Overriding",
            "importance": "HIGH",
            "explanation": "Allows a child class to provide a specific implementation of a method already defined in its parent."
        },
        {
            "concept": "Duck Typing",
            "importance": "MEDIUM",
            "explanation": "A Pythonic way of achieving polymorphism without explicit inheritance."
        }
    ],
    
    "bridge_guidance": "To improve, try rewriting your code so that different classes (like 'Cat' and 'Dog') can both use a 'speak()' method, but produce different results. This demonstrates polymorphism in action.",
    
    "suggested_resources": [
        {
            "title": "Understanding Method Overriding",
            "description": "Learn how subclasses override parent methods to implement polymorphism.",
            "action_item": "Review Python documentation on inheritance and method overriding. Try creating a simple example with Animal, Cat, and Dog classes."
        },
        {
            "title": "Duck Typing in Python",
            "description": "Understand how Python's dynamic typing enables polymorphic behavior without explicit inheritance.",
            "action_item": "Experiment with creating classes that share method names but aren't related by inheritance."
        }
    ],
    
    "metadata": {
        "complexity_level": "Beginner",
        "ai_confidence": "98",
        "plagiarism_similarity": "5"
    }
}

# Example 2: Partial Credit - Good Feedback
test_evaluation_partial = {
    "score": "6",
    "grade": "C",
    "feedback": "You provided a reasonable response that demonstrates partial understanding of the core concepts.",
    
    "topic_diagnostic": "",  # Empty for higher scores
    
    "rubric_breakdown": [
        {
            "criteria": "Relevance to Topic",
            "score": "2",
            "max_score": "5",
            "feedback": "The response addressed most of the question but missed some key aspects."
        },
        {
            "criteria": "Conceptual Clarity",
            "score": "4",
            "max_score": "5",
            "feedback": "Good technical accuracy and clear explanations, though some nuance was missing."
        }
    ],
    
    "missing_concepts": [
        {
            "concept": "Method Overriding",
            "importance": "HIGH",
            "explanation": "This is the core mechanism that should have been covered for complete understanding."
        },
        {
            "concept": "Duck Typing",
            "importance": "MEDIUM",
            "explanation": "Important for Python-style polymorphism understanding."
        }
    ],
    
    "bridge_guidance": "Your work shows understanding of basics. However, you need to deepen your knowledge of method overriding, which is the primary way Python implements polymorphism in class hierarchies. The conceptual link is: Inheritance provides the structure, and Method Overriding provides the flexibility.",
    
    "suggested_resources": [
        {
            "title": "OOP Design Patterns",
            "description": "Learn how polymorphism enables design patterns like Strategy and Template Method.",
            "action_item": "Study the Factory pattern as an example of polymorphism in action."
        }
    ],
    
    "metadata": {
        "complexity_level": "Intermediate",
        "ai_confidence": "85",
        "plagiarism_similarity": "12"
    }
}

if __name__ == "__main__":
    print("Testing PDF generation with enhanced evaluation structure...")
    print()
    
    try:
        # Generate PDF for Topic Swap scenario
        print("Generating PDF for Topic Swap scenario (Polymorphism vs Encapsulation)...")
        pdf_bytes = generate_pdf_bytes(
            "Explain Polymorphism in Object-Oriented Programming",
            "[From Student]",
            test_evaluation_topic_swap
        )
        
        # Check if PDF was generated
        if pdf_bytes and len(pdf_bytes) > 0:
            print("SUCCESS! PDF generated successfully.")
            print(f"PDF Size: {len(pdf_bytes)} bytes")
            print()
            
            # Save for inspection
            with open("test_output_topic_swap.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("Saved to: test_output_topic_swap.pdf")
            print()
        else:
            print("ERROR: PDF generation returned empty output")
            print()
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print()
    
    try:
        # Generate PDF for Partial Credit scenario
        print("Generating PDF for Partial Credit scenario...")
        pdf_bytes = generate_pdf_bytes(
            "Explain Polymorphism in Object-Oriented Programming",
            "[From Student]",
            test_evaluation_partial
        )
        
        # Check if PDF was generated
        if pdf_bytes and len(pdf_bytes) > 0:
            print("SUCCESS! PDF generated successfully.")
            print(f"PDF Size: {len(pdf_bytes)} bytes")
            print()
            
            # Save for inspection
            with open("test_output_partial_credit.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("Saved to: test_output_partial_credit.pdf")
            print()
        else:
            print("ERROR: PDF generation returned empty output")
            print()
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print()
