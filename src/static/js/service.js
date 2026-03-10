// Service detail page edit/delete
(function(){
  const detailEl = document.querySelector('[data-service-id]');
  const editBtn = document.getElementById('btn-edit-service');
  const delBtn = document.getElementById('btn-delete-service');
  if (!detailEl) return;
  const id = Number(detailEl.getAttribute('data-service-id'));

  editBtn?.addEventListener('click', async () => {
    const current = {
      service_date: detailEl.getAttribute('data-date') || '',
      start_time: detailEl.getAttribute('data-start') || '',
      end_time: detailEl.getAttribute('data-end') || '',
      preacher: detailEl.getAttribute('data-preacher') || '',
      leader: detailEl.getAttribute('data-leader') || '',
      title: detailEl.getAttribute('data-title') || '',
      notes: detailEl.getAttribute('data-notes') || ''
    };
    const values = await UI.promptForm({
      title: 'Edit Service',
      fields: [
        { name: 'service_date', label: 'Date', type: 'date', value: current.service_date, required: true },
        { name: 'start_time', label: 'Start Time', type: 'time', value: current.start_time, required: true },
        { name: 'end_time', label: 'End Time', type: 'time', value: current.end_time, required: true },
        { name: 'preacher', label: 'Preacher', type: 'text', value: current.preacher },
        { name: 'leader', label: 'Leader', type: 'text', value: current.leader },
        { name: 'title', label: 'Sermon Title', type: 'text', value: current.title },
        { name: 'notes', label: 'Notes', type: 'textarea', rows: 4, value: current.notes },
      ]
    });
    if (!values) return;
    const res = await fetch(`/api/services/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(values)
    });
    if (!res.ok){ UI.toast('Update failed', 'error'); return; }
    UI.toast('Service updated', 'success');
    location.reload();
  });

  delBtn?.addEventListener('click', async () => {
    const ok = await UI.confirm('Delete this service?');
    if (!ok) return;
    const res = await fetch(`/api/services/${id}`, { method: 'DELETE' });
    if (!res.ok){ UI.toast('Delete failed', 'error'); return; }
    UI.toast('Service deleted', 'success');
    window.location = '/';
  });
})();
