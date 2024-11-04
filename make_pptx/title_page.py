import datetime
import calendar

def num_to_kor(word):
    if word == 0:
        return "월"
    elif word == 1:
        return "화"
    elif word == 2:
        return "수"
    elif word == 3:
        return "목"
    elif word == 4:
        return "금"
    elif word == 5:
        return "토"
    elif word == 6:
        return "일"

def make_title_page(prs):
    prs.slides.add_slide(prs.slide_layouts[0])
    current_date = datetime.date.today()

    formatted_date = str(current_date).replace("-",".")
    weekday = num_to_kor(current_date.weekday())
    date = f"{formatted_date} ({weekday})"

    body_shape = None
    slide = prs.slides[0]
    for shape in slide.shapes:
        if shape.has_text_frame:
            body_shape = shape
    
    if body_shape:
        body_shape.text = date