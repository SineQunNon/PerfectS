from pptx.util import Pt
from pptx.enum.text import PP_ALIGN,MSO_ANCHOR

def make_end_page(prs):
    slide_layout = prs.slide_layouts[3]

    slide = prs.slides.add_slide(slide_layout)

    textbox = None
    for shape in slide.shapes:
        if shape.has_text_frame:  # 텍스트 상자가 있는지 확인
            textbox = shape
            break

    if textbox:
        # 텍스트 상자가 있는 경우 기존 내용을 지우지 않고 텍스트 추가
        text_frame = textbox.text_frame

        # 단락 추가
        p = text_frame.add_paragraph()
        p.text = "감사합니다"
        p.font.size = Pt(40)
        p.font.bold = True

        # 텍스트의 가로 정렬을 중앙으로 설정
        p.alignment = PP_ALIGN.CENTER

        # 텍스트 상자의 세로 정렬을 중앙으로 설정
        text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE