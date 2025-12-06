/**
 * HabitPulse - Main Application JavaScript
 */

// Global state
let currentWeekStart = null;
let weekData = null;

// Initialize app
document.addEventListener("DOMContentLoaded", () => {
  initializeApp();
});

async function initializeApp() {
  // Set current week start
  currentWeekStart = getWeekStart(new Date());

  // Load week data
  await loadWeekData();

  // Setup event listeners
  setupEventListeners();
}

function setupEventListeners() {
  // Week navigation
  document
    .getElementById("prev-week-btn")
    .addEventListener("click", () => navigateWeek(-1));
  document
    .getElementById("next-week-btn")
    .addEventListener("click", () => navigateWeek(1));

  // Add task button
  document
    .getElementById("add-task-btn")
    .addEventListener("click", openAddTaskModal);

  // Download report button
  document
    .getElementById("download-report-btn")
    .addEventListener("click", downloadReport);

  // Metric type change (show/hide unit field)
  document.querySelectorAll('input[name="metric-type"]').forEach((radio) => {
    radio.addEventListener("change", handleMetricTypeChange);
  });

  // Frequency change (show/hide custom days)
  document.querySelectorAll('input[name="frequency"]').forEach((radio) => {
    radio.addEventListener("change", handleFrequencyChange);
  });
}

// Week navigation
function getWeekStart(date) {
  const d = new Date(date);
  const day = d.getDay(); // 0 = Sunday
  const diff = d.getDate() - day;
  return new Date(d.setDate(diff));
}

function formatDate(date) {
  return date.toISOString().split("T")[0];
}

