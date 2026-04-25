/**
 * Smart College Management System
 * Main JavaScript — Sidebar toggle, Charts, Interactivity
 */

// ========== Sidebar Toggle ==========
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    sidebar.classList.toggle('active');
    if (overlay) overlay.classList.toggle('active');
}

// Close sidebar on overlay click
document.addEventListener('DOMContentLoaded', function () {
    // Create overlay element for mobile
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    overlay.id = 'sidebarOverlay';
    overlay.addEventListener('click', toggleSidebar);
    document.body.appendChild(overlay);

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // Initialize table search if search input exists
    const tableSearch = document.getElementById('tableSearch');
    if (tableSearch) {
        tableSearch.addEventListener('input', function () {
            const searchTerm = this.value.toLowerCase();
            const table = document.querySelector('.data-table');
            if (!table) return;
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(function (row) {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }
});

// ========== Chart Helpers ==========
const chartColors = {
    primary: '#3b82f6',
    primaryLight: 'rgba(59, 130, 246, 0.1)',
    success: '#10b981',
    successLight: 'rgba(16, 185, 129, 0.1)',
    warning: '#f59e0b',
    warningLight: 'rgba(245, 158, 11, 0.1)',
    danger: '#ef4444',
    dangerLight: 'rgba(239, 68, 68, 0.1)',
    info: '#06b6d4',
    infoLight: 'rgba(6, 182, 212, 0.1)',
    purple: '#8b5cf6',
    purpleLight: 'rgba(139, 92, 246, 0.1)',
};

const chartPalette = [
    '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
    '#06b6d4', '#ec4899', '#14b8a6', '#f97316', '#6366f1'
];

const defaultChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                font: { family: 'Inter', size: 12 },
                usePointStyle: true,
                padding: 16
            }
        }
    },
    scales: {
        x: {
            grid: { display: false },
            ticks: { font: { family: 'Inter', size: 11 } }
        },
        y: {
            grid: { color: 'rgba(0,0,0,0.05)' },
            ticks: { font: { family: 'Inter', size: 11 } },
            beginAtZero: true
        }
    }
};

/**
 * Create a bar chart
 */
function createBarChart(canvasId, labels, datasets, options) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const config = {
        type: 'bar',
        data: { labels: labels, datasets: datasets },
        options: Object.assign({}, defaultChartOptions, options || {})
    };

    return new Chart(ctx, config);
}

/**
 * Create a line chart
 */
function createLineChart(canvasId, labels, datasets, options) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const config = {
        type: 'line',
        data: { labels: labels, datasets: datasets },
        options: Object.assign({}, defaultChartOptions, options || {})
    };

    return new Chart(ctx, config);
}

/**
 * Create a pie/doughnut chart
 */
function createPieChart(canvasId, labels, data, options) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const config = {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: chartPalette.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: Object.assign({
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: { family: 'Inter', size: 12 },
                        usePointStyle: true,
                        padding: 16
                    }
                }
            }
        }, options || {})
    };

    return new Chart(ctx, config);
}

// ========== Fetch API Helper ==========
async function fetchJSON(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        return null;
    }
}

// ========== Form Validation Helper ==========
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    let isValid = true;
    const required = form.querySelectorAll('[required]');

    required.forEach(function (field) {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// ========== Confirm Delete ==========
function confirmDelete(name, formId) {
    if (confirm('Are you sure you want to delete "' + name + '"? This action cannot be undone.')) {
        document.getElementById(formId).submit();
    }
}

// ========== Loading State ==========
function showLoading(buttonId) {
    const btn = document.getElementById(buttonId);
    if (!btn) return;
    // Tiny delay allows form submission to start before button is disabled
    setTimeout(() => {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Processing...';
    }, 10);
}

// ========== Attendance Marking Helper ==========
function markAll(status) {
    const radios = document.querySelectorAll('input[type="radio"][value="' + status + '"]');
    radios.forEach(function (radio) {
        radio.checked = true;
    });
}
