import os
from dotenv import load_dotenv
load_dotenv()

print('ENV SUPABASE_URL present:', bool(os.getenv('SUPABASE_URL')))
print('ENV SUPABASE_KEY present:', bool(os.getenv('SUPABASE_KEY')))

try:
    from backend.database import store_guideline, retrieve_relevant_guideline
    from backend.main import process_assignment_evaluation
except Exception as e:
    print('IMPORT ERROR:', e)
    raise

print('\n--- STORE TEST ---')
try:
    res = store_guideline('TEST QUESTION 123', 'This is the sample solution text.')
    print('store ->', res)
except Exception as e:
    print('STORE EXCEPTION:', e)

print('\n--- RETRIEVE TEST ---')
try:
    out = retrieve_relevant_guideline('TEST QUESTION 123')
    print('retrieve ->', out)
except Exception as e:
    print('RETRIEVE EXCEPTION:', e)

print('\n--- EVALUATION TEST ---')
try:
    ev = process_assignment_evaluation('TEST QUESTION 123','Student answer text here.','Rubric: 5 pts correct city, 5 pts explanation.')
    print('evaluation ->', ev)
except Exception as e:
    print('EVALUATION EXCEPTION:', e)
