// Members autocomplete for inputs with data-member-autocomplete
(function(){
  function bindInput(inp){
    const listId = inp.getAttribute('list') || (inp.id ? inp.id + '-members' : 'members-datalist');
    let dl = document.getElementById(listId);
    if (!dl){ dl = document.createElement('datalist'); dl.id = listId; document.body.appendChild(dl); }
    inp.setAttribute('list', listId);

    let tmr = null;
    inp.addEventListener('input', function(){
      clearTimeout(tmr);
      const q = inp.value.trim();
      if (q.length === 0){ dl.innerHTML=''; return; }
      tmr = setTimeout(async () => {
        try {
          const res = await fetch('/api/members?q=' + encodeURIComponent(q));
          const arr = await res.json();
          dl.innerHTML = arr.map(m => `<option value="${m.name}"></option>`).join('');
        } catch(_) {}
      }, 180);
    });
  }

  function init(){
    document.querySelectorAll('[data-member-autocomplete]').forEach(bindInput);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
