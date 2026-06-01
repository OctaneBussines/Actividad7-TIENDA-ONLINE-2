document.addEventListener('DOMContentLoaded', () => {
  try {
    const elts = Array.from(document.querySelectorAll('body *'));
    const overflowers = elts.filter(e => e.scrollHeight > e.clientHeight + 1);
    if (!overflowers.length) {
      console.info('[debug-overflow] No vertical overflowers found.');
      // Additionally detect elements with overflow CSS that could show scrollbars
      const candidates = elts.filter(e => {
        try {
          const s = getComputedStyle(e);
          return ['auto','scroll','overlay'].includes(s.overflowY) || ['auto','scroll','overlay'].includes(s.overflow);
        } catch (err) { return false; }
      });
      if (!candidates.length) {
        console.info('[debug-overflow] No elements with overflow:auto/scroll detected.');
      } else {
        const rows2 = candidates.map(e=>({
          tag: e.tagName.toLowerCase(),
          cls: e.className || '(no class)',
          id: e.id || '(no id)',
          overflow: getComputedStyle(e).overflow,
          overflowY: getComputedStyle(e).overflowY,
          rect_h: Math.round(e.clientHeight),
          scroll_h: Math.round(e.scrollHeight)
        }));
        console.group('[debug-overflow] Elements with CSS overflow:auto|scroll');
        console.table(rows2);
        console.groupEnd();
      }
      return;
    }
    const rows = overflowers.map(e => ({
      tag: e.tagName.toLowerCase(),
      cls: e.className || '(no class)',
      id: e.id || '(no id)',
      rect_h: Math.round(e.clientHeight),
      scroll_h: Math.round(e.scrollHeight),
      xpath: (function(el){
        let p='';
        while(el && el.nodeType===1){
          let i=0, sib=el;
          while(sib){ if(sib.nodeName===el.nodeName) i++; sib=sib.previousElementSibling; }
          p='/'+el.nodeName.toLowerCase()+'['+i+']'+p;
          el=el.parentElement;
        }
        return p;
      })(e)
    }));
    console.group('[debug-overflow] Elements with scrollHeight > clientHeight');
    console.table(rows);
    console.groupEnd();
    // Also report bounding rects for these overflowers to see which exceed viewport
    try {
      const rectRows = rows.map(r => {
        // try to locate element via xpath-like path
        let el = null;
        try {
          // naive xpath resolver from our generated path
          const parts = r.xpath.split('/').filter(Boolean);
          el = parts.reduce((acc, part) => {
            if (!acc) return document.body;
            const m = part.match(/([a-z0-9]+)\[(\d+)\]/i);
            if (!m) return acc;
            const tag = m[1];
            const idx = parseInt(m[2]);
            let count = 0;
            for (const child of acc.children) {
              if (child.tagName.toLowerCase() === tag) {
                count++;
                if (count === idx) return child;
              }
            }
            return acc;
          }, document.body);
        } catch (er) { el = null; }
        if (!el) return null;
        const rct = el.getBoundingClientRect();
        return {
          tag: el.tagName.toLowerCase(),
          cls: el.className || '(no class)',
          id: el.id || '(no id)',
          top: Math.round(rct.top),
          bottom: Math.round(rct.bottom),
          view_h: window.innerHeight
        };
      }).filter(Boolean);
      if (rectRows.length) {
        console.group('[debug-overflow] Bounding rects for overflowers');
        console.table(rectRows);
        console.groupEnd();
      }
    } catch (e) { /* ignore */ }
  } catch (err) {
    console.error('[debug-overflow] error', err);
  }
});
