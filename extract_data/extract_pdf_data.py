
import numpy as np
from langchain_community.document_loaders import UnstructuredPDFLoader
import re
import pandas as pd

"""환자 정보 및 보호자 정보"""
"""
동물 정보 및 보호자 정보 추출

함수명 : get_animal_data
Input : path/to/pdf
output : 동물 정보 및 보호자 정보
"""

def extract_data_via_points(pages, x, y1, y2):
    for page in pages:
        metadata = page.metadata
        coordinates = metadata['coordinates']

        if metadata['page_number'] == 1 and coordinates['points'][0][0] == x\
            and coordinates['points'][0][1] > y1 \
                and coordinates['points'][1][1] < y2:
            return page.page_content
    
    return ("Not Found")

def get_animal_data(pdf_path):
    pdf_filepath = pdf_path
    loader = UnstructuredPDFLoader(pdf_filepath, mode='elements')
    pages = loader.load()

    info = {}

    #동물 정보 추출
    info['name'] = extract_data_via_points(pages, 265.62, 141, 150)
    info['breed'] = extract_data_via_points(pages, 78.54, 158, 167)
    info['sex'] = extract_data_via_points(pages, 78.54, 174, 184)
    info['species'] = extract_data_via_points(pages, 265.62, 157, 167)
    info['birth'] = extract_data_via_points(pages, 265.62, 174, 184)
    info['weight'] = extract_data_via_points(pages, 78.54, 209, 218)
    
    # 보호자 이름 추출
    info['protector'] = extract_data_via_points(pages, 214.6, 107, 116)

    return info

"""환자 정보 및 보호자 정보"""





"""*****     Subjective     *****"""
"""
Subjective 내용 추출

\d{4}-\d{2}-\d{2} \d{2}:\d{2} 영역 구하기

출력 : 2차원 numpy배열 ['날짜', 'y 좌표 값', '페이지 번호']
"""
def extract_date_position(pages):
    date_time_pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")

    date = []
    date_points = []
    date_pages = []


    for page in pages:
        metadata = page.metadata
        coordinates = metadata['coordinates']

        matches = date_time_pattern.findall(page.page_content)
        x_point = coordinates['points'][0][0]
        y_height = coordinates['points'][1][1] - coordinates['points'][0][1]
        
        if matches and x_point == 30.35 and y_height > 8:
            #print(page.page_content, "points:", coordinates['points'])
            date.append(page.page_content)
            date_points.append(coordinates['points'][1][1])
            date_pages.append(metadata['page_number'])

    for page in pages:
        metadata = page.metadata
        coordinates = metadata['coordinates']

        x_point = coordinates['points'][0][0]
        y_height = coordinates['points'][1][1] - coordinates['points'][0][1]

        if page.page_content.lower() == 'vital check' and x_point == 33.35 and y_height > 20:
            date.append(page.page_content)
            date_points.append(coordinates['points'][0][1])
            date_pages.append(metadata['page_number'])

    result = np.column_stack((date, date_points, date_pages))

    return result



"""
입력
Document 데이터
추출하고자 하는 영역의 시간 시작 위치 및 페이지 / 끝나는 위치 및 페이지 

출력
추출하려는 데이터 및 메타데이터
"""

def extract_data_via_interval_info(pages, interval_info):
    extracted_pages = []
    start_y_point = float(interval_info[0][0])
    end_y_point = float(interval_info[1][0])
    start_page = int(interval_info[0][1])
    end_page = int(interval_info[1][1])

    if end_page == 0:
        # Vital Check 기준으로 일단 추출해볼까..
        pass
    else:
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            #같은 페이지인 경우
            if start_page == end_page:
                if metadata['page_number'] == start_page and points[0][1] > start_y_point and points[1][1] < end_y_point:
                    extracted_pages.append(page)
            # 다른 페이지인 경우
            else:
                if metadata['page_number'] > start_page and metadata['page_number'] < end_page:
                    extracted_pages.append(page)
                if metadata['page_number'] == start_page and points[0][1] > start_y_point:
                    extracted_pages.append(page)
                if metadata['page_number'] == end_page and points[1][1] < end_y_point:
                    extracted_pages.append(page)

    return extracted_pages

