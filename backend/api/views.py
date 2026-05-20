import os
import uuid
import re  # أضفنا مكتبة التعابير النمطية لتنظيف العلامات المائية
import aspose.words as aw
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import g4f

class PDFToWordView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        pdf_file = request.FILES.get('pdf')
        if not pdf_file:
            return Response({'error': 'لم يتم اختيار ملف'}, status=400)

        unique_id = uuid.uuid4().hex
        pdf_path = os.path.join(settings.MEDIA_ROOT, f"temp_{unique_id}.pdf")
        docx_path = os.path.join(settings.MEDIA_ROOT, f"converted_{unique_id}.docx")

        with open(pdf_path, 'wb+') as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)

        try:
            # 1. استخراج النص باستخدام Aspose
            loadOptions = aw.loading.PdfLoadOptions()
            pdf_doc = aw.Document(pdf_path, loadOptions)
            raw_text = pdf_doc.to_string(aw.SaveFormat.TEXT)

            # --- التنظيف الذكي (Regex) للعلامات المائية ---
            # سيقوم بحذف أي سطر يحتوي على كلمة Evaluation أو Aspose.Words مهما كان العام أو الرابط
            clean_text = re.sub(r"Evaluation Only\..*?Aspose Pty Ltd\.", "", raw_text, flags=re.IGNORECASE | re.DOTALL)
            clean_text = re.sub(r"Created with an evaluation copy of Aspose\.Words\..*?(https?://\S+)?", "", clean_text, flags=re.IGNORECASE | re.DOTALL)
            
            lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
            extracted_text = '\n'.join(lines)

            if not extracted_text.strip():
                raise Exception("المستند فارغ أو عبارة عن صور فقط ولا يمكن قراءته.")

            print("جاري تصحيح النص باستخدام الذكاء الاصطناعي...")

            # 2. تصحيح النص باستخدام g4f (بشكل إلزامي)
            prompt = f"""
            أنت مصحح لغوي عربي محترف. النص التالي مستخرج من PDF وفيه أخطاء في التعرف على الحروف (مثل: سايقح التكاسح، شــر،، عوايل).
            المطلوب:
            1. صحح الأخطاء الإملائية فقط لتعود الكلمات لشكلها العربي الصحيح المفهوم.
            2. حافظ على العناوين والتقسيم كما هو.
            3. أعد النص المصحح فقط بدون أي مقدمات أو تعليقات.
            
            النص:
            {extracted_text}
            """

            try:
                # استخدمنا gpt-4 لأنه مدعوم وأكثر ذكاءً
                response = g4f.ChatCompletion.create(
                    model="gpt-4", 
                    messages=[{"role": "user", "content": prompt}]
                )
                
                clean_formatted_text = response

                # التأكد من أن الرد صالح وليس فارغاً
                if not clean_formatted_text or len(clean_formatted_text) < 50:
                    raise Exception("الرد من الذكاء الاصطناعي كان فارغاً.")
                    
            except Exception as ai_err:
                # إيقاف العملية فوراً وإرسال خطأ للواجهة (No Fallback)
                raise Exception(f"تعذر الاتصال بخادم الذكاء الاصطناعي للتصحيح اللغوي. يرجى المحاولة بعد قليل.")

            print("تم التصحيح، جاري إنشاء ملف الوورد...")

            # 3. كتابة ملف الوورد مع دعم الاتجاه العربي (RTL) الصارم
            doc = Document()
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn

            lines = clean_formatted_text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                clean_line = line.replace('**', '').replace('#', '').strip()
                clean_line = '\u200F' + clean_line

                p = doc.add_paragraph()
                # المحاذاة لليسار مع دعم RTL
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.line_spacing = 2
                
                pPr = p._element.get_or_add_pPr()
                bidi = OxmlElement('w:bidi')
                bidi.set(qn('w:val'), '1')
                pPr.append(bidi)
                
                run = p.add_run(clean_line)
                
                rPr = run._element.get_or_add_rPr()
                rtl = OxmlElement('w:rtl')
                rtl.set(qn('w:val'), '1')
                rPr.append(rtl)
                
                lang = OxmlElement('w:lang')
                lang.set(qn('w:bidi'), 'ar-SA') 
                rPr.append(lang)
                
                run.font.name = 'Arial' 
                run.font.size = Pt(16)

            doc.save(docx_path)
            file_url = request.build_absolute_uri(f"{settings.MEDIA_URL}converted_{unique_id}.docx")
            return Response({'docx_url': file_url})

        except Exception as e:
            print(f"Error Output: {str(e)}")
            return Response({'error': str(e)}, status=500)
        
        finally:
            # تنظيف ملف الـ PDF فقط (ملف الورد سيتم مسحه بواسطة السكريبت التلقائي)
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except:
                    pass