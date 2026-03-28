// Schedule (moments) UI for service detail
(function(){
  function ready(fn){
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  ready(function(){
    const wrapper = document.querySelector('[data-service-id]');
    if (!wrapper) return;

    const serviceId = Number(wrapper.getAttribute('data-service-id'));
    const listEl = document.getElementById('moments-list');
    const emptyEl = document.getElementById('moments-empty');
    const presetTrigger = document.getElementById('preset-moment-trigger');
    const presetLabel = document.getElementById('preset-moment-label');
    const presetMenu = document.getElementById('preset-moment-menu');
    const addPresetBtn = document.getElementById('btn-add-preset-moment');
    const editorOverlay = document.getElementById('moment-editor-overlay');
    const editorBackdrop = document.getElementById('moment-editor-backdrop');
    const editorId = document.getElementById('moment-editor-id');
    const editorTitle = document.getElementById('moment-editor-title');
    const editorResponsible = document.getElementById('moment-editor-responsible');
    const editorTime = document.getElementById('moment-editor-time');
    const editorNotes = document.getElementById('moment-editor-notes');
    const editorSave = document.getElementById('btn-save-moment-editor');
    const editorClose = document.getElementById('btn-close-moment-editor');
    const editorCancel = document.getElementById('btn-cancel-moment-editor');

    if (!serviceId || !listEl || !emptyEl) return;

    let presetMoments = [];
    let selectedPreset = null;

    function toast(message, type){
      if (window.UI && UI.toast) UI.toast(message, type);
    }

    function syncAddPresetState(){
      if (!addPresetBtn) return;
      addPresetBtn.disabled = !selectedPreset;
      if (presetLabel) presetLabel.textContent = selectedPreset ? selectedPreset.name : 'Add moment...';
    }

    function closePresetMenu(){
      presetMenu?.classList.add('hidden');
    }

    function openPresetMenu(){
      if (!presetMenu || presetMoments.length === 0) return;
      presetMenu.classList.remove('hidden');
    }

    function renderPresetMenu(){
      if (!presetMenu) return;
      if (presetMoments.length === 0) {
        presetMenu.innerHTML = '<div class="px-3 py-2 text-sm text-gray-500">No moments available</div>';
        return;
      }
      presetMenu.innerHTML = presetMoments.map(function(m){
        const isSelected = selectedPreset && selectedPreset.id === m.id;
        return '<button type="button" class="flex w-full items-center justify-between rounded-md px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700' + (isSelected ? ' bg-gray-100 dark:bg-gray-700' : '') + '" data-preset-id="' + m.id + '">' + String(m.name || '') + '</button>';
      }).join('');
    }

    function installMemberAutocomplete(inp){
      if (!inp) return;
      const listId = 'members-datalist';
      const dl = document.getElementById(listId);
      if (!dl) return;
      inp.setAttribute('list', listId);
      let tmr = null;
      inp.addEventListener('input', function(){
        clearTimeout(tmr);
        const q = inp.value.trim();
        if (!q) {
          dl.innerHTML = '';
          return;
        }
        tmr = setTimeout(async function(){
          try {
            const res = await fetch('/api/members?q=' + encodeURIComponent(q));
            const arr = await res.json();
            dl.innerHTML = arr.map(function(m){ return '<option value="' + m.name + '"></option>'; }).join('');
          } catch (_) {}
        }, 200);
      });
    }

    function openEditor(moment){
      if (!editorOverlay) return;
      editorId.value = String(moment.id || '');
      editorTitle.value = moment.title || '';
      editorResponsible.value = moment.responsible || '';
      editorTime.value = moment.time ? String(moment.time).slice(0, 5) : '';
      editorNotes.value = moment.notes || '';
      editorOverlay.classList.remove('hidden');
      editorTitle.focus();
    }

    function closeEditor(){
      if (!editorOverlay) return;
      editorOverlay.classList.add('hidden');
      editorId.value = '';
      editorTitle.value = '';
      editorResponsible.value = '';
      editorTime.value = '';
      editorNotes.value = '';
    }

    function rowHTML(moment){
      const time = moment.time ? String(moment.time).slice(0, 5) : '';
      const responsible = moment.responsible || '-';
      const notes = moment.notes ? ' - ' + moment.notes : '';
      return [
        '<li class="py-2 flex items-center justify-between gap-2">',
        '  <div class="min-w-0">',
        '    <div class="text-sm"><span class="text-gray-500">', moment.position, '.</span> <span class="font-medium">', moment.title, '</span></div>',
        '    <div class="text-xs text-gray-600 dark:text-gray-400">Responsible: ', responsible, '</div>',
        '    <div class="text-xs text-gray-500">', time, notes, '</div>',
        '  </div>',
        '  <div class="flex items-center gap-2 shrink-0">',
        '    <button data-id="', moment.id, '" data-action="up" class="px-2 py-1 rounded-md border text-xs hover:bg-gray-100 dark:border-gray-700 dark:hover:bg-gray-700" title="Move up">Up</button>',
        '    <button data-id="', moment.id, '" data-action="down" class="px-2 py-1 rounded-md border text-xs hover:bg-gray-100 dark:border-gray-700 dark:hover:bg-gray-700" title="Move down">Down</button>',
        '    <button data-id="', moment.id, '" data-action="edit" class="px-2 py-1 rounded-md border text-xs hover:bg-gray-100 dark:border-gray-700 dark:hover:bg-gray-700">Edit</button>',
        '    <button data-id="', moment.id, '" data-action="delete" class="px-2 py-1 rounded-md border text-xs text-red-600 border-red-300 hover:bg-red-50 dark:text-red-300 dark:border-red-700 dark:hover:bg-red-900/30">Delete</button>',
        '  </div>',
        '</li>'
      ].join('');
    }

    async function load(){
      try {
        const res = await fetch(`/api/services/${serviceId}/moments`);
        if (!res.ok) throw new Error('load failed');
        const moments = await res.json();
        listEl.innerHTML = moments.map(rowHTML).join('');
        emptyEl.classList.toggle('hidden', moments.length > 0);
      } catch (_) {
        listEl.innerHTML = '';
        emptyEl.classList.remove('hidden');
      }
    }

    async function loadPresetMoments(){
      if (!presetMenu) return;
      try {
        const res = await fetch(`/api/services/${serviceId}/preset-moments`);
        if (!res.ok) throw new Error('preset load failed');
        presetMoments = await res.json();
        selectedPreset = null;
        renderPresetMenu();
        syncAddPresetState();
      } catch (_) {
        presetMoments = [];
        selectedPreset = null;
        renderPresetMenu();
        syncAddPresetState();
      }
    }

    async function addSelectedPresetMoment(){
      if (!selectedPreset) return;
      const title = (selectedPreset.name || '').trim();
      if (!title) return;

      const res = await fetch(`/api/services/${serviceId}/moments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: title, moment_id: selectedPreset.id || null })
      });

      if (!res.ok) {
        toast('Add failed', 'error');
        selectedPreset = null;
        syncAddPresetState();
        return;
      }

      selectedPreset = null;
      syncAddPresetState();
      renderPresetMenu();
      closePresetMenu();
      toast('Moment added', 'success');
      load();
    }

    async function moveMoment(id, direction){
      const res = await fetch(`/api/services/${serviceId}/moments`);
      if (!res.ok) {
        toast('Reorder failed', 'error');
        return;
      }

      const moments = await res.json();
      const currentIndex = moments.findIndex(x => x.id === id);
      if (currentIndex < 0) return;

      const targetIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
      if (targetIndex < 0 || targetIndex >= moments.length) return;

      const current = moments[currentIndex];
      const target = moments[targetIndex];

      await fetch(`/api/services/${serviceId}/moments/${current.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ position: target.position })
      });

      await fetch(`/api/services/${serviceId}/moments/${target.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ position: current.position })
      });

      load();
    }

    async function editMoment(id){
      try {
        const res = await fetch(`/api/services/${serviceId}/moments`);
        if (!res.ok) throw new Error('load failed');
        const moments = await res.json();
        const moment = moments.find(function(x){ return x.id === id; });
        if (!moment) return;
        openEditor(moment);
      } catch (_) {
        toast('Update failed', 'error');
      }
    }

    presetTrigger?.addEventListener('click', function(){
      if (!presetMenu) return;
      if (presetMenu.classList.contains('hidden')) openPresetMenu();
      else closePresetMenu();
    });
    addPresetBtn?.addEventListener('click', addSelectedPresetMoment);
    presetMenu?.addEventListener('click', function(e){
      const btn = e.target.closest('[data-preset-id]');
      if (!btn) return;
      const id = Number(btn.getAttribute('data-preset-id'));
      selectedPreset = presetMoments.find(function(m){ return m.id === id; }) || null;
      renderPresetMenu();
      syncAddPresetState();
      closePresetMenu();
    });
    document.addEventListener('click', function(e){
      if (!presetMenu || presetMenu.classList.contains('hidden')) return;
      if (presetMenu.contains(e.target) || presetTrigger?.contains(e.target)) return;
      closePresetMenu();
    });

    editorSave?.addEventListener('click', async function(){
      const id = Number(editorId.value);
      if (!id) return;

      let memberId = null;
      const responsible = (editorResponsible.value || '').trim();
      if (responsible) {
        const memberRes = await fetch('/api/members/ensure', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: responsible })
        });
        if (memberRes.ok) {
          const member = await memberRes.json();
          memberId = member.id;
        }
      }

      const saveRes = await fetch(`/api/services/${serviceId}/moments/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: (editorTitle.value || '').trim(),
          responsible: responsible || null,
          time: editorTime.value || null,
          notes: (editorNotes.value || '').trim() || null,
          responsible_member_id: memberId
        })
      });

      if (!saveRes.ok) {
        toast('Update failed', 'error');
        return;
      }

      closeEditor();
      toast('Updated', 'success');
      load();
    });

    editorClose?.addEventListener('click', closeEditor);
    editorCancel?.addEventListener('click', closeEditor);
    editorBackdrop?.addEventListener('click', closeEditor);

    listEl.addEventListener('click', async function(e){
      const btn = e.target.closest('button');
      if (!btn) return;

      const id = Number(btn.dataset.id);
      const action = btn.dataset.action;
      if (!id || !action) return;

      if (action === 'delete') {
        const ok = window.UI && UI.confirm ? await UI.confirm('Delete this item?') : window.confirm('Delete this item?');
        if (!ok) return;

        const res = await fetch(`/api/services/${serviceId}/moments/${id}`, { method: 'DELETE' });
        if (!res.ok) {
          toast('Delete failed', 'error');
          return;
        }

        toast('Deleted', 'success');
        load();
        return;
      }

      if (action === 'edit') {
        editMoment(id);
        return;
      }

      if (action === 'up' || action === 'down') {
        moveMoment(id, action);
      }
    });

    load();
    loadPresetMoments();
    installMemberAutocomplete(editorResponsible);
  });
})();
