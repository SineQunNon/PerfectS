import pandas as pd
import logging

def plan_exists(pages):
    page_num = 0
    y_point = 0
    for page in pages:
        if page.page_content.lower() == '코드' and page.metadata['coordinates']['points'][0][0] == 30.35:
            page_num = page.metadata['page_number']
            y_point = page.metadata['coordinates']['points'][1][1]
    
    return page_num != 0, page_num, y_point

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
        "코드": [],
        "항목명": [],
        "수량": [],
        "일투": [],
        "일수": [],
        "총투": [],
        "Route": [],
        "Dose": []
    }

    y_points = []
    page_info = []
    for page in pages:
        if page.metadata['coordinates']['points'][0][0] == 30.35:
            y_points.append(page.metadata['coordinates']['points'][0][1])
            page_info.append(page.metadata['page_number'])
            plan['코드'].append(page.page_content)

    for point, page_ in zip(y_points, page_info):
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

        not_present = True
        max_point = min(338.74, max_point)
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            if points[0][0] > max_point and points[0][0] < 368 and points[0][1] > (point - 4.0) and points[0][1] < (point + 4.0) and metadata['page_number'] == page_:
                plan['일투'].append(page.page_content)
                max_point = max(max_point, points[2][0])
                not_present = False
        if not_present:
            plan['일투'].append(None)

        not_present = True
        max_point = min(369.93, max_point)
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            if points[0][0] > max_point and points[0][0] < 390 and points[0][1] > (point - 4.0) and points[0][1] < (point + 4.0) and metadata['page_number'] == page_:
                plan['일수'].append(page.page_content)
                max_point = max(max_point, points[2][0])
                not_present = False
        if not_present:
            plan['일수'].append(None)

        not_present = True
        max_point = min(max_point, 403)
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            if points[0][0] > max_point and points[0][0] < 430 and points[0][1] > (point - 4.0) and points[0][1] < (point + 4.0) and metadata['page_number'] == page_:
                plan['총투'].append(page.page_content)
                max_point = max(max_point, points[2][0])
                not_present = False
        if not_present:
            plan['총투'].append(None)

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

    # for i in plan:
    #     print("길이 : ", len(plan[i]))
    # print(plan)
    try:
        plan_df = pd.DataFrame(plan)
        return plan_df
    except ValueError as e:
        logging.error(f"Error processing in make_plan_table : {e}")
        return pd.DataFrame()
        
