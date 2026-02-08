document.addEventListener("DOMContentLoaded", () => {
  loadSongs();
});

async function loadSongs() {
  const songs = await apiFetch("/songs/");

  const root = document.getElementById("songs-root");
  root.innerHTML = "";

  songs.forEach(song => {
    const el = document.createElement("div");
    el.textContent = `${song.hymn_number} - ${song.title}`;
    root.appendChild(el);
  });
}