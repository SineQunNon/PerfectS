import sys
import os



# loader 모듈이 있는 경로를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'loader')))

from main import get_soap
from pdf_loader import load_pdf

pdf_filepath = '/Users/sinequanon/Documents/PerfectS/data/pdf_data/TEST_04.pdf'
pages = load_pdf(pdf_filepath)

soap_result = get_soap(pages)

print(len(soap_result))
content = []
for i in range(len(soap_result)):
    #print(soap_result[i]['date'])
    content.append(soap_result[i]['date'])
    #print(soap_result[i]['subjective'])
    content.append(soap_result[i]['subjective'])

print(content)
from langchain import hub
from langchain_community.chat_models.openai import ChatOpenAI
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain.document_loaders import WebBaseLoader
from langchain.schema.runnable import RunnablePassthrough

llm = ChatOpenAI(model_name='gpt-4-turbo')