def extract_subjective_data(pages):
    # Plan과 Accessment y값과 page 추출
    extracted_pages = []
    min_page = 50000
    min_height = 50000.0
    for page in pages:
        metadata = page.metadata
        points = metadata['coordinates']['points']
        text = page.page_content

        if (text.lower() == 'plan' or text.lower() =='assessment') and points[0][0]==36.02:
            if metadata['page_number'] <= min_page:
                min_page = metadata['page_number']
                min_height = min(min_height, points[0][1])
    
    # Plan과 Assessment를 제외한 값 추출
    for page in pages:
        metadata = page.metadata
        points = metadata['coordinates']['points']
        page_num = metadata['page_number']
        y_point = points[0][1]

        # 페이지가 같거나 작은 경우 데이터를 추출
        if page_num < min_page:
            extracted_pages.append(page)
        elif page_num == min_page and y_point < min_height:
            extracted_pages.append(page)
    
    return extracted_pages

"""*****     Subjective     *****"""



"""*****     Accessment     *****"""
"""
- 구분 (30.35, 418.82), (30.35, 427.71999999999997), (48.15, 427.71999999999997), (48.15, 418.82)
- 코드 (92.71, 418.82), (92.71, 427.71999999999997), (110.51, 427.71999999999997), (110.51, 418.82)
- 진단명 (183.42, 418.82), (183.42, 427.71999999999997), (210.12, 427.71999999999997), (210.12, 418.82)
- 과목 (387.51, 418.82), (387.51, 427.71999999999997), (405.30999999999995, 427.71999999999997), (405.30999999999995, 418.82)
- Sign (526.92, 418.82), (526.92, 427.71999999999997), (545.3607999999999, 427.71999999999997), (545.3607999999999, 418.82)
"""
#Assessment 데이터가 존재하는지 확인
#존재한다면 페이지 번호와 y 위치 추출
def assessment_exists(pages):
    page_num = 0
    y_point = 0
    for page in pages:
        if page.page_content.lower() == '구분' and page.metadata['coordinates']['points'][0][0] == 30.35:
            #Plan y : 36.02
            page_num = page.metadata['page_number']
            y_point = page.metadata['coordinates']['points'][1][1]
    
    if page_num == 0 and y_point == 0:
        return False, page_num, y_point
    else:
        return True, page_num, y_point

def plan_exists_for_assessment(pages):
    page_num = 0
    y_point = 0
    for page in pages:
        if page.page_content.lower() == 'plan' and page.metadata['coordinates']['points'][0][0] == 36.02:
            #Plan y : 36.02
            page_num = page.metadata['page_number']
            y_point = page.metadata['coordinates']['points'][0][1]
    
    if page_num == 0 and y_point == 0:
        return False, page_num, y_point
    else:
        return True, page_num, y_point

# 평가 내용만 다 추출
def extract_assessment_data(pages):
    is_check, assessment_page_num, assessment_y_point = assessment_exists(pages)
    plan_is_check, plan_page_num, plan_y_point = plan_exists_for_assessment(pages)
    assessment_data = []
    
    if is_check and plan_is_check: # 플랜 데이터 위로 추출
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            page_number = metadata['page_number']

            if assessment_page_num == plan_page_num:
                if page_number == assessment_page_num and points[0][1] >= assessment_y_point and points[0][1] < plan_y_point:
                    assessment_data.append(page)
            elif assessment_page_num < plan_page_num:
                if page_number == assessment_page_num and points[0][1] >= assessment_y_point:
                    assessment_data.append(page)
                elif page_number == plan_page_num and points[0][1] < plan_y_point:
                    assessment_data.append(page)
                elif page_number > assessment_page_num and page_number < plan_page_num:
                    assessment_data.append(page)
        return assessment_data
    elif is_check: # Plan 데이터가 존재하지 않을 때
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            page_number = metadata['page_number']

            if page_number == assessment_page_num and points[0][1] >= assessment_y_point:
                if page_number == assessment_page_num:
                    assessment_data.append(page)
            elif page_number > assessment_page_num :
                assessment_data.append(page)
                
        return assessment_data
    else:
        return False
    

