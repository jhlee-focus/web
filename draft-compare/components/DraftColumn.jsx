// DraftColumn — one draft column with paragraph cards
const { useState: useStateDC, useRef: useRefDC, useEffect: useEffectDC } = React;

function DraftColumn({
  index, draft, onUpdateContent, onUpdateTitle, onDeleteParagraph,
  onAddParagraph, onAddAll, onRemoveAll, onDeactivate, isConfirmingDeactivate,
  reflectedIds, dismissedIds,
  onToggleDismiss, colorClass,
}) {
  const [isPreview, setIsPreview] = useStateDC(false);
  const [isInputtingRaw, setIsInputtingRaw] = useStateDC(false);
  const [rawText, setRawText] = useStateDC('');
  const [isFileDragOver, setIsFileDragOver] = useStateDC(false);
  const fileInputRef = useRefDC(null);
  const rawInputRef = useRefDC(null);

  useEffectDC(() => {
    if (isInputtingRaw && rawInputRef.current) rawInputRef.current.focus();
  }, [isInputtingRaw]);

  const handleDragStart = (e, p) => {
    e.dataTransfer.setData('application/json', JSON.stringify({ type: 'new-paragraph', paragraph: p }));
    e.dataTransfer.effectAllowed = 'copy';
  };
  const handleStartInput = () => {
    const currentText = draft.paragraphs.map((p) => p.text).join('\n\n');
    setRawText(currentText);
    setIsInputtingRaw(true);
  };
  const handleFinishInput = () => {
    // fileName: undefined → App에서 기존 파일명 유지 (수동 편집 시 뱃지 보존)
    if (rawText.trim() !== '') onUpdateContent(rawText, undefined);
    setIsInputtingRaw(false);
  };
  const handlePaste = async () => {
    if (!isInputtingRaw) {
      handleStartInput();
      setTimeout(async () => {
        try {
          if (navigator.clipboard && navigator.clipboard.readText) {
            const text = await navigator.clipboard.readText();
            if (text) setRawText((prev) => (prev ? prev + '\n' + text : text));
          }
        } catch {}
      }, 50);
    }
  };
  const readFileIntoDraft = (file) => {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result;
      onUpdateContent(text, file.name);
      setIsInputtingRaw(false);
    };
    reader.readAsText(file);
  };
  const handleFileUpload = (e) => { readFileIntoDraft(e.target.files?.[0]); };

  const handleColumnDragOver = (e) => {
    if (e.dataTransfer.types && Array.from(e.dataTransfer.types).includes('Files')) {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'copy';
      setIsFileDragOver(true);
    }
  };
  const handleColumnDragLeave = (e) => {
    // only reset when leaving the column boundary
    if (e.currentTarget.contains(e.relatedTarget)) return;
    setIsFileDragOver(false);
  };
  const handleColumnDrop = (e) => {
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      // Accept text-ish files by extension or mime
      const ok = /\.(md|markdown|txt)$/i.test(file.name) || file.type.startsWith('text/') || file.type === '';
      if (ok) {
        e.preventDefault();
        readFileIntoDraft(file);
      }
    }
    setIsFileDragOver(false);
  };

  const I = window.Icon;

  return (
    <div
      onDragOver={handleColumnDragOver}
      onDragLeave={handleColumnDragLeave}
      onDrop={handleColumnDrop}
      className={`relative h-full flex flex-col rounded-xl border shadow-sm ${colorClass} overflow-hidden transition-all duration-300 ${isFileDragOver ? 'ring-2 ring-indigo-400 ring-offset-2' : ''}`}>
      {isFileDragOver && (
        <div className="pointer-events-none absolute inset-0 z-40 bg-indigo-50/80 backdrop-blur-[1px] flex flex-col items-center justify-center text-indigo-600 border-2 border-dashed border-indigo-400 rounded-xl">
          <I.Upload size={28} />
          <p className="mt-2 text-sm font-bold">파일을 놓아 이 초안에 로드</p>
          <p className="text-[11px] text-indigo-500 mt-1">.md / .markdown / .txt</p>
        </div>
      )}
      <div className="px-4 py-3 border-b flex flex-col gap-2 bg-white/60 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 min-w-0 flex-1">
            <span className="font-bold text-slate-400 whitespace-nowrap text-sm">{draft.title}:</span>
            <input
              type="text"
              value={draft.customTitle || ''}
              onChange={(e) => onUpdateTitle(e.target.value)}
              placeholder="별칭 입력..."
              className="bg-transparent border-none outline-none font-bold text-slate-700 text-sm placeholder:text-slate-300 placeholder:font-normal focus:bg-white/50 px-1.5 py-0.5 rounded transition-all min-w-0 flex-1"
            />
          </div>
          <div className="flex items-center gap-2 shrink-0 ml-2">
            <button type="button" onClick={handleStartInput}
              className={`p-1.5 rounded-md transition-all ${isInputtingRaw ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-indigo-600 hover:bg-white'}`}
              title="전체 텍스트 편집/입력">
              <I.Edit size={14} />
            </button>
            <div className="flex p-0.5 bg-slate-100 rounded-lg border border-slate-200">
              <button type="button" onClick={() => setIsPreview(false)}
                className={`px-2 py-1 rounded-md text-[10px] font-bold transition-all ${!isPreview ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-400 hover:text-slate-600'}`}>원본</button>
              <button type="button" onClick={() => setIsPreview(true)}
                className={`px-2 py-1 rounded-md text-[10px] font-bold transition-all ${isPreview ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-400 hover:text-slate-600'}`}>미리보기</button>
            </div>
            {onDeactivate && (
              <button type="button" onClick={onDeactivate}
                className={`p-1.5 rounded-md transition-all ${
                  isConfirmingDeactivate
                    ? 'bg-red-500 text-white shadow-sm animate-pulse'
                    : 'text-slate-400 hover:text-rose-600 hover:bg-rose-50'
                }`}
                title={isConfirmingDeactivate ? '한 번 더 누르면 초안 비우기' : '이 초안 숨기기 (한 번 더 눌러야 내용 초기화)'}
                aria-label={isConfirmingDeactivate ? '확인: 초안 숨기기' : '초안 숨기기'}>
                {isConfirmingDeactivate ? <I.Trash size={14} /> : <I.X size={14} />}
              </button>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-1.5">
          <div className="flex gap-1">
            <button type="button" onClick={handlePaste}
              className="flex-1 flex items-center justify-center gap-1.5 py-1.5 bg-white border border-slate-200 rounded-md text-[11px] font-medium text-slate-600 hover:bg-indigo-50 hover:text-indigo-600 transition-all shadow-sm active:scale-95">
              <I.Clipboard size={12} /> 붙여넣기
            </button>
            <button type="button" onClick={() => fileInputRef.current?.click()}
              className="flex-1 flex items-center justify-center gap-1.5 py-1.5 bg-white border border-slate-200 rounded-md text-[11px] font-medium text-slate-600 hover:bg-indigo-50 hover:text-indigo-600 transition-all shadow-sm active:scale-95">
              <I.Upload size={12} /> 파일
            </button>
            <input type="file" ref={fileInputRef} className="hidden" accept=".txt,.md" onChange={handleFileUpload} />
          </div>

          <div className="flex gap-1">
            <button type="button" onClick={onAddAll} disabled={draft.paragraphs.length === 0}
              className="flex-1 flex items-center justify-center gap-1.5 py-1.5 bg-indigo-50 border border-indigo-100 rounded-md text-[10px] font-bold text-indigo-700 hover:bg-indigo-100 transition-all active:scale-95 disabled:opacity-50">
              <I.ListPlus size={12} /> 모두 선택
            </button>
            <button type="button" onClick={onRemoveAll} disabled={draft.paragraphs.length === 0}
              className="flex-1 flex items-center justify-center gap-1.5 py-1.5 bg-rose-50 border border-rose-100 rounded-md text-[10px] font-bold text-rose-700 hover:bg-rose-100 transition-all active:scale-95 disabled:opacity-50">
              <I.ListX size={12} /> 모두 해제
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar relative">
        {isInputtingRaw ? (
          <div className="h-full flex flex-col gap-3">
            <textarea
              ref={rawInputRef}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder="여기에 원고를 직접 입력하거나 붙여넣으세요..."
              className="flex-1 w-full p-4 text-sm bg-white border border-indigo-200 rounded-xl outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 resize-none font-sans leading-relaxed text-slate-700 shadow-inner" />
            <button type="button" onClick={handleFinishInput}
              className="w-full flex items-center justify-center gap-2 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-bold shadow-lg transition-all active:scale-95">
              <I.Save size={16} /> 입력 완료 및 분석
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {draft.fileName && (
              <div className="bg-indigo-50/50 border border-indigo-100 rounded-lg p-3 flex items-center gap-2 shadow-sm">
                <I.FileText size={16} />
                <div className="flex flex-col min-w-0">
                  <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-tighter leading-none mb-0.5">불러온 파일</span>
                  <span className="text-xs font-bold text-indigo-700 truncate">{draft.fileName}</span>
                </div>
              </div>
            )}
            {draft.paragraphs.length === 0 && !draft.fileName && (
              <div className="flex flex-col items-center justify-center py-14 text-center text-slate-400">
                <I.FileText size={28} />
                <p className="mt-2 text-xs">붙여넣기 / 파일 / 편집 버튼으로<br/>원고를 추가하세요</p>
              </div>
            )}
            {draft.paragraphs.map((p) => {
              const isReflected = reflectedIds.has(p.id);
              const isBlind = dismissedIds.has(p.id);
              const coord = `${(p.sourceDraftIndex ?? 0) + 1}-${(p.sourceParaIndex ?? 0) + 1}`;
              return (
                <div key={p.id}
                  draggable={!isBlind}
                  onDragStart={(e) => handleDragStart(e, p)}
                  onClick={() => { if (!isBlind && !isReflected) onAddParagraph(p); }}
                  title={isReflected ? '이미 최종 원고에 반영됨 (드래그로만 추가/이동)' : (isBlind ? '블라인드 처리됨' : '클릭하여 최종 원고에 추가')}
                  className={`group relative bg-white p-4 pt-7 rounded-lg border shadow-sm transition-all duration-300
                    ${isBlind ? 'opacity-30 grayscale' : (isReflected ? 'cursor-default' : 'cursor-pointer hover:border-indigo-400 hover:ring-2 hover:ring-indigo-100')}
                    ${isReflected ? 'border-emerald-300 ring-1 ring-emerald-50 bg-emerald-50/10' : 'border-slate-200'}`}>
                  <div className="absolute top-2 left-2 px-1.5 py-0.5 bg-slate-100 text-slate-500 text-[10px] font-bold rounded border border-slate-200">{coord}</div>
                  <div className="absolute top-2 right-2 flex items-center gap-1 z-20">
                    {isReflected && (
                      <div className="flex items-center gap-1 px-1.5 py-0.5 bg-emerald-100 text-emerald-700 text-[10px] font-bold rounded border border-emerald-200">
                        <I.Check size={10} /> 반영됨
                      </div>
                    )}
                    <button type="button"
                      onClick={(e) => { e.preventDefault(); e.stopPropagation(); onDeleteParagraph(p.id); }}
                      className="p-1 rounded text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                      title="단락 삭제">
                      <I.X size={14} />
                    </button>
                    <button type="button"
                      onClick={(e) => { e.preventDefault(); e.stopPropagation(); onToggleDismiss(p.id); }}
                      className={`p-1 rounded hover:bg-slate-100 transition-colors ${isBlind ? 'text-indigo-600' : 'text-slate-400 hover:text-indigo-600'}`}
                      title={isBlind ? '블라인드 해제' : '블라인드 처리'}>
                      {isBlind ? <I.EyeOff size={14} /> : <I.Eye size={14} />}
                    </button>
                  </div>
                  <div className="text-sm text-slate-700 leading-relaxed">
                    {isPreview ? (
                      React.createElement(window.MarkdownRenderer, { content: p.text })
                    ) : (
                      <p className="whitespace-pre-wrap pointer-events-none">{p.text}</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

window.DraftColumn = DraftColumn;
