(function(){
  const form = document.getElementById("song-form");
  const list = document.getElementById("songs-list");
  if (!list) return; // Only on Songs page

  async function fetchSongs(){
    const res = await fetch('/songs/');
    if (!res.ok) throw new Error('Failed to load songs');
    return res.json();
  }

  function render(songs){
    list.innerHTML = '';
    songs.forEach(s => {
      const li = document.createElement('li');
      li.className = 'py-2 flex items-center justify-between';
      li.innerHTML = `
        <div class="truncate"><span class="font-medium">${s.hymn_number}</span> — ${s.title}</div>
        <div class="flex items-center gap-2">
          <button data-action="edit" data-id="${s.id}" class="px-2 py-1 rounded-md border text-xs hover:bg-gray-100 dark:border-gray-700 dark:hover:bg-gray-700">Edit</button>
          <button data-action="delete" data-id="${s.id}" class="px-2 py-1 rounded-md border text-xs text-red-600 border-red-300 hover:bg-red-50 dark:text-red-300 dark:border-red-700 dark:hover:bg-red-900/30">Delete</button>
        </div>`;
      list.appendChild(li);
    });
  }

  async function load(){
    const songs = await fetchSongs();
    render(songs);
  }

  list.addEventListener('click', async (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    const id = Number(btn.dataset.id);

    if (btn.dataset.action === 'edit'){
      // get current data
      const songs = await fetchSongs();
      const song = songs.find(x => x.id === id);
      const values = await UI.promptForm({
        title: 'Edit Song',
        fields: [
          { name: 'title', label: 'Title', type: 'text', value: song.title, required: true },
          { name: 'hymn_number', label: 'Hymn #', type: 'number', value: song.hymn_number, required: true },
          { name: 'misc', label: 'Misc', type: 'text', value: song.misc || '' },
        ]
      });
      if (!values) return;
      const payload = { title: values.title.toUpperCase(), hymn_number: Number(values.hymn_number), misc: values.misc || null };
      const res = await fetch(`/songs/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (!res.ok){ const err = await res.json().catch(()=>({detail:'Update failed'})); UI.toast(err.detail || 'Update failed', 'error'); return; }
      UI.toast('Song updated', 'success');
      load();
    }

    if (btn.dataset.action === 'delete'){
      const ok = await UI.confirm('Delete this song?');
      if (!ok) return;
      const res = await fetch(`/songs/${id}`, { method: 'DELETE' });
      if (!res.ok){ UI.toast('Delete failed', 'error'); return; }
      UI.toast('Song deleted', 'success');
      load();
    }
  });

  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
      title: document.getElementById("title").value.toUpperCase(),
      hymn_number: parseInt(document.getElementById("hymn_number").value),
      misc: document.getElementById("misc").value || null,
    };
    const response = await fetch("/songs/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
    if (!response.ok) { const err = await response.json().catch(()=>({detail:'Error'})); UI.toast(err.detail || 'Error adding song', 'error'); return; }
    form.reset();
    UI.toast('Song added', 'success');
    load();
  });

  load();
})();