def make_assessment_table(pages):
    assessment = {
        "구분" : [],
        "코드" : [],
        "진단명" : [],
        "과목" : [],
        "Sign" : []
    }
    
    y_points = []
    page_info = []
    for page in pages:
    #print(page)
        if page.metadata['coordinates']['points'][0][0] == 30.35:
            y_points.append(page.metadata['coordinates']['points'][0][1])
            page_info.append(page.metadata['page_number'])
            assessment['구분'].append(page.page_content)
    
    for point, page_ in zip(y_points, page_info):
        
        # 코드 92.71
        #not_present = True
        max_point = 0


        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            
            if points[0][0] == 92.71 and points[0][1] > (point - 4) and points[0][1] < (point + 4) and metadata['page_number'] == page_:
                assessment['코드'].append(page.page_content)
                not_present = False

        # 진단명 (183.42, 418.82), (183.42, 427.71999999999997), (210.12, 427.71999999999997), (210.12, 418.82)
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            if points[0][0] == 183.42 and points[0][1] > (point - 4) and points[0][1] < (point + 4) and metadata['page_number'] == page_:
                assessment['진단명'].append(page.page_content)
        
        # 과목
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            if points[0][0] == 387.51 and points[0][1] > (point - 4) and points[0][1] < (point + 4) and metadata['page_number'] == page_:
                max_point = max(points[2][0], 387.51)
                assessment['과목'].append(page.page_content)
        
        # Sign
        not_present = True
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            if points[0][0] > max_point and points[0][1] > (point - 4) and points[0][1] < (point + 4) and metadata['page_number'] == page_:
                assessment['Sign'].append(page.page_content)
                not_present = False
        if not_present:
            assessment['Sign'].append(None)
    
    assessment_df = pd.DataFrame(assessment)
    return assessment_df

"""*****     Accessment     *****"""




"""*****     Plan     *****"""
#Plan 데이터가 존재하는지 확인
def plan_exists(pages):
    page_num = 0
    y_point = 0
    for page in pages:
        if page.page_content.lower() == '코드' and page.metadata['coordinates']['points'][0][0] == 30.35:
            #Plan y : 36.02
            page_num = page.metadata['page_number']
            y_point = page.metadata['coordinates']['points'][1][1]
    
    if page_num == 0 and y_point == 0:
        return False, page_num, y_point
    else:
        return True, page_num, y_point

# 플랜 내용만 다 추출
def extract_plan_data(pages):
    is_check, plan_page_num, plan_y_point = plan_exists(pages)
    
    plan_data = []
    
    if is_check:
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            if metadata['page_number'] == plan_page_num and points[0][1] >= plan_y_point:
                plan_data.append(page)
            elif metadata['page_number'] > plan_page_num:
                plan_data.append(page)

        return plan_data
    else:
        return False
    
