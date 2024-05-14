from llama_cpp import Llama

llm = Llama(
      model_path="/path/to/model/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf",
      n_gpu_layers=-1,
      n_ctx=8192,
)

description = "render a pyramid in isometric view"

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

prompt2 = "Write me C code that compiles to a .gb file given the following description. Do not return any other text, just the full C code enclosed in backticks. The code should be error free and concise, do not make any assumptions. You'll want to use `#include <gb/gb.h>` in your headers and use `joypad()` to wait for user control. It will be compiled and ran on a Nintendo GameBoy, so be visually creative. Description: a simple pong game where the player plays against the computer"

output = llm(
      prompt,
      max_tokens=None,
)

print(output['choices'][0]['text'])