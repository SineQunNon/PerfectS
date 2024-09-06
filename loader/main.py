from loader.pdf_loader import load_pdf
from loader.animal_info import get_animal_data
from loader.subjective import extract_date_position, extract_data_via_interval_info, extract_subjective_data
from loader.assessment import assessment_exists, plan_exists_for_assessment, extract_assessment_data, make_assessment_table
from loader.plan import plan_exists, extract_plan_data, make_plan_table
from loader.vital_check import extract_vital_check, make_vital_check_table
from loader.lab import extract_lab_data_all, extract_lab_table_date, extract_lab_data_via_interval_info, extract_lab_data, make_lab_table

import numpy as np

def get_soap(pages):
    data = extract_date_position(pages)
    soap_result = []

    for i in range(len(data)-1):
        soap_one = {
            "date": '',
            "subjective": [],
            "assessment": [],
            "plan": []
        }

        y_point = []
        page_num = []
        y_point.append(data[i][1])
        page_num.append(data[i][2])
        y_point.append(data[i+1][1])
        page_num.append(data[i+1][2])
        
        interval_info = np.column_stack((y_point, page_num))
        extracted_pages = extract_data_via_interval_info(pages, interval_info)

        subjective_data = extract_subjective_data(extracted_pages)
        soap_one['date'] = data[i][0]
        for page in subjective_data:
            soap_one['subjective'].append(page.page_content)

        assessment_data = extract_assessment_data(extracted_pages)
        if assessment_data:
            assessment_table = make_assessment_table(assessment_data)
            soap_one['assessment'].append(assessment_table)

        plan_data = extract_plan_data(extracted_pages)
        if plan_data:
            plan_table = make_plan_table(plan_data)
            soap_one['plan'].append(plan_table)
                
        soap_result.append(soap_one)

    return soap_result

def get_LLM_input(animal_info, soaps):
    llm_input = f"{str(animal_info)}\n" 

    for soap in soaps:
        llm_input += f"{soap['date']}\n"
        for data in soap['subjective']:
            llm_input += f"{data}\n"
    return llm_input

def get_vital_check(pages):
    vital_check_data = extract_vital_check(pages)
    vital_check_table = make_vital_check_table(vital_check_data)
    return vital_check_table

def get_lab(pages):
    lab_tables = []
    lab_pages = extract_lab_data_all(pages)
    lab_pages_date = extract_lab_table_date(lab_pages)
    lab_date = np.append(lab_pages_date, [[0,0,0]], axis=0)

    for i in range(len(lab_date)-1):
        lab_one = {
            'date': '',
            'table': ''
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
        extracted_pages = extract_lab_data(extracted_pages)

        lab_table = make_lab_table(extracted_pages)
        lab_one['table'] = lab_table
        lab_tables.append(lab_one)
    
    return lab_tables

# Test
def main(pdf_filepath):
    #pdf_filepath = '/Users/sinequanon/Documents/PerfectS/data/pdf_data/TEST_12.pdf'
    pages = load_pdf(pdf_filepath)

    animal_info = get_animal_data(pages)
    soap_result = get_soap(pages)
    vital_check_table = get_vital_check(pages)
    lab_tables = get_lab(pages)

    #print(animal_info)
    #print(soap_result)
    #print(vital_check_table)
    #print(lab_tables)
    return soap_result, vital_check_table, lab_tables, animal_info

if __name__ == "__main__":
    main("/Users/sinequanon/Documents/PerfectS/data/pdf_data/TEST_01.pdf")
