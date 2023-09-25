# This implementation of self-consistency is not very stable due to the LLM often returning the Final Answer in the wrong format, making it challenging for the Final Answer value to be parsed and correctly accounted for.
# https://arxiv.org/pdf/2203.11171.pdf

import openai
import os
import dotenv
import re
import random

from .CoT import create_cot_prompt

dotenv.load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

model = 'gpt-3.5-turbo'

def perform_sc(question, subject=None, n=2, n_samples=5): # question contains only the input to the question
    results = []

    for sample in range(n_samples):
        # Create cot prompt from random samples
        cot_prompt = create_cot_prompt(few_shot=True, subject=subject, n=n)
        final_cot_prompt = cot_prompt.replace("{question}", question)
        instruction = "The final answer should be returned as 'Final Answer: [final_answer]' and be as concise as possible. For example, if the question is: 'Which is a faster way to get home? Option 1: Take an 10 minutes bus, then an 40 minute bus, and finally a 10 minute train. Option 2: Take a 90 minutes train, then a 45 minute bike ride, and finally a 10 minute bus.' final_answer should consist of only 'Option 2'"
        final_cot_prompt += instruction

        msg = [
            {'role': 'system', 'content': final_cot_prompt}
        ]

        # Get the final answer for the prompt
        response = openai.ChatCompletion.create(
            model=model,
            messages=msg,
            max_tokens=500,
        )
        # Determine the final answer given by the model
        answer = response['choices'][0]['message']['content']
        pattern = re.compile(r'Final Answer: (.+)')
        match = re.search(pattern, answer)
        # If a match is found, extract the final answer
        if match:
            final_answer = match.group(1)
        else:
            final_answer = "No match found."

        # Logic to add final answer to the results table
        found = False
        for result in results:
            if result['Final Answer'] == final_answer:
                result['Count'] += 1
                found = True
                break
        if not found:
            results.append({"Final Answer": final_answer, "Count": 1})

    # Find the most common final answer. Handle the case where there is a tie for first place by randomly selecting one of the final answers
    max_count = max([result['Count'] for result in results])
    candidates = [result for result in results if result['Count'] == max_count]
    chosen_dict = random.choice(candidates)
    chosen_answer = chosen_dict['Final Answer']
    
    return chosen_answer