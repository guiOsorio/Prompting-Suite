import openai
import os
import dotenv

dotenv.load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

# Define LLM model and system prompt
model = 'gpt-3.5-turbo'
system_prompt = 'You are a helpful assistant.'
messages = [
        {'role': 'system', 'content': system_prompt}
    ]

def add_message(messages, role, message):
    messages.append({'role': role, 'content': message})
    return messages

# Start conversation
while True:
    user_input = input("Input (type 'exit' to end the conversation): ")

    if user_input == 'exit':
        print(messages)
        break

    # Add user input
    messages = add_message(messages, 'user', user_input)
    # Call LLM
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=100,
    )
    # Add LLM's output (answer) to memory
    answer = response['choices'][0]['message']['content']
    messages = add_message(messages, 'assistant', answer)

    print(answer)