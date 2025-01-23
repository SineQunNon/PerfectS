from pptx import Presentation
from make_pptx.get_template import get_template
from make_pptx.title_page import make_title_page
from make_pptx.soap_pages import make_soap_pages
import logging
from Rag.loader.main import *
from Rag.loader.pdf_loader import load_pdf
from make_pptx.main import *

log_dir='/home/user/PerfectS_test/logs'

# 로그 설정
logging.basicConfig(filename=f'{log_dir}/logfile.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


prs = Presentation("/home/user/PerfectS_test/make_pptx/template/template_final.pptx")

pdf_path = '/home/user/PerfectS_test/data/pdf_input/1066724580_김유나(손대하)_2032937_(cat)소미_20241205.pdf'

#prs = main_presentation(pdf_path)

#main(pdf_path)
table, table_2 = get_pptx_AnionGap_and_other_tables(pdf_path)

print(table)