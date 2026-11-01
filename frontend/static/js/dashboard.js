/**
 * MediLens - Patient Command Center Interactive Features
 * Handles search filtering, status tabs, dose checklist, and print view.
 */

document.addEventListener("DOMContentLoaded", function () {
  // 1. Live Real-time Clock
  const clockEl = document.getElementById("liveClock");
  if (clockEl) {
    function updateClock() {
      const now = new Date();
      clockEl.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    updateClock();
    setInterval(updateClock, 1000);
  }

  // 2. Medicine Cabinet Search & Filter Tabs
  const searchInput = document.getElementById("cabinetSearch");
  const filterTabs = document.querySelectorAll(".filter-tab-btn");
  const tableRows = document.querySelectorAll("#cabinetTableBody tr[data-status]");
  let activeFilter = "all";

  function applyFilters() {
    const query = searchInput ? searchInput.value.toLowerCase().trim() : "";

    tableRows.forEach(row => {
      const status = row.getAttribute("data-status");
      const name = (row.querySelector(".med-name-cell strong")?.textContent || "").toLowerCase();
      const generic = (row.querySelector(".med-name-cell span")?.textContent || "").toLowerCase();

      const matchesSearch = !query || name.includes(query) || generic.includes(query);

      let matchesTab = true;
      if (activeFilter === "expiring") {
        matchesTab = (status === "Expiring soon");
      } else if (activeFilter === "expired") {
        matchesTab = (status === "Expired");
      } else if (activeFilter === "safe") {
        matchesTab = (status !== "Expiring soon" && status !== "Expired");
      }

      if (matchesSearch && matchesTab) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
  }

  filterTabs.forEach(tab => {
    tab.addEventListener("click", function () {
      filterTabs.forEach(t => t.classList.remove("active"));
      this.classList.add("active");
      activeFilter = this.getAttribute("data-filter") || "all";
      applyFilters();
    });
  });

  // 3. Today's Medication Tracker (Mark as Taken Action)
  const doseButtons = document.querySelectorAll(".btn-dose-action");
  doseButtons.forEach(btn => {
    btn.addEventListener("click", function () {
      const itemCard = this.closest(".dose-card-item");
      const isTaken = itemCard.classList.contains("is-taken");

      if (isTaken) {
        itemCard.classList.remove("is-taken");
        this.classList.remove("completed");
        this.innerHTML = '<i class="fa-solid fa-check"></i> <span>Mark Taken</span>';
      } else {
        itemCard.classList.add("is-taken");
        this.classList.add("completed");
        this.innerHTML = '<i class="fa-solid fa-circle-check"></i> <span>Taken ✓</span>';
      }
    });
  });

  // 4. Print / Export Medical Summary for Doctor Visit
  const printBtn = document.getElementById("printSummaryBtn");
  if (printBtn) {
    printBtn.addEventListener("click", function () {
      window.print();
    });
  }
});
