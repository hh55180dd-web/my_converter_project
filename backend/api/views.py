import os
import uuid
import aspose.words as aw
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

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

            # تنظيف العلامة المائية لـ Aspose
            clean_text = raw_text.replace("Evaluation Only. Created with Aspose.Words. Copyright 2003-2024 Aspose Pty Ltd.", "")
            clean_text = clean_text.replace("Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/", "")
            
            lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
            extracted_text = '\n'.join(lines)

            print(f"حجم النص المستخرج: {len(extracted_text)} حرف")

            if not extracted_text.strip():
                raise Exception("المستند فارغ أو عبارة عن صور فقط.")

            # ==========================================
            # 2. تخطي الذكاء الاصطناعي (مؤقتاً للاختبار)
            # ==========================================
            # نأخذ النص المستخرج ونعطيه مباشرة لمتغير الوورد
            clean_formatted_text = extracted_text 

            # 3. كتابة ملف الوورد مع دعم الاتجاه العربي (RTL) الصارم
            doc = Document()
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn

            lines = clean_formatted_text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # إضافة علامة (RLM) المخفية في بداية النص لإجبار الرموز على البقاء يميناً
                clean_line = '\u200F' + line

                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                
                # إجبار الفقرة على الاتجاه العربي
                pPr = p._element.get_or_add_pPr()
                bidi = OxmlElement('w:bidi')
                bidi.set(qn('w:val'), '1')
                pPr.append(bidi)
                
                run = p.add_run(clean_line)
                
                # إجبار الحروف على الاتجاه العربي وتحديد اللغة
                rPr = run._element.get_or_add_rPr()
                rtl = OxmlElement('w:rtl')
                rtl.set(qn('w:val'), '1')
                rPr.append(rtl)
                
                lang = OxmlElement('w:lang')
                lang.set(qn('w:bidi'), 'ar-SA') 
                rPr.append(lang)
                
                run.font.name = 'Arial' 
                run.font.size = Pt(12)

            doc.save(docx_path)
            file_url = request.build_absolute_uri(f"{settings.MEDIA_URL}converted_{unique_id}.docx")
            return Response({'docx_url': file_url})

        except Exception as e:
            print(f"Error Output: {str(e)}")
            return Response({'error': str(e)}, status=500)
        
        finally:
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except:
                    pass