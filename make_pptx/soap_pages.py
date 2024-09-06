from pptx.util import Inches, Cm, Pt
from pptx import Presentation

from llm.get_ppt_input import get_ppt_input

def get_signalment_page_data(signalment_str):
    parts = [item.strip() for line in signalment_str.split('\n') for item in line.split(',')]

    keywords = ['Name', 'Breed', 'Species', 'Age', 'Sex', 'BW']
    data = {}

    for part in parts:
        for keyword in keywords:
            if part.startswith(keyword):
                data[keyword] = part.split(': ')[1].strip()

    # 텍스트 생성
    signalment_text = (
        f"• Name : {data.get('Name', 'N/A')}\n\n"
        f"• Breed : {data.get('Breed', 'N/A')}\n\n"
        f"• Species : {data.get('Species', 'N/A')}\n\n"
        f"• Age : {data.get('Age', 'N/A')}\n\n"
        f"• Sex : {data.get('Sex', 'N/A')}\n\n"
        f"• BW : {data.get('BW', 'N/A')}\n\n"
    )
    
    return signalment_text

def get_soap_text(body_text):
    body_texts = [item.strip() for line in body_text.split('\n') for item in line.split(',')]
    text = ""

    for txt in body_texts:
        text += f"• {txt}\n\n"

    return text



def add_soap_pages(prs, slide_index, title_text, body_text, append=True):
    """
    슬라이드의 제목과 본문(텍스트 상자)에 텍스트를 추가하는 함수.
    제목에는 'signalment' 텍스트를 추가하고, 본문에는 signalment_text를 추가합니다.
    append가 True인 경우 본문 텍스트를 기존 텍스트 뒤에 추가하고, False인 경우 기존 텍스트를 덮어씁니다.
    """
    # 슬라이드를 가져옵니다.
    slide = prs.slides[slide_index]

    # 제목 텍스트 상자를 찾고 "signalment"를 삽입합니다.
    title_shape = slide.shapes.title
    if title_shape:
        title_shape.text = title_text
        for p in title_shape.text_frame.paragraphs:
            for run in p.runs:
                run.font.bold = True

    # 본문(텍스트 상자)을 찾습니다.
    body_shape = None
    for shape in slide.shapes:
        if shape.has_text_frame and shape != title_shape:
            body_shape = shape
            break
    
    if body_shape:
        text_frame = body_shape.text_frame
        if not append:
            text_frame.clear()  # 기존 텍스트 지우기
        p = text_frame.add_paragraph()
        p.text = body_text
        p.font.size = Pt(28)            # 글꼴 크기 설정
        p.font.bold = False             # 글꼴 굵기 설정
        p.font.name = 'Microsoft GothicNeo'           # 글꼴 설정

        p.bullet = True  
        #p.bullet.char = '\u2022'  # 속이 찬 둥근 글머리 기호 (•)
        #p.bullet.font.color.rgb = RGBColor(0, 0, 0)  # 글머리 기호 색상을 검정으로 설정
        p.level = 0  # 글머리 기호 레벨 설정 (0은 기본 레벨)

        
        body_shape.left = Inches(0.8)     # 왼쪽 여백 설정
        body_shape.top = Inches(2)      # 상단 여백 설정
        body_shape.width = Inches(10)    # 너비 설정
        body_shape.height = Inches(5) 
    else:
        print(f"Slide {slide_index} does not have a content area.")

def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def make_soap_pages(prs, pdf_path):
    answer = get_ppt_input(pdf_path)
    signalment_text = get_signalment_page_data(answer.signalment)

    add_soap_pages(prs, slide_index=1, title_text="Signalment", body_text=signalment_text, append=True)

    attributes = ['chief_complaint', 'body_check', 'diagnosis', 'plan_edu', 'sugery', 'a_record', 'postcare']
    slide_index = 2 
    for attr in attributes:
        if hasattr(answer, attr):
            if attr == 'chief_complaint':
                title = 'Chief Complaint'
            elif attr == 'body_check':
                title = 'Body Check'
            elif attr == 'diagnosis':
                title = 'Diagnosis'
            elif attr == 'plan_edu':
                title = 'Plan Education'
            elif attr == 'sugery':
                title = 'Sugery'
            elif attr == 'a_record':
                title = 'Anesthesia Record'
            elif attr == 'postcare':
                title = 'Postoperative Care'
            else:
                title = 'N/A'
            
            body = getattr(answer, attr)

            body = get_soap_text(body)

            if len(body.split('\n\n')) < 6:
                slide_layout = prs.slide_layouts[1]
                prs.slides.add_slide(slide_layout)
                add_soap_pages(prs, slide_index, title, body, append=True)
                slide_index += 1
            else:
                body_lines = body.split('\n\n')

                for chunk in chunk_list(body_lines, 6):
                    slide_layout = prs.slide_layouts[1]
                    prs.slides.add_slide(slide_layout)
                    chunk_text = "\n".join(chunk)
                    add_soap_pages(prs, slide_index, title, chunk_text, append=True)
                    slide_index+=1