// Chart.js integrations for Citizen & Admin Dashboard Analytics

document.addEventListener("DOMContentLoaded", () => {
    const analyticsEl = document.getElementById("dashboard-analytics");
    if (!analyticsEl) return;
    
    // Parse JSON-encoded statistics data from data attributes
    const statusData = JSON.parse(analyticsEl.dataset.status || "{}");
    const categoryData = JSON.parse(analyticsEl.dataset.categories || "{}");
    const monthlyData = JSON.parse(analyticsEl.dataset.monthly || "{}");
    
    // Render Doughnut chart for Status
    initStatusChart(statusData);
    
    // Render Bar chart for Categories
    initCategoryChart(categoryData);
    
    // Render Line chart for Monthly Progress
    initMonthlyChart(monthlyData);
});

function initStatusChart(statusData) {
    const canvas = document.getElementById("statusChart");
    if (!canvas) return;
    
    const labels = Object.keys(statusData);
    const data = Object.values(statusData);
    
    // Map status names to specific HSL theme palettes
    const bgColors = labels.map(label => {
        if (label === 'Pending') return 'rgba(245, 158, 11, 0.2)'; // Amber
        if (label === 'In Progress') return 'rgba(59, 130, 246, 0.2)'; // Blue
        if (label === 'Resolved') return 'rgba(16, 185, 129, 0.2)'; // Emerald
        return 'rgba(148, 163, 184, 0.2)';
    });
    
    const borderColors = labels.map(label => {
        if (label === 'Pending') return '#f59e0b';
        if (label === 'In Progress') return '#3b82f6';
        if (label === 'Resolved') return '#10b981';
        return '#94a3b8';
    });
    
    new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: bgColors,
                borderColor: borderColors,
                borderWidth: 2,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#cbd5e1',
                        font: { family: 'Outfit', size: 12, weight: 500 },
                        padding: 15
                    }
                }
            }
        }
    });
}

function initCategoryChart(categoryData) {
    const canvas = document.getElementById("categoryChart");
    if (!canvas) return;
    
    const labels = Object.keys(categoryData);
    const data = Object.values(categoryData);
    
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Complaints Reported',
                data: data,
                backgroundColor: 'rgba(6, 182, 212, 0.25)', // Cyan
                borderColor: '#06b6d4',
                borderWidth: 2,
                borderRadius: 8,
                barThickness: 20
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
                    ticks: {
                        color: '#94a3b8',
                        font: { family: 'Outfit', size: 10 }
                    }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
                    ticks: {
                        color: '#94a3b8',
                        font: { family: 'Outfit', size: 11 },
                        stepSize: 1,
                        precision: 0
                    }
                }
            }
        }
    });
}

function initMonthlyChart(monthlyData) {
    const canvas = document.getElementById("monthlyChart");
    if (!canvas) return;
    
    const labels = Object.keys(monthlyData);
    const data = Object.values(monthlyData);
    
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Complaints',
                data: data,
                borderColor: '#10b981', // Emerald
                backgroundColor: 'rgba(16, 185, 129, 0.08)',
                borderWidth: 3.5,
                fill: true,
                tension: 0.35,
                pointBackgroundColor: '#10b981',
                pointBorderColor: '#0f172a',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
                    ticks: {
                        color: '#94a3b8',
                        font: { family: 'Outfit', size: 11 }
                    }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
                    ticks: {
                        color: '#94a3b8',
                        font: { family: 'Outfit', size: 11 },
                        stepSize: 1,
                        precision: 0
                    }
                }
            }
        }
    });
}
