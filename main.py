import openai
import os
import dotenv

from methods.CoT import create_cot_prompt, possible_subjects, cot_examples
from methods.self_consistency import perform_sc

dotenv.load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

# Define LLM model and system prompt
model = 'gpt-3.5-turbo'
possible_methods = ['cot', 'cot+sc']

def create_system_prompt(cot_few_shot=None, cot_subject=None, cot_n=None, method=None):
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
def chat(messages, cot=False, sc=False, sc_subject=None, sc_n=None, sc_n_samples=None):
    user_input = input("Input (type 'exit' to end the conversation): ")

    # Terminate chat if input is 'exit'
    if user_input == 'exit':
        return
    else:
        # Add user input
        messages = add_message(messages, 'user', user_input)

        # Self-consistency
        if sc == True:
            answer = perform_sc(question=user_input, subject=sc_subject, n=sc_n, n_samples=sc_n_samples)
            print(answer)
            return
        
        # Chain-of-thought
        elif cot:
            # Call LLM
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=500,
            )
            answer = response['choices'][0]['message']['content']
        
            # Add LLM's output (answer) to memory
            new_messages = add_message(messages, 'assistant', answer)

            print(answer)

            chat(new_messages, cot=cot)


# Terminal interface for user to choose the prompting technique to be used
selected_method = input(f"Type the index of a prompting method to be selected. Available methods are {[(i, method) for i, method in enumerate(possible_methods)]}\n")
selected_method = int(selected_method)

if selected_method not in range(0, len(possible_methods)):
    raise ValueError("Invalid index selected")

# CoT
if possible_methods[selected_method] == 'cot':
    init_msg = create_system_prompt(cot_few_shot=True, cot_subject=None, cot_n=2, method='cot')
    chat(messages=init_msg, cot=True)
# CoT + SC - not a chatbot, made for one input/output pair only
elif possible_methods[selected_method] == 'cot+sc':
    # Select subject and validate it
    sc_subject = input(f"Select a subject from the following list {[subject for subject in possible_subjects]}: ")
    if sc_subject == None:
        pass
    elif sc_subject not in possible_subjects:
        raise ValueError("Not a valid subject")
    
    # Select number of cot shots and validate it
    sc_n = int(input("Select the number of cot shots: "))
    if sc_subject == None:
        all_shots = [item for sublist in cot_examples.values() for item in sublist]
        if sc_n > len(all_shots):
            raise ValueError(f"n is too large. The total number of examples provided is {len(all_shots)}")
    else:
        subject_len = len(cot_examples[sc_subject])
        if sc_n > subject_len:
            raise ValueError(f"n is too large. The selected subject has {subject_len} examples")

    sc_n_samples = int(input("Select the number of samples to be used in sc: "))
    init_msg = create_system_prompt()
    chat(messages=init_msg, sc=True, sc_subject=sc_subject, sc_n=sc_n, sc_n_samples=sc_n_samples)
# Auto-CoT


# Which is a faster way to get home? Option 1: Take an 10 minutes bus, then an 40 minute bus, and finally a 10 minute train. Option 2: Take a 90 minutes train, then a 45 minute bike ride, and finally a 10 minute bus.