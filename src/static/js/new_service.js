(function(){
  function ensureCount(form){ let el = form.querySelector('input[name="moments_count"]'); if(!el){ el = document.createElement('input'); el.type = 'hidden'; el.name = 'moments_count'; el.value = '0'; form.prepend(el); } return el; }
  function getCount(form){ return parseInt(ensureCount(form).value||'0'); }
  function setCount(form, v){ ensureCount(form).value = String(v); }
  function ensureContainer(form){
    let c = form.querySelector('.space-y-3');
    if(!c){ c = document.createElement('div'); c.className = 'space-y-3'; const hdr = form.querySelector('.flex.items-center.justify-between'); if(hdr) hdr.insertAdjacentElement('afterend', c); else form.appendChild(c); }
    return c;
  }
  function addDynamicMoment(title, duration, id, pos){
    const form = document.querySelector('form[action="/services/new"]');
    if(!form) return;
    const container = ensureContainer(form);
    let idx = getCount(form) + 1; setCount(form, idx);
    const wrap = document.createElement('div');
    wrap.className = 'rounded-md border border-gray-200 dark:border-gray-700 p-3';
    wrap.setAttribute('data-pos', String(isNaN(pos)?9999:pos));
    wrap.innerHTML = [
      '<div class="text-sm font-medium mb-2">', title, '</div>',
      '<input type="hidden" name="moment_title_', idx, '" value="', title.replace(/"/g,'&quot;'), '">',
      (id ? ['<input type="hidden" name="moment_id_', idx, '" value="', id, '">'].join('') : ''),
      '<input type="hidden" name="moment_duration_', idx, '" value="', (duration||0), '">',
      '<div class="grid sm:grid-cols-3 gap-3">',
      '  <label class="block text-sm">',
      '    <span class="text-gray-700">Time</span>',
      '    <input type="time" name="moment_time_', idx, '" class="mt-1 w-full rounded-md border-gray-300 focus:border-brand focus:ring-brand">',
      '  </label>',
      '  <label class="block text-sm sm:col-span-2">',
      '    <span class="text-gray-700">Responsible</span>',
      '    <input type="text" name="moment_responsible_', idx, '" data-member-autocomplete class="mt-1 w-full rounded-md border-gray-300 focus:border-brand focus:ring-brand" placeholder="Name">',
      '  </label>',
      '  <label class="block text-sm sm:col-span-3">',
      '    <span class="text-gray-700">Notes</span>',
      '    <input type="text" name="moment_notes_', idx, '" class="mt-1 w-full rounded-md border-gray-300 focus:border-brand focus:ring-brand" placeholder="Optional">',
      '  </label>',
      '</div>'
    ].join('');
    container.appendChild(wrap);
    renumberAndSort(container);
  }
  function renumberAndSort(container){
    const blocks = Array.from(container.children);
    blocks.sort((a,b)=> (parseInt(a.getAttribute('data-pos')||'9999') - parseInt(b.getAttribute('data-pos')||'9999')));
    blocks.forEach(b=>container.appendChild(b));
    const form = container.closest('form');
    const count = blocks.length;
    setCount(form, count);
    for(let i=1;i<=count;i++){
      const el = blocks[i-1];
      const fix = (sel, base)=>{ const inp = el.querySelector(sel); if(inp){ inp.name = `${base}_${i}`; } };
      fix('input[name^="moment_title_"]','moment_title');
      fix('input[name^="moment_id_"]','moment_id');
      fix('input[name^="moment_duration_"]','moment_duration');
      fix('input[name^="moment_time_"]','moment_time');
      fix('input[name^="moment_responsible_"]','moment_responsible');
      fix('input[name^="moment_notes_"]','moment_notes');
    }
  }
  function parseTime(str){ if(!str) return null; const m=str.match(/^(\d{1,2}):(\d{2})$/); if(!m) return null; const d=new Date(); d.setHours(+m[1],+m[2],0,0); return d; }
  function fmt(d){ return ('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2); }
  function addMin(d, min){ const nd=new Date(d.getTime()); nd.setMinutes(nd.getMinutes()+(+min||0)); return nd; }
  function autofill(onlyEmpty){
    try{
      const startInp = document.querySelector('input[name="start_time"]');
      const startDate = parseTime(startInp && startInp.value);
      if(!startDate){
        if(window.UI && UI.toast) UI.toast('Please set the service start time first', 'warning'); else alert('Please set the service start time first');
        if(startInp) startInp.focus();
        return;
      }
      const totalEl = document.querySelector('input[name="moments_count"]'); if(!totalEl) return;
      const total = parseInt(totalEl.value||'0'); if(!total) return;
      let cur = new Date(startDate.getTime());
      for(let i=1;i<=total;i++){
        const tInp = document.querySelector(`input[name="moment_time_${i}"]`);
        const durEl = document.querySelector(`input[name="moment_duration_${i}"]`);
        if(tInp && (!onlyEmpty || !tInp.value)) tInp.value = fmt(cur);
        const dur = durEl ? parseInt(durEl.value||'0') : 0; if(dur>0) cur = addMin(cur, dur);
      }
    }catch(_){ }
  }
  document.addEventListener('DOMContentLoaded', function(){
    const form = document.querySelector('form[action="/services/new"]');
    if(form){ const container = form.querySelector('.space-y-3'); if(container) renumberAndSort(container); }
    const sel = document.getElementById('extra-moment-select');
    const btnAdd = document.getElementById('add-moment');
    if(sel && btnAdd){
      btnAdd.addEventListener('click', function(){
        const st = document.querySelector('input[name="start_time"]');
        const hasStart = st && /^(\d{1,2}):(\d{2})$/.test(st.value);
        if(!hasStart){ if(window.UI && UI.toast) UI.toast('Please set the service start time first', 'warning'); else alert('Please set the service start time first'); if(st) st.focus(); return; }
        const opt = sel.options[sel.selectedIndex];
        const title = opt && opt.value ? opt.value : null; if(!title) return;
        const dur = parseInt(opt.getAttribute('data-duration') || '0');
        const id = opt.getAttribute('data-id') || '';
        const pos = parseInt(opt.getAttribute('data-position') || '9999');
        addDynamicMoment(title, isNaN(dur)?0:dur, id, pos);
        sel.selectedIndex = 0;
      });
    }
    const btnAuto = document.getElementById('btn-autofill-times');
    if(btnAuto){ btnAuto.addEventListener('click', function(){ autofill(false); }); }
    const start = document.querySelector('input[name="start_time"]');
    if(start){ start.addEventListener('change', function(){ if(/^(\d{1,2}):(\d{2})$/.test(start.value)) autofill(true); }); }
  });
})();
