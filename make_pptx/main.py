import os
import logging
from pptx import Presentation

from make_pptx.get_template import get_template
from make_pptx.lab_pages import make_lab_hct_page, make_lab_aniongap_other_page
from make_pptx.title_page import make_title_page
from make_pptx.vital_check_pages import make_vital_check_page
from make_pptx.soap_pages import make_soap_pages
from make_pptx.img_pages import make_chart_img_pages
from make_pptx.end_page import make_end_page

import time

def main_presentation(pdf_path):
    pptx_template = get_template('template_final.pptx')

    if not os.path.exists(pptx_template):
        print("pptx template file does not exist")
        exit(1)

    prs = Presentation(pptx_template)

    try:
        make_title_page(prs)
        logging.info(f"make_title_page done : {pdf_path}")
    except Exception as e:
        logging.error(f"Unexpected error processing in make_title_page {pdf_path} : {str(e)}")

    try:
        make_soap_pages(prs, pdf_path)
        logging.info(f"make_soap_pages done : {pdf_path}")
    except Exception as e:
        logging.error(f"Unexpected error processing in make_soap_pages {pdf_path} : {str(e)}")

    try:
        make_chart_img_pages(prs, pdf_path)
        logging.info(f"make_chart_img_pages done : {pdf_path}")
    except Exception as e:
        logging.error(f"Unexpected error processing in {pdf_path} : {str(e)}")
    
    try:
        make_vital_check_page(prs, pdf_path)
        logging.info(f"make_vital_check_page done : {pdf_path}")
    except Exception as e:
        logging.error(f"Unexpected error processing in make_vital_check_page {pdf_path} : {str(e)}")

    try:
        make_lab_hct_page(prs, pdf_path)
        logging.info(f"make_lab_hct_page done : {pdf_path}")
    except Exception as e:
        logging.error(f"Unexpected error processing in make_lab_hct_page {pdf_path} : {str(e)}")

    try:
        make_lab_aniongap_other_page(prs, pdf_path)
        logging.info(f"make_lab_aniongap_other_page done : {pdf_path}")
    except Exception as e:
        logging.error(f"Unexpected error processing in make_lab_aniongap_other_page {pdf_path} : {str(e)}")

    try:
        make_end_page(prs)
        logging.info(f"make_end_page done : {pdf_path}")
    except Exception as e:
        logging.error(f"Unexpected error processing in make_end_page {pdf_path} : {str(e)}")
    

    # 저장 플로우
    #prs.save(save_path)
    return prs


# if __name__=="__main__":
#    main_presentation("/home/pjw/PerfectS_beta/data/pdf_input/TEST_01.pdf","/home/pjw/PerfectS_beta/data/pptx_output/test.pptx")

