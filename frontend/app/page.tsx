"use client";
import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState('');

  const handleUpload = async () => {
    if (!file) {
      alert("الرجاء اختيار ملف PDF");
      return;
    }

    const formData = new FormData();
    formData.append('pdf', file);

    setLoading(true);
    setDownloadUrl('');

    try {
      // إرسال الملف للباك-إند
      const response = await axios.post('http://127.0.0.1:8000/api/convert/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setDownloadUrl(response.data.docx_url);
    } catch (error: any) {
      alert("خطأ في التحويل: " + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 bg-gray-100">
      <div className="w-full max-w-md p-8 bg-white rounded-2xl shadow-xl">
        <h1 className="text-2xl font-bold text-center text-gray-800 mb-8">
          محول PDF إلى Word
        </h1>
        
        <div className="space-y-4">
          <input 
            type="file" 
            accept=".pdf" 
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="w-full p-2 border border-dashed border-blue-400 rounded-lg"
          />

          <button 
            onClick={handleUpload}
            disabled={loading}
            className={`w-full py-3 rounded-lg font-bold text-white transition ${
              loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {loading ? "جاري المعالجة..." : "تحويل إلى Word"}
          </button>

          {downloadUrl && (
            <div className="p-4 mt-4 bg-green-50 border border-green-200 rounded-lg text-center">
              <p className="text-green-700 mb-2">🎉 اكتمل التحويل!</p>
              <a 
                href={downloadUrl} 
                className="inline-block px-6 py-2 bg-green-600 text-white rounded-full hover:bg-green-700 transition"
              >
                تحميل ملف Word
              </a>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}