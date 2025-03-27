document.addEventListener("DOMContentLoaded", () => {
    const searchForm = document.getElementById("searchForm");
    const searchInput = document.getElementById("searchInput");
  
    searchForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const query = searchInput.value.trim();
  
      if (!query) return;
  
      const urlParams = isNaN(query)
        ? `title=${encodeURIComponent(query)}`
        : `imageId=${encodeURIComponent(query)}`;
  
      try {
        const resp = await fetch(`/images/search?${urlParams}`);
        const data = await resp.json();
  
        const container = document.querySelector(".container");
        container.innerHTML = `<h1>Search Results</h1>`;
  
        if (!data.images || data.images.length === 0) {
          container.innerHTML += `<p class="text-muted">No matching images found.</p>`;
          return;
        }
  
        const row = document.createElement("div");
        row.classList.add("row");
  
        data.images.forEach((img) => {
          const col = document.createElement("div");
          col.classList.add("col-md-4", "mb-4");
          col.innerHTML = `
            <div class="card shadow-sm h-100">
              <img src="/storage/${img.fileName}" class="card-img-top" alt="${img.title}">
              <div class="card-body">
                <h5 class="card-title">${img.title}</h5>
                <p class="card-text">${img.description || ""}</p>
                <span class="badge bg-${img.isVisible === "public" ? "success" : "warning"}">
                  ${img.isVisible}
                </span>
              </div>
            </div>
          `;
          row.appendChild(col);
        });
  
        container.appendChild(row);
      } catch (err) {
        console.error("Search error:", err);
      }
    });
  });
  