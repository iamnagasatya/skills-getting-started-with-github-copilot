document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
            <h4>${name}</h4>
            <p>${details.description}</p>
            <p><strong>Schedule:</strong> ${details.schedule}</p>
            <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
            <div class="participants-section">
              <strong>Participants (${details.participants.length}):</strong>
              <ul class="participants-list"></ul>
            </div>
          `;

        activitiesList.appendChild(activityCard);

        // Populate participants list with delete buttons
        const participantsUl = activityCard.querySelector('.participants-list');
        details.participants.forEach(participant => {
          const li = document.createElement('li');
          li.textContent = participant;

          // Create delete button (simple "×" icon)
          const delBtn = document.createElement('button');
          delBtn.className = 'delete-btn';
          delBtn.setAttribute('aria-label', `Unregister ${participant}`);
          delBtn.innerHTML = '&times;';

          delBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();

            try {
              const resp = await fetch(`/activities/${encodeURIComponent(name)}/participants?email=${encodeURIComponent(participant)}`, {
                method: 'DELETE'
              });

              const result = await resp.json();
              if (resp.ok) {
                messageDiv.textContent = result.message;
                messageDiv.className = 'success';
                messageDiv.classList.remove('hidden');
                // Refresh list
                fetchActivities();
              } else {
                messageDiv.textContent = result.detail || 'Failed to unregister';
                messageDiv.className = 'error';
                messageDiv.classList.remove('hidden');
              }

              setTimeout(() => messageDiv.classList.add('hidden'), 5000);
            } catch (err) {
              console.error('Error unregistering participant:', err);
              messageDiv.textContent = 'Failed to unregister. Please try again.';
              messageDiv.className = 'error';
              messageDiv.classList.remove('hidden');
              setTimeout(() => messageDiv.classList.add('hidden'), 5000);
            }
          });

          li.appendChild(delBtn);
          participantsUl.appendChild(li);
        });

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities list to show new participant
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
