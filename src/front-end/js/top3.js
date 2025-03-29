document.addEventListener("DOMContentLoaded", () => {
    fetch("/analytics/most-active")
      .then(resp => resp.json())
      .then(data => {
        const container = document.getElementById("top3Container");
        container.innerHTML = "";
        data.users.forEach(u => {
          const card = document.createElement("div");
          card.className = "card mb-3";
          card.innerHTML = `
            <div class="card-body">
              <h5 class="card-title">${u.username}</h5>
              <p class="card-text">Uploaded ${u.imageCount} images</p>
            </div>
          `;
          container.appendChild(card);
        });
      })
      .catch(err => {
        console.error("Error fetching top 3 uploaders:", err);
      });
  });
  