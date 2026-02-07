// Feedback Modal Management
const feedbackBtn = document.getElementById("feedbackBtn")
const closeFeedback = document.getElementById("closeFeedback")
const feedbackOverlay = document.getElementById("feedbackOverlay")
const feedbackForm = document.getElementById("feedbackForm")

// Open modal
feedbackBtn.addEventListener("click", () => {
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
  feedbackOverlay.classList.add("active")
  document.body.style.overflow = "hidden"
})

// Close modal
closeFeedback.addEventListener("click", () => {
  feedbackOverlay.classList.remove("active")
  document.body.style.overflow = "auto"
})

// Close modal when clicking outside
feedbackOverlay.addEventListener("click", (e) => {
  if (e.target === feedbackOverlay) {
    feedbackOverlay.classList.remove("active")
    document.body.style.overflow = "auto"
  }
})

// Handle form submission
feedbackForm.addEventListener("submit", async (e) => {
  e.preventDefault()

  const formData = new FormData(feedbackForm)
  const company = formData.get("company")
  const comment = formData.get("comment")

  console.log("[v0] Submitting feedback:", { company, comment })

  try {
    // Send to backend - adjust endpoint as needed
    const response = await fetch("/api/feedback", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        company: company,
        comment: comment,
        timestamp: new Date().toISOString(),
      }),
    })

    if (response.ok) {
      console.log("[v0] Feedback submitted successfully")
      feedbackForm.reset()
      feedbackOverlay.classList.remove("active")
      document.body.style.overflow = "auto"

      // Optional: Show success message
      alert("Thank you for your feedback!")
    } else {
      console.error("[v0] Failed to submit feedback:", response.status)
      alert("Failed to submit feedback. Please try again.")
    }
  } catch (error) {
    console.error("[v0] Error submitting feedback:", error)
    alert("An error occurred. Please try again.")
  }
})

// Company Grid Selection
const companyGrid = document.getElementById("companyGrid")
if (companyGrid) {
  const companyBoxes = companyGrid.querySelectorAll(".company-box")

  companyBoxes.forEach((box) => {
    box.addEventListener("click", () => {
      const companyName = box.getAttribute("data-company")
      console.log("[v0] Selected company:", companyName)

      // Optional: Filter feedback by company or perform other actions
      // You can add filtering logic here
    })
  })
}

// Keyboard shortcut to open feedback modal (Ctrl/Cmd + K)
document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "k") {
    e.preventDefault()
    feedbackOverlay.classList.add("active")
    document.body.style.overflow = "hidden"
  }
})

// Close modal with Escape key
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && feedbackOverlay.classList.contains("active")) {
    feedbackOverlay.classList.remove("active")
    document.body.style.overflow = "auto"
  }
})

console.log("[v0] Openfeed UI initialized successfully")

document.addEventListener("DOMContentLoaded", function () {
  const toggleBtn = document.getElementById("theme-toggle");

  // Load saved theme
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "light") {
    document.body.classList.add("light-theme");
  }

  toggleBtn.addEventListener("click", function () {
    document.body.classList.toggle("light-theme");

    // Save preference
    if (document.body.classList.contains("light-theme")) {
      localStorage.setItem("theme", "light");
    } else {
      localStorage.setItem("theme", "dark");
    }
  });
});
