#!/usr/bin/env python
"""
Quick test to verify environment variables are loaded correctly
"""
import os
from dotenv import load_dotenv

print("\n" + "="*70)
print("ENVIRONMENT VARIABLES TEST")
print("="*70)

# Test 1: Check if .env file exists in root
root_env = os.path.join(os.path.dirname(__file__), ".env")
print(f"\n1. Root .env file:")
print(f"   Path: {root_env}")
print(f"   Exists: {os.path.exists(root_env)}")

# Test 2: Load from root
print(f"\n2. Loading .env from root...")
load_dotenv(root_env, override=True)

# Test 3: Check all required variables
print(f"\n3. Checking loaded variables:")
variables = ["GROQ_API_KEY", "GROQ_MODEL", "SUPABASE_URL", "SUPABASE_KEY"]
all_ok = True

for var in variables:
    value = os.getenv(var)
    if value:
        if len(value) > 30:
            display = f"{value[:20]}...({len(value)} chars)"
        else:
            display = value
        print(f"   ✓ {var}: {display}")
    else:
        print(f"   ✗ {var}: NOT LOADED")
        all_ok = False

# Test 4: Try to create ChatGroq to verify API key works
print(f"\n4. Testing ChatGroq initialization...")
try:
    from langchain_groq import ChatGroq
    
    groq_key = os.getenv("GROQ_API_KEY")
    groq_model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
    
    if not groq_key:
        print("   ✗ GROQ_API_KEY is None!")
        all_ok = False
    else:
        print(f"   Creating ChatGroq with model: {groq_model}")
        print(f"   API Key length: {len(groq_key)}")
        
        llm = ChatGroq(
            model=groq_model,
            groq_api_key=groq_key,
            temperature=0
        )
        print("   ✓ ChatGroq initialized successfully!")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    all_ok = False

# Test 5: Summary
print(f"\n5. Summary:")
if all_ok:
    print("   ✓ All checks passed! Environment is configured correctly.")
else:
    print("   ✗ Some checks failed. See details above.")

print("="*70 + "\n")
