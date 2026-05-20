"use client";
import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState('');
  const [error, setError] = useState('');

  const handleUpload = async () => {
    if (!file) {
      setError("الرجاء إرفاق المستند أولاً");
      return;
    }

    const formData = new FormData();
    formData.append('pdf', file);

    setLoading(true);
    setDownloadUrl('');
    setError('');

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/convert/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setDownloadUrl(response.data.docx_url);
    } catch (err: any) {
      setError(err.response?.data?.error || "حدث خطأ غير متوقع أثناء الاتصال بالخادم المركزي.");
    } finally {
      setLoading(false);
    }
  };

  return (
    // الخلفية العامة باستخدام اللون الرمادي الفاتح
    <main dir="rtl" className="flex min-h-screen flex-col items-center justify-center p-4 bg-[#d9d9d9] font-sans selection:bg-[#988561] selection:text-white">
      
      {/* البطاقة الرئيسية مع إطار علوي باللون الذهبي/البرونزي */}
      <div className="w-full max-w-xl p-8 bg-white rounded-xl shadow-2xl border-t-8 border-t-[#988561] relative overflow-hidden">
        
        {/* زخرفة خلفية خفيفة جداً باللون الكحلي العميق */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-[#052326] opacity-5 rounded-bl-full pointer-events-none"></div>

        {/* --- منطقة شعار النسر السوري --- */}
        <div className="flex justify-center mb-6 relative z-10">
          <div className="w-28 h-28 flex items-center justify-center bg-[#d9d9d9]/30 rounded-full border-2 border-[#988561] p-2 shadow-inner">
            <img 
              src="/eagle-logo.png" 
              alt="شعار الجمهورية" 
              className="object-contain w-full h-full drop-shadow-md"
            />
          </div>
        </div>
        
        {/* الترويسة الرسمية */}
        <div className="text-center mb-8 relative z-10">
          <h1 className="text-2xl font-bold text-[#052326] mb-2 tracking-wide">
            البوابة الرقمية لمعالجة الوثائق
          </h1>
          <p className="text-sm font-medium text-[#988561]">
            نظام استخراج وتنسيق النصوص (النسخة المعتمدة)
          </p>
        </div>
        
        <div className="space-y-6 relative z-10">
          
          {/* منطقة رفع الملفات */}
          <label className={`flex flex-col items-center justify-center w-full h-40 border-2 border-dashed rounded-lg cursor-pointer transition-all duration-300 ${file ? 'border-[#052326] bg-[#052326]/5' : 'border-[#988561] bg-[#d9d9d9]/20 hover:bg-[#d9d9d9]/40'}`}>
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              {file ? (
                <>
                  <svg className="w-12 h-12 text-[#052326] mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="mb-2 text-sm text-[#052326] font-bold">{file.name}</p>
                  <p className="text-xs text-[#988561] font-medium">انقر هنا لتعديل المرفق</p>
                </>
              ) : (
                <>
                  <svg className="w-12 h-12 text-[#988561] mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                  <p className="mb-2 text-sm text-[#052326]"><span className="font-bold">استعرض المستند</span> أو قم بالسحب والإفلات</p>
                  <p className="text-xs text-[#052326]/60">صيغة PDF فقط</p>
                </>
              )}
            </div>
            <input 
              type="file" 
              accept=".pdf" 
              onChange={(e) => {
                setFile(e.target.files?.[0] || null);
                setError('');
                setDownloadUrl('');
              }}
              className="hidden"
            />
          </label>

          {/* رسائل الخطأ */}
          {error && (
            <div className="p-4 bg-red-50 border-r-4 border-red-700 text-red-800 text-sm font-medium rounded shadow-sm flex items-center">
              <svg className="w-5 h-5 ml-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              {error}
            </div>
          )}

          {/* زر التنفيذ */}
          <button 
            onClick={handleUpload}
            disabled={loading || !file}
            className={`relative w-full flex justify-center py-4 px-4 rounded-md text-md font-bold transition-all duration-300 ${
              loading || !file 
                ? 'bg-[#d9d9d9] text-[#052326]/50 cursor-not-allowed' 
                : 'bg-[#052326] text-[#d9d9d9] hover:bg-[#988561] hover:text-[#052326] shadow-lg hover:shadow-xl active:scale-[0.98]'
            }`}
          >
            {loading ? (
              <div className="flex items-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 currentColor" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                جاري معالجة وتوثيق البيانات...
              </div>
            ) : (
              "البدء بمعالجة الوثيقة"
            )}
          </button>

          {/* نتيجة التحويل */}
          {downloadUrl && (
            <div className="p-6 mt-6 bg-[#d9d9d9]/20 border border-[#988561] rounded-lg text-center animate-fade-in-up">
              <div className="flex justify-center mb-4">
                <div className="bg-[#052326] p-3 rounded-full text-[#988561]">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                </div>
              </div>
              <h3 className="text-lg font-bold text-[#052326] mb-2">تم تجهيز المستند بنجاح</h3>
              <p className="text-sm text-[#052326]/70 mb-5">الوثيقة جاهزة للتحميل بصيغة وورد المعتمدة.</p>
              <a 
                href={downloadUrl} 
                className="inline-flex items-center justify-center w-full px-6 py-3 bg-[#988561] text-[#052326] font-bold rounded-md hover:bg-[#052326] hover:text-[#988561] transition-colors duration-300"
              >
                <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                تحميل الوثيقة
              </a>
            </div>
          )}
        </div>
      </div>
      
      {/* التذييل الرسمي */}
      <p className="mt-8 text-xs font-medium text-[#052326]/60 tracking-wider">
        جميع الحقوق محفوظة © {new Date().getFullYear()}
      </p>
    </main>
  );
}