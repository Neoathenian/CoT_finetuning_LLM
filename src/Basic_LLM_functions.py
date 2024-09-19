
def Call_LLM(messages,model,tokenizer,max_new_tokens=1280):
    """This is the base function to call the LLM model. It takes a list of messages, the model and tokenizer and returns the answer (as a string).
        The list of messages has to be in the format [{"from": "human", "value": question}, {"from": "assistant", "value": answer}, ...]
    """
    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
    ).to("cuda")

    #text_streamer = TextStreamer(tokenizer)
    #out = model.generate(input_ids=inputs, streamer=text_streamer, max_new_tokens=1280, use_cache=True)
    #I´m avoiding the text streamer for now, as it is verbose (it prints the generated text)
    out = model.generate(input_ids=inputs, max_new_tokens=max_new_tokens, use_cache=True,attention_mask=(inputs != tokenizer.pad_token_id).long())
    return tokenizer.batch_decode(out)[0].split("<|im_start|>assistant")[-1].replace("<|im_end|>", "").strip()


#from transformers import TextStreamer
def Get_answer(question,model,tokenizer,max_new_tokens=1280):
    """This function takes a question and returns the answer from the model. Input str question, output str."""
    messages = [
        {"from": "human", "value": question},
    ]
    return Call_LLM(messages,model,tokenizer,max_new_tokens=max_new_tokens)
    

class LLM_Conection():
    """This class is to abstract away the api connection allowing for local models.
        The idea is that the user modifies the LLM_conection.Get_answer function to connect to the model of choice (api or local model)."""
    def __init__(self,model=None,tokenizer=None):
        self.model=model
        self.tokenizer=tokenizer

    def Get_answer(self,prompt,max_new_tokens=1280):
        """Returns the answer from the model given a prompt. Input str prompt, output str."""
        return Get_answer(prompt,self.model,self.tokenizer,max_new_tokens=max_new_tokens)

    def set_model(self,model,tokenizer):
        self.model=model
        self.tokenizer=tokenizer

#This is the global LLM class that has to be modified to connect to the model of choice
LLM_conection=LLM_Conection()


############################ Up to here the basics, below are some basic stuff that don´t merit another .py yet ############################


def Answer_is_correct(question, solution,answer):
    """This function takes a question, a solution and an answer and returns True if the answer is correct, False if it is wrong.
        The function uses the LLM_conection.Get_answer function to get the answer from the model."""
    prompt= f"""this is the question: {question}, and this is the answer given by a chatbot {answer}.
                Knowing that the answer is {solution}, did it get it right? 
                Answer with a simple yes or no."""
    
    result=LLM_conection.Get_answer(prompt,max_new_tokens=5)

    
    if "yes" in result and "no" in result:
        print(f"SOMETHLING WENT WRONG with {question}")
        return False
    elif "yes" in result:
        return True
    else:
        return False



