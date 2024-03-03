import os
import time
from google.cloud import bigquery
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

print("sidecar sleeping 60sec")
time.sleep(60)
print("sidecar creating ready file")
f = open("/workdir/ready", "a")
f.write("ready")
f.close()
print("sidecar sleeping 60sec")
time.sleep(60)
print("sidecar creating terminated file")
f = open("/workdir/terminated", "a")
f.write("terminated")
f.close()
print("testing hook")
for i in range(10):
    print("hook exists: {}", os.path.isfile("/workdir/hook"))
    time.sleep(1)
print("sidecar quits")
quit()

client = bigquery.Client()

# Perform a query.
QUERY = (
    'SELECT * FROM `k-pipe-test-system.orchestrator.step_events`'
)
query_job = client.query(QUERY)  # API request
rows = query_job.result()  # Waits for query to finish

for row in rows:
    print(row)


class MyHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print(f'event type: {event.event_type}  path : {event.src_path}')


if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path='/tmp/', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
            print(".")
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
