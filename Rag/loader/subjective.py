import re
import numpy as np

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

def extract_data_via_interval_info(pages, interval_info):
    extracted_pages = []
    start_y_point = float(interval_info[0][0])
    end_y_point = float(interval_info[1][0])
    start_page = int(interval_info[0][1])
    end_page = int(interval_info[1][1])

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

def extract_subjective_data(pages):
    extracted_pages = []
    min_page = 50000
    min_height = 50000.0
    for page in pages:
        metadata = page.metadata
        points = metadata['coordinates']['points']
        text = page.page_content

        if (text.lower() == 'plan' or text.lower() == 'assessment') and points[0][0] == 36.02:
            if metadata['page_number'] <= min_page:
                min_page = metadata['page_number']
                min_height = min(min_height, points[0][1])

    for page in pages:
        metadata = page.metadata
        points = metadata['coordinates']['points']
        page_num = metadata['page_number']
        y_point = points[0][1]

        if page_num < min_page:
            extracted_pages.append(page)
        elif page_num == min_page and y_point < min_height:
            extracted_pages.append(page)

    return extracted_pages
