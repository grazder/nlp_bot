from datetime import datetime, timedelta

datetime_now = datetime.now()
delta = timedelta(days=1)
print(datetime.strftime(datetime_now + delta, "%d.%m.%Y"))
