import os
import time
import logging
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pdfminer.pdfparser import PDFSyntaxError
from make_pptx.main import main_presentation
from dotenv import load_dotenv
load_dotenv()

# 로그 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(current_dir, 'logs')
logging.basicConfig(filename=f'{log_dir}/logfile.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

os.environ['PYTHONPATH'] = current_dir
os.environ['PYTHONIOENCODING'] = 'utf-8'

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        start_time = time.time()

        if event.is_directory:
            logging.info("디렉터리 파일이 들어옴.")
            return None
        else:
            print("파일 들어옴")
            # MIME 타입 확인
        
            # pdf 파일 들어올 시 pptx 생성 플로우 넣어 주기
            # 파일의 확장가가 pdf인지 확인
            if event.src_path.lower().endswith('.pdf'):
            #if 'pdf' in file_mime_type:
                logging.info(f'PDF 파일이 들어옴: {event.src_path}')
                #os.chmod(event.src_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

                pdf_path = event.src_path
                file_name = os.path.splitext(os.path.basename(pdf_path))[0]
                #file_name = os.path.basename(pdf_path)
                print(file_name)
                #save_path = os.path.join(current_dir, 'data', 'pptx_output', f'{file_name}.pptx')
                save_path = f"/home/pjw/mnt/volume1/SAMC NAS/허찬/PerfestS_test/pptx_output/{file_name}.pptx"
                end_time = time.time()
                try:
                    main_presentation(pdf_path, save_path)
                    logging.info(f"Successfully Make Presentation : {save_path}, Running Time : {end_time-start_time} seconds")
                    os.remove(pdf_path)
                except PDFSyntaxError as e:
                    logging.error(f"PDF 파일 처리 중 오류 발생: {e}")
                    try:
                        os.remove(pdf_path)
                        logging.info(f"손상된 PDF 파일 삭제 완료 : {pdf_path}")
                    except Exception as delete_error:
                        logging.error(f"손상된 PDF 파일 삭제 중 오류 발생: {delete_error}")
            else:
                logging.info(f"PDF 이외의 파일이 들어옴 : {event.src_path}")
                try:
                    os.remove(event.src_path)
                    logging.info(f"파일 삭제 완료 : {event.src_path}")
                except Exception as e:
                    logging.error(f"파일 삭제 중 오류 발생: {event.src_path} - {e}")

def monitor_folder(path_to_watch):
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__=="__main__":
    print("start to monitor folder")
    # 공유 스토리지 경로 추가
    #pdf_path = os.path.join(current_dir, "data/pdf_input")
    pdf_path = "/home/pjw/mnt/volume1/SAMC NAS/허찬/PerfestS_test/pdf_input"
    print(pdf_path)
    monitor_folder(pdf_path)
