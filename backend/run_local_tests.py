from types import SimpleNamespace
import importlib
import sys
import os

# Ensure project root is on sys.path so `backend` package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Create minimal fake modules for missing optional dependencies used by database.py
import types
if 'langchain_huggingface' not in sys.modules:
    m = types.ModuleType('langchain_huggingface')
    class HuggingFaceEmbeddings:
        def __init__(self, model_name=None):
            self.model_name = model_name
    m.HuggingFaceEmbeddings = HuggingFaceEmbeddings
    sys.modules['langchain_huggingface'] = m

if 'langchain_community.vectorstores' not in sys.modules:
    pkg = types.ModuleType('langchain_community')
    sub = types.ModuleType('langchain_community.vectorstores')
    class SupabaseVectorStore:
        def __init__(self, client=None, embedding=None, table_name=None, query_name=None):
            pass
        @staticmethod
        def from_texts(texts, embedding, client, table_name, query_name, metadatas=None):
            return True
        def similarity_search(self, query, k=1):
            return []
    sub.SupabaseVectorStore = SupabaseVectorStore
    sys.modules['langchain_community'] = pkg
    sys.modules['langchain_community.vectorstores'] = sub

# Reload database to pick up recent changes
import backend.database as database
importlib.reload(database)

# Fake vector store that can be configured to return results or not
class FakeVectorStore:
    def __init__(self, client=None, embedding=None, table_name=None, query_name=None):
        self._mode = FakeVectorStore.mode
    @staticmethod
    def set_mode(mode):
        # mode: 'hit' -> returns a vector hit with metadata.solution
        # 'nohit' -> returns [] to force fallback
        FakeVectorStore.mode = mode

    def similarity_search(self, query, k=1):
        if getattr(FakeVectorStore, 'mode', 'hit') == 'hit':
            return [SimpleNamespace(metadata={"solution": "Vector-store solution text for: %s" % query})]
        return []

# Fake supabase client used by SQL fallback
class FakeSupabaseClient:
    def __init__(self, rows=None):
        self._rows = rows or []
    def table(self, name):
        return self
    def select(self, *args, **kwargs):
        return self
    def limit(self, n):
        return self
    def execute(self):
        return {"data": self._rows}


def test_vector_hit():
    print("\n--- Test: Vector hit ---")
    FakeVectorStore.set_mode('hit')
    database.SupabaseVectorStore = FakeVectorStore
    database.supabase = FakeSupabaseClient(rows=[])
    res = database.retrieve_relevant_guideline("What is testing?")
    print("Result:", res)

def test_sql_fallback():
    print("\n--- Test: Vector miss, SQL fallback hit ---")
    FakeVectorStore.set_mode('nohit')
    database.SupabaseVectorStore = FakeVectorStore
    # rows with different metadata shapes
    rows = [
        {"metadatas": {"solution": "SQL fallback solution text."}},
        {"metadata": '{"solution": "JSON-encoded solution"}'}
    ]
    database.supabase = FakeSupabaseClient(rows=rows)
    res = database.retrieve_relevant_guideline("Another question?")
    print("Result:", res)

def test_no_results():
    print("\n--- Test: No vector hit and no SQL rows ---")
    FakeVectorStore.set_mode('nohit')
    database.SupabaseVectorStore = FakeVectorStore
    database.supabase = FakeSupabaseClient(rows=[])
    res = database.retrieve_relevant_guideline("No match question")
    print("Result:", res)

if __name__ == '__main__':
    test_vector_hit()
    test_sql_fallback()
    test_no_results()
