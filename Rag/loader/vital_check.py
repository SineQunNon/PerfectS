import pandas as pd
import logging

def extract_vital_check(pages):
    extracted_pages = []
    vital_page_num = 0
    vital_y_point = 0
    vaccination_page_num = 0
    vaccination_y_point = 0
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
        
        if page.page_content.lower() == 'vaccination' and x_point == 33.35 and y_height > 20:
            vaccination_y_point = coordinates['points'][0][1]
            vaccination_page_num = metadata['page_number']

        if page.page_content.lower() == 'lab' and x_point == 33.35 and y_height > 20:
            lab_y_point = coordinates['points'][0][1]
            lab_page_num = metadata['page_number']
    
    if vaccination_page_num != 0 and vaccination_y_point != 0:
        lab_page_num = vaccination_page_num
        lab_y_point = vaccination_y_point

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
        '날짜': [],
        '시간': [],
        'BW(Kg)': [],
        'BT(C)': [],
        'BP(mmHg)': [],
        'HR(/min)': [],
        'Sign': []
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
    
    try:
        vital_check_df = pd.DataFrame(vital_check)
        return vital_check_df
    except ValueError as e:
        logging.error(f"Error processing in make_vital_check_table : {e}")
        return pd.DataFrame()
