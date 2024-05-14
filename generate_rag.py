from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.llms.llama_cpp.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

model_url = "https://huggingface.co/NousResearch/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"

llm = LlamaCPP(
    model_url=model_url,
    model_path=None,
    temperature=0.1,
    max_new_tokens=2048,
    context_window=8192,
    generate_kwargs={},
    model_kwargs={"n_gpu_layers": 1},
    messages_to_prompt=messages_to_prompt,
    completion_to_prompt=completion_to_prompt,
    verbose=True,
)

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

documents = SimpleDirectoryReader(
    "./data"
).load_data()

index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

query_engine = index.as_query_engine(llm=llm)

description = "a simple tic tac toe game where the player plays against the computer"

prompt2 = "Write me C code that compiles to a .gb file given the following description. Do not return any other text, just the C code in backticks. It will be compiled and ran on a Nintendo GameBoy. Description: {description}".format(description=description)

prompt = """
Write me C code that compiles to a .gb file given the following description. 
Do not return any other text, just the full C code enclosed in backticks.
The code should be error free and concise, do not make any assumptions. Everything should be in one file. Define any methods or variables you need.
Use tiling to draw sprites.
You'll want to use `#include <gb/gb.h>` in your headers and use `joypad()` to wait for user control.

It will be compiled and ran on a Nintendo GameBoy, so be visually creative.

Description: 

{description}

""".format(description=description)

prompt3 = "Use the provided header documentation to write C code that compiles to a .gb file to be run on a GameBoy. The program should be a simple interactive game."

response = query_engine.query(prompt2)

print(response)