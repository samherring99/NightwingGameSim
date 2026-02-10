"""
RAG-based GameBoy C code generator.

Uses LlamaIndex with retrieval-augmented generation to create GBDK-compatible C code.
Retrieves relevant documentation from the data/ directory to inform code generation.
"""

import sys
from pathlib import Path
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.llms.llama_cpp.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from config import config


# Global index cache (loaded once per session)
_index_cache = None


def get_index():
    """
    Get or create the RAG index from data directory.

    Returns:
        VectorStoreIndex instance with loaded documentation
    """
    global _index_cache

    if _index_cache is not None:
        return _index_cache

    # Validate data directory
    if not config.DATA_DIR.exists():
        raise ValueError(f"Data directory not found: {config.DATA_DIR}")

    if config.VERBOSE:
        print(f"Loading documents from {config.DATA_DIR}...")

    # Load documents
    documents = SimpleDirectoryReader(str(config.DATA_DIR)).load_data()

    if config.VERBOSE:
        print(f"Loaded {len(documents)} documents")
        print(f"Creating embeddings with {config.RAG_EMBED_MODEL}...")

    # Create embedding model
    embed_model = HuggingFaceEmbedding(model_name=config.RAG_EMBED_MODEL)

    # Configure LlamaIndex settings
    Settings.embed_model = embed_model

    # Create index
    _index_cache = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

    if config.VERBOSE:
        print("RAG index created successfully")

    return _index_cache


def create_llm():
    """
    Create LlamaCPP instance for RAG queries.

    Returns:
        Configured LlamaCPP instance
    """
    # Check if local model path is set
    if config.LOCAL_MODEL_PATH and Path(config.LOCAL_MODEL_PATH).exists():
        model_path = config.LOCAL_MODEL_PATH
        model_url = None
        if config.VERBOSE:
            print(f"Using local model: {model_path}")
    else:
        # Fall back to downloading model
        model_url = "https://huggingface.co/NousResearch/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
        model_path = None
        if config.VERBOSE:
            print(f"Downloading model from HuggingFace...")

    return LlamaCPP(
        model_url=model_url,
        model_path=model_path,
        temperature=0.1,
        max_new_tokens=2048,
        context_window=8192,
        generate_kwargs={},
        model_kwargs={"n_gpu_layers": -1},  # Use all available GPU layers
        messages_to_prompt=messages_to_prompt,
        completion_to_prompt=completion_to_prompt,
        verbose=config.VERBOSE,
    )


def generate_code(prompt: str, system_prompt: str = None) -> str:
    """
    Generate GameBoy C code using RAG with LlamaIndex.

    Args:
        prompt: User request for what game/program to create
        system_prompt: Optional custom system prompt (uses default if None)

    Returns:
        Generated C code as string
    """
    # Load system prompt from file if not provided
    if system_prompt is None:
        if config.SYSTEM_PROMPT_FILE.exists():
            system_prompt = config.SYSTEM_PROMPT_FILE.read_text()
        else:
            system_prompt = (
                "Write me C code that compiles to a .gb file given the following description. "
                "Do not return any other text, just the full C code enclosed in backticks. "
                "The code should be error free and concise, do not make any assumptions. "
                "Everything should be in one file. Define any methods or variables you need. "
                "Use tiling to draw sprites. "
                "You'll want to use `#include <gb/gb.h>` in your headers and use `joypad()` to wait for user control. "
                "It will be compiled and ran on a Nintendo GameBoy, so be visually creative."
            )

    # Construct full query
    full_query = f"{system_prompt}\n\nDescription: {prompt}"

    # Get RAG index
    index = get_index()

    # Create LLM
    llm = create_llm()

    # Create query engine
    query_engine = index.as_query_engine(llm=llm)

    # Generate code
    if config.VERBOSE:
        print("Generating code with RAG...")

    response = query_engine.query(full_query)

    return str(response)


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "a simple tic tac toe game where the player plays against the computer"

    try:
        code = generate_code(prompt)
        print(code)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)