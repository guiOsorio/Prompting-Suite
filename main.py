import openai
import os
import dotenv

from methods.CoT import create_cot_prompt

dotenv.load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

# Define LLM model and system prompt
model = 'gpt-3.5-turbo'
possible_methods = ['cot']

def create_system_prompt(cot_few_shot, cot_subject, cot_n, method=None):
    if method in possible_methods:
        if method.lower() == 'cot':
            system_prompt = create_cot_prompt(few_shot=cot_few_shot, subject=cot_subject, n=cot_n)
    elif method == None:
        system_prompt = 'You are a helpful assistant.'
    else:
        raise ValueError(f"the method selected is invalid. Available methods are {possible_methods}")

    init_msg = [
        {'role': 'system', 'content': system_prompt}
    ]

    return init_msg

def add_message(messages, role, message):
    messages.append({'role': role, 'content': message})
    return messages

# Start conversation
def chat(messages):
    user_input = input("Input (type 'exit' to end the conversation): ")

    # Terminate chat if input is 'exit'
    if user_input == 'exit':
        print(messages)
    else:
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
        new_messages = add_message(messages, 'assistant', answer)

        print(answer)

        chat(new_messages)

    
init_msg = create_system_prompt(cot_few_shot=True, cot_subject=None, cot_n=2, method='cot')
chat(messages=init_msg)
    

