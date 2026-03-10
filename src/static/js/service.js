// Service detail page edit/delete
(function(){
  const detailEl = document.querySelector('[data-service-id]');
  const editBtn = document.getElementById('btn-edit-service');
  const delBtn = document.getElementById('btn-delete-service');
  if (!detailEl) return;
  const id = Number(detailEl.getAttribute('data-service-id'));

  function currentData(){
    return {
      service_date: detailEl.getAttribute('data-date') || '',
      start_time: detailEl.getAttribute('data-start') || '',
      end_time: detailEl.getAttribute('data-end') || '',
      preacher: detailEl.getAttribute('data-preacher') || '',
      leader: detailEl.getAttribute('data-leader') || '',
      title: detailEl.getAttribute('data-title') || '',
      notes: detailEl.getAttribute('data-notes') || ''
    };
  }

  editBtn?.addEventListener('click', async () => {
    try{
      const cur = currentData();
      const values = await UI.promptForm({
        title: (window.I18N ? I18N.t('service') : 'Service'),
        fields: [
          { name: 'service_date', label: (window.I18N? I18N.t('date'):'Date'), type: 'date', value: cur.service_date, required: true },
          { name: 'start_time', label: (window.I18N? I18N.t('start_time'):'Start Time'), type: 'time', value: cur.start_time, required: true },
          { name: 'end_time', label: (window.I18N? I18N.t('end_time'):'End Time'), type: 'time', value: cur.end_time, required: true },
          { name: 'preacher', label: (window.I18N? I18N.t('preacher'):'Preacher'), type: 'text', value: cur.preacher },
          { name: 'leader', label: (window.I18N? I18N.t('leader'):'Leader'), type: 'text', value: cur.leader },
          { name: 'title', label: (window.I18N? I18N.t('sermon_title'):'Sermon Title'), type: 'text', value: cur.title },
          { name: 'notes', label: (window.I18N? I18N.t('notes'):'Notes'), type: 'textarea', rows: 4, value: cur.notes }
        ]
      });
      if (!values) return;
      const res = await fetch(`/api/services/${id}`, {
        method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(values)
      });
      if (!res.ok){ UI.toast('Update failed', 'error'); return; }
      UI.toast('Service updated', 'success');
      location.reload();
    } catch(e){
      console.error('Edit service failed', e);
      UI.toast('Edit failed', 'error');
    }
  });

  delBtn?.addEventListener('click', async () => {
    try{
      const ok = await UI.confirm('Delete this service?');
      if (!ok) return;
      const res = await fetch(`/api/services/${id}`, { method: 'DELETE' });
      if (!res.ok){ UI.toast('Delete failed', 'error'); return; }
      UI.toast('Service deleted', 'success');
      window.location = '/';
    } catch(e){ console.error('Delete failed', e); UI.toast('Delete failed', 'error'); }
  });
})();
