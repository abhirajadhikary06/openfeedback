/**
 * Openfeed - Feedback Management JavaScript
 * Handles feedback modal functionality and dynamic feedback display
 */

document.addEventListener("DOMContentLoaded", function () {
  // Get DOM elements
  const feedbackBtn = document.getElementById("feedbackBtn");
  const feedbackOverlay = document.getElementById("feedbackOverlay");
  const closeFeedback = document.getElementById("closeFeedback");
  const feedbackForm = document.getElementById("feedbackForm");

  // Open feedback modal
  feedbackBtn.addEventListener("click", function () {
    // Check if user is authenticated
    const authState = document.getElementById('auth-state');
    const isLoggedIn = authState && authState.dataset.loggedIn === 'true';
    
    if (!isLoggedIn) {
      // Show alert and redirect to login
      if (confirm("Please login to share feedback. Click OK to go to the login page.")) {
        window.location.href = '/auth/login';
      }
      return;
    }
    
    // User is authenticated, open modal
    feedbackOverlay.classList.add("active");
  });

  // Close feedback modal
  closeFeedback.addEventListener("click", function () {
    feedbackOverlay.classList.remove("active");
  });

  // Close modal when clicking outside
  feedbackOverlay.addEventListener("click", function (e) {
    if (e.target === feedbackOverlay) {
      feedbackOverlay.classList.remove("active");
    }
  });

  // Form submission handler
  feedbackForm.addEventListener("submit", function (e) {
    e.preventDefault();
    
    const formData = new FormData(feedbackForm);
    const data = {
      company: formData.get("company"),
      comment: formData.get("comment"),
    };

    // Submit feedback to server
    fetch("/submit_feedback", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          alert("Feedback submitted successfully!");
          feedbackForm.reset();
          feedbackOverlay.classList.remove("active");

          // Add the new feedback to the page dynamically
          addFeedbackToPage(data.feedback);
        } else {
          alert("Error submitting feedback: " + (data.message || "Unknown error"));
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred while submitting your feedback.");
      });
  });

  /**
   * Dynamically adds new feedback to the page without requiring a reload
   * @param {Object} feedback - The feedback object from the server response
   */
  function addFeedbackToPage(feedback) {
    // Use the feedback manager if available, otherwise fall back to direct DOM manipulation
    if (window.feedbackManager) {
      window.feedbackManager.addNewFeedback(feedback);
    } else {
      // Fallback to original method
      const feedbackGrid = document.getElementById("hofGrid");

      // Create the new feedback card HTML
      const feedbackCard = document.createElement("div");
      feedbackCard.className = "feedback-box";
      feedbackCard.style.animation = "modalSlideIn 0.5s ease";

      feedbackCard.innerHTML = `
        <div class="feedback-box-header">
          <div class="feedback-company">
            ${
              feedback.company_logo
                ? `<img class="feedback-company-logo" src="${feedback.company_logo}" alt="${feedback.company_name} logo">`
                : `<div class="feedback-company-logo" style="background-color: #4285f4; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold;">
                    ${feedback.company_name[0].toUpperCase()}
                  </div>`
            }
            <span class="feedback-company-name">${feedback.company_name}</span>
          </div>
          <span class="sentiment-badge ${feedback.sentiment}">
            ${feedback.sentiment.charAt(0).toUpperCase() + feedback.sentiment.slice(1)}
          </span>
        </div>
        <div class="feedback-box-content">
          <p class="feedback-text">"${feedback.comment}"</p>
        </div>
      `;

      // Add the new feedback card at the beginning of the grid
      feedbackGrid.insertBefore(feedbackCard, feedbackGrid.firstChild);
    }
  }
});