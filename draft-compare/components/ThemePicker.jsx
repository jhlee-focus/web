// ThemePicker — floating bottom-right control to switch body theme classes
const { useState: useStateTP, useEffect: useEffectTP } = React;

const THEMES = [
  { id: 'default', label: '기본', bodyClass: '' },
  { id: 'editorial', label: 'Editorial', bodyClass: 'themed theme-editorial' },
  { id: 'mono', label: 'Mono', bodyClass: 'themed theme-mono' },
  { id: 'hybrid', label: 'Hybrid', bodyClass: 'themed theme-hybrid' },
  { id: 'notion', label: 'Notion', bodyClass: 'themed theme-notion' },
  { id: 'terminal', label: 'Terminal', bodyClass: 'themed theme-terminal' },
  { id: 'blueprint', label: 'Blueprint', bodyClass: 'themed theme-blueprint' },
  { id: 'corkboard', label: 'Corkboard', bodyClass: 'themed theme-corkboard' },
  { id: 'canvas', label: 'Canvas', bodyClass: 'themed theme-canvas' },
];

const STORAGE_KEY_THEME = 'md-draft-theme-v1';

function ThemePicker() {
  const [active, setActive] = useStateTP(() => localStorage.getItem(STORAGE_KEY_THEME) || 'default');

  useEffectTP(() => {
    const cur = THEMES.find((t) => t.id === active) || THEMES[0];
    document.body.className = cur.bodyClass;
    localStorage.setItem(STORAGE_KEY_THEME, active);
  }, [active]);

  return (
    <div className="theme-picker" role="group" aria-label="테마 선택">
      {THEMES.map((t) => (
        <button
          key={t.id}
          type="button"
          className={active === t.id ? 'active' : ''}
          onClick={() => setActive(t.id)}
          title={`${t.label} 테마`}
          aria-pressed={active === t.id}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}

window.ThemePicker = ThemePicker;
