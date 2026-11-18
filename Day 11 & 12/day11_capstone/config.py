"""
config.py - every setting for the pipeline lives here.

Swapping from local to cloud (Day 12) means changing only the environment
variables below, never the code in the other files.
"""
import os

# --- Which LLM answers the questions -------------------------------------
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3.5:4b-q4_K_M")

# --- Which model turns text into vectors (stays local, even on Day 12) ----
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "http://localhost:11434/v1")
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "ollama")
# nomic-embed-text was trained with these two prefixes. Without them the
# similarity scores are noticeably worse.
DOC_PREFIX = os.getenv("DOC_PREFIX", "search_document: ")
QUERY_PREFIX = os.getenv("QUERY_PREFIX", "search_query: ")

# --- Chunking and retrieval ----------------------------------------------
# CHUNK_SIZE and CHUNK_OVERLAP are in CHARACTERS (RecursiveCharacterTextSplitter),
# not tokens. 512 characters is roughly 115 tokens on these PDFs.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K = int(os.getenv("TOP_K", "8"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "bootcamp_docs")
# "plain" or "layout" - how pypdf pulls text out of each page (see ingest.py).
EXTRACTION_MODE = os.getenv("EXTRACTION_MODE", "plain")

# --- Generation ----------------------------------------------------------
SYSTEM_PROMPT = """You are a helpful assistant answering questions based on provided context.
Use ONLY the context below to answer. If the answer is not in the context, say "I cannot find this information in the provided documents."

Context:
{context}
"""
TEMPERATURE = 0.3
# Qwen3.5 "thinks" by default and the thinking eats the token cap. "none" turns it off.
REASONING_EFFORT = os.getenv("REASONING_EFFORT", "none")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
# Ollama wants "max_tokens"; the Day 12 cloud model wants "max_completion_tokens".
TOKEN_LIMIT_PARAM = os.getenv("TOKEN_LIMIT_PARAM", "max_tokens")

# --- Paths ---------------------------------------------------------------
DOCUMENTS_DIR = "documents"
CHROMA_DIR = "chroma_db"
TEST_QUESTIONS_FILE = "test_questions.json"
PIPELINE_OUTPUTS_FILE = "pipeline_outputs.json"
