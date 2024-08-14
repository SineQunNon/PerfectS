import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from llm.get_ppt_input import get_ppt_input

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return None
        else:
            # pdf 파일 들어올 시 pptx 생성 플로우 넣어 주기

            # 파일의 확장가가 pdf인지 확인
            if event.src_path.lower().endswith('.pdf'):
                print(f'PDF 파일이 들어옴: {event.src_path}')
                pdf_path = event.src_path
                answer = get_ppt_input(pdf_path)
                print(answer)
            else:
                print(f"PDF 이외의 파일이 들어옴 : {event.src_path}")
            
            #저장까지 하는 플로우


def monitor_folder(path_to_watch):
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__=="__main__":
    # 공유 스토리지 경로 추가
    folder_to_monitor = "/Users/sinequanon/Documents/PerfectS/main"
    monitor_folder(folder_to_monitor)
