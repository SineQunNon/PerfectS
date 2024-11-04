import re
import numpy as np
import pandas as pd
from Rag.loader.pdf_loader import load_pdf

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

        if matches and x_point == 36.02 and y_height > 10:
            date.append(page.page_content)
            date_points.append(coordinates['points'][0][1])
            date_pages.append(metadata['page_number'])
    
    result = np.column_stack((date, date_points, date_pages))
    return result

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

            if start_page == end_page:
                if metadata['page_number'] == start_page and points[0][1] > start_y_point and points[1][1] < end_y_point:
                    extracted_pages.append(page)
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

def make_lab_table(pages):
    lab = {
        "검사명": [],
        "결과값": [],
        "단위": [],
        "status": [],
        "MIN": [],
        "MAX": [],
        "Description": []
    }

    y_points = []
    page_info = []
    for page in pages:
        if page.metadata['coordinates']['points'][0][0] == 30.35:
            y_points.append(page.metadata['coordinates']['points'][0][1])
            page_info.append(page.metadata['page_number'])
            lab['검사명'].append(page.page_content)

    for point, page_ in zip(y_points, page_info):
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            if points[0][0] > 240 and points[0][0] < 342 and points[0][1] > (point - 4) and points[0][1] < (point + 4) and metadata['page_number'] == page_:
                result = page.page_content
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
        
        not_present = True
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            if points[0][0] == 342.16 and points[0][1] > (point - 4) and points[0][1] < (point + 4) and metadata['page_number'] == page_:
                lab['status'].append(page.page_content)
                not_present = False
        if not_present:
            lab['status'].append(None)

        not_present = True
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            if points[0][0] > 380 and points[2][0] < 460 and points[0][1] > (point - 4) and points[0][1] < (point + 4) and metadata['page_number'] == page_:
                lab['MIN'].append(page.page_content)
                not_present = False
        if not_present:
            lab['MIN'].append(None)

        not_present = True
        for page in pages:
            metadata = page.metadata
            points = metadata['coordinates']['points']
            if points[0][0] > 450 and points[2][0] < 485 and points[0][1] > (point - 4) and points[0][1] < (point + 4) and metadata['page_number'] == page_:
                lab['MAX'].append(page.page_content)
                not_present = False
        if not_present:
            lab['MAX'].append(None)

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