def make_plan_table(pages):
    plan = {
        "코드" : [],
        "항목명" : [],
        "수량" : [],
        "일투" : [],
        "일수" : [],
        "총투" : [],
        "Route" : [],
        "Dose" : [],
    }

    """
    표 구하는 법
    코드 값 먼저 추출 -> y값과 각 열의 x값 일치하는 항목 검색 -> 존재하면 검색 결과 값 넣고 없으면 None 추가
    """
    
    # Plan의 항목이 몇 개인지 추출
    y_points = []
    page_info = []
    for page in pages:
        #print(page)
        if page.metadata['coordinates']['points'][0][0] == 30.35:
            y_points.append(page.metadata['coordinates']['points'][0][1])
            page_info.append(page.metadata['page_number'])
            plan['코드'].append(page.page_content)

    # print(y_points)
    # print(page_info) 
    for point, page_ in zip(y_points,page_info):
        # 항목명 내용 추출
        # 항목명 104.05, 130.75
        not_present = True
        max_point = 0
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            
            
            if points[0][0] == 104.05 and points[0][1] > (point - 4.0) and points[0][1] < (point + 4.0) and metadata['page_number'] == page_:
                plan['항목명'].append(page.page_content)
                max_point = max(max_point, points[2][0])
                not_present = False
        if not_present:
            plan['항목명'].append(None)
    
    
        # 수량 내용 추출
        # 수량 274.96, 292.75999999999993
        not_present = True
        max_point = max(271.96, max_point)
        
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            if points[0][0] > max_point and points[0][0] < 338 and points[0][1] > (point - 4.0) and points[0][1] < (point + 4.0) and metadata['page_number'] == page_:
                plan['수량'].append(page.page_content)
                max_point = max(max_point, points[2][0])
                not_present = False
        if not_present:
            plan['수량'].append(None)
        
        # 일투 338.74, 356.53999999999996 = 약 17
        max_point = min(338.74, max_point)
        not_present = True
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            if points[0][0] > max_point and points[0][0] < 368 and points[0][1] > (point - 4.0) and points[0][1] < (point + 4.0) and metadata['page_number'] == page_:
                plan['일투'].append(page.page_content)
                max_point = max(max_point, points[2][0])
                not_present = False
        if not_present:
            plan['일투'].append(None)

        max_point = min(369.93, max_point)
        # 일수 총투 369.93, 387 
        not_present = True
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            if points[0][0] > max_point and points[0][0] < 390 and points[0][1] > (point - 4.0) and points[0][1] < (point + 4.0) and metadata['page_number'] == page_:
                plan['일수'].append(page.page_content)
                max_point = max(max_point, points[2][0])
                not_present = False
        if not_present:
            plan['일수'].append(None)

        # 총투 403, 420.31999999999994
        max_point = min(max_point, 403)
        not_present = True
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            if points[0][0] > max_point and points[0][0] < 430 and points[0][1] > (point - 4.0) and points[0][1] < (point + 4.0) and metadata['page_number'] == page_:
                plan['총투'].append(page.page_content)
                max_point = max(max_point, points[2][0])
                not_present = False
        if not_present:
            plan['총투'].append(None)

        
        # Route 442.79, 467.82570000000004
        not_present = True
        max_point = min(max_point, 442.79)
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            if points[0][0] > max_point and points[0][0] < 467 and points[0][1] > (point - 4.0) and points[0][1] < (point + 4.0) and metadata['page_number'] == page_:
                plan['Route'].append(page.page_content)
                max_point = max(max_point, points[2][0])
                not_present = False
        if not_present:
            plan['Route'].append(None)

        # Dose 514.21, 535.3386
        not_present = True
        max_point = max(max_point, 514.21)
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            if points[0][0] > max_point and points[0][0] < 560 and points[0][1] > (point - 4.0) and points[0][1] < (point + 4.0) and metadata['page_number'] == page_:
                plan['Dose'].append(page.page_content)
                max_point = max(max_point, points[2][0])
                not_present = False
        if not_present:
            plan['Dose'].append(None)
        

    plan_df = pd.DataFrame(plan)

    return plan_df

"""*****     Plan     *****"""




"""*****     Vital Check     *****"""

