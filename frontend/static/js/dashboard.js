/**
 * MediLens - Patient Command Center Interactive Features
 * Handles search filtering, status tabs, dose checklist, anti-double-dosing closer, and print view.
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

  // 3. Print / Export Medical Summary for Doctor Visit
  const printBtn = document.getElementById("printSummaryBtn");
  if (printBtn) {
    printBtn.addEventListener("click", function () {
      window.print();
    });
  }
});

// 4. Dose Taken / Anti-Double-Dosing Closer Engine
window.recordDoseTaken = async function (medicineName, reminderId, medicineId, buttonElement) {
  const itemCard = buttonElement ? buttonElement.closest(".dose-card-item") : null;
  const broadcastBanner = document.getElementById("doseBroadcastBanner");

  if (buttonElement) {
    buttonElement.disabled = true;
    buttonElement.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Updating...</span>';
  }

  try {
    const response = await fetch("/auth/dose-taken", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        medicine_name: medicineName,
        reminder_id: reminderId,
        medicine_id: medicineId,
      }),
    });

    const data = await response.json();

    if (data.success) {
      if (itemCard) {
        itemCard.classList.add("is-taken");
        const parentCol = buttonElement.parentElement;
        buttonElement.remove();

        const badge = document.createElement("div");
        badge.className = "dose-confirmed-badge";
        badge.innerHTML = `<i class="fa-solid fa-circle-check"></i> <span>Taken at ${data.time_str} by ${data.administered_by}</span>`;
        parentCol.appendChild(badge);
      }

      if (broadcastBanner) {
        broadcastBanner.style.display = "flex";
        broadcastBanner.innerHTML = `
          <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fa-solid fa-circle-check" aria-hidden="true"></i>
            <span>${data.message}</span>
          </div>
          <button class="flash-close-btn" onclick="this.parentElement.style.display='none'">&times;</button>
        `;
        broadcastBanner.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    } else {
      alert(data.error || "Could not log dose status.");
      if (buttonElement) {
        buttonElement.disabled = false;
        buttonElement.innerHTML = '<i class="fa-solid fa-check"></i> <span>Mark Taken</span>';
      }
    }
  } catch (err) {
    console.error("Dose logging failed:", err);
    if (buttonElement) {
      buttonElement.disabled = false;
      buttonElement.innerHTML = '<i class="fa-solid fa-check"></i> <span>Mark Taken</span>';
    }
  }
};
