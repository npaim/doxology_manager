// Sidebar: Upcoming services
(function(){
  document.addEventListener('DOMContentLoaded', async function(){
    const root = document.getElementById('sidebar-upcoming');
    if (!root) return;
    try {
      const res = await fetch('/api/services/upcoming?limit=5');
      const items = await res.json();
      if (!Array.isArray(items) || items.length === 0){
        const d = new Date().toISOString().slice(0,10);
        root.innerHTML = `<div class="text-sm text-gray-500">${(window.I18N ? I18N.t('no_items') : 'No items yet.')}
          <a class="underline" href="/services/new?date=${d}">${(window.I18N ? I18N.t('new_service') : 'New Service')}</a>
        </div>`;
        return;
      }
      root.innerHTML = items.map(it => `
        <a href="/services/${it.id}" class="block rounded-md border border-gray-200 dark:border-gray-700 p-3 hover:bg-gray-50 dark:hover:bg-gray-800">
          <div class="text-sm font-medium">${it.title ? it.title : (window.I18N? I18N.t('service') : 'Service')}</div>
          <div class="text-xs text-gray-600 dark:text-gray-400 mt-1">${it.date} · ${it.time || ''}</div>
          <div class="text-xs text-gray-600 dark:text-gray-400">${(window.I18N? I18N.t('preacher') : 'Preacher')}: ${it.preacher || '-'}</div>
        </a>
      `).join('');
    } catch(e){
      root.innerHTML = `<div class="text-sm text-red-600">Error loading upcoming</div>`;
    }
  });
})();