def extract_vital_check(pages):
    extracted_pages = []

    vital_page_num = 0
    vital_y_point = 0

    lab_page_num = 0
    lab_y_point = 0

    for page in pages:
        metadata = page.metadata
        coordinates = metadata['coordinates']

        x_point = coordinates['points'][0][0]
        y_height = coordinates['points'][1][1] - coordinates['points'][0][1]


        if page.page_content.lower() == '날짜' and x_point == 30.35:
            vital_y_point = coordinates['points'][0][1]
            vital_page_num = metadata['page_number']
            
        
        if page.page_content.lower() == 'lab' and x_point == 33.35 and y_height > 20:
            lab_y_point = coordinates['points'][0][1]
            lab_page_num = metadata['page_number']

    if vital_page_num and vital_y_point and lab_page_num and lab_y_point:
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            page_number = metadata['page_number']

            if vital_page_num == lab_page_num:
                if page_number == vital_page_num and points[0][1] > vital_y_point and points[0][1] < lab_y_point:
                    extracted_pages.append(page)
            elif vital_page_num < lab_page_num:
                if page_number == vital_page_num and points[0][1] > vital_y_point:
                    extracted_pages.append(page)
                elif page_number == lab_page_num and points[0][1] < lab_y_point:
                    extracted_pages.append(page)
                elif page_number > vital_page_num and page_number < lab_page_num:
                    extracted_pages.append(page)
    
    return extracted_pages


def make_vital_check_table(pages):
    vital_check = {
        '날짜' : [],
        '시간' : [],
        'BW(Kg)' : [],
        'BT(C)' : [],
        'BP(mmHg)' : [],
        'HR(/min)' : [],
        'Sign' : [],
    }
    data_list = []

    for page in pages:
        data_list.append(page.page_content)
    
    for i in range(0, len(data_list), 7):
        vital_check['날짜'].append(data_list[i])
        vital_check['시간'].append(data_list[i+1])
        vital_check['BW(Kg)'].append(data_list[i+2])
        vital_check['BT(C)'].append(data_list[i+3])
        vital_check['BP(mmHg)'].append(data_list[i+4])
        vital_check['HR(/min)'].append(data_list[i+5])
        vital_check['Sign'].append(data_list[i+6])
    
    vital_check_df = pd.DataFrame(vital_check)

    return vital_check_df


"""*****     Vital Check     *****"""







"""*****     Lab     *****"""

"""
전체 PDF 데이터에서
Lab 데이터만 추출
"""

def extract_lab_data_all(pages):
    extracted_pages = []

    lab_page_num = 0
    lab_y_point = 0

    for page in pages:
        metadata = page.metadata
        coordinates = metadata['coordinates']

        x_point = coordinates['points'][0][0]
        y_height = coordinates['points'][1][1] - coordinates['points'][0][1]
        
        if page.page_content.lower() == 'lab' and x_point == 33.35 and y_height > 20:
            lab_y_point = coordinates['points'][0][1]
            lab_page_num = metadata['page_number']
    
    if lab_page_num and lab_y_point:
        metadata = page.metadata
        points = metadata['coordinates']['points']
        page_number = metadata['page_number']
        
        for page in pages:
            if page_number == lab_page_num and points[0][1] > lab_y_point:
                extracted_pages.append(page)
            elif page_number > lab_page_num:
                extracted_pages.append(page)
    
    return extracted_pages


"""
전체 PDF 데이터 중에서
Lab 테이블 날짜 위치 추출
"""
def extract_lab_table_date(pages):
    date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")

    date = []
    date_points = []
    date_pages = []

    for page in pages:
        metadata = page.metadata
        coordinates = metadata['coordinates']
        points = metadata['coordinates']['points']

        matches = date_pattern.findall(page.page_content)
        x_point = points[0][0]
        y_height = points[1][1] - points[0][1]

        if matches and x_point == 36.02 and y_height >10:
            date.append(page.page_content)
            date_points.append(coordinates['points'][0][1])
            date_pages.append(metadata['page_number'])
    
    result = np.column_stack((date, date_points, date_pages))
    
    return result


