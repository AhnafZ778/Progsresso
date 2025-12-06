// Pomodoro Timer Functionality
let pomodoroState = {
    isRunning: false,
    timeLeft: 25 * 60,
    duration: 25,
    sessionId: null,
    linkedTaskId: null,
    linkedTaskTitle: null,
    interval: null
};

// Sound file path - CHANGE THIS TO YOUR PREFERRED SOUND
const TIMER_SOUND_PATH = '/static/sounds/TIMER_COMPLETE_SOUND.mp3';

function initPomodoro() {
    loadFocusStats();
    loadTodaySessions();
    updateTimerDisplay();
}

function updateTimerDisplay() {
    const mins = Math.floor(pomodoroState.timeLeft / 60);
    const secs = pomodoroState.timeLeft % 60;
    document.getElementById('timer-display').textContent = 
        `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    
    // Update progress ring
    const progress = 1 - (pomodoroState.timeLeft / (pomodoroState.duration * 60));
    const ring = document.getElementById('timer-ring');
    if (ring) {
        const circumference = 2 * Math.PI * 90;
        ring.style.strokeDashoffset = circumference * (1 - progress);
    }
}

async function startTimer() {
    if (pomodoroState.isRunning) return;
    
    pomodoroState.isRunning = true;
    document.getElementById('start-btn').classList.add('hidden');
    document.getElementById('pause-btn').classList.remove('hidden');
    
    // Start session in backend
    try {
        const r = await fetch('/api/focus/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                duration_minutes: pomodoroState.duration,
                kanban_item_id: pomodoroState.linkedTaskId
            })
        });
        const data = await r.json();
        pomodoroState.sessionId = data.session.id;
    } catch(e) {
        console.error('Failed to start session:', e);
    }
    
    pomodoroState.interval = setInterval(() => {
        pomodoroState.timeLeft--;
        updateTimerDisplay();
        
        if (pomodoroState.timeLeft <= 0) {
            completeTimer();
        }
    }, 1000);
}

function pauseTimer() {
    if (!pomodoroState.isRunning) return;
    
    pomodoroState.isRunning = false;
    clearInterval(pomodoroState.interval);
    document.getElementById('start-btn').classList.remove('hidden');
    document.getElementById('pause-btn').classList.add('hidden');
}

async function completeTimer() {
    pauseTimer();
    playSound();
    
    // Complete session in backend
    if (pomodoroState.sessionId) {
        try {
            await fetch(`/api/focus/complete/${pomodoroState.sessionId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
        } catch(e) {
            console.error('Failed to complete session:', e);
        }
    }
    
    toast('Focus session complete!', 'success');
    resetTimer();
    loadFocusStats();
    loadTodaySessions();
}

function resetTimer() {
    pauseTimer();
    pomodoroState.timeLeft = pomodoroState.duration * 60;
    pomodoroState.sessionId = null;
    updateTimerDisplay();
}

function setTimerDuration(mins) {
    pomodoroState.duration = mins;
    pomodoroState.timeLeft = mins * 60;
    updateTimerDisplay();
    closeModal('timer-settings-modal');
    
    // Update active button
    document.querySelectorAll('.duration-btn').forEach(btn => {
        btn.classList.remove('active');
        if (parseInt(btn.dataset.mins) === mins) btn.classList.add('active');
    });
}

function linkTask(taskId, taskTitle) {
    pomodoroState.linkedTaskId = taskId;
    pomodoroState.linkedTaskTitle = taskTitle;
    document.getElementById('linked-task').textContent = taskTitle || 'No task linked';
    closeModal('link-task-modal');
}

function unlinkTask() {
    pomodoroState.linkedTaskId = null;
    pomodoroState.linkedTaskTitle = null;
    document.getElementById('linked-task').textContent = 'No task linked';
}

function playSound() {
    try {
        const audio = new Audio(TIMER_SOUND_PATH);
        audio.play().catch(() => {
            // Fallback: browser notification
            if (Notification.permission === 'granted') {
                new Notification('Focus Session Complete!', {
                    body: 'Great work! Take a break.',
                    icon: '/static/icons/icon_tomato.png'
                });
            }
        });
    } catch(e) {
        console.log('Sound not available');
    }
}

async function loadFocusStats() {
    try {
        const r = await fetch('/api/focus/stats');
        const data = await r.json();
        const stats = data.stats;
        
        document.getElementById('today-hours').textContent = stats.today_hours + 'h';
        document.getElementById('week-hours').textContent = stats.week_hours + 'h';
        document.getElementById('focus-streak').textContent = stats.streak_days + ' days';
        
        // Update motivation display
        const mot = stats.motivation_level;
        const box = document.getElementById('motivation-box');
        const img = document.getElementById('motivation-image');
        const txt = document.getElementById('motivation-text');
        
        if (box && img && txt) {
            box.classList.remove('hidden');
            img.src = mot.image_url;
            txt.textContent = mot.message;
            txt.style.color = '#B91C1C';
        }
    } catch(e) {
        console.error('Failed to load stats:', e);
    }
}

async function loadTodaySessions() {
    try {
        const r = await fetch('/api/focus/today');
        const data = await r.json();
        const container = document.getElementById('session-history');
        
        if (!data.sessions || !data.sessions.length) {
            container.innerHTML = '<p style="color:var(--brown);text-align:center;padding:1rem">No sessions yet today</p>';
            return;
        }
        
        container.innerHTML = data.sessions.map(s => `
            <div class="session-item">
                <span class="session-task">${s.task_title || 'Free focus'}</span>
                <span class="session-duration">${s.duration_minutes} min</span>
                <span class="session-status">${s.is_completed ? '<img src="/static/icons/icon_done.png" style="width: 14px; height: 14px;">' : '...'}</span>
            </div>
        `).join('');
    } catch(e) {
        console.error('Failed to load sessions:', e);
    }
}

function openTimerSettings() {
    openModal('timer-settings-modal');
}

function openLinkTaskModal() {
    // Populate with available tasks
    const container = document.getElementById('linkable-tasks');
    const allTasks = [...(kanbanData?.TODO || []), ...(kanbanData?.IN_PROGRESS || [])];
    
    if (!allTasks.length) {
        container.innerHTML = '<p style="text-align:center;color:var(--brown)">No tasks available</p>';
    } else {
        container.innerHTML = allTasks.map(t => `
            <button class="linkable-task-btn" onclick="linkTask(${t.id}, '${t.title.replace(/'/g, "\\'")}')">
                ${t.title}
            </button>
        `).join('');
    }
    openModal('link-task-modal');
}

/* ===== ICON SETTINGS ===== */
function openIconSettings() {
    const modal = document.getElementById('app-settings-modal');
    modal.classList.add('active');
    
    // Load current size
    const savedSize = localStorage.getItem('iconSize') || 24;
    document.getElementById('icon-size-slider').value = savedSize;
}

function closeIconSettings() {
    document.getElementById('app-settings-modal').classList.remove('active');
}

function updateIconSize(size) {
    document.documentElement.style.setProperty('--icon-size-base', size + 'px');
    localStorage.setItem('iconSize', size);
}

// Initialize icon size
document.addEventListener('DOMContentLoaded', () => {
    const savedSize = localStorage.getItem('iconSize') || 24;
    document.documentElement.style.setProperty('--icon-size-base', savedSize + 'px');
});

// Request notification permission
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}
