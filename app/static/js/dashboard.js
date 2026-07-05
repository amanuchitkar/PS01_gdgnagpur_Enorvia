let dashboardData = null;

async function loadDashboard() {
    try {
        const response = await fetch(`/api/dashboard/${CONVERSATION_ID}`);
        if (!response.ok) throw new Error('Failed to load dashboard');
        dashboardData = await response.json();
        renderDashboard();
    } catch (error) {
        console.error('Dashboard error:', error);
        document.getElementById('loading').innerHTML = `
            <div class="text-center">
                <p class="text-red-500 text-base mb-3">Failed to load dashboard</p>
                <a href="/" class="text-primary-600 hover:text-primary-700 hover:underline text-sm font-medium">← Start new conversation</a>
            </div>`;
    }
}

function renderDashboard() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('dashboard-content').classList.remove('hidden');
    document.getElementById('download-pdf-btn').classList.remove('hidden');

    // Stats
    document.getElementById('stat-emotion').textContent = dashboardData.dominant_emotion || 'neutral';
    document.getElementById('stat-stress').textContent = `${Math.round(dashboardData.average_stress || 0)}/100`;
    document.getElementById('stat-risk').textContent = dashboardData.risk_level || 'low';
    document.getElementById('stat-messages').textContent = dashboardData.message_count || 0;

    // Stress bar color
    const stress = dashboardData.average_stress || 0;
    const stressBar = document.getElementById('stat-stress-bar');
    stressBar.style.width = `${stress}%`;
    if (stress > 70) stressBar.className = 'h-full bg-gradient-to-r from-warm-400 to-red-400 rounded-full transition-all duration-1000 ease-out';
    else if (stress > 40) stressBar.className = 'h-full bg-gradient-to-r from-yellow-400 to-warm-400 rounded-full transition-all duration-1000 ease-out';
    else stressBar.className = 'h-full bg-gradient-to-r from-primary-400 to-calm-400 rounded-full transition-all duration-1000 ease-out';

    // Risk level color
    const riskEl = document.getElementById('stat-risk');
    if (dashboardData.risk_level === 'high') riskEl.classList.add('text-red-600');
    else if (dashboardData.risk_level === 'moderate') riskEl.classList.add('text-amber-600');
    else riskEl.classList.add('text-primary-600');

    // Summary
    document.getElementById('summary-text').textContent = dashboardData.summary || 'No summary available';

    // Concerns
    const concernsList = document.getElementById('concerns-list');
    if (dashboardData.concerns && dashboardData.concerns.length > 0) {
        concernsList.innerHTML = dashboardData.concerns.map(c =>
            `<span class="inline-flex items-center px-3 py-1.5 bg-calm-50 text-calm-700 text-xs font-medium rounded-full border border-calm-100">${escapeHtml(c)}</span>`
        ).join('');
    }

    // Charts
    renderStressChart();
    renderEmotionChart();

    // Wellness Plan
    if (dashboardData.wellness_plan) {
        renderWellnessPlan(dashboardData.wellness_plan);
    }
}

function renderStressChart() {
    const ctx = document.getElementById('stress-chart').getContext('2d');
    const timeline = dashboardData.timeline || [];

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeline.map((_, i) => `Msg ${i + 1}`),
            datasets: [{
                label: 'Stress Score',
                data: timeline.map(t => t.stress_score),
                borderColor: '#f97316',
                backgroundColor: 'rgba(249, 115, 22, 0.08)',
                borderWidth: 2.5,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#ffffff',
                pointBorderColor: '#f97316',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointHoverBackgroundColor: '#f97316',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index',
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1f2937',
                    titleFont: { size: 12, weight: '600' },
                    bodyFont: { size: 11 },
                    padding: 10,
                    cornerRadius: 8,
                    displayColors: false,
                    callbacks: {
                        title: function(context) {
                            return `Message ${context[0].dataIndex + 1}`;
                        },
                        label: function(context) {
                            return `Stress: ${context.parsed.y}/100`;
                        },
                        afterLabel: function(context) {
                            const item = timeline[context.dataIndex];
                            return item ? `Emotion: ${item.emotion}` : '';
                        }
                    }
                }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: '#f3f4f6', drawBorder: false },
                    ticks: {
                        font: { size: 11 },
                        color: '#9ca3af',
                        stepSize: 25,
                        callback: function(value) { return value; }
                    },
                    border: { display: false },
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 11 }, color: '#9ca3af' },
                    border: { display: false },
                }
            }
        }
    });
}

