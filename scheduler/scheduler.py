from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
import pytz


class PostScheduler:
    def __init__(self, timezone: str = "Asia/Seoul", blocking: bool = True):
        self.tz = pytz.timezone(timezone)
        cls = BlockingScheduler if blocking else BackgroundScheduler
        self.scheduler = cls(timezone=self.tz)

    def add_once(self, func, run_at: str, *args, **kwargs):
        """특정 시각에 한 번 실행 (ISO 8601: 2024-12-01T09:00:00)"""
        naive_dt = datetime.fromisoformat(run_at)
        dt = self.tz.localize(naive_dt)
        self.scheduler.add_job(func, DateTrigger(run_date=dt), args=args, kwargs=kwargs)
        print(f"예약 등록: {run_at}")

    def add_recurring(self, func, cron_expr: str, *args, **kwargs):
        """Cron 표현식으로 반복 실행 (예: '0 9 * * 1-5' = 평일 오전 9시)"""
        self.scheduler.add_job(func, CronTrigger.from_crontab(cron_expr, timezone=self.tz), args=args, kwargs=kwargs)
        print(f"반복 예약: {cron_expr}")

    def start(self):
        print("스케줄러 시작됨. Ctrl+C로 종료.")
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("스케줄러 종료.")

    def stop(self):
        self.scheduler.shutdown()
