// FinalColumn — the integration / final manuscript area
const { useState: useStateFC, useRef: useRefFC, useEffect: useEffectFC } = React;

function EditableParagraph({ p, index, onRemove, onUpdateText }) {
  const textareaRef = useRefFC(null);
  const [isEditing, setIsEditing] = useStateFC(false);
  const I = window.Icon;
  const MR = window.MarkdownRenderer;

  const imageData = (() => {
    const m = (p.text || '').trim().match(/^!\[(.*?)\]\((data:image\/[^)]+)\)$/s);
    if (m) return { alt: m[1], src: m[2] };
    return null;
  })();

  const autosize = (el) => {
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
  };

  useEffectFC(() => {
    if (isEditing && textareaRef.current) {
      autosize(textareaRef.current);
      textareaRef.current.focus();
    }
  }, [isEditing]);

  useEffectFC(() => {
    if (isEditing) autosize(textareaRef.current);
  }, [p.text, isEditing]);

  const handleDragStart = (e) => {
    if (isEditing) return;
    e.dataTransfer.setData('application/json', JSON.stringify({ type: 'reorder-paragraph', index, id: p.id }));
  };

  const coord = p.sourceDraftIndex !== undefined && p.sourceParaIndex !== undefined
    ? `${p.sourceDraftIndex + 1}-${p.sourceParaIndex + 1}` : null;

  const coordClass = !coord ? ''
    : p.sourceDraftIndex === 0 ? 'bg-blue-100 text-blue-700 border-blue-200'
    : p.sourceDraftIndex === 1 ? 'bg-emerald-100 text-emerald-700 border-emerald-200'
    : 'bg-amber-100 text-amber-700 border-amber-200';

  return (
    <div
      className={`flex gap-3 lg:gap-4 group bg-white p-4 lg:p-5 pt-8 lg:pt-9 rounded-xl border shadow-sm transition-all relative overflow-hidden
        ${isEditing ? 'ring-2 ring-indigo-100 border-indigo-400' : 'hover:border-indigo-300 border-slate-200 cursor-text'}`}
      onClick={() => !isEditing && setIsEditing(true)}
    >
      {coord && (
        <div className={`absolute top-2 left-2 px-2 py-0.5 rounded text-[10px] font-bold border z-20 ${coordClass}`}>{coord}</div>
      )}
      <div
        draggable={!isEditing}
        onDragStart={handleDragStart}
        className={`flex flex-col items-center gap-2 mt-1 shrink-0 ${isEditing ? 'opacity-30' : 'cursor-grab active:cursor-grabbing'}`}
      >
        {!isEditing && <I.Grip size={18} />}
      </div>
      <div className="flex-1 min-w-0">
        {imageData ? (
          <img src={imageData.src} alt={imageData.alt} className="w-full h-auto rounded-lg border border-slate-200" />
        ) : isEditing ? (
          <textarea
            ref={textareaRef}
            className="w-full text-slate-800 leading-relaxed text-sm lg:text-base bg-transparent border-none outline-none resize-none overflow-hidden p-0 font-sans"
            value={p.text}
            onChange={(e) => onUpdateText(p.id, e.target.value)}
            onBlur={() => setIsEditing(false)}
          />
        ) : (
          <div className="text-slate-800 leading-relaxed text-sm lg:text-base pointer-events-none">
            {React.createElement(MR, { content: p.text })}
          </div>
        )}
      </div>
      <div className="flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-all h-fit shrink-0 relative z-30">
        <button type="button"
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); onRemove(p.id); }}
          className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all">
          <I.X size={16} />
        </button>
        {!isEditing ? (
          <button type="button" onClick={(e) => { e.stopPropagation(); setIsEditing(true); }}
            className="p-1.5 text-slate-400 hover:text-indigo-500 hover:bg-indigo-50 rounded-lg transition-all">
            <I.Edit size={16} />
          </button>
        ) : (
          <button type="button" onClick={(e) => { e.stopPropagation(); setIsEditing(false); }}
            className="p-1.5 bg-indigo-500 text-white hover:bg-indigo-600 rounded-lg shadow-sm transition-all">
            <I.Check size={16} />
          </button>
        )}
      </div>
    </div>
  );
}

