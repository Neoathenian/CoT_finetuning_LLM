import re

from src.Basic_LLM_functions import LLM_conection
#If you want anything here to run, you must connect to LLM_conection a model&tokenizer or modify it for api use
from src.Logger import logger, set_logging_level




# Function to prompt the LLM to think about the question
def think_about_question(question):
    prompt = f"Think about the following question and provide any general information that might be useful to solve it:\n\nQuestion: {question}"
    return LLM_conection.Get_answer(prompt)

# Function to prompt the LLM to reason an answer given the question, information, and correct steps
def reason_answer(question, information, correct_steps):
    prompt = f"Given the question '{question}'"
    if information:
        prompt += f" and the following information:\n{information}"
    if correct_steps:
        prompt += f"\n\nPreviously verified reasoning steps:\n"
        for idx, step in enumerate(correct_steps, start=1):
            prompt += f"{idx}. {step}\n"
        prompt += "\nPlease continue the reasoning from these steps and provide your answer."
    else:
        prompt += "\n\nPlease reason an answer and provide your reasoning."
    prompt += "\nEnd with 'Answer:' followed by your answer."
    return LLM_conection.Get_answer(prompt)

# Function to prompt the LLM to divide reasoning into steps
def divide_reasoning(reasoning):
    prompt = f"Please divide the following reasoning into small, numbered steps:\n\n{reasoning}"
    return LLM_conection.Get_answer(prompt)

# Function to simplify reasoning steps
def simplify_reasoning(steps):
    prompt = "I have the following list of reasoning steps: \n"
    for idx, step in enumerate(steps, start=1):
        prompt += f"{idx}. {step}\n"
    prompt+= """Please simplify them while maintaining the key logical flow and ensuring clarity. 
                Separate each step with ## Step and the number of the step. Ex: ## Step 1. 
                Remove unnecessary details and focus on the core points. 
                Do not add an extra message doing what you´ve done, just list out the different reasoning steps.
    """
    simplified_steps_text = LLM_conection.Get_answer(prompt)

    # Split the simplified steps based on the '## Step' separator using regex
    simplified_steps = re.split(r'## Step \d+', simplified_steps_text)
    
    # Remove any leading or trailing whitespace from each step
    simplified_steps = [step.strip() for step in simplified_steps if step.strip()]
    
    return simplified_steps


# Function to generate an answer given the question and reasoning steps
def generate_answer(question, steps):
    prompt = f"Based on the following reasoning steps, provide the answer to the question '{question}':\n\n"
    for idx, step in enumerate(steps, start=1):
        prompt += f"{idx}. {step}\n"
    prompt += "\nAnswer:"
    answer = LLM_conection.Get_answer(prompt)
    return answer.strip()

# Function to verify a reasoning step in the context of full reasoning and question
def verify_step(step,question, reasoning_steps):
    # Flatten the list of reasoning steps into a string
    reasoning_str = "\n".join(reasoning_steps)
    
    prompt = f"""Question: {question}

                Here is the full reasoning so far:
                {reasoning_str}
                
                Now, evaluate the following step in this context. Answer 'Yes', 'No', or 'Informative'. 
                Provide a brief explanation for 'No' or 'Informative' if needed. 
                Step: {step}
                """
    
    return LLM_conection.Get_answer(prompt)


def Chain_of_thought(question, max_attempts=3, verbose=0):
    set_logging_level(verbose)
    
    attempt = 0
    success = False
    accumulated_correct_steps = []
    information = None  # Initialize information variable

    while attempt < max_attempts and not success:
        attempt += 1

        # Log attempt number and question
        logger.info(f"----------------------\nAttempt {attempt} for question: {question}")

        # Step 1: Think about the question (only in the first attempt)
        if attempt == 1:
            information = think_about_question(question)
            logger.info(f"----------------------Additional information: {information}")

        # Step 2: Reason an answer given the question, information, and correct steps
        reasoning_and_answer = reason_answer(question, information, accumulated_correct_steps)
        logger.debug(f"----------------------\nReasoning and answer: {reasoning_and_answer}")

        # Try to extract the answer from the reasoning
        if 'Answer:' in reasoning_and_answer:
            reasoning_part, answer_part = reasoning_and_answer.rsplit('Answer:', 1)
            reasoning = reasoning_part.strip()
            generated_answer = answer_part.strip()
        else:
            reasoning = reasoning_and_answer.strip()
            generated_answer = None  # Set to None to indicate we need to generate it


        # Step 3: Divide reasoning into steps
        divided_reasoning = divide_reasoning(reasoning)
        steps = []
        for line in divided_reasoning.strip().split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                step = line.lstrip('0123456789.- ').strip()
                steps.append(step)
            else:
                steps.append(line)

        # Step 4: Simplify reasoning steps
        simplified_steps = simplify_reasoning(steps)
        logger.info(f"----------------------\nSimplified steps: {simplified_steps}")

        # If answer is None, generate answer from simplified reasoning steps
        if generated_answer is None:
            generated_answer = generate_answer(question, simplified_steps)
            logger.info(f"----------------------\nGenerated answer: {generated_answer}")

        # Step 5: Verify each simplified step
        all_steps_correct = True
        verified_steps = []
        for step in simplified_steps:
            verification = verify_step(step, question, simplified_steps)
            if verification.lower().startswith('yes'):
                verified_steps.append(step)
            else:
                all_steps_correct = False
                logger.warning(f"----------------------\nStep incorrect: {step}\nVerification: {verification}")
                break  # Stop verifying further steps

        if all_steps_correct:
            logger.info("----------------------")
            logger.info("Question answered with verified reasoning.")
            logger.info(f"Answer: {generated_answer}")
            return {
                "question": question,
                "information": information,
                "simplified_steps": simplified_steps,
                "answer": generated_answer
            }
        else:
            accumulated_correct_steps = verified_steps.copy()
            logger.info(f"Reasoning was not fully correct. Attempts remaining: {max_attempts - attempt}")

    return {
        "question": question,
        "information": "",
        "simplified_steps": "",
        "answer": ""
    }

