import os
import time
from django.conf import settings

def cleanup_media_folder():
    """
    هذه الدالة تقوم بمسح أي ملف في مجلد media
    إذا كان قد مر على إنشائه أكثر من ساعة واحدة (3600 ثانية).
    يمكنك تغيير الوقت حسب الحاجة.
    """
    media_path = settings.MEDIA_ROOT
    if not os.path.exists(media_path):
        return

    # تحديد العمر الأقصى للملف بالثواني (مثلاً ساعة واحدة = 3600)
    # وضعناها ساعة بدلاً من 24 لضمان نظافة السيرفر دائماً
    max_age = 3600 
    current_time = time.time()
    
    deleted_count = 0

    # المرور على كل الملفات في المجلد
    for filename in os.listdir(media_path):
        file_path = os.path.join(media_path, filename)
        
        # التأكد من أنه ملف وليس مجلداً
        if os.path.isfile(file_path):
            file_creation_time = os.path.getctime(file_path)
            file_age = current_time - file_creation_time
            
            # إذا كان عمر الملف أكبر من العمر المسموح، قم بحذفه
            if file_age > max_age:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"فشل حذف الملف {filename}: {e}")
                    
    if deleted_count > 0:
        print(f"تم تنظيف السيرفر: تم حذف {deleted_count} ملفات قديمة من مجلد media.")