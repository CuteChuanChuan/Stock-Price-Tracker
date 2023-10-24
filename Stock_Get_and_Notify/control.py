import time
import datetime
from Stock_Get_and_Notify.stock_main import stock_main

weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

update_frequency_min = 15

run = True

while run:
    now = datetime.datetime.now()
    if now.strftime('%A') in weekdays:

        while 14 >= now.hour >= 9:
            start_time = datetime.datetime.now()

            operating_result = stock_main()

            end_time = datetime.datetime.now()

            operating_result["time_spent"] = str((end_time - start_time).seconds)
            print(operating_result)

            time.sleep(1 * 60 * update_frequency_min)

        if now.hour > 14:
            run = False

    else:
        run = False

