#------------------------get LLM input--------------------------#
from loader.pdf_loader import load_pdf
from loader.main import *
from langchain_openai import ChatOpenAI
from prompt.prompt import get_prompt, get_parser
from langchain_core.runnables import RunnablePassthrough

def get_ppt_input(pdf_path):
    pages = load_pdf(pdf_path)

    soap = get_soap(pages)
    info = get_animal_data(pages)

    llm_input = get_LLM_input(info, soap)

    #------------------------get LLM input--------------------------#
    
    llm = ChatOpenAI(model_name='gpt-4o', temperature=0)

    prompt = get_prompt()
    parser = get_parser()

    #------------------------chain--------------------------#

    chain = {'input' : RunnablePassthrough()} | prompt | llm | parser

    answer = chain.invoke(llm_input)
    
    return answer