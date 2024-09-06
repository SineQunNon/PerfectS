import os
import time
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from llm.get_ppt_input import get_ppt_input
from pdfminer.pdfparser import PDFSyntaxError

# 로그 설정
logging.basicConfig(filename='/Users/sinequanon/Documents/PerfectS/logs/logfile.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return None
        else:
            # pdf 파일 들어올 시 pptx 생성 플로우 넣어 주기

            # 파일의 확장가가 pdf인지 확인
            if event.src_path.lower().endswith('.pdf'):
                print(f'PDF 파일이 들어옴: {event.src_path}')
                logging.info(f'PDF 파일이 들어옴: {event.src_path}')
                pdf_path = event.src_path
                try:
                    answer = get_ppt_input(pdf_path)
                    print(answer)
                except PDFSyntaxError as e:
                    print(f"PDF 파일 처리 중 오류 발생: {e}")
                    logging.error(f"PDF 파일 처리 중 오류 발생: {e}")
                    try:
                        os.remove(pdf_path)
                        print(f"손상된 PDF 파일 삭제 완료 : {pdf_path}")
                        logging.info(f"손상된 PDF 파일 삭제 완료 : {pdf_path}")
                    except Exception as delete_error:
                        print(f"손상된 PDF 파일 삭제 중 오류 발생: {delete_error}")
                        logging.error(f"손상된 PDF 파일 삭제 중 오류 발생: {delete_error}")
            else:
                print(f"PDF 이외의 파일이 들어옴 : {event.src_path}")
                logging.info(f"PDF 이외의 파일이 들어옴 : {event.src_path}")
                try:
                    os.remove(event.src_path)
                    print(f"파일 삭제 완료 : {event.src_path}")
                    logging.info(f"파일 삭제 완료 : {event.src_path}")
                except Exception as e:
                    print(f"파일 삭제 중 오류 발생: {event.src_path} - {e}")
                    logging.error(f"파일 삭제 중 오류 발생: {event.src_path} - {e}")

            #저장까지 하는 플로우

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
    # 공유 스토리지 경로 추가
    folder_to_monitor = "/Users/sinequanon/Documents/PerfectS/main"
    monitor_folder(folder_to_monitor)
