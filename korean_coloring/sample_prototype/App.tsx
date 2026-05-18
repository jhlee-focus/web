
import React, { useState, useRef, useEffect, useCallback } from 'react';
import SlideGenerator from './components/SlideGenerator';
import { Heart, Printer, Type, Image as ImageIcon, X, Download, Search, ExternalLink, ClipboardCheck, User, Calendar } from 'lucide-react';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import { GoogleGenAI } from "@google/genai";

const App: React.FC = () => {
  const [inputText, setInputText] = useState('하츄핑');
  const [childName, setChildName] = useState('');
  // 날짜 초기값을 빈 문자열로 설정하여 자동 입력을 방지합니다.
  const [date, setDate] = useState('');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [groundingLinks, setGroundingLinks] = useState<{title: string, uri: string}[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const slideRef = useRef<HTMLDivElement>(null);

  const handlePrint = () => {
    window.print();
  };

  const handleSearchImage = async () => {
    if (!inputText.trim()) {
      alert("검색할 캐릭터 이름을 입력해주세요!");
      return;
    }

    setIsSearching(true);
    setGroundingLinks([]);
    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      const response = await ai.models.generateContent({
        model: 'gemini-3-pro-preview',
        contents: `${inputText} 캐릭터의 어린이용 색칠공부 도안(coloring book page, line art, outline, white background)을 웹에서 찾아줘. 직접적인 이미지 URL이 있다면 알려주고, 없다면 이미지가 있는 웹사이트 링크들을 나열해줘.`,
        config: {
          tools: [{ googleSearch: {} }],
        },
      });

      const chunks = response.candidates?.[0]?.groundingMetadata?.groundingChunks;
      if (chunks && chunks.length > 0) {
        const links = chunks
          .filter(chunk => chunk.web)
          .map(chunk => ({
            title: chunk.web.title || '출처 링크',
            uri: chunk.web.uri
          }));
        setGroundingLinks(links);

        const textResponse = response.text || "";
        const urlMatch = textResponse.match(/\bhttps?:\/\/\S+\.(?:png|jpg|jpeg|gif|webp)\b/i);
        
        if (urlMatch) {
          setSelectedImage(urlMatch[0]);
        }
      } else {
        alert(`'${inputText}'에 대한 검색 결과를 찾지 못했습니다. 직접 이미지를 찾아 붙여넣어 보세요!`);
      }
    } catch (error) {
      console.error('이미지 검색 오류:', error);
      alert('검색 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.');
    } finally {
      setIsSearching(false);
    }
  };

  const handleSaveAsPDF = async () => {
    if (!slideRef.current) return;
    setIsExporting(true);
    
    setTimeout(async () => {
      try {
        const canvas = await html2canvas(slideRef.current!, {
          scale: 2,
          useCORS: true,
          allowTaint: true,
          backgroundColor: '#ffffff',
          logging: false,
        });
        const imgData = canvas.toDataURL('image/jpeg', 0.95);
        const pdf = new jsPDF({
          orientation: 'landscape',
          unit: 'mm',
          format: 'a4'
        });
        
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
        
        pdf.addImage(imgData, 'JPEG', 0, 0, pdfWidth, pdfHeight);
        pdf.save(`한글공부_${inputText || '연습'}.pdf`);
      } catch (error) {
        console.error('PDF 저장 실패:', error);
        alert("PDF 생성 중 오류가 발생했습니다.");
      } finally {
        setIsExporting(false);
      }
    }, 200);
  };

  const processFile = useCallback((file: File) => {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  }, []);

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) processFile(file);
  };

  const handlePaste = useCallback((event: ClipboardEvent) => {
    const items = event.clipboardData?.items;
    if (items) {
      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
          const file = items[i].getAsFile();
          if (file) {
            processFile(file);
            break;
          }
        }
      }
    }
  }, [processFile]);

  useEffect(() => {
    window.addEventListener('paste', handlePaste);
    return () => window.removeEventListener('paste', handlePaste);
  }, [handlePaste]);

  return (
    <div className="min-h-screen flex flex-col items-center p-4 md:p-8 space-y-6 select-none">
      {/* Header */}
      <header className="no-print w-full max-w-6xl bg-white shadow-xl rounded-3xl p-6 flex flex-col gap-6 border-b-4 border-pink-200">
        <div className="flex flex-col lg:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-4 shrink-0">
            <div className="bg-pink-500 p-3 rounded-2xl text-white shadow-lg">
              <Heart size={28} fill="currentColor" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-gray-800 tracking-tight">아이조아 한글 놀이터</h1>
              <p className="text-sm text-pink-500 font-bold">캐릭터 도안을 찾고 한글을 배워요!</p>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 w-full lg:w-auto items-center">
            <div className="flex w-full sm:w-auto gap-2">
              <div className="relative flex-1 sm:w-48">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-pink-400">
                  <Type size={18} />
                </div>
                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="단어 입력"
                  className="block w-full pl-10 pr-4 py-2.5 border-2 border-pink-50 rounded-xl bg-pink-50 font-bold text-gray-700 focus:outline-none focus:ring-2 focus:ring-pink-400 transition-all text-sm"
                  maxLength={12}
                />
              </div>
              <button
                onClick={handleSearchImage}
                disabled={isSearching || !inputText.trim()}
                className="px-4 py-2.5 bg-indigo-500 text-white rounded-xl hover:bg-indigo-600 transition-all shadow-md active:scale-95 disabled:opacity-50 flex items-center gap-2 font-bold whitespace-nowrap text-sm"
              >
                {isSearching ? <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div> : <Search size={18} />}
                <span>이미지 찾기</span>
              </button>
            </div>

            <div className="flex gap-2">
              <input type="file" ref={fileInputRef} onChange={handleImageUpload} accept="image/*" className="hidden" />
              {!selectedImage ? (
                <button onClick={() => fileInputRef.current?.click()} className="p-2.5 border-2 border-dashed border-gray-200 rounded-xl text-gray-400 hover:bg-gray-50 transition-all" title="업로드">
                  <ImageIcon size={20} />
                </button>
              ) : (
                <button onClick={() => setSelectedImage(null)} className="p-2.5 bg-red-50 text-red-500 rounded-xl hover:bg-red-100 transition-all" title="삭제">
                  <X size={20} />
                </button>
              )}
              <button onClick={handleSaveAsPDF} disabled={isExporting} className="p-2.5 bg-blue-50 text-blue-600 rounded-xl hover:bg-blue-100 transition-all" title="PDF 저장">
                <Download size={20} />
              </button>
              <button onClick={handlePrint} className="px-5 py-2.5 bg-pink-500 text-white font-black rounded-xl hover:bg-pink-600 shadow-lg active:scale-95 transition-all flex items-center gap-2 text-sm">
                <Printer size={18} />
                프린트
              </button>
            </div>
          </div>
        </div>

        {/* Child Info Inputs */}
        <div className="flex flex-wrap gap-4 pt-4 border-t border-gray-100 items-center justify-center lg:justify-start">
          <div className="flex items-center gap-2 bg-gray-50 px-4 py-2 rounded-xl border border-gray-100">
            <User size={16} className="text-gray-400" />
            <span className="text-xs font-bold text-gray-500 whitespace-nowrap">이름:</span>
            <input 
              type="text" 
              value={childName} 
              onChange={(e) => setChildName(e.target.value)} 
              placeholder="아이 이름 입력" 
              className="bg-transparent text-sm font-bold text-gray-700 focus:outline-none w-28 placeholder-gray-300"
            />
          </div>
          <div className="flex items-center gap-2 bg-gray-50 px-4 py-2 rounded-xl border border-gray-100">
            <Calendar size={16} className="text-gray-400" />
            <span className="text-xs font-bold text-gray-500 whitespace-nowrap">날짜:</span>
            <input 
              type="date" 
              value={date} 
              onChange={(e) => setDate(e.target.value)} 
              className="bg-transparent text-sm font-bold text-gray-700 focus:outline-none w-32 cursor-pointer"
            />
          </div>
          <div className="hidden lg:block text-[11px] text-gray-400 italic ml-auto font-medium">
             입력된 이름과 날짜는 학습지 상단에 자동으로 표시됩니다.
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="w-full flex flex-col items-center gap-6">
        {groundingLinks.length > 0 && (
          <div className="no-print w-full max-w-4xl bg-indigo-50 border border-indigo-100 p-4 rounded-2xl flex flex-col gap-3 shadow-sm">
            <h3 className="text-xs font-black text-indigo-500 uppercase tracking-wider flex items-center gap-2">
              <Search size={14} /> '{inputText}' 도안 출처
            </h3>
            <div className="flex flex-wrap gap-2">
              {groundingLinks.map((link, i) => (
                <a key={i} href={link.uri} target="_blank" rel="noopener noreferrer" className="bg-white px-3 py-1.5 rounded-lg text-xs font-bold text-indigo-600 border border-indigo-200 hover:bg-indigo-600 hover:text-white transition-all flex items-center gap-1">
                  {link.title} <ExternalLink size={12} />
                </a>
              ))}
            </div>
            <p className="text-[10px] text-indigo-400 font-bold flex items-center gap-2">
              <ClipboardCheck size={14} className="text-green-500" />
              이미지를 마우스 우클릭으로 복사한 뒤, 여기에 바로 붙여넣기(Ctrl+V) 하세요!
            </p>
          </div>
        )}
        
        <div className="w-full flex justify-center">
          <SlideGenerator 
            text={inputText} 
            imageUrl={selectedImage} 
            childName={childName}
            date={date}
            slideRef={slideRef} 
            isExporting={isExporting} 
          />
        </div>
      </main>

      {/* Loading Overlay */}
      {(isExporting || isSearching) && (
        <div className="fixed inset-0 bg-white/60 backdrop-blur-sm z-50 flex items-center justify-center no-print">
          <div className="text-center bg-white p-10 rounded-3xl shadow-2xl border-4 border-pink-100 animate-in fade-in zoom-in duration-300">
            <div className="relative w-20 h-20 mx-auto mb-6 flex items-center justify-center">
              <div className="absolute inset-0 rounded-full border-4 border-pink-100"></div>
              <div className="absolute inset-0 rounded-full border-4 border-pink-500 border-t-transparent animate-spin"></div>
              <div className="text-pink-500">
                {isExporting ? <Download size={32} /> : <Search size={32} />}
              </div>
            </div>
            <p className="text-xl font-black text-gray-800">
              {isExporting ? "PDF 저장 준비 중..." : `${inputText} 도안 검색 중...`}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
