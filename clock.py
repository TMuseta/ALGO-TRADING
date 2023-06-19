from apscheduler.schedulers.blocking import BlockingScheduler
from main import main  # assuming your bot's main function is named "main" and it's in bot.py

scheduler = BlockingScheduler()

@scheduler.scheduled_job('interval', hours=4.8)  # roughly 5 times a day
def scheduled_main():
    main()

scheduler.start()
