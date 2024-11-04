from Rag.prompt.example import get_examples
from langchain_core.prompts import PromptTemplate

from langchain_core.prompts.few_shot import FewShotPromptTemplate

#------------------------parsor--------------------------#
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

class MedicalSummary(BaseModel):
    signalment : str = Field(description="Singalment")
    chief_complaint : str = Field(description="Chief Complaints")
    body_check : str = Field(description="신체검사")
    diagnosis : str = Field(description="Definitive Diagnosis")
    plan_edu : str = Field(description="Plan & Client Education")
    surgery : str = Field(description="Surgery")
    a_record : str = Field(description="Anesthesia record")
    postcare : str = Field(description="Postoperative care")



def get_parser():
    parser = PydanticOutputParser(pydantic_object=MedicalSummary)

    return parser

#print(parser.get_format_instructions())
#------------------------parsor--------------------------#




def get_prompt():
    #------------------------example selector--------------------------#
    examples = get_examples()    
    example_prompt = PromptTemplate.from_template("""
    #진료소견 내용:
    {input}

    #Answer:
    {answer}
    """)
    #------------------------example selector--------------------------#

    #------------------------prompt--------------------------#

    prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        suffix="""
        진료소견 내용을 잘 파악해서 다음 헤더에 맞춰서 잘 요약해줘. 만약 헤당하는 내용의 헤더가 없으면 답변하지 않아도 돼
        #헤더
    - Signalment
    - Chief Complaint
    - 신체검사
    - Definitive Diagnosis
    - Plan & Client Education
    - Surgery
    - Anesthesia record
    - Postoperative care
        진료소견 내용:\n{input}\n\n

        FORMAT:
        {format}
        
        #Answer:""",
        input_variables=["input"]
    )
    parser = get_parser()
    prompt = prompt.partial(format=parser.get_format_instructions())

    #f_prompt = prompt.partial(foramt=parser.get_format_instructions())
    #print(f_prompt)

    return prompt

    #------------------------prompt--------------------------#

def get_table_propmt():
    template = """
    # 테이블 내용
    {input}

    환자 검질 결과야. 해당 내용을 분석해서 2~3문장으로 요약해줘
    #Answer"""

    prompt = PromptTemplate(
        template = template,
        input_variables=['input'],
    )

    return prompt