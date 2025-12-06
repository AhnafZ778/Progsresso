/**
 * HabitPulse - Progress Logging JavaScript
 */

let currentTask = null;
let currentDate = null;

// Open Progress Modal
function openProgressModal(taskId, dateStr) {
    // Find task from weekData
    currentTask = weekData.tasks.find(t => t.id === taskId);
    currentDate = dateStr;
    
    if (!currentTask) {
        showToast('Task not found', 'error');
        return;
    }
    
    // Check if past date (not today) - don't allow editing past dates unless already logged
    const dayData = currentTask.days.find(d => d.date === dateStr);
    if (dayData.is_past && !dayData.is_today && !dayData.log) {
        showToast('Cannot log progress for past dates', 'warning');
        return;
    }
    
    document.getElementById('progress-task-id').value = taskId;
    document.getElementById('progress-date').value = dateStr;
    document.getElementById('progress-task-name').textContent = currentTask.name;
    document.getElementById('progress-date-label').textContent = formatFullDate(dateStr);
    
    // Render appropriate input based on metric type
    renderProgressInput(currentTask, dayData);
    
    // Set notes if editing
    document.getElementById('progress-notes').value = dayData.log ? dayData.log.notes || '' : '';
    
    document.getElementById('progress-modal').classList.remove('hidden');
}

function renderProgressInput(task, dayData) {
    const container = document.getElementById('progress-input-section');
    const existingValue = dayData.log ? dayData.log.metric_value : null;
    
    switch (task.metric_type) {
        case 'TIME':
            container.innerHTML = `
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        How many ${task.metric_unit || 'minutes'}? *
                    </label>
                    <div class="flex items-center space-x-2">
                        <input type="number" id="progress-value" min="0" step="1" required
                               class="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                               value="${existingValue || ''}" placeholder="e.g., 45">
                        <span class="text-gray-500">${task.metric_unit || 'minutes'}</span>
                    </div>
                    ${task.target_value ? `<p class="text-sm text-gray-500 mt-1">Target: ${task.target_value} ${task.metric_unit || ''}</p>` : ''}
                </div>
            `;
            break;
            
        case 'COUNT':
            container.innerHTML = `
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        How many ${task.metric_unit || 'reps'}? *
                    </label>
                    <div class="flex items-center space-x-2">
                        <input type="number" id="progress-value" min="0" step="1" required
                               class="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                               value="${existingValue || ''}" placeholder="e.g., 25">
                        <span class="text-gray-500">${task.metric_unit || ''}</span>
                    </div>
                    ${task.target_value ? `<p class="text-sm text-gray-500 mt-1">Target: ${task.target_value} ${task.metric_unit || ''}</p>` : ''}
                </div>
            `;
            break;
            
        case 'INTENSITY':
            const intensityValue = existingValue || 5;
            container.innerHTML = `
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-3">
                        Rate your intensity (1-10) *
                    </label>
                    <div class="space-y-3">
                        <input type="range" id="progress-value" min="1" max="10" step="1" 
                               class="intensity-slider" value="${intensityValue}">
                        <div class="flex justify-between text-sm text-gray-500">
                            <span>Low</span>
                            <span class="font-bold text-2xl text-primary-600" id="intensity-display">${intensityValue}</span>
                            <span>High</span>
                        </div>
                    </div>
                </div>
            `;
            
            // Add event listener for slider
            setTimeout(() => {
                const slider = document.getElementById('progress-value');
                const display = document.getElementById('intensity-display');
                slider.addEventListener('input', () => {
                    display.textContent = slider.value;
                });
            }, 0);
            break;
            
        case 'PROGRESS':
            const progressValue = existingValue || 0;
            container.innerHTML = `
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-3">
                        How much progress? *
                    </label>
                    <div class="space-y-3">
                        <input type="range" id="progress-value" min="0" max="100" step="5" 
                               class="progress-slider" value="${progressValue}">
                        <div class="text-center">
                            <span class="font-bold text-3xl text-primary-600" id="progress-display">${progressValue}%</span>
                        </div>
                    </div>
                </div>
            `;
            
            // Add event listener for slider
            setTimeout(() => {
                const slider = document.getElementById('progress-value');
                const display = document.getElementById('progress-display');
                slider.addEventListener('input', () => {
                    display.textContent = slider.value + '%';
                });
            }, 0);
            break;
            
        case 'BOOLEAN':
        default:
            container.innerHTML = `
                <div class="text-center py-4">
                    <div class="text-6xl mb-2">✓</div>
                    <p class="text-gray-600">Mark this task as complete for today</p>
                </div>
            `;
            break;
    }
}

// Close Progress Modal
function closeProgressModal() {
    document.getElementById('progress-modal').classList.add('hidden');
    currentTask = null;
    currentDate = null;
}

// Handle Progress Form Submit
document.getElementById('progress-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const taskId = document.getElementById('progress-task-id').value;
    const dateStr = document.getElementById('progress-date').value;
    const notes = document.getElementById('progress-notes').value.trim() || null;
    
    // Get value based on metric type
    let value = null;
    if (currentTask.metric_type !== 'BOOLEAN') {
        const valueInput = document.getElementById('progress-value');
        if (!valueInput || !valueInput.value) {
            showToast('Please enter a value', 'error');
            return;
        }
        value = parseFloat(valueInput.value);
        
        // Validate ranges
        if (currentTask.metric_type === 'INTENSITY' && (value < 1 || value > 10)) {
            showToast('Intensity must be between 1 and 10', 'error');
            return;
        }
        if (currentTask.metric_type === 'PROGRESS' && (value < 0 || value > 100)) {
            showToast('Progress must be between 0 and 100', 'error');
            return;
        }
        if (value < 0) {
            showToast('Value cannot be negative', 'error');
            return;
        }
    }
    
    try {
        await apiRequest('/api/progress', 'POST', {
            task_id: parseInt(taskId),
            date: dateStr,
            value: value,
            notes: notes
        });
        
        showToast('Progress logged!', 'success');
        closeProgressModal();
        await loadWeekData();
    } catch (error) {
        showToast(error.message, 'error');
    }
});
