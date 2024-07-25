from llm.llm_module import llm_function

def prompt_function():
    result = llm_function()
    return f"receive : {result}"

if __name__=="__main__":
    print(prompt_function())