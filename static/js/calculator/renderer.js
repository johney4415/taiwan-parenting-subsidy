/**
 * Render calculation results to the DOM.
 */

const CalculatorRenderer = (() => {
  "use strict";

  const MONTH_NAMES = [
    "一月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "十一月", "十二月",
  ];

  function formatAmount(amount) {
    return amount.toLocaleString("zh-TW");
  }

  function render(result) {
    renderSummary(result);
    renderOneTimeList(result.one_time_subsidies);
    renderMonthlyList(result.monthly_subsidies);
    renderBirthMonths(result.recommended_birth_months);
  }

  function renderSummary(result) {
    const oneTimeTotal = result.one_time_subsidies.reduce(
      (sum, s) => sum + s.amount,
      0
    );

    const el = (id, text) => {
      const e = document.getElementById(id);
      if (e) e.textContent = text;
    };

    el("result-one-time-total", formatAmount(oneTimeTotal));
    el("result-monthly-total", formatAmount(result.monthly_subsidy_total));
    el("result-net-cost", formatAmount(result.monthly_net_cost));
  }

  function renderOneTimeList(subsidies) {
    const container = document.getElementById("result-one-time-list");
    if (!container) return;

    if (subsidies.length === 0) {
      container.innerHTML =
        '<p class="text-sm text-gray-500">無符合條件的一次性補助。</p>';
      return;
    }

    let html = '<h3 class="text-lg font-semibold text-gray-900 mb-3">一次性補助</h3>';
    html += '<div class="space-y-3">';

    for (const s of subsidies) {
      html += `
        <div class="flex items-center justify-between rounded-lg border border-green-200 bg-green-50 p-4">
          <div>
            <div class="font-medium text-gray-900">${escapeHtml(s.name)}</div>
            <div class="text-sm text-gray-600">${s.notes.map(escapeHtml).join(" · ")}</div>
          </div>
          <div class="text-xl font-bold text-green-700">${formatAmount(s.amount)} 元</div>
        </div>
      `;
    }

    html += "</div>";
    container.innerHTML = html;
  }

  function renderMonthlyList(subsidies) {
    const container = document.getElementById("result-monthly-list");
    if (!container) return;

    if (subsidies.length === 0) {
      container.innerHTML =
        '<p class="text-sm text-gray-500">無符合條件的每月補助。可能因所得稅率超過限制。</p>';
      return;
    }

    let html = '<h3 class="text-lg font-semibold text-gray-900 mb-3">每月補助</h3>';
    html += '<div class="space-y-3">';

    for (const s of subsidies) {
      const durationText = s.duration_months
        ? `最長 ${s.duration_months} 個月`
        : "";

      html += `
        <div class="flex items-center justify-between rounded-lg border border-blue-200 bg-blue-50 p-4">
          <div>
            <div class="font-medium text-gray-900">${escapeHtml(s.name)}</div>
            <div class="text-sm text-gray-600">${s.notes.map(escapeHtml).join(" · ")}</div>
            ${durationText ? `<div class="text-xs text-gray-500 mt-1">${escapeHtml(durationText)}</div>` : ""}
          </div>
          <div class="text-xl font-bold text-blue-700">${formatAmount(s.amount)} 元/月</div>
        </div>
      `;
    }

    html += "</div>";
    container.innerHTML = html;
  }

  function renderBirthMonths(months) {
    const container = document.getElementById("birth-months-grid");
    if (!container || !months || months.length === 0) return;

    let html = "";

    for (const m of months) {
      const bgColor = m.recommended
        ? "border-green-300 bg-green-50"
        : "border-gray-200 bg-white";
      const scoreColor = m.score >= 70
        ? "text-green-600"
        : m.score >= 50
        ? "text-gray-600"
        : "text-red-500";
      const badge = m.recommended
        ? '<span class="inline-block rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">推薦</span>'
        : "";

      html += `
        <div class="rounded-lg border ${bgColor} p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="font-semibold text-gray-900">${MONTH_NAMES[m.month - 1]}</span>
            <div class="flex items-center gap-2">
              ${badge}
              <span class="text-sm font-bold ${scoreColor}">${m.score}分</span>
            </div>
          </div>
          <!-- Score bar -->
          <div class="h-2 w-full rounded-full bg-gray-200 mb-2">
            <div class="h-2 rounded-full ${m.score >= 70 ? "bg-green-500" : m.score >= 50 ? "bg-yellow-400" : "bg-red-400"}"
                 style="width: ${m.score}%"></div>
          </div>
          ${
            m.pros.length > 0
              ? '<ul class="text-xs text-green-700 space-y-0.5">' +
                m.pros.map((p) => "<li>+ " + escapeHtml(p) + "</li>").join("") +
                "</ul>"
              : ""
          }
          ${
            m.cons.length > 0
              ? '<ul class="text-xs text-red-600 space-y-0.5 mt-1">' +
                m.cons.map((c) => "<li>- " + escapeHtml(c) + "</li>").join("") +
                "</ul>"
              : ""
          }
        </div>
      `;
    }

    container.innerHTML = html;
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
  }

  return {
    render: render,
  };
})();
