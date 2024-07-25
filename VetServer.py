
# 파이썬 라이브러리
import pickle, torch, json, time, faiss, pickle, numpy as np, mysql.connector 
from typing import Tuple

# API 키 및 env 설정파일 로드
from dotenv import load_dotenv; 
load_dotenv()

# Nvidie-Embed 라이브러리 : AutoModel -> HuggingFaceEmbedding 으로 대채함
# import torch.nn.functional as F
# from transformers import AutoModel

# langchain 라이브러리
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_teddynote.retrievers import KiwiBM25Retriever

# ================== Retrieval, Embedding ========================
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
# HuggingFaceEmbedding, 부모 클래스의 trust_remote_code=True 수정 필요 -> 오버라이딩으로 불가능.
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
# ================== Retrieval, Embedding ========================

# LangSmith 추적 시작 코드
from langchain_teddynote import logging
logging.langsmith("Flask langsmith")

# Flask BackEnd API 라이브러리
from flask_cors import CORS
from flask import Flask, Response, request, jsonify
app = Flask(__name__)
CORS(app)

class LanguageDetector:
    def __init__(self, text:str):
        self.text = text

    def check_language(self:str):
        korean_only = all(ord('가') <= ord(c) <= ord('힣') for c in self.text)
        english_only = all(ord('A') <= ord(c.upper()) <= ord('Z') for c in self.text)
    
        if korean_only:
            return 'ko'
        elif english_only:
            return 'en'
        else:
            return 'mix'
        

def init_database() -> tuple[mysql.connector]:
    conn = mysql.connector.connect(
        host='10.100.54.176',
        user='root',
        password='ibdp',
        database='ChatVet',  # 데이터베이스 이름
    )

    cursor = conn.cursor()
    
    return conn, cursor

def init_retrieval(conn: mysql.connector, cursor: mysql.connector) -> list[FAISS]:
    embeddings = HuggingFaceEmbeddings(model_name="nvidia/NV-Embed-v1",model_kwargs={'device':'cpu'})
    cursor.execute("SELECT paper_name, journal FROM paper")
    temp = cursor.fetchall()

    jvim1_list = list(x[0] for x in filter(lambda x: x[1] == 'JVIM1', temp))
    jvim2_list = list(x[0] for x in filter(lambda x: x[1] == 'JVIM2', temp))
    sc_list = list(x[0] for x in filter(lambda x: x[1] == 'sciencedirect', temp))

    with open("JVIM1_embed.pkl",'rb') as file:
        jvim1_pairs = pickle.load(file)
        vector_db_jvim1 = FAISS.from_embeddings(jvim1_pairs, embeddings)

    with open("JVIM2_embed.pkl",'rb') as file:
        jvim2_pairs = pickle.load(file)
        vector_db_jvim2 = FAISS.from_embeddings(jvim2_pairs, embeddings)
        
    with open("sciencedirect_embed.pkl",'rb') as file:
        sc_pairs = pickle.load(file)
        vector_db_sc = FAISS.from_embeddings(sc_pairs, embeddings)

    bm25_retriever_jvim1 = KiwiBM25Retriever.from_texts(jvim1_list)
    bm25_retriever_jvim1.k = 50

    bm25_retriever_jvim2 = KiwiBM25Retriever.from_texts(jvim2_list)
    bm25_retriever_jvim2.k = 50

    bm25_retriever_sc = KiwiBM25Retriever.from_texts(sc_list)
    bm25_retriever_sc.k = 50

    return [vector_db_jvim1, vector_db_jvim2, vector_db_sc], [bm25_retriever_jvim1, bm25_retriever_jvim2, bm25_retriever_sc]



def init_ebook_retrivals() -> FAISS:
    ebook_retrival = faiss.read_index("ebook_embedding.index")
    with open('ebook_docs.pkl', 'rb') as file:
        ebook_docs = pickle.load(file)
    return ebook_retrival, ebook_docs


def init_LLM():
    llm = ChatOpenAI(
        model='deepseek-chat', 
        openai_api_key='sk-61882d35abe845658210841b77081aee', 
        openai_api_base='https://api.deepseek.com',
        max_tokens=4096
    )
    
    prompt = ChatPromptTemplate.from_template("{history} {topic}")
    chain = prompt | llm | StrOutputParser()

    return chain



