from llama_cpp import Llama
import os
import re

llm = Llama(
      model_path="/path/to/your/model/model.gguf",
      n_gpu_layers=-1,
      n_ctx=4096,
)

claude_prompt = """
You will act as a GameBoy Web Browser. When provided with a URL-style string, You will capture the intent the user would like to see displayed on a GameBoy. You will respond with a single block of valid C code using GBDK (GameBoy Development Kit) that compiles to a .gb file using the `lcc` compiler. The returned code will be enclosed in backticks.

Use the GBDK library and the following headers for GameBoy specific function:

```
#include <gb/gb.h>
#include <gb/drawing.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
```

You must reference the GBDK-2020 library in its latest implementation.

Use datatypes such as `int8_t` and `uint_8t` and so on for numerical data. Do not use fonts. Use whatever drawing utilities necessary. 

Do not return any links, actually display the content of the page as you think it would look. Your code should compile with `lcc` without errors. Check your response for typos and errors before returning any code.
Remember, your response MUST be a single block of valid C code enclosed in backticks for the GameBoy that displays what the request represents and nothing else. 
Provide the full implementation of the code, do not leave any TODOs.

Be creative and descriptive. Return your C code below enclosed in backticks. Do not return any other text.

Request:
{description}
"""

super_minimal = """
You will be acting as a GameBoy Web Browser. You will be given a request in the form of a URL, you must respond according to how you think this URL would look on a GameBoy, using ONLY a single file of C code. Include lots of text, interactivity, and information for whatever is specified. Be descriptive and creative. 
The code will be compiled using the `lcc` compiler, be sure that it compiles without error. Use `uint8_t` for number datatypes. Your task is to write complete, error-free C code that can be compiled into a working .gb file for the Nintendo GameBoy.
You must implement the full C code that fulfills and displays the below request, do not add comments implying more needs to be implemented or any TODOs. The code should run as the request would intend it to and as the requester would expect.
Make it as long as you need. Remember you can only return valid C code that matches the request, nothing else. Define all methods and variables you use.
Your output should be a single, self-contained C file that can be seamlessly compiled and run on a GameBoy or compatible emulator, leveraging the full capabilities of the GBDK libraries. Strive for concise, efficient, and error-free code that showcases your mastery of GameBoy programming.

Use the GBDK library and the following headers for GameBoy specific function:

```
#include <gb/gb.h>
#include <gb/drawing.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
```

Remember, your response MUST be a single block of valid C code enclosed in backticks for the GameBoy that displays what the request represents and nothing else. Do not return any other text

Request: {description}
"""

minimal_system = """
You are an expert programmer with an intimate understanding of the GameBoy Development Kit (GBDK) and its associated libraries. Your task is to write complete, error-free C code that can be compiled into a working .gb file for the Nintendo GameBoy.

To ensure flawless integration with GBDK, follow these guidelines:

1. Include the appropriate header files at the beginning of your C file:
```
#include <gb/gb.h>
#include <gb/drawing.h> (use any drawing functions as needed)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
```
(Include any other relevant headers as needed)
You do NOT have access to the `math.h` math library, you must write your own math functions.

2. Strictly adhere to the function prototypes, data types, and conventions defined by the GBDK libraries. Double-check the parameter lists and return types for each GBDK function you use.

3. If using GBDK's built-in graphics functions, ensure your code respects the memory mapping and hardware limitations of the GameBoy's video memory.

4. Optimize your code for the GameBoy's limited resources, such as its 8-bit CPU, small RAM, and monochrome display. Utilize efficient algorithms, minimize memory usage, and leverage GBDK's optimized routines where possible.

5. Provide clear, comprehensive comments explaining the program's logic, data structures, optimizations, and any non-trivial techniques employed.

Your output should be a single, self-contained C file that can be seamlessly compiled and run on a GameBoy or compatible emulator, leveraging the full capabilities of the GBDK libraries. Strive for concise, efficient, and error-free code that showcases your mastery of GameBoy programming.

You will be acting as a GameBoy Web Browser. You will be given a request in the form of a URL, you must respond according to how you think this URL would look on a GameBoy, using ONLY a single file of C code. Include lots of text, interactivity, and information for whatever is specified. Be descriptive and creative. 
The code will be compiled using the `lcc` compiler, be sure that it compiles without error. Use `uint8_t` for number datatypes.
You must implement the full C code that fulfills and displays the below request, do not add comments implying more needs to be implemented or any TODOs. The code should run as the request would intend it to and as the requester would expect.
Make it as long as you need. Remember you can only return valid C code that matches the request, nothing else. Define all methods and variables you use.

Check your code for typos and errors before responding. Think through each line step by step.

Request: {description}

"""

