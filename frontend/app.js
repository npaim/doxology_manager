const API_URL = "http://127.0.0.1:8000/songs";

const form = document.getElementById("song-form");
const list = document.getElementById("songs-list");

async function loadSongs() {
  const res = await fetch(API_URL);
  const songs = await res.json();

  list.innerHTML = "";

  songs.forEach(song => {
    const li = document.createElement("li");
    li.textContent = `${song.hymn_number} - ${song.title}`;
    list.appendChild(li);
  });
}

form.addEventListener("submit", async e => {
  e.preventDefault();

  const data = {
    title: document.getElementById("title").value.trim().toUpperCase(),
    hymn_number: Number(document.getElementById("hymn_number").value),
    misc: document.getElementById("misc").value || null
  };

  await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  form.reset();
  loadSongs();
});

loadSongs();
