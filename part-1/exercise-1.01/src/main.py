import time, uuid, re
from datetime import datetime, timezone

if __name__ == "__main__":
    while(True):
        # iso format
        # separator "T" rqeuired
        # express time up to milliseconds
        # use UTC, with "Z" instead of "+00:00"
        current_timestamp = re.sub('\+00:00', 'Z', datetime.now(timezone.utc).isoformat(timespec="milliseconds"))

        # generate a random string using UUID
        random_string = str(uuid.uuid4())

        # print formatted string
        print(f"{current_timestamp}: {random_string}")

        # repeat every 5 seconds
        time.sleep(5)
