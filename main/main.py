import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return None
        else:
            # pdf 파일 들어올 시 pptx 생성 플로우 넣어 주기

            print(f'파일이 생성되었습니다: {event.src_path}')
            #src_path에 대해서 코드 실행

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