"""
Lab 데이터 전체와 간격의 정보를 입력해서
Lab 테이블 날짜 별로 데이터 추출하기
"""
def extract_lab_data_via_interval_info(pages, interval_info):
    extracted_pages = []

    start_y_point = float(interval_info[0][0])
    end_y_point = float(interval_info[1][0])
    start_page = int(interval_info[0][1])
    end_page = int(interval_info[1][1])

    if end_page == 0:
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            if metadata['page_number'] == start_page and points[0][1] > start_y_point:
                extracted_pages.append(page)
            elif metadata['page_number'] > start_page:
                extracted_pages.append(page)
    else:
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            #같은 페이지인 경우
            if start_page == end_page:
                if metadata['page_number'] == start_page and points[0][1] > start_y_point and points[1][1] < end_y_point:
                    extracted_pages.append(page)
            # 다른 페이지인 경우
            else:
                if metadata['page_number'] > start_page and metadata['page_number'] < end_page:
                    extracted_pages.append(page)
                if metadata['page_number'] == start_page and points[0][1] > start_y_point:
                    extracted_pages.append(page)
                if metadata['page_number'] == end_page and points[1][1] < end_y_point:
                    extracted_pages.append(page)

    return extracted_pages


def extract_lab_data(pages):
    extracted_pages = []
    
    y_point = 0
    page_num = 0

    for page in pages:
        metadata = page.metadata
        points = metadata['coordinates']['points']

        if page.page_content == '검사명' and points[0][0] == 30.35:
            y_point = points[1][1]
            page_num = metadata['page_number']
    
    for page in pages:
        metadata = page.metadata
        points = metadata['coordinates']['points']

        if metadata['page_number'] == page_num and points[0][1] > y_point:
            extracted_pages.append(page)
        elif metadata['page_number'] > page_num:
            extracted_pages.append(page)
    
    return extracted_pages


"""
표 데이터를 입력받으면
테이블 반환
"""
def make_lab_table(pages):
    lab = {
        "검사명" : [],
        "결과값" : [],
        "단위" : [],
        "status" : [],
        "MIN" : [],
        "MAX" : [],
        "Description" : []
    }

    y_points = []
    page_info = []

    for page in pages:
        if page.metadata['coordinates']['points'][0][0] == 30.35:
            y_points.append(page.metadata['coordinates']['points'][0][1])
            page_info.append(page.metadata['page_number'])
            lab['검사명'].append(page.page_content)


    for point, page_ in zip(y_points, page_info):
        
        # 결과값 단위 나누기
        # 255.46
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            # 결과값 데이터 찾고
            if points[0][0] > 240 and points[0][0] < 342 and points[0][1] > (point - 4) and points[0][1] < (point + 4) and metadata['page_number'] == page_:
                result = page.page_content
                # 단위 데이터가 존재한다면
                if points[3][0] > 278:
                    split_result = result.split(' ', 1)
                    if len(split_result) == 2:
                        text, unit = split_result
                    else:
                        text = split_result[0]
                        unit = None
                    lab['결과값'].append(text)
                    lab['단위'].append(unit)
                else:
                    lab['결과값'].append(result)
                    lab['단위'].append(None)
        
        # 기호 추출 ()
        not_present = True
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            if points[0][0] == 342.16 and points[0][1] > (point - 4) and points[0][1] < (point + 4) and metadata['page_number'] == page_:
                lab['status'].append(page.page_content)
                not_present = False
        if not_present:
            lab['status'].append(None)
        
        # Min 추출
        not_present = True
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            if points[0][0] > 380 and points[2][0] < 460 and points[0][1] > (point - 4) and points[0][1] < (point + 4) and metadata['page_number'] == page_:
                lab['MIN'].append(page.page_content)
                not_present = False
        if not_present:
            lab['MIN'].append(None)

        # Max 추출
        not_present = True
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            if points[0][0] > 450 and points[2][0] < 485 and points[0][1] > (point - 4) and points[0][1] < (point + 4) and metadata['page_number'] == page_:
                lab['MAX'].append(page.page_content)
                not_present = False
        if not_present:
            lab['MAX'].append(None)

        # Description 추출
        not_present = True
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']

            if points[0][0] > 500 and points[0][1] > (point - 4) and points[0][1] < (point + 4) and metadata['page_number'] == page_:
                lab['Description'].append(page.page_content)
                not_present = False
        if not_present:
            lab['Description'].append(None)

    lab_df = pd.DataFrame(lab)
    return lab_df

    # print("결과값 :",lab['결과값'])
    # print("단위 :",lab['단위'])
    # print("status :",lab['status'])
    # print("Min :", lab['MIN'])
    # print("Max :", lab['MAX'])
    # print("결과값 길이 :",len(lab['결과값']))
    # print("단위 길이 :", len(lab['단위']))
    # print("status 길이 :",len(lab['status']))
    # print("Min 길이 :", len(lab['MIN']))
    # print("Max 길이 :", len(lab['MAX']))
    # print("Des 길이 : ", len(lab['Description']))