function formatDateDisplay(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function formatFullDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

async function navigateWeek(direction) {
  const newStart = new Date(currentWeekStart);
  newStart.setDate(newStart.getDate() + direction * 7);
  currentWeekStart = newStart;
  await loadWeekData();
}

async function loadWeekData() {
  try {
    const dateStr = formatDate(currentWeekStart);
    const response = await fetch(`/api/progress/week?date=${dateStr}`);

    if (!response.ok) throw new Error("Failed to load week data");

    weekData = await response.json();
    renderWeekView();
    updateCharts();
  } catch (error) {
    showToast("Failed to load data: " + error.message, "error");
  }
}

function renderWeekView() {
  // Update week label
  const weekEnd = new Date(currentWeekStart);
  weekEnd.setDate(weekEnd.getDate() + 6);

  const startLabel = formatDateDisplay(weekData.week_start);
  const endLabel = formatDateDisplay(weekData.week_end);
  const year = new Date(weekData.week_start).getFullYear();
  document.getElementById(
    "week-label"
  ).innerHTML = `<img src=\"/static/icons/icon_calendar.png\" style=\"width: 16px; height: 16px; vertical-align: middle; margin-right: 4px;\"> ${startLabel} - ${endLabel}, ${year}`;

  // Update day headers with dates
  for (let i = 0; i < 7; i++) {
    const dayDate = new Date(currentWeekStart);
    dayDate.setDate(dayDate.getDate() + i);
    const dayHeader = document.getElementById(`day-${i}`);
    const isToday = formatDate(dayDate) === formatDate(new Date());
    dayHeader.innerHTML = `<span class="${
      isToday ? "text-primary-600 font-bold" : ""
    }">${
      ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][i]
    }</span><br><span class="text-xs ${
      isToday ? "text-primary-500" : "text-gray-400"
    }">${dayDate.getDate()}</span>`;
  }

  // Render tasks
  const tbody = document.getElementById("task-table-body");
  const emptyState = document.getElementById("empty-state");

  if (weekData.tasks.length === 0) {
    tbody.innerHTML = "";
    emptyState.classList.remove("hidden");
    return;
  }

  emptyState.classList.add("hidden");
  tbody.innerHTML = weekData.tasks.map((task) => renderTaskRow(task)).join("");
}

function renderTaskRow(task) {
  const healthClass = getHealthClass(task.health_score);
  const healthColor = getHealthColor(task.health_score);

  let daysHtml = "";
  for (let i = 0; i < 7; i++) {
    const day = task.days[i];
    daysHtml += renderTaskCell(task, day, i);
  }

  return `
        <tr class="task-row border-b border-gray-100 ${healthClass}" data-task-id="${
    task.id
  }">
            <td class="px-6 py-3">
                <div class="flex items-center">
                    <span class="health-indicator" style="background-color: ${healthColor};" 
                          title="Health: ${Math.round(
                            task.health_score * 100
                          )}%"></span>
                    <div>
                        <span class="font-medium text-gray-900">${escapeHtml(
                          task.name
                        )}</span>
                        ${
                          task.target_value
                            ? `<span class="text-xs text-gray-500 ml-2">(${
                                task.target_value
                              } ${task.metric_unit || ""})</span>`
                            : ""
                        }
                    </div>
                </div>
            </td>
            ${daysHtml}
            <td class="px-2 py-3">
                <div class="flex items-center justify-center space-x-1">
                    <button onclick="openEditTaskModal(${
                      task.id
                    })" class="action-btn text-gray-400 hover:text-gray-600" title="Edit">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                        </svg>
                    </button>
                    <button onclick="openDeleteModal(${task.id}, '${escapeHtml(
    task.name
  )}')" class="action-btn delete text-gray-400" title="Delete">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                    </button>
                </div>
            </td>
        </tr>
    `;
}

function renderTaskCell(task, day, dayIndex) {
  if (!day.is_scheduled) {
    return `<td class="px-4 py-3 text-center task-cell not-scheduled disabled">—</td>`;
  }

  const isCompleted = day.log && day.log.is_completed;
  const isMissed = !isCompleted && day.is_past && !day.is_today;
  const isPending = !isCompleted && (day.is_today || !day.is_past);

  let icon = "○";
  let stateClass = "pending";
  let valueDisplay = "";

  if (isCompleted) {
    icon = "✓";
    stateClass = "completed";
    if (day.log.metric_value !== null && task.metric_type !== "BOOLEAN") {
      const displayValue = formatMetricValue(
        day.log.metric_value,
        task.metric_type,
        task.metric_unit
      );
      valueDisplay = `<div class="metric-value">${displayValue}</div>`;
    }
  } else if (isMissed) {
    icon = "✗";
    stateClass = "missed";
  }

  const todayClass = day.is_today ? "today" : "";
  const clickable = !day.is_past || day.is_today || isCompleted;
  const disabledClass = !clickable ? "disabled" : "";

  return `
        <td class="px-4 py-3 text-center">
            <div class="task-cell ${stateClass} ${todayClass} ${disabledClass}" 
                 ${
                   clickable
                     ? `onclick="openProgressModal(${task.id}, '${day.date}')"`
                     : ""
                 }>
                <div>
                    <span class="text-lg">${icon}</span>
                    ${valueDisplay}
                </div>
            </div>
        </td>
    `;
}

function formatMetricValue(value, metricType, unit) {
  if (value === null || value === undefined) return "";

  switch (metricType) {
    case "TIME":
      return `${value}${unit ? unit.charAt(0) : "m"}`;
    case "PROGRESS":
      return `${Math.round(value)}%`;
    case "INTENSITY":
      return `${value}/10`;
    case "COUNT":
      return `${value}`;
    default:
      return "";
  }
}

function getHealthClass(score) {
  if (score >= 0.8) return "health-excellent";
  if (score >= 0.6) return "health-good";
  if (score >= 0.4) return "health-moderate";
  if (score >= 0.2) return "health-poor";
  return "health-critical";
}

function getHealthColor(score) {
  if (score >= 0.8) return "#22c55e";
  if (score >= 0.6) return "#84cc16";
  if (score >= 0.4) return "#eab308";
  if (score >= 0.2) return "#f97316";
  return "#ef4444";
}

// Modal controls
function handleMetricTypeChange(e) {
  const unitSection = document.getElementById("metric-unit-section");
  if (e.target.value === "BOOLEAN") {
    unitSection.classList.add("hidden");
  } else {
    unitSection.classList.remove("hidden");
  }
}

function handleFrequencyChange(e) {
  const customDaysSection = document.getElementById("custom-days-section");
  if (e.target.value === "CUSTOM") {
    customDaysSection.classList.remove("hidden");
  } else {
    customDaysSection.classList.add("hidden");
  }
}

// Download report
async function downloadReport() {
  try {
    showToast("Generating report...", "info");
    const response = await fetch("/api/reports/pdf?weeks=4");

    if (!response.ok) throw new Error("Failed to generate report");

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "habitpulse_report.pdf";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    showToast("Report downloaded!", "success");
  } catch (error) {
    showToast("Failed to download report: " + error.message, "error");
  }
}

// Toast notifications
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");

  const bgColor = {
    success: "bg-green-500",
    error: "bg-red-500",
    info: "bg-primary-500",
    warning: "bg-yellow-500",
  }[type];

  const icon = {
    success: '<img src="/static/icons/icon_done.png" style="width: 16px; height: 16px;">',
    error: '<img src="/static/icons/icon_cross.png" style="width: 16px; height: 16px;">',
    info: '<img src="/static/icons/icon_document.png" style="width: 16px; height: 16px;">',
    warning: '<img src="/static/icons/icon_stopwatch.png" style="width: 16px; height: 16px;">',
  }[type];

  const toast = document.createElement("div");
  toast.className = `toast ${bgColor} text-white px-4 py-3 rounded-lg shadow-lg flex items-center space-x-2`;
  toast.innerHTML = `<span>${icon}</span><span>${escapeHtml(message)}</span>`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("toast-exit");
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Utility functions
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// API helper
async function apiRequest(url, method = "GET", data = null) {
  const options = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  const response = await fetch(url, options);
  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.error || "Request failed");
  }

  return result;
}
