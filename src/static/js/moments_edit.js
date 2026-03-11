(function(){
  function q(sel, root=document){ return root.querySelector(sel); }
  function qa(sel, root=document){ return Array.from(root.querySelectorAll(sel)); }
  async function fetchJSON(url, opts){ const r = await fetch(url, opts); if(!r.ok) throw new Error(await r.text()); return r.json(); }

  async function listMembers(qs){ const r = await fetch('/api/members?q='+encodeURIComponent(qs)); return r.json(); }

  function memberAutocomplete(input){
    const dl = q('#members-datalist');
    input.setAttribute('list','members-datalist');
    let tmr=null;
    input.addEventListener('input', ()=>{
      clearTimeout(tmr);
      const v = input.value.trim(); if(!v){ dl.innerHTML=''; return; }
      tmr=setTimeout(async()=>{ try{ const arr = await listMembers(v); dl.innerHTML = arr.map(m=>`<option value="${m.name}"></option>`).join(''); }catch(_){} },200);
    });
  }

  function rowTpl(m){
    const id = m?.id || '';
    const pos = m?.position || '';
    const title = m?.title || '';
    const responsible = m?.responsible || '';
    const time = m?.time || '';
    const notes = m?.notes || '';
    return [`
      <tr data-id="${id}">
        <td class="py-2 pr-2 align-top"><input type="number" class="w-16 rounded-md border-gray-300 dark:border-gray-700" name="position" value="${pos}"></td>
        <td class="py-2 pr-2 align-top"><input type="text" class="w-full rounded-md border-gray-300 dark:border-gray-700" name="title" value="${title}"></td>
        <td class="py-2 pr-2 align-top"><input type="text" class="w-full rounded-md border-gray-300 dark:border-gray-700" name="responsible" value="${responsible}" list="members-datalist"></td>
        <td class="py-2 pr-2 align-top"><input type="time" class="w-28 rounded-md border-gray-300 dark:border-gray-700" name="time" value="${(time||'').slice(0,5)}"></td>
        <td class="py-2 pr-2 align-top"><input type="text" class="w-full rounded-md border-gray-300 dark:border-gray-700" name="notes" value="${notes}"></td>
        <td class="py-2 pr-2 align-top">
          <button data-act="up" class="px-2 py-1 rounded-md border text-xs hover:bg-gray-100 dark:border-gray-700 dark:hover:bg-gray-700">↑</button>
          <button data-act="down" class="px-2 py-1 rounded-md border text-xs hover:bg-gray-100 dark:border-gray-700 dark:hover:bg-gray-700">↓</button>
          <button data-act="delete" class="px-2 py-1 rounded-md border text-xs text-red-600 border-red-300 hover:bg-red-50 dark:text-red-300 dark:border-red-700 dark:hover:bg-red-900/30">Delete</button>
        </td>
      </tr>
    `].join('');
  }

  function renumber(tbody){
    const rows = qa('tr', tbody);
    rows.sort((a,b)=> (parseInt(q('[name=position]',a).value||'9999') - parseInt(q('[name=position]',b).value||'9999')));
    rows.forEach(r=>tbody.appendChild(r));
    rows.forEach((r,i)=>{ q('[name=position]',r).value = i+1; });
  }

  document.addEventListener('DOMContentLoaded', async function(){
    const serviceId = Number(q('[data-service-id]').getAttribute('data-service-id'));
    const tbody = q('#moments-edit-rows');
    const btnAdd = q('#btn-add-row');
    const btnSave = q('#btn-save-all');

    // load
    const moments = await fetchJSON(`/api/services/${serviceId}/moments`);
    tbody.innerHTML = moments.map(rowTpl).join('');
    qa('[name=responsible]', tbody).forEach(memberAutocomplete);

    // actions
    tbody.addEventListener('click', (e)=>{
      const btn = e.target.closest('button'); if(!btn) return;
      const tr = e.target.closest('tr');
      if(btn.dataset.act==='delete'){ tr.remove(); return; }
      if(btn.dataset.act==='up' || btn.dataset.act==='down'){
        const rows = qa('tr', tbody);
        const idx = rows.indexOf(tr); if(idx<0) return;
        const swap = btn.dataset.act==='up' ? idx-1 : idx+1;
        if(swap<0 || swap>=rows.length) return;
        const posA = q('[name=position]', rows[idx]).value;
        const posB = q('[name=position]', rows[swap]).value;
        q('[name=position]', rows[idx]).value = posB;
        q('[name=position]', rows[swap]).value = posA;
        renumber(tbody);
      }
    });

    btnAdd.addEventListener('click', ()=>{
      const tmp = document.createElement('tbody');
      tmp.innerHTML = rowTpl({ position: (qa('tr',tbody).length+1) });
      const tr = tmp.firstElementChild; tbody.appendChild(tr);
      memberAutocomplete(q('[name=responsible]', tr));
    });

    btnSave.addEventListener('click', async ()=>{
      try{
        UI.toast('Saving...', 'info');
        renumber(tbody);
        const rows = qa('tr', tbody);
        // Compute existing ids from server to detect deletes
        const current = await fetchJSON(`/api/services/${serviceId}/moments`);
        const currentIds = new Set(current.map(m=>m.id));
        const seenIds = new Set();
        for(const r of rows){
          const id = (r.getAttribute('data-id')||'').trim();
          const payload = {
            title: q('[name=title]',r).value.trim(),
            responsible: q('[name=responsible]',r).value.trim() || null,
            time: q('[name=time]',r).value || null,
            notes: q('[name=notes]',r).value.trim() || null,
            position: parseInt(q('[name=position]',r).value||'0',10) || 1,
          };
          // ensure member id silently
          let memberId = null;
          if(payload.responsible){
            try{
              const mm = await fetchJSON('/api/members/ensure', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: payload.responsible }) });
              memberId = mm.id;
            }catch(_){ /* ignore */ }
          }
          payload.responsible_member_id = memberId;
          if(id){
            seenIds.add(Number(id));
            await fetchJSON(`/api/services/${serviceId}/moments/${id}`, { method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
          } else {
            await fetchJSON(`/api/services/${serviceId}/moments`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
          }
        }
        // deletions
        for(const id of currentIds){ if(!seenIds.has(id)){ await fetch(`/api/services/${serviceId}/moments/${id}`, { method:'DELETE' }); } }
        UI.toast('Saved', 'success');
        window.location = `/services/${serviceId}`;
      }catch(err){ UI.toast('Save failed', 'error'); }
    });
  });
})();
