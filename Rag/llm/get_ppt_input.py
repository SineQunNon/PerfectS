#------------------------get LLM input--------------------------#
from Rag.loader.pdf_loader import load_pdf
from Rag.prompt.prompt import get_prompt, get_parser, get_table_propmt
from Rag.loader.main import *

from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def get_ppt_input(pdf_path):
    pages = load_pdf(pdf_path)

    soap = get_soap(pages)
    info = get_animal_data(pages)

    llm_input = get_LLM_input(info, soap)

    #------------------------get LLM input--------------------------#
    
    llm = ChatOpenAI(model_name='gpt-4-turbo', temperature=0)

    prompt = get_prompt()
    parser = get_parser()

    #------------------------chain--------------------------#

    chain = {'input' : RunnablePassthrough()} | prompt | llm | parser

    answer = chain.invoke(llm_input)
    
    return answer


def get_lab_table_summary_input(table_str):
    llm = ChatOpenAI(model_name='gpt-4-turbo', temperature=0)

    prompt = get_table_propmt()

    chain = {'input' : RunnablePassthrough()} | prompt | llm | StrOutputParser()

    answer = chain.invoke(table_str)

    return answer