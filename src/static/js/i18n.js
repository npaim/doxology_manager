// Simple client-side i18n
(function(){
  const STORAGE_KEY = 'dm_lang';
  const dict = {
    'en': {
      today: 'Today', month: 'Month', week: 'Week', day: 'Day',
      calendar: 'Calendar', songs: 'Songs', new_service: 'New Service', toggle_theme: 'Toggle Theme',
      calendar_title: 'Church Calendar', service: 'Service', details: 'Details', schedule: 'Schedule',
      order_of_service: 'Order of Service', add_item: 'Add Item', add_moment: 'Add Moment', edit: 'Edit', delete: 'Delete', back: 'Back',
      export_csv: 'Export CSV', print: 'Print', date: 'Date', start: 'Start', end: 'End',
      preacher: 'Preacher', leader: 'Leader', sermon_title: 'Sermon Title', notes: 'Notes',
      no_items: 'No items yet. Click “Add Item”.', no_moments: 'No moments yet. Click "Add Moment".', save_service: 'Save Service', update_service: 'Update Service',
      service_leader: 'Service Leader', start_time: 'Start Time', end_time: 'End Time', add_song: 'Add Song',
      hymn_number: 'Hymn #', misc: 'Misc', upcoming: 'Upcoming',
      church_admin: 'Church Admin', add_leader: 'Add Leader', logout: 'Logout', login: 'Login', menu: 'Menu',
      quick_create: 'Quick Create', quick_create_help: 'Pick a date, then choose the service template.', choose_template: 'Choose Template',
      choose_service_type: 'Choose Service Type', update_date: 'Update Date', no_templates: 'No templates found. Add some in the DB first.',
      service_template: 'Service Template'
    },
    'pt-br': {
      today: 'Hoje', month: 'Mês', week: 'Semana', day: 'Dia',
      calendar: 'Calendário', songs: 'Cânticos', new_service: 'Novo Culto', toggle_theme: 'Tema',
      calendar_title: 'Calendário da Igreja', service: 'Culto', details: 'Detalhes', schedule: 'Ordem do Culto',
      order_of_service: 'Ordem do Culto', add_item: 'Adicionar Item', add_moment: 'Adicionar Momento', edit: 'Editar', delete: 'Excluir', back: 'Voltar',
      export_csv: 'Exportar CSV', print: 'Imprimir', date: 'Data', start: 'Início', end: 'Fim',
      preacher: 'Pregador', leader: 'Dirigente', sermon_title: 'Título da Mensagem', notes: 'Observações',
      no_items: 'Ainda sem itens. Clique em “Adicionar Item”.', no_moments: 'Ainda sem momentos. Clique em "Adicionar Momento".', save_service: 'Salvar Culto', update_service: 'Atualizar Culto',
      service_leader: 'Líder do Culto', start_time: 'Hora de Início', end_time: 'Hora de Término', add_song: 'Adicionar Cântico',
      hymn_number: 'Nº do Hinário', misc: 'Obs.', upcoming: 'Próximos',
      church_admin: 'Administração da Igreja', add_leader: 'Adicionar Líder', logout: 'Sair', login: 'Entrar', menu: 'Menu',
      quick_create: 'Criação Rápida', quick_create_help: 'Escolha uma data e depois o modelo do culto.', choose_template: 'Escolher Modelo',
      choose_service_type: 'Escolha o Tipo de Culto', update_date: 'Atualizar Data', no_templates: 'Nenhum modelo encontrado. Adicione alguns no banco primeiro.',
      service_template: 'Modelo do Culto'
    }
  };

  let current = (localStorage.getItem(STORAGE_KEY) || (navigator.language || 'en')).toLowerCase();
  if (!dict[current]) current = current.startsWith('pt') ? 'pt-br' : 'en';

  function t(key){ const d = dict[current] || dict['en']; return d[key] || key; }

  function apply(root=document){
    root.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n'); if (!key) return;
      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') el.placeholder = t(key);
      else el.textContent = t(key);
    });
    root.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder'); if (key) el.setAttribute('placeholder', t(key));
    });
  }

  function setLang(lang){
    if (!dict[lang]) return;
    current = lang;
    try { localStorage.setItem(STORAGE_KEY, lang); } catch(_){}
    try { document.documentElement.setAttribute('lang', lang); } catch(_){}
    apply(document);
    try {
      document.dispatchEvent(new CustomEvent('dm:language-changed', { detail: { lang } }));
    } catch(_) {}
  }
  function getLang(){ return current; }

  window.I18N = { t, apply, setLang, getLang };
})();
