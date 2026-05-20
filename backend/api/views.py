import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from pdf2docx import Converter

class PDFToWordView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        pdf_file = request.FILES.get('pdf')
        
        if not pdf_file:
            return Response({'error': 'No file uploaded'}, status=400)

        # 1. حفظ ملف الـ PDF مؤقتاً
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'temp.pdf')
        docx_path = os.path.join(settings.MEDIA_ROOT, 'converted.docx')

        # التأكد من وجود مجلد media
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)

        with open(pdf_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)

        try:
            # 2. عملية التحويل
            cv = Converter(pdf_path)
            cv.convert(docx_path, start=0, end=None)
            cv.close()

            # 3. إرسال رابط تحميل الملف
            file_url = request.build_absolute_uri(settings.MEDIA_URL + 'converted.docx')
            return Response({'docx_url': file_url})

        except Exception as e:
            return Response({'error': str(e)}, status=500)