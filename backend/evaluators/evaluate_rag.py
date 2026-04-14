"""
RAG Evaluation Script using LangSmith
======================================
Evaluates the Langchain-chatbot RAG pipeline using 4 LLM-as-judge metrics:

1. Correctness   - Response vs reference answer (requires ground-truth)
2. Relevance     - Response vs input question (no reference needed)
3. Groundedness  - Response vs retrieved documents (no reference needed)
4. Retrieval Relevance - Retrieved docs vs input question (no reference needed)

Run from the /backend directory:
    python -m evaluators.evaluate_rag
"""

import os
import sys

# ─── Path setup so the script finds sibling modules ───────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

# ─── Imports ──────────────────────────────────────────────────────────────────
from typing import List
from typing_extensions import Annotated, TypedDict

from langchain_openai import ChatOpenAI
from langsmith import Client, traceable

from data_insertion.db_operations import query_documents
from logging_config import get_logger

logger = get_logger(__name__)

# ─── Environment variables ────────────────────────────────────────────────────
OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY", "lm-studio")
OPENAI_API_BASE  = os.getenv("OPENAI_API_BASE", "http://192.168.0.103:1234/v1")
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "qwen/qwen3-1.7b")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# ─── LLMs ─────────────────────────────────────────────────────────────────────
# RAG bot LLM  (temperature=1 -> creative answers)
rag_llm = ChatOpenAI(
    model=GENERATION_MODEL,
    base_url=OPENAI_API_BASE,
    api_key=OPENAI_API_KEY,
    temperature=1,
)

# Evaluator LLM (temperature=0 -> deterministic judgements)
eval_llm = ChatOpenAI(
    model=GENERATION_MODEL,
    base_url=OPENAI_API_BASE,
    api_key=OPENAI_API_KEY,
    temperature=0,
)


import re

# ─── RAG bot (the system under test) ──────────────────────────────────────────
PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rag_prompt.md")
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    RAG_PROMPT_TEMPLATE = f.read()

@traceable()
def rag_bot(question: str) -> dict:
    """
    Retrieves relevant documents from Qdrant then generates a concise answer.
    Returns a dict with 'answer' (str) and 'documents' (List[str]).
    """
    logger.info("RAG bot invoked for question: %s", question)

    # Retrieve from Qdrant (returns list of text strings)
    docs: List[str] = query_documents(query=question) or []

    docs_string = "\n\n".join(docs) if docs else "No relevant documents found."

    prompt = RAG_PROMPT_TEMPLATE.format(context=docs_string, question=question)

    ai_msg = rag_llm.invoke(prompt)

    # Clean the <think> tags just like in graph.py for qwen
    clean_text = re.sub(r"<think>.*?</think>", "", ai_msg.content, flags=re.DOTALL).strip()
    
    logger.info("Generated answer: %s", clean_text[:120])

    return {"answer": clean_text, "documents": docs}


# ─── Dataset ───────────────────────────────────────────────────────────────────
# These Q&A pairs should cover content you've inserted into Qdrant.
# Edit them to match your actual indexed documents.
EXAMPLES = [
    {
        "inputs":  {"question": "How do I create a simple Langchain Agent?"},
        "outputs": {"answer": "You can create an agent using an LLM, a list of tools, and an agent type like zero-shot-react-description, then initializing it with initialize_agent()."},
    },
    {
        "inputs":  {"question": "What is LCEL in LangChain?"},
        "outputs": {"answer": "LCEL stands for LangChain Expression Language. It is a declarative way to easily compose chains together using the pipe (|) operator."},
    },
    {
        "inputs":  {"question": "Explain the difference between a chain and an agent."},
        "outputs": {"answer": "A chain executes a predetermined sequence of calls, whereas an agent uses an LLM to dynamically determine which actions or tools to use in what order."},
    },
    {
        "inputs":  {"question": "What is a retriever in Langchain?"},
        "outputs": {"answer": "A retriever is an interface that returns documents given an unstructured query. It is typically used with a vector store in RAG applications."},
    },
    {
        "inputs":  {"question": "How does memory work in Langchain?"},
        "outputs": {"answer": "Memory allows a chain or agent to remember previous interactions. Classes like ConversationBufferMemory store past conversatons and insert them into the prompt execution."},
    },
    {
        "inputs":  {"question": "What are LangChain tools?"},
        "outputs": {"answer": "Tools are functions that agents can use to interact with the world, such as a search engine, an API, or a calculator."},
    },
    {
        "inputs":  {"question": "What is the purpose of LangSmith?"},
        "outputs": {"answer": "LangSmith is an observability and evaluation platform for LLM applications that allows you to trace, monitor, and evaluate LangChain pipelines."},
    },
    {
        "inputs":  {"question": "What is LangGraph and how does it differ from standard LangChain?"},
        "outputs": {"answer": "LangGraph is an extension of LangChain used to build robust, stateful multi-actor applications with cyclic computational steps, unlike the typically linear DAGs of LCEL."},
    },
    {
        "inputs":  {"question": "How can I integrate an OpenAI model in LangChain?"},
        "outputs": {"answer": "You can integrate an OpenAI model by importing ChatOpenAI or OpenAI from langchain_openai and instantiating it with your API key from your environment variables."},
    },
    {
        "inputs":  {"question": "What is a Document object in LangChain?"},
        "outputs": {"answer": "A Document object is a piece of text (page_content) accompanied by optional metadata. They are commonly created by Document Loaders before being embedded."},
    },
]