function FinalColumn({ paragraphs, onRemove, onReorder, onUpdateText, onAddNew, onClear }) {
  const [dropIndicator, setDropIndicator] = useStateFC({ index: -1, position: null });
  const [isGroupedView, setIsGroupedView] = useStateFC(false);
  const [isClearConfirm, setIsClearConfirm] = useStateFC(false);
  const imageInputRef = useRefFC(null);
  const I = window.Icon;
  const MR = window.MarkdownRenderer;

  useEffectFC(() => {
    if (paragraphs.length === 0) setIsClearConfirm(false);
    if (isClearConfirm) {
      const t = setTimeout(() => setIsClearConfirm(false), 3000);
      return () => clearTimeout(t);
    }
  }, [isClearConfirm, paragraphs.length]);

  const makeId = (prefix) => {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) return `${prefix}-${crypto.randomUUID()}`;
    return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
  };

  const handleImageFiles = async (files, atIndex) => {
    const imageFiles = Array.from(files).filter((f) => f.type.startsWith('image/'));
    if (imageFiles.length === 0) return;
    // 모든 파일을 병렬로 읽어 순서를 보존하며 atIndex부터 차례로 삽입
    const readAsDataURL = (file) => new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (ev) => resolve({ name: file.name, data: ev.target?.result });
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
    try {
      const results = await Promise.all(imageFiles.map(readAsDataURL));
      results.forEach((r, i) => {
        const newPara = { id: makeId('img'), text: `![${r.name}](${r.data})` };
        onAddNew(newPara, atIndex === undefined ? undefined : atIndex + i);
      });
    } catch (err) {
      console.error('image read failed', err);
    }
  };

  const handleDragOver = (e, index) => {
    e.preventDefault();
    if (isGroupedView) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const mid = rect.top + rect.height / 2;
    setDropIndicator({ index, position: e.clientY < mid ? 'top' : 'bottom' });
  };
  const handleDragLeave = () => setDropIndicator({ index: -1, position: null });
  const handleDrop = (e, dropIndex) => {
    e.preventDefault();
    if (isGroupedView) return;
    const dataStr = e.dataTransfer.getData('application/json');
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleImageFiles(files, dropIndicator.position === 'bottom' ? dropIndex + 1 : dropIndex);
      setDropIndicator({ index: -1, position: null });
      return;
    }
    if (!dataStr) return;
    const data = JSON.parse(dataStr);
    const finalIndex = dropIndicator.position === 'bottom' ? dropIndex + 1 : dropIndex;
    if (data.type === 'new-paragraph') onAddNew(data.paragraph, finalIndex);
    else if (data.type === 'reorder-paragraph') {
      const sourceIndex = data.index;
      if (sourceIndex !== finalIndex && sourceIndex !== finalIndex - 1) {
        const target = sourceIndex < finalIndex ? finalIndex - 1 : finalIndex;
        onReorder(sourceIndex, target);
      }
    }
    setDropIndicator({ index: -1, position: null });
  };
  const handleMainDrop = (e) => {
    if (isGroupedView) return;
    if (dropIndicator.index === -1) {
      const files = e.dataTransfer.files;
      if (files && files.length > 0) { handleImageFiles(files, paragraphs.length); return; }
      const dataStr = e.dataTransfer.getData('application/json');
      if (!dataStr) return;
      const data = JSON.parse(dataStr);
      if (data.type === 'new-paragraph') onAddNew(data.paragraph, paragraphs.length);
    }
  };
  const handleClearClick = (e) => {
    e.stopPropagation();
    if (isClearConfirm) { onClear(); setIsClearConfirm(false); } else setIsClearConfirm(true);
  };

  const fullCombined = paragraphs.map((p) => p.text).join('\n\n');

  return (
    <div className="h-full flex flex-col rounded-xl border border-indigo-200 bg-white shadow-lg overflow-hidden"
      onDragOver={(e) => e.preventDefault()} onDrop={handleMainDrop}>
      <div className="px-6 py-4 border-b border-indigo-100 bg-indigo-50/50 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-indigo-600 animate-pulse"></div>
          <h3 className="font-bold text-indigo-900">최종 원고 (통합 영역)</h3>
          <span className="text-xs text-indigo-400 font-medium ml-1">{paragraphs.length}단락</span>
        </div>
        <div className="flex items-center gap-2">
          <button type="button" onClick={() => setIsGroupedView(!isGroupedView)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shadow-sm active:scale-95 border ${
              isGroupedView ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-indigo-600 border-indigo-200 hover:bg-indigo-50'}`}>
            {isGroupedView ? <I.LayoutList size={14} /> : <I.FileText size={14} />}
            {isGroupedView ? '단락으로 보기' : '묶어보기'}
          </button>
          <div className="w-px h-6 bg-indigo-200 mx-1"></div>
          <input type="file" ref={imageInputRef} className="hidden" accept="image/*"
            onChange={(e) => e.target.files && handleImageFiles(e.target.files, paragraphs.length)} />
          <button type="button" onClick={() => imageInputRef.current?.click()}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-indigo-200 rounded-lg text-xs font-bold text-indigo-600 hover:bg-indigo-50 transition-all shadow-sm active:scale-95">
            <I.Image size={14} /> 이미지 추가
          </button>
          <div className="w-px h-6 bg-indigo-200 mx-1"></div>
          <button type="button" onClick={handleClearClick} disabled={paragraphs.length === 0}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all shadow-sm active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed border min-w-[85px] justify-center ${
              isClearConfirm ? 'bg-red-500 text-white border-red-600 animate-pulse'
              : 'bg-white text-slate-400 border-slate-200 hover:text-red-500 hover:border-red-100'}`}
            title={isClearConfirm ? '한 번 더 눌러서 삭제' : '전체 삭제'}>
            <I.Trash size={14} />
            <span className="text-[10px] font-bold whitespace-nowrap">
              {isClearConfirm ? '정말 삭제?' : '전체 삭제'}
            </span>
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 lg:p-6 custom-scrollbar bg-slate-50/30">
        <div className="max-w-3xl mx-auto min-h-full pb-20">
          {isGroupedView ? (
            <div className="bg-white p-8 lg:p-12 rounded-2xl border border-slate-200 shadow-sm">
              <div className="text-slate-800 leading-relaxed text-sm lg:text-base">
                {React.createElement(MR, { content: fullCombined || '*원고가 비어있습니다.*' })}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {paragraphs.map((p, index) => (
                <div key={p.id}
                  onDragOver={(e) => handleDragOver(e, index)}
                  onDragLeave={handleDragLeave}
                  onDrop={(e) => handleDrop(e, index)}
                  className="relative">
                  {dropIndicator.index === index && dropIndicator.position === 'top' && (
                    <div className="absolute -top-2 left-0 right-0 h-1 bg-indigo-500 rounded-full z-10 animate-pulse" />
                  )}
                  <EditableParagraph p={p} index={index} onRemove={onRemove} onUpdateText={onUpdateText} />
                  {dropIndicator.index === index && dropIndicator.position === 'bottom' && (
                    <div className="absolute -bottom-2 left-0 right-0 h-1 bg-indigo-500 rounded-full z-10 animate-pulse" />
                  )}
                </div>
              ))}
              {paragraphs.length === 0 && (
                <div className="flex flex-col items-center justify-center py-20 px-10 text-center border-2 border-dashed border-slate-200 rounded-2xl bg-slate-50"
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => {
                    e.preventDefault();
                    const dataStr = e.dataTransfer.getData('application/json');
                    if (dataStr) {
                      const data = JSON.parse(dataStr);
                      if (data.type === 'new-paragraph') onAddNew(data.paragraph, 0);
                    } else if (e.dataTransfer.files.length > 0) {
                      handleImageFiles(e.dataTransfer.files, 0);
                    }
                  }}>
                  <div className="bg-indigo-100 text-indigo-500 p-4 rounded-full mb-4">
                    <I.Plus size={28} />
                  </div>
                  <h4 className="text-slate-700 font-semibold mb-2">통합할 준비가 되었습니다</h4>
                  <p className="text-slate-500 text-sm leading-relaxed">
                    왼쪽 초안의 단락을 클릭하거나 드래그하여 이곳에 배치하세요.<br/>
                    이미지 파일을 드롭해 삽입할 수도 있습니다.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

window.FinalColumn = FinalColumn;
