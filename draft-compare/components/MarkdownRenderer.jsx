// MarkdownRenderer — renders markdown with marked + KaTeX math
const { useMemo, useEffect, useRef } = React;

function MarkdownRenderer({ content, className = '' }) {
  const containerRef = useRef(null);

  const htmlContent = useMemo(() => {
    if (typeof window !== 'undefined' && window.marked) {
      try {
        // Pre-process bold so `**텍스트**조사` still renders
        const processed = (content || '').replace(/\*\*(?=\S)(.*?\S)\*\*/g, '<strong>$1</strong>');
        const renderer = new window.marked.Renderer();
        renderer.link = function (arg) {
          let href, title, text;
          if (typeof arg === 'string') { href = arg; title = arguments[1]; text = arguments[2]; }
          else ({ href, title, text } = arg);
          return `<a href="${href}" ${title ? `title="${title}"` : ''} target="_blank" rel="noopener noreferrer">${text}</a>`;
        };
        renderer.image = function (arg) {
          let href, title, text;
          if (typeof arg === 'string') { href = arg; title = arguments[1]; text = arguments[2]; }
          else ({ href, title, text } = arg);
          return `<img src="${href}" alt="${text || ''}" ${title ? `title="${title}"` : ''} class="max-w-full h-auto rounded-lg shadow-md my-4" />`;
        };
        const rawHtml = window.marked.parse(processed, { renderer, gfm: true, breaks: true, mangle: false, headerIds: false });
        if (window.DOMPurify) {
          return window.DOMPurify.sanitize(rawHtml, {
            ADD_ATTR: ['target', 'rel'],
            ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto|tel|data:image\/(?:png|jpe?g|gif|webp|svg\+xml));?|#|\/|\.)/i,
          });
        }
        return rawHtml;
      } catch (e) {
        console.error('marked parse error', e);
        return content;
      }
    }
    return content;
  }, [content]);

  useEffect(() => {
    if (containerRef.current && typeof window !== 'undefined' && window.renderMathInElement) {
      try {
        window.renderMathInElement(containerRef.current, {
          delimiters: [
            { left: '$$', right: '$$', display: true },
            { left: '$', right: '$', display: false },
            { left: '\\(', right: '\\)', display: false },
            { left: '\\[', right: '\\]', display: true },
          ],
          throwOnError: false,
        });
      } catch (e) { console.error('KaTeX error', e); }
    }
  }, [htmlContent]);

  return (
    <div
      ref={containerRef}
      className={`markdown-content ${className}`}
      dangerouslySetInnerHTML={{ __html: htmlContent }}
    />
  );
}

window.MarkdownRenderer = MarkdownRenderer;