function renderEmotionChart() {
    const ctx = document.getElementById('emotion-chart').getContext('2d');
    const freq = dashboardData.emotion_frequency || {};
    const labels = Object.keys(freq);
    const data = Object.values(freq);

    const colors = [
        '#22c55e', '#0ea5e9', '#f97316', '#ef4444', '#8b5cf6',
        '#ec4899', '#14b8a6', '#f59e0b', '#6366f1', '#84cc16'
    ];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.map(l => l.charAt(0).toUpperCase() + l.slice(1)),
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 3,
                borderColor: '#ffffff',
                hoverBorderWidth: 0,
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '55%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 16,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        font: { size: 12 },
                        color: '#4b5563',
                    }
                },
                tooltip: {
                    backgroundColor: '#1f2937',
                    titleFont: { size: 12, weight: '600' },
                    bodyFont: { size: 11 },
                    padding: 10,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percent = Math.round((context.parsed / total) * 100);
                            return ` ${context.label}: ${context.parsed} (${percent}%)`;
                        }
                    }
                }
            }
        }
    });
}

function renderWellnessPlan(plan) {
    // Assessment
    if (plan.overall_assessment) {
        document.querySelector('#plan-assessment p').textContent = plan.overall_assessment;
    }

    // Days
    const daysContainer = document.getElementById('wellness-days');
    if (plan.days && plan.days.length > 0) {
        daysContainer.innerHTML = plan.days.map(day => `
            <div class="bg-gray-50 rounded-lg p-4 md:p-5 border border-gray-100 hover:border-primary-100 hover:bg-primary-50/20 transition-all">
                <div class="flex items-center gap-3 mb-4">
                    <span class="w-9 h-9 bg-primary-100 text-primary-700 rounded-lg flex items-center justify-center text-sm font-bold shadow-sm">${day.day}</span>
                    <h4 class="text-sm md:text-base font-semibold text-gray-800">${escapeHtml(day.theme)}</h4>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                    ${day.activities.map(act => `
                        <div class="bg-white rounded-lg p-3 md:p-4 border border-gray-100 shadow-sm">
                            <div class="flex items-center gap-2 mb-2">
                                <span class="text-xs font-semibold text-primary-600 uppercase tracking-wide">${escapeHtml(act.time)}</span>
                                <span class="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">${escapeHtml(act.duration)}</span>
                            </div>
                            <p class="text-sm font-medium text-gray-800 mb-1">${escapeHtml(act.activity)}</p>
                            <p class="text-xs text-gray-500 leading-relaxed">${escapeHtml(act.description)}</p>
                            <p class="text-xs text-primary-600 mt-2 italic leading-relaxed">"${escapeHtml(act.reason)}"</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
    }

    // Recurring habits
    const habitsList = document.getElementById('habits-list');
    if (plan.recurring_habits && plan.recurring_habits.length > 0) {
        habitsList.innerHTML = plan.recurring_habits.map(habit => `
            <div class="bg-primary-50 rounded-lg p-4 border border-primary-100">
                <p class="text-sm font-semibold text-gray-800 mb-1">${escapeHtml(habit.habit)}</p>
                <p class="text-xs font-medium text-primary-600 mb-2">${escapeHtml(habit.frequency)}</p>
                <p class="text-xs text-gray-600 leading-relaxed">${escapeHtml(habit.reason)}</p>
            </div>
        `).join('');
    }

    // Reminders
    const remindersList = document.getElementById('reminders-list');
    if (plan.important_reminders && plan.important_reminders.length > 0) {
        remindersList.innerHTML = plan.important_reminders.map(r =>
            `<li class="text-sm text-amber-800 flex items-start gap-2">
                <svg class="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                <span class="leading-relaxed">${escapeHtml(r)}</span>
            </li>`
        ).join('');
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Load dashboard on page load
document.addEventListener('DOMContentLoaded', loadDashboard);

async function downloadPDF() {
    const btn = document.getElementById('download-pdf-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = `<svg class="w-4 h-4 animate-spin inline-block" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg> Generating...`;
    btn.disabled = true;

    try {
        const response = await fetch(`/api/report/${CONVERSATION_ID}/pdf`);
        if (!response.ok) throw new Error('PDF generation failed');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `kindered_wellness_report.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    } catch (error) {
        console.error('PDF download error:', error);
        alert('Failed to generate PDF report. Please try again.');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}
