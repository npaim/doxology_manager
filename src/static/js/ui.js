// UI helpers: toasts, modals, theme, mobile menu
window.UI = (function(){
  const q = (sel, root=document) => root.querySelector(sel);
  const qa = (sel, root=document) => Array.from(root.querySelectorAll(sel));

  // Toasts
  const toastRoot = () => document.getElementById('toast-root');
  function toast(message, type = 'info'){
    const el = document.createElement('div');
    el.className = 'rounded-md px-4 py-2 shadow border text-sm transition-opacity ' +
      (type === 'success' ? 'bg-green-50 border-green-200 text-green-700 dark:bg-green-900/40 dark:border-green-700 dark:text-green-200' :
       type === 'error'   ? 'bg-red-50 border-red-200 text-red-700 dark:bg-red-900/40 dark:border-red-700 dark:text-red-200' :
                           'bg-gray-50 border-gray-200 text-gray-700 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200');
    el.textContent = message;
    toastRoot()?.appendChild(el);
    setTimeout(() => el.classList.add('opacity-0'), 3200);
    setTimeout(() => el.remove(), 3600);
  }

  // Simple modal builder
  function buildModal(title, bodyNode, actions){
    const overlay = document.createElement('div');
    overlay.className = 'fixed inset-0 z-50 flex items-center justify-center';

    const backdrop = document.createElement('div');
    backdrop.className = 'absolute inset-0 bg-black/40';

    const panel = document.createElement('div');
    panel.className = 'relative z-10 w-full max-w-md rounded-lg border bg-white dark:bg-gray-800 dark:border-gray-700 p-5 shadow-lg';

    const header = document.createElement('div');
    header.className = 'text-lg font-semibold mb-3';
    header.textContent = title || '';

    const body = document.createElement('div');
    body.className = 'text-sm';
    body.appendChild(bodyNode);

    const footer = document.createElement('div');
    footer.className = 'mt-5 flex justify-end gap-2';

    (actions || []).forEach(a => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = (a.primary
        ? 'bg-brand hover:bg-blue-600 text-white'
        : 'border border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-100') + ' px-3 py-2 rounded-md text-sm';
      btn.textContent = a.label;
      btn.addEventListener('click', () => a.onClick?.());
      footer.appendChild(btn);
    });

    panel.appendChild(header);
    panel.appendChild(body);
    panel.appendChild(footer);

    overlay.appendChild(backdrop);
    overlay.appendChild(panel);

    return { overlay, close: () => overlay.remove() };
  }

  function confirm(message){
    return new Promise(resolve => {
      const body = document.createElement('div');
      body.textContent = message;
      let mdl;
      mdl = buildModal('Confirm', body, [
        { label: 'Cancel', onClick: () => { mdl.close(); resolve(false); } },
        { label: 'Confirm', primary: true, onClick: () => { mdl.close(); resolve(true); } },
      ]);
      document.body.appendChild(mdl.overlay);
    });
  }

  function promptForm({ title, fields }){
    return new Promise(resolve => {
      const form = document.createElement('form');
      form.className = 'space-y-3';

      const inputs = {};
      fields.forEach(f => {
        const wrap = document.createElement('label');
        wrap.className = 'block text-sm font-medium';
        const span = document.createElement('span');
        span.className = 'text-gray-700 dark:text-gray-200';
        span.textContent = f.label;
        const input = f.type === 'textarea' ? document.createElement('textarea') : document.createElement('input');
        if (f.type && f.type !== 'textarea') input.type = f.type;
        if (f.rows && f.type === 'textarea') input.rows = f.rows;
        input.className = 'mt-1 w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-900 focus:border-brand focus:ring-brand';
        if (f.value != null) input.value = f.value;
        if (f.required) input.required = true;
        wrap.appendChild(span);
        wrap.appendChild(input);
        form.appendChild(wrap);
        inputs[f.name] = input;
      });

      // optional hook for callers to augment the form (e.g., autocomplete)
      if (window.__ui_onInit) {
        try { window.__ui_onInit({ form, inputs }); } catch(_) {}
      }

      let mdl;
      mdl = buildModal(title || 'Edit', form, [
        { label: 'Cancel', onClick: () => { mdl.close(); resolve(null); } },
        { label: 'Save', primary: true, onClick: () => {
            const values = {};
            for (const [k, el] of Object.entries(inputs)) values[k] = el.value;
            mdl.close();
            resolve(values);
          } },
      ]);
      document.body.appendChild(mdl.overlay);
    });
  }

  // Theme toggle
  function setTheme(mode){
    const root = document.documentElement;
    if (mode === 'dark') root.classList.add('dark'); else root.classList.remove('dark');
    try { localStorage.setItem('dm_theme', mode); } catch(_) {}
  }
  function toggleTheme(){
    const isDark = document.documentElement.classList.contains('dark');
    setTheme(isDark ? 'light' : 'dark');
  }
  function bindThemeToggles(){
    qa('#theme-toggle, #theme-toggle-mobile').forEach(btn => btn?.addEventListener('click', toggleTheme));
  }

  // Mobile menu
  function bindMobileMenu(){
    const openBtn = q('#btn-mobile-menu');
    const closeBtn = q('#btn-mobile-close');
    const menu = q('#mobile-menu');
    const backdrop = q('#mobile-menu-backdrop');
    const open = () => menu?.classList.remove('hidden');
    const close = () => menu?.classList.add('hidden');
    openBtn?.addEventListener('click', open);
    closeBtn?.addEventListener('click', close);
    backdrop?.addEventListener('click', close);
  }

  // Init on DOM ready
  document.addEventListener('DOMContentLoaded', () => {
    bindThemeToggles();
    bindMobileMenu();
  });

  return { toast, confirm, promptForm, toggleTheme };
})();
