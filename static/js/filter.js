/**
 * Simple filtering for the subsidies index page.
 */

document.addEventListener("DOMContentLoaded", function () {
  const filterBtns = document.querySelectorAll(".filter-btn");
  const items = document.querySelectorAll(".subsidy-item");

  if (filterBtns.length === 0) return;

  filterBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      const filter = this.getAttribute("data-filter");

      // Update active state
      filterBtns.forEach(function (b) {
        b.classList.remove(
          "active",
          "bg-primary-600",
          "text-white"
        );
        b.classList.add(
          "border",
          "border-gray-300",
          "text-gray-700"
        );
      });
      this.classList.add("active", "bg-primary-600", "text-white");
      this.classList.remove(
        "border",
        "border-gray-300",
        "text-gray-700"
      );

      // Filter items
      items.forEach(function (item) {
        if (filter === "all" || item.getAttribute("data-type") === filter) {
          item.classList.remove("hidden");
        } else {
          item.classList.add("hidden");
        }
      });
    });
  });
});
