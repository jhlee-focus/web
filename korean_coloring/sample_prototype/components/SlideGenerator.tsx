
import React from 'react';
// Added Heart to the imports from lucide-react
import { Clipboard, User, Calendar, Heart } from 'lucide-react';

interface SlideGeneratorProps {
  text: string;
  imageUrl: string | null;
  childName?: string;
  date?: string;
  slideRef?: React.RefObject<HTMLDivElement | null>;
  isExporting?: boolean;
}

const SlideGenerator: React.FC<SlideGeneratorProps> = ({ 
  text, 
  imageUrl, 
  childName = '', 
  date = '', 
  slideRef, 
  isExporting = false 
}) => {
  const characters = text.split('');
  const columnCount = characters.length || 1;

  const rows = [
    { weight: 'font-[900]', label: 'Black' },
    { weight: 'font-[700]', label: 'Bold' },
    { weight: 'font-[400]', label: 'Regular' }
  ];

  const cellHeight = "h-[45mm]";
  const fontSize = "text-[100px]"; 

  return (
    <div 
      ref={slideRef}
      className="slide-container border border-gray-200 shadow-2xl relative flex overflow-hidden w-full max-w-[1122px] bg-white rounded-xl"
    >
      {/* Left Half: Image & Header Info Section */}
      <div className="w-1/2 h-full border-r border-gray-200 flex flex-col p-6 overflow-hidden relative">
        {/* Child Info Area (Name / Date) */}
        <div className="flex justify-between items-center mb-6 px-4">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 border-b-2 border-pink-100 pb-1 min-w-[120px]">
              <User size={18} className="text-pink-300" />
              <span className="text-sm font-black text-pink-400 mr-2">이름:</span>
              <span className="text-lg font-black text-gray-700">
                {childName || <span className="text-gray-100">________________</span>}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 border-b-2 border-pink-100 pb-1 min-w-[140px]">
              <Calendar size={18} className="text-pink-300" />
              <span className="text-sm font-black text-pink-400 mr-2">날짜:</span>
              <span className="text-lg font-black text-gray-700 font-mono">
                {date || <span className="text-gray-100">____ / __ / __</span>}
              </span>
            </div>
          </div>
        </div>

        {/* Main Content Area (Image Slot) */}
        <div className="flex-1 flex items-center justify-center relative p-6">
          {imageUrl ? (
            <img 
              src={imageUrl} 
              alt="Worksheet target" 
              crossOrigin="anonymous"
              className="max-w-full max-h-[160mm] object-contain pointer-events-none transition-all"
            />
          ) : (
            <div className="flex flex-col items-center gap-4 text-gray-100 select-none no-print">
              <div className="rotate-[-10deg] border-4 border-dashed border-gray-50 p-12 rounded-[50px] text-center">
                 <Clipboard size={72} className="mx-auto mb-6 opacity-30" />
                 <p className="font-black text-4xl">도안을 찾거나</p>
                 <p className="font-black text-4xl mt-2">여기에 붙여넣기!</p>
              </div>
              <span className="text-xs font-bold text-gray-200 uppercase tracking-[0.2em] mt-4">(Ctrl + V)</span>
            </div>
          )}
        </div>
        
        {/* Bottom Labeling Area (Optional/Aesthetic) */}
        <div className="absolute bottom-6 left-10 opacity-30">
          <div className="flex items-center gap-2 text-pink-200">
             {/* Fix: Heart icon is now imported correctly */}
             <Heart size={16} fill="currentColor" />
             <span className="text-[10px] font-black uppercase tracking-widest">I-JOA Hangeul Play</span>
          </div>
        </div>
      </div>

      {/* Right Half: Writing Practice Section */}
      <div className="w-1/2 h-full flex items-center justify-center p-8 bg-[#fafafa]">
        <div 
          className="w-full border-t border-l border-black grid overflow-hidden bg-white shadow-md rounded-sm"
          style={{ gridTemplateColumns: `repeat(${columnCount}, minmax(0, 1fr))` }}
        >
          {rows.map((row, rowIndex) => (
            <React.Fragment key={`row-${rowIndex}`}>
              {characters.length > 0 ? (
                characters.map((char, charIndex) => (
                  <div 
                    key={`${rowIndex}-${charIndex}`}
                    className={`
                      ${cellHeight}
                      flex items-center justify-center 
                      border-r border-b border-black text-center select-none overflow-hidden
                    `}
                  >
                    <div className="flex items-center justify-center w-full h-full pointer-events-none relative">
                      <span className={`
                        outline-text leading-none inline-block 
                        ${row.weight} ${fontSize} 
                        transform
                        ${isExporting ? '-translate-y-10' : 'translate-y-0'}
                      `}>
                        {char}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className={`${cellHeight} border-r border-b border-black`}></div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Center fold guide */}
      <div className="absolute left-1/2 top-0 bottom-0 w-[1px] bg-gray-100 no-print pointer-events-none"></div>
    </div>
  );
};

export default SlideGenerator;
