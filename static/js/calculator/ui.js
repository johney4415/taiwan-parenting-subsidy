/**
 * Form handling and progressive disclosure for the calculator.
 */

const CalculatorUI = (() => {
  "use strict";

  let subsidyData = null;

  function init() {
    loadData();
    bindEvents();
  }

  function loadData() {
    var staticPrefix = window.SITE_STATIC_PREFIX || "/static/";
    fetch(staticPrefix + "data/subsidies.json")
      .then((response) => {
        if (!response.ok) throw new Error("Failed to load subsidy data");
        return response.json();
      })
      .then((data) => {
        subsidyData = data.subsidies;
      })
      .catch((err) => {
        console.error("Error loading subsidy data:", err);
      });
  }

  function bindEvents() {
    const form = document.getElementById("calculator-form");
    if (!form) return;

    form.addEventListener("submit", handleSubmit);

    // Parental leave toggle
    const plCheckbox = document.getElementById("parental-leave");
    if (plCheckbox) {
      plCheckbox.addEventListener("change", function () {
        const salaryInput = document.getElementById("salary-input");
        if (salaryInput) {
          salaryInput.classList.toggle("hidden", !this.checked);
        }
      });
    }
  }

  function getFormData() {
    return {
      city_code: document.getElementById("city").value,
      birth_order: parseInt(document.getElementById("birth-order").value, 10),
      care_type: document.querySelector('input[name="care_type"]:checked')?.value || "quasi_public",
      income_tax_rate: parseInt(document.getElementById("income-tax-rate").value, 10),
      parental_leave: document.getElementById("parental-leave").checked,
      insured_salary: parseInt(document.getElementById("insured-salary").value, 10) || 0,
    };
  }

  function handleSubmit(e) {
    e.preventDefault();

    if (!subsidyData) {
      alert("資料載入中，請稍後再試。");
      return;
    }

    const userInput = getFormData();
    if (!userInput.city_code) {
      alert("請選擇縣市。");
      return;
    }

    const result = SubsidyEngine.calculateAll(userInput, subsidyData);
    CalculatorRenderer.render(result);

    // Show results and scroll to them
    const resultsEl = document.getElementById("calculator-results");
    if (resultsEl) {
      resultsEl.classList.remove("hidden");
      resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function getSubsidyData() {
    return subsidyData;
  }

  return {
    init: init,
    getFormData: getFormData,
    getSubsidyData: getSubsidyData,
  };
})();
