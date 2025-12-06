/**
 * HabitPulse - Charts JavaScript
 */

let weeklyChart = null;
let trendChart = null;

function updateCharts() {
    if (!weekData || weekData.tasks.length === 0) {
        // Clear charts if no data
        if (weeklyChart) {
            weeklyChart.destroy();
            weeklyChart = null;
        }
        if (trendChart) {
            trendChart.destroy();
            trendChart = null;
        }
        return;
    }
    
    updateWeeklyChart();
    loadTrendChart();
}

function updateWeeklyChart() {
    const ctx = document.getElementById('weekly-chart').getContext('2d');
    
    // Calculate completion percentages for each task
    const labels = weekData.tasks.map(t => t.name.length > 15 ? t.name.substring(0, 15) + '...' : t.name);
    const data = weekData.tasks.map(task => {
        const scheduledDays = task.days.filter(d => d.is_scheduled).length;
        const completedDays = task.days.filter(d => d.is_scheduled && d.log && d.log.is_completed).length;
        return scheduledDays > 0 ? Math.round((completedDays / scheduledDays) * 100) : 0;
    });
    
    const backgroundColors = weekData.tasks.map(task => {
        const score = task.health_score;
        if (score >= 0.8) return 'rgba(34, 197, 94, 0.8)';
        if (score >= 0.6) return 'rgba(132, 204, 22, 0.8)';
        if (score >= 0.4) return 'rgba(234, 179, 8, 0.8)';
        if (score >= 0.2) return 'rgba(249, 115, 22, 0.8)';
        return 'rgba(239, 68, 68, 0.8)';
    });
    
    if (weeklyChart) {
        weeklyChart.destroy();
    }
    
    weeklyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Completion %',
                data: data,
                backgroundColor: backgroundColors,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.y}% complete`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

async function loadTrendChart() {
    try {
        const response = await fetch('/api/reports/summary?weeks=4');
        if (!response.ok) throw new Error('Failed to load trend data');
        
        const data = await response.json();
        renderTrendChart(data.summary);
    } catch (error) {
        console.error('Failed to load trend chart:', error);
    }
}

function renderTrendChart(summary) {
    const ctx = document.getElementById('trend-chart').getContext('2d');
    
    if (!summary.tasks || summary.tasks.length === 0) {
        if (trendChart) {
            trendChart.destroy();
            trendChart = null;
        }
        return;
    }
    
    // Get week labels
    const weeks = [];
    const weekLabels = [];
    for (let i = 3; i >= 0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - (i * 7));
        const weekStart = getWeekStart(d);
        weeks.push(formatDate(weekStart));
        weekLabels.push(formatDateDisplay(formatDate(weekStart)));
    }
    
    // Build datasets for each task
    const datasets = summary.tasks.slice(0, 5).map((task, index) => {
        const colors = [
            'rgba(99, 102, 241, 1)',   // Indigo
            'rgba(236, 72, 153, 1)',   // Pink
            'rgba(34, 197, 94, 1)',    // Green
            'rgba(249, 115, 22, 1)',   // Orange
            'rgba(6, 182, 212, 1)'     // Cyan
        ];
        
        // Get completion rate for each week
        const data = weeks.map(weekDate => {
            const weekData = task.weekly_data.find(w => w.week_start === weekDate);
            if (!weekData) return 0;
            
            // Calculate scheduled days for this task in this week
            // For simplicity, assume 7 days if daily, etc.
            let scheduledDays = 7;
            if (task.frequency === 'WEEKDAYS') scheduledDays = 5;
            if (task.frequency === 'WEEKENDS') scheduledDays = 2;
            if (task.frequency === 'CUSTOM' && task.custom_days) {
                scheduledDays = task.custom_days.split(',').length;
            }
            
            return scheduledDays > 0 ? Math.round((weekData.completed_days / scheduledDays) * 100) : 0;
        });
        
        return {
            label: task.name.length > 12 ? task.name.substring(0, 12) + '...' : task.name,
            data: data,
            borderColor: colors[index % colors.length],
            backgroundColor: colors[index % colors.length].replace('1)', '0.1)'),
            fill: true,
            tension: 0.4,
            borderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6
        };
    });
    
    if (trendChart) {
        trendChart.destroy();
    }
    
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: weekLabels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        padding: 15,
                        font: {
                            size: 11
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}
