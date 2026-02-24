/**
 * Theme Toggle - Dark/Light theme switching across all pages
 * Persists user preference via localStorage
 */
(function () {
  // Apply saved theme IMMEDIATELY to prevent flash of wrong theme
  var savedTheme = localStorage.getItem("theme");
  if (savedTheme === "light") {
    document.body.classList.add("light-theme");
  }

  document.addEventListener("DOMContentLoaded", function () {
    var toggleBtn = document.getElementById("theme-toggle");
    if (!toggleBtn) return;

    var toggleIcon = toggleBtn.querySelector("i");

    function updateIcon() {
      if (!toggleIcon) return;
      if (document.body.classList.contains("light-theme")) {
        toggleIcon.classList.remove("fa-moon");
        toggleIcon.classList.add("fa-sun");
      } else {
        toggleIcon.classList.remove("fa-sun");
        toggleIcon.classList.add("fa-moon");
      }
    }

    // Set initial icon based on current theme
    updateIcon();

    toggleBtn.addEventListener("click", function () {
      document.body.classList.toggle("light-theme");

      if (document.body.classList.contains("light-theme")) {
        localStorage.setItem("theme", "light");
      } else {
        localStorage.setItem("theme", "dark");
      }
      updateIcon();
    });
  });
})();
