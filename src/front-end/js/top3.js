document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("top3Container");
    if (!container) {
      alert("No #top3Container found in landing_page.html");
      return;
    }
  
    try {
      const resp = await fetch("/analytics/most-active");
      if (!resp.ok) {
        throw new Error("Failed to fetch top 3 users");
      }

      const data = await resp.json();
      if (!data.users || data.users.length === 0) {
        container.innerHTML = "<p class='text-muted'>No data found.</p>";
        return;
      }
  
      container.innerHTML = "";
      data.users.forEach((user) => {
        const col = document.createElement("div");
        col.className = "col-md-4 mb-3"; 
        col.innerHTML = `
          <div class="card shadow-sm h-100">
            <div class="card-body d-flex flex-column">
              <h5 class="card-title">${user.username}</h5>
              <p class="card-text mb-1">ID: ${user.userId}</p>
              <p class="text-muted">Uploaded <strong>${user.imageCount}</strong> images</p>
            </div>
          </div>
        `;
        container.appendChild(col);
      });
    } catch (err) {
      console.error("Error fetching top 3 uploaders:", err);
      container.innerHTML = `<p class='text-danger'>Could not load top 3: ${err.message}</p>`;
    }
  });
  