DATASET_NAME = "Langchain Concepts RAG Evaluation"


# ─── Grade schemas ─────────────────────────────────────────────────────────────

class CorrectnessGrade(TypedDict):
    explanation: Annotated[str, ..., "Step-by-step reasoning before the verdict"]
    correct: Annotated[bool, ..., "True if the answer is factually correct vs ground truth"]


class RelevanceGrade(TypedDict):
    explanation: Annotated[str, ..., "Step-by-step reasoning before the verdict"]
    relevant: Annotated[bool, ..., "True if the answer addresses the question"]


class GroundedGrade(TypedDict):
    explanation: Annotated[str, ..., "Step-by-step reasoning before the verdict"]
    grounded: Annotated[bool, ..., "True if the answer is grounded in the retrieved documents"]


class RetrievalRelevanceGrade(TypedDict):
    explanation: Annotated[str, ..., "Step-by-step reasoning before the verdict"]
    relevant: Annotated[bool, ..., "True if retrieved docs are relevant to the question"]


# ─── Evaluator LLMs with structured output ────────────────────────────────────
correctness_llm        = eval_llm.with_structured_output(CorrectnessGrade,        method="json_schema", strict=True)
relevance_llm          = eval_llm.with_structured_output(RelevanceGrade,          method="json_schema", strict=True)
grounded_llm           = eval_llm.with_structured_output(GroundedGrade,           method="json_schema", strict=True)
retrieval_relevance_llm = eval_llm.with_structured_output(RetrievalRelevanceGrade, method="json_schema", strict=True)


# ─── Evaluator prompts ─────────────────────────────────────────────────────────

CORRECTNESS_INSTRUCTIONS = """You are a teacher grading a quiz.
You will be given a QUESTION, the GROUND TRUTH (correct) ANSWER, and the STUDENT ANSWER.

Grade criteria:
1. Grade based ONLY on factual accuracy relative to the ground truth answer.
2. The student answer must not contain conflicting statements.
3. Extra correct information is OK.

A correctness value of True means ALL criteria are met.
A correctness value of False means at least one criterion is not met.

Reason step-by-step before giving your verdict."""

RELEVANCE_INSTRUCTIONS = """You are a teacher grading a quiz.
You will be given a QUESTION and a STUDENT ANSWER.

Grade criteria:
1. The STUDENT ANSWER must be concise and directly address the QUESTION.
2. The STUDENT ANSWER must help answer the QUESTION.

A relevance value of True means ALL criteria are met.
A relevance value of False means at least one criterion is not met.

Reason step-by-step before giving your verdict."""

GROUNDED_INSTRUCTIONS = """You are a teacher grading a quiz.
You will be given FACTS (retrieved documents) and a STUDENT ANSWER.

Grade criteria:
1. The STUDENT ANSWER must be grounded in the FACTS.
2. The STUDENT ANSWER must NOT contain hallucinated information outside the FACTS.

A grounded value of True means ALL criteria are met.
A grounded value of False means at least one criterion is not met.

Reason step-by-step before giving your verdict."""

RETRIEVAL_RELEVANCE_INSTRUCTIONS = """You are a teacher grading a quiz.
You will be given a QUESTION and a set of FACTS (retrieved documents).

Grade criteria:
1. Identify FACTS that are completely unrelated to the QUESTION.
2. If FACTS contain ANY keywords or semantic meaning related to the QUESTION, they are relevant.
3. Some unrelated information is OK as long as the FACTS are largely relevant.

A relevance value of True means the FACTS contain relevant content.
A relevance value of False means the FACTS are completely unrelated to the QUESTION.

Reason step-by-step before giving your verdict."""


# ─── Evaluator functions ───────────────────────────────────────────────────────

def correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> bool:
    """Evaluates factual correctness of the answer against a reference answer."""
    prompt = (
        f"QUESTION: {inputs['question']}\n"
        f"GROUND TRUTH ANSWER: {reference_outputs['answer']}\n"
        f"STUDENT ANSWER: {outputs['answer']}"
    )
    grade = correctness_llm.invoke([
        {"role": "system", "content": CORRECTNESS_INSTRUCTIONS},
        {"role": "user",   "content": prompt},
    ])
    logger.info("[correctness] %s -> %s | %s", inputs["question"][:60], grade["correct"], grade["explanation"][:80])
    return grade["correct"]


def relevance(inputs: dict, outputs: dict) -> bool:
    """Evaluates whether the answer is relevant and helpful for the question."""
    prompt = (
        f"QUESTION: {inputs['question']}\n"
        f"STUDENT ANSWER: {outputs['answer']}"
    )
    grade = relevance_llm.invoke([
        {"role": "system", "content": RELEVANCE_INSTRUCTIONS},
        {"role": "user",   "content": prompt},
    ])
    logger.info("[relevance] %s -> %s | %s", inputs["question"][:60], grade["relevant"], grade["explanation"][:80])
    return grade["relevant"]


def groundedness(inputs: dict, outputs: dict) -> bool:
    """Evaluates whether the answer is grounded in the retrieved documents (no hallucination)."""
    docs = outputs.get("documents", [])
    doc_string = "\n\n".join(docs) if docs else "No documents retrieved."
    prompt = (
        f"FACTS:\n{doc_string}\n\n"
        f"STUDENT ANSWER: {outputs['answer']}"
    )
    grade = grounded_llm.invoke([
        {"role": "system", "content": GROUNDED_INSTRUCTIONS},
        {"role": "user",   "content": prompt},
    ])
    logger.info("[groundedness] %s -> %s | %s", inputs["question"][:60], grade["grounded"], grade["explanation"][:80])
    return grade["grounded"]


def retrieval_relevance(inputs: dict, outputs: dict) -> bool:
    """Evaluates whether the retrieved documents are relevant to the question."""
    docs = outputs.get("documents", [])
    doc_string = "\n\n".join(docs) if docs else "No documents retrieved."
    prompt = (
        f"QUESTION: {inputs['question']}\n\n"
        f"FACTS:\n{doc_string}"
    )
    grade = retrieval_relevance_llm.invoke([
        {"role": "system", "content": RETRIEVAL_RELEVANCE_INSTRUCTIONS},
        {"role": "user",   "content": prompt},
    ])
    logger.info("[retrieval_relevance] %s -> %s | %s", inputs["question"][:60], grade["relevant"], grade["explanation"][:80])
    return grade["relevant"]


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    client = Client(api_key=LANGSMITH_API_KEY)

    # ── Create dataset (idempotent) ──────────────────────────────────────────
    if client.has_dataset(dataset_name=DATASET_NAME):
        print(f"[INFO] Dataset '{DATASET_NAME}' already exists - reusing it.")
    else:
        print(f"[INFO] Creating dataset '{DATASET_NAME}' in LangSmith ...")
        dataset = client.create_dataset(dataset_name=DATASET_NAME)
        client.create_examples(dataset_id=dataset.id, examples=EXAMPLES)
        print(f"[INFO] Uploaded {len(EXAMPLES)} examples.")

    # ── Target function (wraps the RAG bot) ─────────────────────────────────
    def target(inputs: dict) -> dict:
        return rag_bot(inputs["question"])

    # ── Run evaluation ───────────────────────────────────────────────────────
    print("[INFO] Starting evaluation run ...")

    experiment_results = client.evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[correctness, groundedness, relevance, retrieval_relevance],
        experiment_prefix="rag-langchain-chatbot",
        metadata={
            "version":    "qdrant+qwen3-1.7b",
            "model":      GENERATION_MODEL,
            "embeddings": os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3"),
        },
    )

    print("\n[INFO] Evaluation complete!")
    print(f"[INFO] View results at: https://smith.langchain.com/")

    # Print a quick summary if pandas is available
    try:
        import pandas as pd  # noqa: F401
        df = experiment_results.to_pandas()
        print("\n── Score summary ──────────────────────────────")
        score_cols = [c for c in df.columns if "score" in c.lower() or c in
                      ("correctness", "relevance", "groundedness", "retrieval_relevance")]
        if score_cols:
            print(df[score_cols].describe())
        else:
            print(df.to_string(max_rows=10))
    except ImportError:
        print("[INFO] Install pandas to see a local summary: pip install pandas")


if __name__ == "__main__":
    main()