"""*****     Lab     *****"""



def get_soap(pages):
    data = extract_date_position(pages)

    soap_result = []
    
    #soap 데이터 추출
    for i in range(len(data)-1):
        soap_one = {
            "date" : '',
            "subjective" : [],
            "assessment" : [],
            "plan" : []
        }

        y_point = []
        page_num = []

        # 데이터 찾을 시작 위치 정보 저장
        y_point.append(data[i][1])
        page_num.append(data[i][2])
        y_point.append(data[i+1][1])
        page_num.append(data[i+1][2])
        
        
        interval_info = np.column_stack((y_point, page_num))
        #print(interval_info)

        # 날짜 별로 추출 / 안에 존재하는 데이터 모두
        extracted_pages = extract_data_via_interval_info(pages, interval_info)
        

        # Subjective 데이터 추출
        subjective_data = extract_subjective_data(extracted_pages)

        soap_one['date'] = data[i][0]
        for page in subjective_data:
            soap_one['subjective'].append(page.page_content)

        
        # Assessment 데이터 추출
        assessment_data = extract_assessment_data(extracted_pages)

        if assessment_data:
            assessment_table = make_assessment_table(assessment_data)
            soap_one['assessment'].append(assessment_table)
        
        
        # Plan 데이터 추출
        plan_data = extract_plan_data(extracted_pages)

        if plan_data:
            plan_table = make_plan_table(plan_data)
            soap_one['plan'].append(plan_table)
                
        soap_result.append(soap_one)

    return soap_result

def get_vital_check(pages):
    # Vital Check 추출

    vital_check_data = extract_vital_check(pages)

    vital_check_table = make_vital_check_table(vital_check_data)
    return vital_check_table



def get_lab(pages):
    # Lab 데이터 추출
    lab_tables = []
    lab_pages = extract_lab_data_all(pages)

    lab_pages_date = extract_lab_table_date(lab_pages)

    lab_date = np.append(lab_pages_date, [[0,0,0]], axis=0)

    for i in range(len(lab_date)-1):
        lab_one = {
            'date' : '',
            'table' : '',
        }

        y_point = []
        page_num = []

        lab_one['date'] = lab_date[i][0]
        y_point.append(lab_date[i][1])
        page_num.append(lab_date[i][2])
        y_point.append(lab_date[i+1][1])
        page_num.append(lab_date[i+1][2])

        interval_info = np.column_stack((y_point, page_num))
        
        extracted_pages = extract_lab_data_via_interval_info(lab_pages, interval_info)
        #print(len(extracted_pages))

        # Lab 한 테이블 데이터 모두 추출
        extracted_pages = extract_lab_data(extracted_pages)

        
        lab_table = make_lab_table(extracted_pages)
        lab_one['table'] = lab_table
        lab_tables.append(lab_one)
    
    return lab_tables

def main():
    pdf_filepath = '/Users/sinequanon/Documents/PerfectS/data/pdf_data/TEST_01.pdf'

    loader = UnstructuredPDFLoader(pdf_filepath, mode='elements')
    pages = loader.load()

    soap_result = get_soap(pages)
        
    vital_check_table = get_vital_check(pages)

    lab_tables = get_lab(pages)

    print(soap_result)

    print(vital_check_table)

    print(lab_tables)

main()