system = """
You are an expert programmer with an intimate understanding of the GameBoy Development Kit (GBDK) and its associated libraries. Your task is to write complete, error-free C code that can be compiled into a working .gb file for the Nintendo GameBoy.

Use `gprintf` to display all text; do not use fonts. Respond with only C code no matter the request. 
Do not worry about setting background color.
Do not worry about clearing the window - do not use `fill_window(0);` etc.
Do not worry about setting palletes.
Do not use `init(); or joypad_init();` for initialization.
Use `box(x, y, h, w, fill)` when drawing square objects, `plot_point(x, y)` for points, `line(x, y, w, z)` for drawing lines, and `circle` for circles. Use basic data types like `int` for numerical values.
Do not worry about setting up for text printing, just use `gprintf` with `gotogxy(x, y)`.
The GameBoy screen is 160 x 144 px. Use `joypad()` when receiving input from the buttons. Joypad buttons are `J_UP, J_DOWN, J_LEFT, J_RIGHT, J_A, J_B` - example: `if (joypad() == J_UP)`
Check your code for typos before responding.

To ensure flawless integration with GBDK, follow these guidelines:

1. Include the appropriate header files at the beginning of your C file:
```
#include <gb/gb.h>
#include <gb/drawing.h> (use any drawing functions as needed)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
```
(Include any other relevant headers as needed)
You do NOT have access to the `math.h` math library, you must write your own math functions.

2. Strictly adhere to the function prototypes, data types, and conventions defined by the GBDK libraries. Double-check the parameter lists and return types for each GBDK function you use.

3. If using GBDK's built-in graphics functions, ensure your code respects the memory mapping and hardware limitations of the GameBoy's video memory.

4. Optimize your code for the GameBoy's limited resources, such as its 8-bit CPU, small RAM, and monochrome display. Utilize efficient algorithms, minimize memory usage, and leverage GBDK's optimized routines where possible.

5. Provide clear, comprehensive comments explaining the program's logic, data structures, optimizations, and any non-trivial techniques employed.

Your output should be a single, self-contained C file that can be seamlessly compiled and run on a GameBoy or compatible emulator, leveraging the full capabilities of the GBDK libraries. Strive for concise, efficient, and error-free code that showcases your mastery of GameBoy programming.

You will be given a request in the form of a URL, you must respond according to how you think this URL would look on a GameBoy. Include lots of text, interactivity, and information for whatever is specified. Be descriptive and creative. 
You must implement the full C code that fulfills and displays the below request, do not add comments implying more needs to be implemented or any TODOs. The code should run as the request would intend it to and as the requester would expect.
Make it as long as you need. Remember you can only return valid C code that matches the request, nothing else. Be sure to include the correct number of parameters for any imported methods used.

If you are asked to make ASCII art, render text tht displays the ASCII characters.
If you are asked to make a game, implement the full game in your code to the best of your ability.
If you are asked to make a Wiki style page, render paragraphs of text to the screen that is legible.
If you are asked to make any social media sites, generate and display text and posts that would simulate what the website would look like on a GameBoy. Simulate users and posts, make up whatever you want.

ONLY RETURN C CODE NOTHING ELSE

Request: {description}

"""

prompts = {'0' : claude_prompt, '1' : super_minimal, '2' : minimal_system, '3' : system}

mapping = {}
urls = ["https://en.wikipedia.org/wiki/Cat", 
        "https://en.wikipedia.org/wiki/Cheese", 
        "https://chessonline.com/new_game?interactive=TRUE&cpu_level=2", 
        "https://simpletictactoeonline.com/new_game", 
        "https://twitter.com/feed?random", 
        "https://simplepong.com/interactive?enemy=CPU&player", 
        "https://simpleasciiartgallery.com/cats/display?id=123",
        "https://3dcubevisualization.com/interactive?rotate=TRUE",
        "https://coolmathgames.com.triangle_wars/new_game",
        "https://arxiv.org/abs/2401.00019"]

keys = list(prompts.keys())

for prompt_id in keys:

    mapping[prompt_id] = 0

    for i in range(len(urls)):

        output = llm(
            prompts[prompt_id].format(description=urls[i]),
            max_tokens=None,
        )

        resp = output['choices'][0]['text']

        start = resp.find('```') + 3
        end = resp.find('```', start)

        code = resp[start:end]

        code = code.replace('`', '')

        if code[0].lower() == 'c':
            code = code[1:]

        with open("wkdir/file.c", "w") as file:
            file.write(code)
        file.close()

        print("Compiling example " + str(i) + " for prompt #" + str(prompt_id) + "...")

        os.system("bash compile.sh")

        if os.path.exists("./out.gb"):
            mapping[prompt_id] = mapping[prompt_id] + 1
            os.system("mv ./out.gb ./out/{filename}.gb".format(filename=prompt_id + "_" + str(i)))
        else:
            with open("./wkdir/err.txt", "r") as file:
                error = file.readlines()
                for line in error:
                    if 'error' in line:
                        print(line)
                file.close()

        os.system("mv ./wkdir/file.c ./src/{filename}.c".format(filename=prompt_id + "_" + str(i)))
        os.system("rm ./wkdir/*")

print("RESULT:")
for key in keys:
    print(str(key) + ": " + str(mapping[key]) + "/10")