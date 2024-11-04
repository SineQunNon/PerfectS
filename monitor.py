import os
import logging

from pdfminer.pdfparser import PDFSyntaxError

from make_pptx.main import main_presentation
from Rag.loader.pdf_loader import load_pdf
from dotenv import load_dotenv
import time

load_dotenv()
PDF_INPUT = os.getenv("PDF_PATH")
PPTX_OUTPUT = os.getenv("PPTX_PATH")
log_dir = os.getenv("LOG_PATH")

processed_files = set()

# 로그 설정
logging.basicConfig(filename=f'{log_dir}/logfile.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def generate_new_filename(save_path):
    base, extension = os.path.splitext(save_path)  # 파일 경로와 확장자 분리
    counter = 1

    # 중복된 파일이 존재할 경우 숫자를 붙여 새로운 파일명 생성
    while os.path.exists(save_path):
        save_path = f"{base}_{counter}{extension}"
        counter += 1

    return save_path


def process_pdf_files(directory):
    global processed_files

    try:
        for filename in os.listdir(directory):
            if filename.startswith('.'):
                logging.info(f"숨김 파일 무시: {filename}")
                continue
            
            filepath = os.path.join(directory, filename)
            
            if filename.endswith(".pdf") and filepath not in processed_files:
                try:
                    logging.info(f"PDF file detecting : {filepath}")
                    
                    pages = load_pdf(filepath)
                    if not pages:
                        logging.error(f"Warning : PSEOF occuring : {filepath}")
                        continue
                    
                    logging.info(f"start to process : {pdf_path}")
                    start_time = time.time()
                    processed_files.add(filepath)

                    file_name = os.path.splitext(filename)[0]
                    #print(file_name)
                    
                    #dirpath = os.path.dirname
                    save_path = f"{PPTX_OUTPUT}/{file_name}.pptx"
                    
                    prs = main_presentation(filepath)
                    
                    # 저장하기
                    try:
                        if os.path.exists(save_path):
                            save_path = generate_new_filename(save_path)
                        prs.save(save_path)
                    except FileExistsError as e:
                        logging.error(e)
                    except Exception as e:
                        logging.error(e)
                    
                    if os.path.exists(filepath):                            
                        os.remove(filepath)
                    processed_files.remove(filepath)
                    end_time = time.time()
                    logging.info(f"Successfully Make Presentation : {save_path}, Running Time : {end_time-start_time} seconds")
                except PDFSyntaxError as e:
                    logging.error(f"PDF 파일 처리 중 오류 발생 : {e}")
                    try:
                        if os.path.exists(filepath):                            
                            os.remove(filepath)
                            logging.info(f"손상된 PDF 파일 삭제 완료 : {filepath}")
                    except Exception as delete_error:
                        logging.error(f"손상된 PDF 파일 삭제 중 오류 발생: {delete_error}")
            elif filepath in processed_files:
                if os.path.exists(filepath):
                    logging.info(f"이미 처리된 파일이 존재합니다. : {filepath}")
                    os.remove(filepath)
            else:
                filepath = os.path.join(directory, filename)
                logging.info(f"pdf 이외의 파일이 들어왔습니다. : {filepath}")

                if os.path.exists(filepath):
                    os.remove(filepath)
                logging.info(f"파일을 삭제하였습니다. : {filepath}")
    except PDFSyntaxError as e:
        pass

def monitor_directory(directory, interval=15):
    while True:
        process_pdf_files(directory)
        time.sleep(interval)
    
if __name__=="__main__":
    pdf_path = f"{PDF_INPUT}"
    print(f"start to monitor : {pdf_path}")

    monitor_directory(pdf_path)