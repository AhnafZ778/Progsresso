/**
 * HabitPulse - Task Management JavaScript
 */

// Open Add Task Modal
function openAddTaskModal() {
    const taskModalTitle = document.getElementById('task-modal-title');
    if (taskModalTitle) {
        taskModalTitle.innerHTML = '<img src="/static/icons/icon_sparkles.png" style="width: 20px; height: 20px; vertical-align: middle; margin-right: 6px;"> Add New Habit';
    }
    document.getElementById('task-form').reset();
    document.getElementById('task-id').value = '';
    document.getElementById('metric-type-section').style.display = 'block';
    document.getElementById('metric-unit-section').classList.add('hidden');
    document.getElementById('custom-days-section').classList.add('hidden');
    
    // Reset radio buttons to defaults
    document.querySelector('input[name="metric-type"][value="BOOLEAN"]').checked = true;
    document.querySelector('input[name="frequency"][value="DAILY"]').checked = true;
    
    // Reset custom day checkboxes
    document.querySelectorAll('input[name="custom-day"]').forEach(cb => cb.checked = false);
    
    document.getElementById('task-modal').classList.remove('hidden');
}

// Open Edit Task Modal
async function openEditTaskModal(taskId) {
    try {
        const response = await apiRequest(`/api/tasks/${taskId}`);
        const task = response.task;
        
        document.getElementById('task-modal-title').innerHTML = '<img src="/static/icons/icon_pencil.png" style="width: 20px; height: 20px; vertical-align: middle; margin-right: 6px;"> Edit Habit';
        document.getElementById('task-id').value = task.id;
        document.getElementById('task-name').value = task.name;
        document.getElementById('task-description').value = task.description || '';
        document.getElementById('metric-unit').value = task.metric_unit || '';
        document.getElementById('target-value').value = task.target_value || '';
        
        // Set metric type (disabled for editing)
        document.querySelectorAll('input[name="metric-type"]').forEach(radio => {
            radio.checked = radio.value === task.metric_type;
            radio.disabled = true; // Can't change metric type
        });
        document.getElementById('metric-type-section').style.opacity = '0.6';
        
        // Show/hide unit section
        if (task.metric_type !== 'BOOLEAN') {
            document.getElementById('metric-unit-section').classList.remove('hidden');
        } else {
            document.getElementById('metric-unit-section').classList.add('hidden');
        }
        
        // Set frequency
        document.querySelectorAll('input[name="frequency"]').forEach(radio => {
            radio.checked = radio.value === task.frequency;
        });
        
        // Set custom days
        if (task.frequency === 'CUSTOM' && task.custom_days) {
            document.getElementById('custom-days-section').classList.remove('hidden');
            const days = task.custom_days.split(',');
            document.querySelectorAll('input[name="custom-day"]').forEach(cb => {
                cb.checked = days.includes(cb.value);
            });
        } else {
            document.getElementById('custom-days-section').classList.add('hidden');
        }
        
        document.getElementById('task-modal').classList.remove('hidden');
    } catch (error) {
        showToast('Failed to load task: ' + error.message, 'error');
    }
}

// Close Task Modal
function closeTaskModal() {
    document.getElementById('task-modal').classList.add('hidden');
    
    // Re-enable metric type radios
    document.querySelectorAll('input[name="metric-type"]').forEach(radio => {
        radio.disabled = false;
    });
    document.getElementById('metric-type-section').style.opacity = '1';
}

// Handle Task Form Submit
document.getElementById('task-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const taskId = document.getElementById('task-id').value;
    const isEdit = !!taskId;
    
    // Gather form data
    const metricType = document.querySelector('input[name="metric-type"]:checked').value;
    const frequency = document.querySelector('input[name="frequency"]:checked').value;
    
    const data = {
        name: document.getElementById('task-name').value.trim(),
        description: document.getElementById('task-description').value.trim() || null,
        metric_type: metricType,
        metric_unit: metricType !== 'BOOLEAN' ? document.getElementById('metric-unit').value.trim() : null,
        target_value: document.getElementById('target-value').value ? parseFloat(document.getElementById('target-value').value) : null,
        frequency: frequency
    };
    
    // Handle custom days
    if (frequency === 'CUSTOM') {
        const customDays = Array.from(document.querySelectorAll('input[name="custom-day"]:checked'))
            .map(cb => cb.value)
            .join(',');
        
        if (!customDays) {
            showToast('Please select at least one day', 'error');
            return;
        }
        data.custom_days = customDays;
    }
    
    // Validate
    if (!data.name) {
        showToast('Task name is required', 'error');
        return;
    }
    
    if (metricType !== 'BOOLEAN' && !data.metric_unit) {
        showToast('Unit is required for this metric type', 'error');
        return;
    }
    
    try {
        if (isEdit) {
            // Don't send metric_type for edits
            delete data.metric_type;
            await apiRequest(`/api/tasks/${taskId}`, 'PUT', data);
            showToast('Habit updated!', 'success');
        } else {
            await apiRequest('/api/tasks', 'POST', data);
            showToast('Habit created!', 'success');
        }
        
        closeTaskModal();
        await loadWeekData();
    } catch (error) {
        showToast(error.message, 'error');
    }
});

// Delete Modal
function openDeleteModal(taskId, taskName) {
    document.getElementById('delete-task-id').value = taskId;
    document.getElementById('delete-task-name').textContent = `Are you sure you want to delete "${taskName}"?`;
    document.getElementById('delete-modal').classList.remove('hidden');
}

function closeDeleteModal() {
    document.getElementById('delete-modal').classList.add('hidden');
}

async function deleteTask(permanent) {
    const taskId = document.getElementById('delete-task-id').value;
    
    try {
        await apiRequest(`/api/tasks/${taskId}`, 'DELETE', { permanent });
        showToast(permanent ? 'Habit deleted!' : 'Habit archived!', 'success');
        closeDeleteModal();
        await loadWeekData();
    } catch (error) {
        showToast(error.message, 'error');
    }
}
