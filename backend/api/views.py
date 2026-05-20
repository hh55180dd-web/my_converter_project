import os
import uuid
import aspose.words as aw
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

class PDFToWordView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        pdf_file = request.FILES.get('pdf')
        
        if not pdf_file:
            return Response({'error': 'الرجاء اختيار ملف PDF صالح'}, status=400)

        # 1. تجهيز المجلدات والأسماء
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)

        unique_id = uuid.uuid4().hex
        original_name = os.path.splitext(pdf_file.name)[0]
        
        pdf_filename = f"input_{unique_id}.pdf"
        docx_filename = f"{original_name}_{unique_id}.docx"
        
        pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)
        docx_path = os.path.join(settings.MEDIA_ROOT, docx_filename)

        try:
            # 2. حفظ ملف الـ PDF المرفوع
            with open(pdf_path, 'wb+') as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            # 3. إعدادات التحويل
            # تم حذف display_doc_title لأنه غير مدعوم في هذه النسخة
            loadOptions = aw.loading.PdfLoadOptions()
            
            # تحميل الملف باستخدام الإعدادات الأساسية
            doc = aw.Document(pdf_path, loadOptions)
            for section in doc.sections:
                section = section.as_section()
                # التأكد من أن اتجاه الصفحة يدعم العربي (RTL)
                section.page_setup.bidi = True 
            
            # خيارات حفظ متقدمة
            saveOptions = aw.saving.OoxmlSaveOptions(aw.SaveFormat.DOCX)
            # استخدام نظام تنسيق يحافظ على الجداول وأماكن النصوص
            saveOptions.compliance = aw.saving.OoxmlCompliance.ISO29500_2008_TRANSITIONAL
            
            # تنفيذ التحويل
            doc.save(docx_path, saveOptions)

            # 4. تجهيز رابط التحميل (URL)
            file_url = request.build_absolute_uri(f"{settings.MEDIA_URL}{docx_filename}")

            return Response({
                'message': 'تم التحويل بنجاح',
                'docx_url': file_url,
                'file_name': f"{original_name}.docx"
            })

        except Exception as e:
            # طباعة الخطأ في التيرمينال لمعرفة التفاصيل إذا حدث خطأ آخر
            print(f"Conversion Error: {str(e)}") 
            return Response({'error': f'فشل التحويل: {str(e)}'}, status=500)
        
        finally:
            # 5. تنظيف ملف الـ PDF بعد التحويل
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except:
                    pass