# 데이터베이스 커서 로드
conn, cursor = init_database()
print("DataBase Connection Success")

# 벡터기반 리트리버, BM기반 리트리버, 원문 문서정보 로드
vector_retrievers, bm25_retrievers = init_retrieval(conn, cursor)
print("Retrieval Load Finished")


# LLM 로드
llm_chain = init_LLM()
print("LLM Chain Load Finished")
# Ebook 기반 리트리버 로드
ebook_retrival, ebook_docs = init_ebook_retrivals()
print("Ebook-Retrieval Load Finished")


def re_ranking(docs: list[Document]):
    pass


# VectorDB Search langsmith Runnable 변환 코드 ===================================
def get_retrieval_results(query : list[str]):
    state = query[1].split(",")
    k = query[2]
    
    docs_list = []
    for idx in range(len(state)):
        if state[idx] == 'true' :
            docs_list.extend(vector_retrievers[idx].similarity_search_with_score(query[0],50))
        else:
            pass

    sorted_list = sorted(docs_list,key = lambda x:x[1])[:k] # VectorDB는 낮은 스코어가 유사도가 높음
    pair_form = [(x[0].page_content,x[1]) for x in sorted_list]  

    return [pair_form,"VectorSearch"] # Runnable 로그추적을 위한 더미 데이터 반환

smith_chain = (RunnablePassthrough() | RunnableLambda(get_retrieval_results))
# VectorDB Search langsmith Runnable 변환 코드 ===================================



# BM25 Search langsmith Runnable 변환 코드 =======================================
def get_bm25retrieval_results(query : list[str]):
    state = query[1].split(",")
    k = query[2]

    # 각 BM25 리트리버의 결과값을 k로 설정
    for retriever_idx in range(len(bm25_retrievers)): 
        bm25_retrievers[retriever_idx].k = k

    docs_list = []
    for idx in range(len(state)):
        if state[idx] == 'true':
            docs_list.extend(bm25_retrievers[idx].search_with_score(query[0]))

    pair_form = sorted([(dict(x)['page_content'], dict(x)['metadata']['score']) for x in docs_list], key=lambda x:x[1], reverse=True)

    return [pair_form,"BM25 Search"] # Runnable 로그추적을 위한 더미 데이터 반환

smith_chain_bm25 = (RunnablePassthrough() | RunnableLambda(get_bm25retrieval_results))
# BM25 Search langsmith Runnable 변환 코드 =======================================



@app.route('/search')
def vectorRetrival():
    global vectorDB_retrival, documents, k
    conn, cursor = init_database()

    query = request.args.get('QUERY', 'None Query')  
    state = request.args.get('STATE', 'None State')
    k = int(request.args.get("k","10"))
    
    if query == "None Query": return f"쿼리를 입력하세요."
    
    # 한국어, or 영어 탐지
    Language_detector = LanguageDetector(query.replace(" ","").strip())

    # 언어가 ko, mix 인 경우 - Vector Search
    if Language_detector.check_language() != 'en':
        start_time = time.time()
        result = smith_chain.invoke([query,state,k])[0]
        search_time = time.time()-start_time
        distance = "Euclidian(L2)"
    else : # 언어가 영어인경우 - BM25 
        start_time = time.time()
        result = smith_chain_bm25.invoke([query,state,k])[0]
        search_time = time.time()-start_time
        distance = "BM25(TF-IDF)"


    json_structure = {
        'k': k,
        'search_time': search_time,  # 가데이터로 채워줌
        'datas': []  # 작은 사전들이 들어갈 리스트
    }

    for doc in result:
        title = doc[0]
        sim = doc[1]

        sql = "SELECT * FROM paper WHERE paper_name = %s"
        cursor.execute(sql, (title,))
        contents = cursor.fetchall()[0]

        data_structure = {
            'title' : str(contents[1]).strip(),
            'abstract' : str(contents[2].strip()),
            'authors' : str(contents[3].strip()),
            'published' : str(contents[4].strip()),
            'url' : str(contents[5].strip()),
            'journal' : str(contents[6].strip()),
            'ko_title' : str(contents[8].strip()),
            'ko_abstract' : str(contents[9].strip()),
            'distance' : str(sim),
            'distance_method' : str(distance)
        }
        
        json_structure['datas'].append(data_structure)

    return jsonify(json_structure)






