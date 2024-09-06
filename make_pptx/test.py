import os
from pptx import Presentation

from get_template import get_template
from make_pptx.lab_pages import make_lab_page
from make_pptx.vital_check_pages import make_vital_check_page
from soap_pages import make_soap_pages
from img_pages import make_chart_img_pages
from end_page import make_end_page

import time

def main_presentation(pdf_path):
    pptx_template = get_template()
    if not os.path.exists(pptx_template):
        print("pptx template file does not exist")
        exit(1)

    prs = Presentation(pptx_template)
    start_time = time.time()
    make_soap_pages(prs, pdf_path)

    make_chart_img_pages(prs, pdf_path) 

    make_vital_check_page(prs, pdf_path)

    make_lab_page(prs, pdf_path)

    make_end_page(prs)
    end_time = time.time()

    # 저장 플로우
    save_path = '/Users/sinequanon/Documents/PerfectS/data/pptx/test_pptx.pptx'
    prs.save(save_path)
    print(f"successfully saved : {save_path}")
    print(f"시간 : {end_time - start_time}s")

if __name__=="__main__":
    main_presentation("/Users/sinequanon/Documents/PerfectS/data/pdf_data/TEST_04.pdf")




