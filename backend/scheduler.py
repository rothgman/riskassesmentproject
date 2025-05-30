import time
from threading import Thread

def update_scores_periodically(interval_sec=3600):
    def job():
        while True:
            print("⏳ Scheduled score update would run here.")
            time.sleep(interval_sec)
    
    thread = Thread(target=job, daemon=True)
    thread.start()