# Ebook 기반 Streaming GPT
# Retrieval구조 HuggingFaceEmbedding모듈로 변경 필요
@app.route('/Test_Ebook')
def LLMResponse4():
    global ebook_retrival, ebook_docs
    query = request.args.get('QUERY', 'World')  
    r_doc = request.args.get("DOCUMENT","None")

    system_prompt = '''
    수의학 분야의 문서가 주어지면, 사용자의 질문에 정확하게 답변해야 합니다.

    =============================================================================
    문서는 다음과 같습니다:{}

    =============================================================================
    사용자의 질문은 다음과 같습니다: {}

    =============================================================================
    답변은 반드시 한국어로 작성해야 합니다.
    '''
    #주어진 문서에 사용자의 질문에 관련된 내용이 없다면, "이 문서에서는 찾을 수 없습니다"라고 답변해야 합니다.
    #'''

    query_embedding = nivia_embedding_embed([str(query)],'query')
    query_embedding = np.array(query_embedding).astype('float32')
    query_embedding_2d = query_embedding.reshape(1, -1)

    k = 10
    D, I = ebook_retrival.search(query_embedding_2d, k)

    topk_data = ""

    for idx in I[0]:
        topk_data += str(ebook_docs[idx])

    final_prompt = system_prompt.format(topk_data, query)

    print("Final Prompt Length = ", len(final_prompt))

    stream_input = {"history": "", "topic": final_prompt}
    t = time.time()

    def generate():
        for chunk in llm_chain.stream(stream_input):
            yield chunk

    response_time = time.time() - t

    json_structure = {
        'query': str(query),
        'search_pdf_name': str(r_doc),
        'chunk_search_k': str(k),
        'LLM_Response_time': str(response_time),
        'Answer': 'Streaming response'
    }

    # 응답 헤더에 JSON 형식의 메타데이터 추가
    headers = {
        'Content-Type': 'text/plain',
        'X-Metadata': json.dumps(json_structure)
    }

    return Response(generate(), headers=headers, content_type='text/plain')



from flask import send_from_directory
import os

@app.route('/pdf/<path:filename>')
def download_file(filename):
    print("PDF NAME = ",filename)
    return send_from_directory('static', filename)

app.run(host="0.0.0.0", port=5000,debug=False)


# # Ebook 기반 검색 (Vector DB)
# @app.route('/Ebook')
# def EbookVectorRetrival():
#     global ebook_retrival, ebook_docs

#     query = request.args.get('QUERY', 'None Query')  # 쿼리 문자열에서 'name' 파라미터 가져오기
    

#     if query == "None Query": return f"쿼리를 입력하세요."

#     query_embedding = nivia_embedding_embed([str(query)],'query')
#     query_embedding = np.array(query_embedding).astype('float32')
#     query_embedding_2d = query_embedding.reshape(1, -1)
#     distance_method = "Euclidian (L2)"

#     k = 10
#     start_time = time.time()
#     result = ebook_retrival.search(query_embedding_2d, k)
#     search_time = time.time()-start_time

#     json_structure = {
#         'k': k,
#         'search_time': search_time,  
#         'datas': []  
#     }

#     distance, indices = result[0][0], result[1][0]

#     sim_idx = 0

#     for idx in indices:
#         dict_data = dict(ebook_docs[idx])

#         page_content = dict_data['page_content']
#         meta_data = dict_data['metadata']
#         sim_data = distance[sim_idx]
#         sim_idx += 1

#         if "Downloaded from" in page_content:
#             page_content = page_content.split("Downloaded from")[0]

#         data_structure = {
#             'title' : meta_data,
#             'content' : page_content,
#             'sim' : str(sim_data),
#             'distance' : distance_method
#         }

#         json_structure['datas'].append(data_structure)

#     return jsonify(json_structure)





