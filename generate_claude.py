import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="your-api-key",
)

message = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=2048,
    temperature=0.0,
    system="You are an expert GameBoy software developer who writes perfect C code from a given request. Do not respond with any other text, just the full C code enclosed in backticks.",
    messages=[
        {"role": "user", "content": "Request: a creative and pretty visualization"}
    ]
)

print(message.content[0].text)