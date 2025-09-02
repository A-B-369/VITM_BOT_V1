import ollama

# Run your custom model
response = ollama.chat(model="vitm_bot", messages=[
    {"role": "user", "content": "Hello"}
])

print(response["message"]["content"])
