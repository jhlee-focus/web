// App — top-level state, persistence, layout
const { useState: useStateApp, useCallback, useMemo, useRef: useRefApp, useEffect: useEffectApp } = React;

const STORAGE_KEY = 'md-draft-compare-v1';

const newId = (prefix = 'id') => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) return `${prefix}-${crypto.randomUUID()}`;
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
};

function App() {
  const I = window.Icon;

  const loadInitial = () => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try { return JSON.parse(saved); } catch {}
    }
    return null;
  };
  const initial = loadInitial();

  const migrateDrafts = (raw) => {
    const defaults = [
      { id: 1, title: '초안 1', customTitle: '', paragraphs: [], active: true },
      { id: 2, title: '초안 2', customTitle: '', paragraphs: [], active: false },
      { id: 3, title: '초안 3', customTitle: '', paragraphs: [], active: false },
    ];
    if (!raw) return defaults;
    return defaults.map((def, i) => {
      const d = raw[i];
      if (!d) return def;
      return {
        ...def,
        ...d,
        active: typeof d.active === 'boolean'
          ? d.active
          : (d.paragraphs && d.paragraphs.length > 0) || i === 0,
      };
    });
  };
  const [drafts, setDrafts] = useStateApp(migrateDrafts(initial?.drafts));
  const [finalParagraphs, setFinalParagraphs] = useStateApp(initial?.finalParagraphs || []);
  const [dismissedParagraphIds, setDismissedParagraphIds] = useStateApp(
    new Set(initial?.dismissedParagraphIds || [])
  );
  const [saveStatus, setSaveStatus] = useStateApp('saved'); // 'saved' | 'saving' | 'error'
  const [saveError, setSaveError] = useStateApp('');
  const [confirmDeactivateIdx, setConfirmDeactivateIdx] = useStateApp(-1);
  const globalFileInputRef = useRefApp(null);

  useEffectApp(() => {
    const saved = localStorage.getItem('md-draft-font-size');
    if (saved) document.documentElement.style.fontSize = saved + 'px';
  }, []);

  useEffectApp(() => {
    setSaveStatus('saving');
    const t = setTimeout(() => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
          drafts, finalParagraphs,
          dismissedParagraphIds: Array.from(dismissedParagraphIds),
        }));
        setSaveStatus('saved');
        setSaveError('');
      } catch (err) {
        // QuotaExceededError 등 — 인라인 base64 이미지가 누적되면 5MB 한도 초과
        setSaveStatus('error');
        setSaveError(err && err.name === 'QuotaExceededError'
          ? '저장 용량 초과 — 큰 이미지를 제거하거나 내보낸 후 정리하세요.'
          : '저장 실패: ' + (err && err.message ? err.message : 'unknown'));
        console.error('localStorage save failed', err);
      }
    }, 500);
    return () => clearTimeout(t);
  }, [drafts, finalParagraphs, dismissedParagraphIds]);

  useEffectApp(() => {
    if (confirmDeactivateIdx === -1) return;
    const t = setTimeout(() => setConfirmDeactivateIdx(-1), 3000);
    return () => clearTimeout(t);
  }, [confirmDeactivateIdx]);

  const parseTextToParagraphs = (text, draftIndex) => {
    return (text || '')
      .split(/\n\s*\n+/)
      .map((p) => p.trim())
      .filter((p) => p !== '')
      .map((paraText, pIdx) => {
        const id = newId(`draft-${draftIndex}-${pIdx}`);
        return { id, text: paraText, sourceDraftIndex: draftIndex, sourceParaIndex: pIdx, originalId: id };
      });
  };

  const updateDraftContent = useCallback((idx, text, fileName) => {
    setDrafts((prev) => {
      const next = [...prev];
      // fileName: undefined이면 기존 값 유지 (수동 편집 시 파일명 보존)
      const nextFileName = fileName === undefined ? next[idx].fileName : fileName;
      next[idx] = { ...next[idx], fileName: nextFileName, paragraphs: parseTextToParagraphs(text, idx), active: true };
      return next;
    });
  }, []);

  const activateDraft = useCallback((idx) => {
    setDrafts((prev) => { const next = [...prev]; next[idx] = { ...next[idx], active: true }; return next; });
  }, []);
  const requestDeactivateDraft = useCallback((idx) => {
    setConfirmDeactivateIdx((cur) => (cur === idx ? -1 : idx));
  }, []);
  const deactivateDraft = useCallback((idx) => {
    // Deactivate and clear content + remove its paragraphs from final
    setDrafts((prev) => { const next = [...prev]; next[idx] = { ...next[idx], active: false, paragraphs: [], fileName: undefined, customTitle: '' }; return next; });
    setFinalParagraphs((prev) => prev.filter((p) => p.sourceDraftIndex !== idx));
    setConfirmDeactivateIdx(-1);
  }, []);
  const updateDraftTitle = useCallback((idx, newCustomTitle) => {
    setDrafts((prev) => { const next = [...prev]; next[idx] = { ...next[idx], customTitle: newCustomTitle }; return next; });
  }, []);
  const removeParagraphFromDraft = useCallback((draftIdx, paraId) => {
    setDrafts((prev) => prev.map((d, i) => i === draftIdx ? { ...d, paragraphs: d.paragraphs.filter((p) => p.id !== paraId) } : d));
  }, []);

  const handleGlobalFileUpload = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    const sorted = Array.from(files).sort((a, b) => a.name.localeCompare(b.name));
    const newDrafts = [...drafts];
    for (let i = 0; i < Math.min(sorted.length, 3); i++) {
      const file = sorted[i];
      const text = await file.text();
      newDrafts[i] = { ...newDrafts[i], fileName: file.name, paragraphs: parseTextToParagraphs(text, i), active: true };
    }
    setDrafts(newDrafts);
    if (globalFileInputRef.current) globalFileInputRef.current.value = '';
  };

  const addParagraphToFinal = useCallback((paragraph, atIndex) => {
    const originalId = paragraph.originalId || paragraph.id;
    setFinalParagraphs((prev) => {
      // 같은 originalId가 이미 final에 있으면 click 추가는 무시 (드래그-드랍은 atIndex 지정으로 인지된 의도이므로 허용)
      if (atIndex === undefined && originalId && prev.some((p) => p.originalId === originalId)) {
        return prev;
      }
      const newPara = { ...paragraph, id: newId('final'), originalId };
      if (atIndex !== undefined) { const next = [...prev]; next.splice(atIndex, 0, newPara); return next; }
      return [...prev, newPara];
    });
  }, []);

  const reflectedIds = useMemo(() => new Set(finalParagraphs.map((p) => p.originalId).filter(Boolean)), [finalParagraphs]);

  const addAllFromDraft = useCallback((draftIdx) => {
    const source = drafts[draftIdx];
    const toAdd = source.paragraphs.filter((p) => !reflectedIds.has(p.id));
    setFinalParagraphs((prev) => [
      ...prev,
      ...toAdd.map((p) => ({ ...p, id: newId('final'), originalId: p.id })),
    ]);
  }, [drafts, reflectedIds]);
  const removeAllFromDraft = useCallback((draftIdx) => {
    setFinalParagraphs((prev) => prev.filter((p) => p.sourceDraftIndex !== draftIdx));
  }, []);
  const removeParagraphFromFinal = useCallback((id) => setFinalParagraphs((prev) => prev.filter((p) => p.id !== id)), []);
  const updateFinalParagraphText = useCallback((id, newText) => setFinalParagraphs((prev) => prev.map((p) => p.id === id ? { ...p, text: newText } : p)), []);
  const moveParagraphInFinal = useCallback((dragIndex, hoverIndex) => {
    setFinalParagraphs((prev) => {
      const updated = [...prev];
      const [removed] = updated.splice(dragIndex, 1);
      updated.splice(hoverIndex, 0, removed);
      return updated;
    });
  }, []);
  const toggleDismissParagraph = useCallback((id) => {
    setDismissedParagraphIds((prev) => { const next = new Set(prev); if (next.has(id)) next.delete(id); else next.add(id); return next; });
  }, []);
  const clearFinal = useCallback(() => setFinalParagraphs([]), []);

  const exportText = () => {
    const full = finalParagraphs.map((p) => p.text).join('\n\n');
    const blob = new Blob([full], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'final_manuscript.md'; a.click();
    URL.revokeObjectURL(url);
  };

  const colorClasses = [
    'border-blue-200 bg-blue-50/30',
    'border-emerald-200 bg-emerald-50/30',
    'border-amber-200 bg-amber-50/30',
  ];

  const DraftColumn = window.DraftColumn;
  const FinalColumn = window.FinalColumn;

  return (
    <div className="h-screen flex flex-col bg-slate-50 overflow-hidden">
      <header className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between shrink-0 shadow-sm z-50">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-600 p-2 rounded-lg text-white">
            <I.Layers size={20} />
          </div>
          <div className="flex flex-col">
            <h1 className="text-lg font-bold text-slate-800 tracking-tight leading-tight">MD 초안 비교 <span className="text-indigo-600">워크스페이스</span></h1>
            <div className="flex items-center gap-1.5 text-[10px]" title={saveStatus === 'error' ? saveError : ''}>
              <span className={`w-1.5 h-1.5 rounded-full ${
                saveStatus === 'saved' ? 'bg-emerald-500'
                : saveStatus === 'error' ? 'bg-red-500'
                : 'bg-amber-500 animate-pulse'
              }`}></span>
              <span className={`font-medium uppercase tracking-wider ${saveStatus === 'error' ? 'text-red-600' : 'text-slate-400'}`}>
                {saveStatus === 'saved' ? '브라우저에 저장됨'
                  : saveStatus === 'error' ? '저장 실패'
                  : '저장 중...'}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center border border-slate-200 rounded-lg bg-white shadow-sm overflow-hidden">
            <button onClick={() => {
              const cur = parseFloat(document.documentElement.style.fontSize) || 14;
              const next = Math.max(11, cur - 1);
              document.documentElement.style.fontSize = next + 'px';
              localStorage.setItem('md-draft-font-size', String(next));
            }}
              className="px-2.5 py-2 text-slate-600 hover:bg-slate-50 active:scale-95 transition-all"
              title="글자 작게"
              aria-label="글자 작게">
              <span className="font-semibold text-xs">A−</span>
            </button>
            <div className="w-px h-5 bg-slate-200"></div>
            <button onClick={() => {
              document.documentElement.style.fontSize = '14px';
              localStorage.setItem('md-draft-font-size', '14');
            }}
              className="px-2.5 py-2 text-slate-500 hover:bg-slate-50 active:scale-95 transition-all text-[10px] font-semibold uppercase tracking-wider"
              title="기본 크기로 되돌리기">
              기본
            </button>
            <div className="w-px h-5 bg-slate-200"></div>
            <button onClick={() => {
              const cur = parseFloat(document.documentElement.style.fontSize) || 14;
              const next = Math.min(22, cur + 1);
              document.documentElement.style.fontSize = next + 'px';
              localStorage.setItem('md-draft-font-size', String(next));
            }}
              className="px-2.5 py-2 text-slate-600 hover:bg-slate-50 active:scale-95 transition-all"
              title="글자 크게"
              aria-label="글자 크게">
              <span className="font-semibold text-sm">A+</span>
            </button>
          </div>
          <div className="w-px h-6 bg-slate-200"></div>
          <input type="file" ref={globalFileInputRef} className="hidden" multiple accept=".txt,.md" onChange={handleGlobalFileUpload} />
          <button onClick={() => globalFileInputRef.current?.click()}
            className="flex items-center gap-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 px-4 py-2 rounded-lg text-sm font-semibold transition-all shadow-sm active:scale-95"
            title="여러 파일을 한 번에 불러와 초안들에 배정합니다">
            <span className="text-indigo-500"><I.FolderOpen size={16} /></span>
            전체 파일 불러오기
          </button>
          <div className="w-px h-6 bg-slate-200 mx-1"></div>
          <button onClick={exportText} disabled={finalParagraphs.length === 0}
            className="flex items-center gap-2 border border-slate-200 hover:bg-slate-50 text-slate-700 px-4 py-2 rounded-lg text-sm font-semibold transition-all active:scale-95 shadow-sm disabled:opacity-40 disabled:cursor-not-allowed">
            <I.Download size={16} /> 내보내기
          </button>
        </div>
      </header>

      <main className="flex-1 p-4 flex flex-col overflow-hidden">
        <div className="flex flex-1 gap-4 overflow-x-auto overflow-y-hidden pb-2 h-full">
          {drafts.map((draft, idx) => (
            draft.active ? (
              <div key={draft.id} className="min-w-[320px] flex-1 flex flex-col h-full">
                <DraftColumn
                  index={idx}
                  draft={draft}
                  onUpdateContent={(text, fileName) => updateDraftContent(idx, text, fileName)}
                  onUpdateTitle={(newTitle) => updateDraftTitle(idx, newTitle)}
                  onDeleteParagraph={(paraId) => removeParagraphFromDraft(idx, paraId)}
                  onAddParagraph={addParagraphToFinal}
                  onAddAll={() => addAllFromDraft(idx)}
                  onRemoveAll={() => removeAllFromDraft(idx)}
                  onDeactivate={() =>
                    confirmDeactivateIdx === idx ? deactivateDraft(idx) : requestDeactivateDraft(idx)
                  }
                  isConfirmingDeactivate={confirmDeactivateIdx === idx}
                  reflectedIds={reflectedIds}
                  dismissedIds={dismissedParagraphIds}
                  onToggleDismiss={toggleDismissParagraph}
                  colorClass={colorClasses[idx] || colorClasses[2]}
                />
              </div>
            ) : (
              <div key={draft.id} className="w-16 shrink-0 flex flex-col h-full">
                <button
                  type="button"
                  onClick={() => activateDraft(idx)}
                  title={`${draft.title} 추가`}
                  className={`group h-full w-full rounded-xl border-2 border-dashed ${colorClasses[idx] || colorClasses[2]} hover:border-indigo-400 hover:bg-indigo-50/40 transition-all flex flex-col items-center justify-center gap-3 text-slate-400 hover:text-indigo-600 active:scale-[0.98]`}
                >
                  <div className="bg-white border border-slate-200 group-hover:border-indigo-200 rounded-full p-2 shadow-sm">
                    <I.Plus size={18} />
                  </div>
                  <div className="flex flex-col items-center gap-1 text-[11px] font-bold tracking-wider text-slate-400 group-hover:text-indigo-600">
                    {`${draft.title} 추가`.split('').map((ch, i) => (
                      <span key={i}>{ch === ' ' ? '\u00a0' : ch}</span>
                    ))}
                  </div>
                </button>
              </div>
            )
          ))}
          <div className="min-w-[480px] flex-[2] flex flex-col h-full relative">
            <FinalColumn
              paragraphs={finalParagraphs}
              onRemove={removeParagraphFromFinal}
              onReorder={moveParagraphInFinal}
              onUpdateText={updateFinalParagraphText}
              onAddNew={addParagraphToFinal}
              onClear={clearFinal}
            />
          </div>
        </div>
      </main>

      {saveStatus === 'error' && (
        <div role="alert"
          className="fixed bottom-16 left-1/2 -translate-x-1/2 z-[60] bg-red-50 border border-red-200 text-red-800 px-4 py-2 rounded-lg shadow-lg text-xs font-semibold flex items-center gap-2 max-w-[90vw]">
          <span className="w-1.5 h-1.5 rounded-full bg-red-500"></span>
          <span>{saveError}</span>
        </div>
      )}

      <footer className="bg-white border-t border-slate-200 px-6 py-2 text-[10px] text-slate-400 text-center shrink-0">
        MD 초안 비교 워크스페이스 · 세 개의 마크다운 초안을 단락 단위로 비교하고 하나로 합성하세요
      </footer>

      {window.ThemePicker && React.createElement(window.ThemePicker)}
    </div>
  );
}

window.App = App;
