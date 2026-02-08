console.log("APP.JS LOADED");


document
  .getElementById("song-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = {
      title: document.getElementById("title").value.toUpperCase(),
      hymn_number: parseInt(
        document.getElementById("hymn_number").value
      ),
      misc: document.getElementById("misc").value,
    };

    const response = await fetch("/songs/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const err = await response.json();
      alert(err.detail);
      return;
    }

    await loadSongs();
    document.getElementById("song-form").reset();
  });


  async function loadSongs() {
  const response = await fetch("/songs/");
  const songs = await response.json();

  const list = document.getElementById("songs-list");
  list.innerHTML = "";

  songs.forEach((song) => {
    const li = document.createElement("li");
    li.innerText = `${song.hymn_number} — ${song.title}`;
    list.appendChild(li);
  });
}

loadSongs();

