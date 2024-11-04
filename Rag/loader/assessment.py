import pandas as pd

def assessment_exists(pages):
    page_num = 0
    y_point = 0
    for page in pages:
        if page.page_content.lower() == '구분' and page.metadata['coordinates']['points'][0][0] == 30.35:
            page_num = page.metadata['page_number']
            y_point = page.metadata['coordinates']['points'][1][1]
    
    return page_num != 0, page_num, y_point

def plan_exists_for_assessment(pages):
    page_num = 0
    y_point = 0
    for page in pages:
        if page.page_content.lower() == 'plan' and page.metadata['coordinates']['points'][0][0] == 36.02:
            page_num = page.metadata['page_number']
            y_point = page.metadata['coordinates']['points'][0][1]
    
    return page_num != 0, page_num, y_point

def extract_assessment_data(pages):
    is_check, assessment_page_num, assessment_y_point = assessment_exists(pages)
    plan_is_check, plan_page_num, plan_y_point = plan_exists_for_assessment(pages)
    assessment_data = []
    
    if is_check and plan_is_check:
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
    elif is_check:
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            page_number = metadata['page_number']

            if page_number == assessment_page_num and points[0][1] >= assessment_y_point:
                if page_number == assessment_page_num:
                    assessment_data.append(page)
            elif page_number > assessment_page_num:
                assessment_data.append(page)
                
        return assessment_data
    else:
        return False
    
def make_assessment_table(pages):
    assessment = {
        "구분": [],
        "코드": [],
        "진단명": [],
        "과목": [],
        "Sign": []
    }

    y_points = []
    page_info = []
    for page in pages:
        if page.metadata['coordinates']['points'][0][0] == 30.35:
            y_points.append(page.metadata['coordinates']['points'][0][1])
            page_info.append(page.metadata['page_number'])
            assessment['구분'].append(page.page_content)

    for point, page_ in zip(y_points, page_info):
        max_point = 0

        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            if points[0][0] == 92.71 and points[0][1] > (point - 4) and points[0][1] < (point + 4) and metadata['page_number'] == page_:
                assessment['코드'].append(page.page_content)
        
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            if points[0][0] == 183.42 and points[0][1] > (point - 4) and points[0][1] < (point + 4) and metadata['page_number'] == page_:
                assessment['진단명'].append(page.page_content)
        
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            if points[0][0] == 387.51 and points[0][1] > (point - 4) and points[0][1] < (point + 4) and metadata['page_number'] == page_:
                max_point = max(points[2][0], 387.51)
                assessment['과목'].append(page.page_content)
        
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
