from django.apps import AppConfig
import os

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # يمنع تشغيل المجدول مرتين أثناء التطوير (بسبب الـ auto-reload في Django)
        if os.environ.get('RUN_MAIN', None) != 'true':
            return
            
        from apscheduler.schedulers.background import BackgroundScheduler
        from .tasks import cleanup_media_folder
        
        # إنشاء المجدول الذي سيعمل في الخلفية
        scheduler = BackgroundScheduler()
        
        # إضافة المهمة لتعمل كل 60 دقيقة
        scheduler.add_job(cleanup_media_folder, 'interval', minutes=60)
        
        # بدء التشغيل
        scheduler.start()
        print("تم تفعيل نظام التنظيف التلقائي للملفات (Background Scheduler).")