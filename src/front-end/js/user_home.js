// Fetch and display images when the page loads
window.onload = function () {
  const userId = document.getElementById("userId").value;

  fetch(`/users/${userId}/image-count`)
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("imageCount").textContent = data.count;
    });

  // Load images
  fetch(`/users/${userId}/images`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      const imagesContainer = document.getElementById("imagesContainer");
      imagesContainer.innerHTML = ""; // Clear existing content

      data.images.forEach((image) => {
        const imageCard = document.createElement("div");
        imageCard.classList.add("col-md-4", "mb-4");
        imageCard.innerHTML = `
          <div class="card shadow-sm h-100">
            <img src="/storage/${image.fileName}" class="card-img-top" alt="${
          image.title
        }">
            <div class="card-body">
              <h5 class="card-title">${image.title}</h5>
              <p class="card-text">${image.description}</p>
              <span class="badge bg-${
                image.isVisible === "public" ? "success" : "warning"
              }">${image.isVisible}</span>
              <div class="mt-2">
                <button class="btn btn-sm btn-warning edit-btn" data-image-id="${
                  image.imageId
                }">Edit</button>
                <button class="btn btn-sm btn-danger delete-btn" data-image-id="${
                  image.imageId
                }">Delete</button>
              </div>
            </div>
          </div>`;
        imagesContainer.appendChild(imageCard);
      });

      // Add delete handlers
      document.querySelectorAll(".delete-btn").forEach((btn) => {
        btn.addEventListener("click", handleDelete);
      });

      // Add edit handlers
      document.querySelectorAll(".edit-btn").forEach((btn) => {
        btn.addEventListener("click", handleEdit);
      });
    })
    .catch((error) => {
      console.error("Error fetching images:", error);
    });

  // Handle image upload
  const uploadForm = document.getElementById("uploadForm");
  uploadForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(uploadForm);
    const userId = document.getElementById("userId").value;

    fetch(`/users/${userId}/images`, {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (!response.ok) throw new Error("Upload failed");
        return response.json();
      })
      .then((data) => {
        if (data.uri) {
          window.location.reload();
        }
      })
      .catch((error) => {
        console.error("Upload error:", error);
        alert("Upload failed: " + error.message);
      });
  });

  // Handle edit form submissions
  document.addEventListener("submit", handleEditSubmit);
};

// Delete image handler
function handleDelete(e) {
  const imageId = e.target.dataset.imageId;
  const userId = document.getElementById("userId").value;

  if (confirm("Are you sure you want to delete this image?")) {
    fetch(`/users/${userId}/images`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ image_id: imageId }),
    })
      .then((response) => {
        if (response.ok) {
          e.target.closest(".col-md-4").remove();
        } else {
          alert("Failed to delete image");
        }
      })
      .catch((error) => console.error("Delete error:", error));
  }
}

// Edit button handler
function handleEdit(e) {
  const imageId = e.target.dataset.imageId;
  const cardBody = e.target.closest(".card-body");
  const currentTitle = cardBody.querySelector(".card-title").textContent;
  const currentDesc = cardBody.querySelector(".card-text").textContent;
  const currentVisibility = cardBody.querySelector(".badge").textContent;

  // Create edit form
  cardBody.innerHTML = `
    <form class="edit-form" data-image-id="${imageId}">
      <div class="mb-2">
        <input type="text" class="form-control" 
               value="${currentTitle}" name="title" required>
      </div>
      <div class="mb-2">
        <textarea class="form-control" 
                  name="desc" rows="2">${currentDesc}</textarea>
      </div>
      <div class="mb-2">
        <select class="form-select" name="isVisible">
          <option value="public" ${
            currentVisibility === "public" ? "selected" : ""
          }>Public</option>
          <option value="private" ${
            currentVisibility === "private" ? "selected" : ""
          }>Private</option>
        </select>
      </div>
      <div class="d-flex gap-2">
        <button type="submit" class="btn btn-primary btn-sm">Save</button>
        <button type="button" class="btn btn-secondary btn-sm cancel-edit">Cancel</button>
      </div>
    </form>`;

  // Add cancel handler
  cardBody.querySelector(".cancel-edit").addEventListener("click", () => {
    window.location.reload();
  });
}

// Edit form submission handler
function handleEditSubmit(e) {
  if (e.target.matches(".edit-form")) {
    e.preventDefault();
    const imageId = e.target.dataset.imageId;
    const formData = new FormData(e.target);

    fetch(`/images/${imageId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams(formData),
    })
      .then((response) => {
        if (response.ok) {
          window.location.reload();
        } else {
          alert("Failed to update image");
        }
      })
      .catch((error) => console.error("Update error:", error));
  }
}

document.getElementById("profileForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const updateData = {
    newUsername: document.getElementById("newUsername").value,
    newEmail: document.getElementById("newEmail").value,
    newPassword: document.getElementById("newPassword").value,
    currentPassword: document.getElementById("currentPassword").value,
  };

  fetch(`/users/${userId}/update`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(updateData),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("Profile updated successfully!");
        if (data.requiresVerification) {
          alert("Verification email sent to new address");
        }
        window.location.reload();
      } else {
        showFormErrors(data.errors);
      }
    })
    .catch((error) => console.error("Update error:", error));
});

function showFormErrors(errors) {
  // Reset feedback
  document
    .querySelectorAll(".is-invalid")
    .forEach((el) => el.classList.remove("is-invalid"));
  document
    .querySelectorAll(".invalid-feedback")
    .forEach((el) => (el.textContent = ""));

  // Show new errors
  for (const [field, message] of Object.entries(errors)) {
    const input = document.getElementById(field);
    const feedback = document.getElementById(`${field}Feedback`);
    if (input && feedback) {
      input.classList.add("is-invalid");
      feedback.textContent = message;
    }
  }
}
