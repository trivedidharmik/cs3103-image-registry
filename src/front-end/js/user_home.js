// Fetch and display images when the page loads
window.onload = function () {
  const userId = document.getElementById("userId").value; // Get user ID dynamically (to be passed from backend)

  fetch(`/users/${userId}/images`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      const imagesContainer = document.getElementById("imagesContainer");
      data.images.forEach((image) => {
        const imageCard = document.createElement("div");
        imageCard.classList.add("col-md-4", "mb-4");
        imageCard.innerHTML = `
        <div class="card shadow-sm h-100">
          <img src="/storage/${image.fileName}" class="card-img-top" alt="${image.title}">
          <div class="card-body">
            <h5 class="card-title">${image.title}</h5>
            <p class="card-text">${image.description}</p>
            <span class="badge bg-success">${image.isVisible}</span>
          </div>
        </div>
      `;
        imagesContainer.appendChild(imageCard);
      });
    })
    .catch((error) => {
      console.error("Error fetching images:", error);
    });

  // Handle the form submission for image upload
  const uploadForm = document.getElementById("uploadForm");
  uploadForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(uploadForm);
    const userId = document.getElementById("userId").value;

    fetch(`/users/${userId}/images`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.uri) {
          alert("Image uploaded successfully!");
          window.location.reload(); // Reload the page to show the new image
        }
      })
      .catch((error) => {
        console.error("Error uploading image:", error);
      });
  });
};
