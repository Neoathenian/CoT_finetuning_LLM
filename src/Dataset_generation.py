import random
import time
import os
from datetime import datetime
from src.Basic_LLM_functions import LLM_conection
#If you want anything here to run, you must connect to LLM_conection a model&tokenizer or modify it for api use

def read_list_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Read lists from files
main_topics = read_list_from_file('Prompts_and_co/list_main_topics.txt')
difficulties = read_list_from_file('Prompts_and_co/list_difficulties.txt')
problem_types = read_list_from_file('Prompts_and_co/list_problem_types.txt')
conceptual_connectors = read_list_from_file('Prompts_and_co/list_conceptual_connectors.txt')



def generate_question_parameters():
    return {
        'main_topic': random.choice(main_topics),
        'difficulty': random.choice(difficulties),
        'problem_type': random.choice(problem_types),
        'conceptual_connector': random.choice(conceptual_connectors)
    }

def format_subtopic_prompt(params):
    with open('Prompts_and_co/prompt_generate_subtopic.txt', 'r') as file:
        template = file.read()
    return template.format(**params)

def format_question_prompt(params):
    with open('Prompts_and_co/prompt_generate_question.txt', 'r') as file:
        template = file.read()
    return template.format(**params)


def generate_subtopic(params,model,tokenizer):
    prompt = format_subtopic_prompt(params)
    response = LLM_conection.Get_answer(prompt)
    
    if isinstance(response, list) and len(response) > 0:
        return response[0].text.strip()
    else:
        return response.strip()  # Changed to handle string response

def generate_question(params,model,tokenizer):
    prompt = format_question_prompt(params)
    response = LLM_conection.Get_answer(prompt)
    
    if isinstance(response, list) and len(response) > 0:
        return response[0].text.strip()
    else:
        return response.strip()  # Changed to handle string response

def generate_full_question(model,tokenizer):
    params = generate_question_parameters()
    subtopic = generate_subtopic(params,model,tokenizer)
    
    params['subtopic'] = subtopic
    question = generate_question(params,model,tokenizer)
    
    return {
        'main_topic': params['main_topic'],
        'difficulty': params['difficulty'],
        'problem_type': params['problem_type'],
        'conceptual_connector': params['conceptual_connector'],
        'subtopic': subtopic,
        'question': question
    }

def save_question_and_log(question_data, subtopic_prompt, question_prompt,folder="Dataset_creation/questions"):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"sample_{timestamp}_{question_data['main_topic'].replace(' ', '_')}.txt"
    
    # Save question
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, filename), 'w') as file:
        file.write(question_data['question'])
    
    # Save log
    os.makedirs('log', exist_ok=True)
    with open(os.path.join('log', filename), 'w') as file:
        file.write(f"Main Topic: {question_data['main_topic']}\n")
        file.write(f"Difficulty: {question_data['difficulty']}\n")
        file.write(f"Problem Type: {question_data['problem_type']}\n")
        file.write(f"Conceptual Connector: {question_data['conceptual_connector']}\n")
        file.write(f"Subtopic: {question_data['subtopic']}\n\n")
        file.write("Subtopic Prompt Template:\n")
        file.write(subtopic_prompt + "\n\n")
        file.write("Question Prompt Template:\n")
        file.write(question_prompt + "\n\n")
        file.write("Generated Question:\n")
        file.write(question_data['question'])


with open('Prompts_and_co/prompt_generate_subtopic.txt', 'r') as file:
    subtopic_prompt_template = file.read()

with open('Prompts_and_co/prompt_generate_question.txt', 'r') as file:
    question_prompt_template = file.read()
