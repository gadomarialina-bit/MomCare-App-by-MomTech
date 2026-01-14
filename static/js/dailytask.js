
document.addEventListener('DOMContentLoaded', () => {
    const calendarGrid = document.getElementById('calendarGrid');
    const currentMonthDisplay = document.getElementById('currentMonthDisplay');
    const prevMonthBtn = document.getElementById('prevMonthBtn');
    const nextMonthBtn = document.getElementById('nextMonthBtn');
    const timelineGrid = document.getElementById('timelineGrid');

    // Modal elements
    const modal = document.getElementById('taskModal');
    const modalTitle = document.getElementById('modalTitle');
    const taskForm = document.getElementById('taskForm');
    const closeBtn = document.querySelector('.close-btn');
    const btnAddTask = document.getElementById('addTaskBtn');

    // Edit/Delete
    const btnEditTask = document.getElementById('editTaskBtn');
    const btnDeleteTask = document.getElementById('deleteSelectedTaskBtn');
    const deleteTaskModal = document.getElementById('deleteTaskModal');
    const cancelDeleteTaskBtn = document.getElementById('cancelDeleteTaskBtn');
    const confirmDeleteTaskBtn = document.getElementById('confirmDeleteTaskBtn');

    // Toast notifications
    function showToast(message, type = 'info', timeout = 3000) {
        const container = document.getElementById('toastContainer');
        if (!container) { console.log(message); return; }
        const toast = document.createElement('div');
        const base = 'px-4 py-2 rounded-md shadow-lg flex items-center gap-3 text-sm';
        let color = 'bg-white text-gray-800 border';
        if (type === 'success') color = 'bg-green-50 text-green-800 border border-green-200';
        if (type === 'error') color = 'bg-red-50 text-red-800 border border-red-200';
        if (type === 'info') color = 'bg-blue-50 text-blue-800 border border-blue-200';
        toast.className = `${base} ${color}`;
        toast.innerHTML = `<div class="flex-1">${message}</div><button class="ml-2 text-xs text-gray-500 close-toast">✕</button>`;
        container.appendChild(toast);
        const remover = () => { toast.remove(); };
        toast.querySelector('.close-toast').addEventListener('click', remover);
        setTimeout(remover, timeout);
    }

    let currentDate = new Date();
    const today = new Date();
    let selectedDate = new Date(); // default to today
    let selectedTaskId = null; // for edit/delete
    let fetchedTasks = [];

    // --- CALENDAR LOGIC ---
    function renderCalendar(date) {
        calendarGrid.innerHTML = '';
        const year = date.getFullYear();
        const month = date.getMonth();

        currentMonthDisplay.textContent = date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        // Empty slots for previous month
        for (let i = 0; i < firstDay; i++) {
            const emptyCell = document.createElement('div');
            emptyCell.className = 'calendar-empty p-2';
            calendarGrid.appendChild(emptyCell);
        }

        // Days
        for (let d = 1; d <= daysInMonth; d++) {
            const dayCell = document.createElement('div');
            dayCell.textContent = d;
            dayCell.className = 'calendar-day text-center px-2 py-1 rounded cursor-pointer hover:bg-sky-100 text-sm';

            // Apply Tailwind highlight if this is the selected date
            if (selectedDate && d === selectedDate.getDate() && month === selectedDate.getMonth() && year === selectedDate.getFullYear()) {
                dayCell.classList.add('bg-amber-300', 'text-green-900', 'font-semibold');
            }

            // Subtle highlight for today's date (not the same as selected)
            if (d === today.getDate() && month === today.getMonth() && year === today.getFullYear()) {
                // don't override selected styling
                if (!(selectedDate && d === selectedDate.getDate() && month === selectedDate.getMonth() && year === selectedDate.getFullYear())) {
                    dayCell.classList.add('ring-2', 'ring-green-300');
                }
            }

            dayCell.addEventListener('click', () => {
                selectedDate = new Date(year, month, d);
                renderCalendar(currentDate); // re-render to update active classes
                loadTasks(); // fetch/filter tasks for this date
                // enable Add Task button visually (Tailwind classes)
                btnAddTask.classList.remove('opacity-60', 'cursor-not-allowed');
            });

            calendarGrid.appendChild(dayCell);
        }
    }

    prevMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar(currentDate);
    });

    nextMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar(currentDate);
    });

    // --- TIMELINE LOGIC ---
    function renderTimeline() {
        timelineGrid.innerHTML = '';

        // Always render the 24-hour grid to avoid layout shifts
        for (let i = 0; i < 24; i++) {
            const hourDiv = document.createElement('div');
            hourDiv.className = 'timeline-hour h-14 border-t border-gray-200 relative';
            hourDiv.setAttribute('data-hour', `${i}:00`);
            const label = document.createElement('div');
            label.className = 'absolute -left-16 -top-1 text-xs text-gray-500';
            label.textContent = `${i}:00`;
            hourDiv.appendChild(label);
            timelineGrid.appendChild(hourDiv);
        }

        // If no date selected, show a centered overlay message but keep the grid
        if (!selectedDate) {
            const overlay = document.createElement('div');
            overlay.className = 'absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white bg-opacity-90 px-4 py-2 rounded-md shadow z-10 pointer-events-none text-gray-500';
            overlay.textContent = 'Please select a date from the calendar to view or add tasks.';
            timelineGrid.appendChild(overlay);
            // visually disable add button
            btnAddTask.classList.add('opacity-60', 'cursor-not-allowed');
            // clear stats/priority
            updateStats([]);
            return;
        }

        // If date is selected, enable add button
        btnAddTask.classList.remove('opacity-60', 'cursor-not-allowed');

        // Render tasks
        // Filter tasks by selectedDate
        const dateStr = selectedDate.toISOString().split('T')[0]; // YYYY-MM-DD
        const todaysAllTasks = fetchedTasks.filter(t => t.task_date === dateStr);
        // separate active tasks (not completed) from completed ones
        const todaysTasks = todaysAllTasks.filter(t => !t.completed);
        const doneTasks = todaysAllTasks.filter(t => t.completed);

        // Prepare tasks with minute ranges
        const tasksWithRange = todaysTasks.map(t => ({
            ...t,
            startMin: Math.round((t.start_time || 0) * 60),
            endMin: Math.round(((t.start_time || 0) + (t.duration || 0)) * 60)
        })).sort((a, b) => a.startMin - b.startMin || a.endMin - b.endMin);

        // Cluster overlapping tasks
        const clusters = [];
        tasksWithRange.forEach(t => {
            if (!clusters.length) { clusters.push({ items: [t], end: t.endMin }); return; }
            const last = clusters[clusters.length - 1];
            if (t.startMin < last.end) {
                last.items.push(t);
                last.end = Math.max(last.end, t.endMin);
            } else {
                clusters.push({ items: [t], end: t.endMin });
            }
        });

        // Layout each cluster side-by-side
        const baseLeft = 16; // px inside timeline
        const gap = 8; // px between columns
        const containerWidth = timelineGrid.clientWidth || timelineGrid.getBoundingClientRect().width || 600;

        clusters.forEach(cluster => {
            const colsEnd = [];
            const items = cluster.items;
            // assign columns greedily
            items.forEach(item => {
                let col = colsEnd.findIndex(end => item.startMin >= end);
                if (col === -1) { col = colsEnd.length; colsEnd.push(item.endMin); }
                else { colsEnd[col] = Math.max(colsEnd[col], item.endMin); }
                item._col = col;
            });

            const totalCols = colsEnd.length || 1;
            const availWidth = Math.max(containerWidth - baseLeft - 16, 200);
            const colWidth = Math.floor((availWidth - (totalCols - 1) * gap) / totalCols);

            // render items
            items.forEach(task => {
                const taskEl = document.createElement('div');
                taskEl.className = 'task-item absolute rounded-md px-2 py-1 text-sm text-[#104b0b] shadow flex items-start justify-between';
                if (task.is_priority) taskEl.classList.add('priority', 'border-2', 'border-red-600');
                const top = task.startMin;
                const height = Math.max(task.endMin - task.startMin, 10);
                const leftPx = baseLeft + (task._col * (colWidth + gap));
                taskEl.style.top = `${top}px`;
                taskEl.style.height = `${height}px`;
                taskEl.style.left = `${leftPx}px`;
                taskEl.style.width = `${colWidth}px`;
                taskEl.setAttribute('data-task-id', task.id);
                taskEl.style.backgroundColor = getColor(task.color);

                const titleDiv = document.createElement('div');
                titleDiv.className = 'flex-1 truncate pr-2';
                titleDiv.textContent = task.title;

                const doneBtn = document.createElement('button');
                doneBtn.className = 'ml-2 text-green-700 bg-white/60 hover:bg-white/80 rounded-full w-7 h-7 flex items-center justify-center text-xs';
                doneBtn.title = 'Mark as done';
                doneBtn.innerHTML = '<i class="fas fa-check"></i>';
                doneBtn.addEventListener('click', (e) => { e.stopPropagation(); markTaskDone(task.id, true); });

                taskEl.appendChild(titleDiv);
                taskEl.appendChild(doneBtn);
                taskEl.addEventListener('click', (e) => { e.stopPropagation(); selectTask(task.id); });
                timelineGrid.appendChild(taskEl);
            });
        });

        // Update counts (pass all tasks for the date so completed count is accurate)
        updateStats(todaysAllTasks);

        // Render the completed tasks list for this date
        renderDoneList(doneTasks);
    }

    function getColor(colorName) {
        // map names from select to hex
        switch (colorName) {
            case 'orange': return '#fecc47'; // brand-yellow
            case 'green': return '#5a8d26'; // brand-light-green
            case 'yellow-green': return '#D6E6C7'; // lighter green
            default: return '#fecc47';
        }
    }

    function selectTask(id) {
        selectedTaskId = id;
        // Dim all tasks and remove previous highlight
        document.querySelectorAll('.task-item').forEach(el => {
            el.style.opacity = '0.6';
            el.classList.remove('ring-2', 'ring-amber-300', 'ring-green-400');
        });

        // Highlight the selected task (green ring)
        const el = document.querySelector(`.task-item[data-task-id="${id}"]`);
        if (el) {
            el.style.opacity = '1';
            el.classList.add('ring-2', 'ring-green-400');
        }
    }

    function updateStats(tasks) {
        const completed = tasks.filter(t => t.completed).length;
        document.getElementById('taskDoneCount').textContent = `${completed} Tasks Completed`;

        const priorityList = document.getElementById('priorityList');
        priorityList.innerHTML = '';
        tasks.filter(t => t.is_priority).forEach(t => {
            const li = document.createElement('li');
            li.textContent = t.title;
            priorityList.appendChild(li);
        });
    }

    // --- API CALLS ---
    function loadTasks() {
        fetch('/api/tasks')
            .then(res => res.json())
            .then(data => {
                fetchedTasks = data;
                renderTimeline();
            })
            .catch(err => console.error('Error loading tasks:', err));
    }

    function markTaskDone(id, done) {
        fetch(`/api/tasks/${id}`, {
            method: 'PUT', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ completed: done })
        }).then(async res => {
            if (!res.ok) {
                const d = await res.json().catch(() => ({}));
                showToast('Unable to update task: ' + (d.error || res.status), 'error');
                return;
            }
            showToast(done ? 'Task marked done' : 'Task restored', 'success');
            loadTasks();
            selectedTaskId = null;
        }).catch(err => { console.error(err); showToast('Network error', 'error'); });
    }

    function renderDoneList(doneTasks) {
        const doneListEl = document.getElementById('doneList');
        if (!doneListEl) return;
        doneListEl.innerHTML = '';
        if (!doneTasks || !doneTasks.length) {
            doneListEl.innerHTML = '<li class="text-xs text-gray-400">No completed tasks for this date.</li>';
            return;
        }
        doneTasks.forEach(t => {
            const li = document.createElement('li');
            li.className = 'flex items-center justify-between p-2 border rounded-md bg-gray-50';
            const left = document.createElement('div');
            left.className = 'flex-1';
            left.innerHTML = `<div class="font-medium truncate">${escapeHtml(t.title)}</div><div class="text-xs text-gray-500">${t.start_time !== null ? (t.start_time + 'h') : ''}</div>`;
            const undo = document.createElement('button');
            undo.className = 'text-xs text-blue-600 px-2 py-1 rounded-md';
            undo.textContent = 'Undo';
            undo.addEventListener('click', () => markTaskDone(t.id, false));
            li.appendChild(left);
            li.appendChild(undo);
            doneListEl.appendChild(li);
        });
    }

    // --- REMINDER API ---
    // Scheduled reminder items (multiple) handlers follow

    // --- Scheduled reminder items (multiple) ---
    const addReminderToggle = document.getElementById('addReminderToggle');
    const addReminderForm = document.getElementById('addReminderForm');
    const newReminderTitle = document.getElementById('newReminderTitle');
    const newReminderAt = document.getElementById('newReminderAt');
    const newReminderMessage = document.getElementById('newReminderMessage');
    const createReminderBtn = document.getElementById('createReminderBtn');
    const cancelCreateReminderBtn = document.getElementById('cancelCreateReminderBtn');
    const reminderListEl = document.getElementById('reminderList');
    // Delete reminder modal elements
    const deleteReminderModal = document.getElementById('deleteReminderModal');
    const cancelDeleteReminderBtn = document.getElementById('cancelDeleteReminderBtn');
    const confirmDeleteReminderBtn = document.getElementById('confirmDeleteReminderBtn');
    let pendingReminderDeleteId = null;

    function toggleAddForm(show) {
        if (!addReminderForm) return;
        addReminderForm.classList.toggle('hidden', !show);
    }

    if (addReminderToggle) addReminderToggle.addEventListener('click', () => toggleAddForm(true));
    if (cancelCreateReminderBtn) cancelCreateReminderBtn.addEventListener('click', (e) => { e.preventDefault(); toggleAddForm(false); });

    function loadReminderItems() {
        if (!reminderListEl) return;
        fetch('/api/reminders')
            .then(res => {
                if (res.status === 401) throw new Error('Not authenticated');
                return res.json();
            })
            .then(data => {
                const items = data.reminders || [];
                reminderListEl.innerHTML = '';
                items.forEach(item => {
                    const li = document.createElement('li');
                    li.className = 'p-2 border rounded-md bg-gray-50';
                    const when = item.remind_at ? new Date(item.remind_at).toLocaleString() : 'No time';
                    li.innerHTML = `<div class="flex justify-between items-start">
                        <div>
                            <div class="font-semibold">${escapeHtml(item.title || '(no title)')}</div>
                            <div class="text-xs text-gray-600">${when}</div>
                            <div class="text-sm mt-1">${escapeHtml(item.message || '')}</div>
                        </div>
                        <div class="flex flex-col items-end gap-2">
                            <button data-id="${item.id}" class="edit-reminder text-blue-600 text-sm">Edit</button>
                            <button data-id="${item.id}" class="delete-reminder text-red-600 text-sm">Delete</button>
                        </div>
                    </div>`;
                    reminderListEl.appendChild(li);
                });
                // attach delete/edit handlers
                document.querySelectorAll('.delete-reminder').forEach(btn => btn.addEventListener('click', (e) => {
                    const id = e.target.getAttribute('data-id');
                    // open modal to confirm deletion
                    pendingReminderDeleteId = id;
                    if (deleteReminderModal) deleteReminderModal.classList.remove('hidden');
                }));
                document.querySelectorAll('.edit-reminder').forEach(btn => btn.addEventListener('click', (e) => {
                    const id = e.target.getAttribute('data-id');
                    startEditReminder(id);
                }));
            }).catch(err => console.error('Error loading reminder items:', err));
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str).replace(/[&<>"']/g, function (s) {
            return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": "&#39;" })[s];
        });
    }

    function createReminder() {
        const payload = {
            title: newReminderTitle.value,
            message: newReminderMessage.value,
            remind_at: newReminderAt.value || null
        };
        createReminderBtn.disabled = true;
        fetch('/api/reminders', {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
        }).then(res => res.json()).then(data => {
            createReminderBtn.disabled = false;
            if (data.error) { showToast('Unable to create reminder: ' + data.error, 'error'); return; }
            // clear form
            newReminderTitle.value = '';
            newReminderAt.value = '';
            newReminderMessage.value = '';
            toggleAddForm(false);
            loadReminderItems();
        }).catch(err => { createReminderBtn.disabled = false; console.error(err); showToast('Error creating reminder', 'error'); });
    }

    function deleteReminder(id) {
        fetch(`/api/reminders/${id}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(() => {
                showToast('Reminder deleted', 'success');
                loadReminderItems();
            }).catch(err => { console.error(err); showToast('Error deleting reminder', 'error'); });
    }

    function startEditReminder(id) {
        // fetch item and replace its list entry with an edit form
        fetch('/api/reminders').then(res => res.json()).then(data => {
            const item = (data.reminders || []).find(r => String(r.id) === String(id));
            if (!item) { showToast('Reminder not found', 'error'); return; }
            // build edit form
            const li = document.createElement('li');
            li.className = 'p-2 border rounded-md bg-gray-50';
            li.innerHTML = `
                <input class="w-full mb-2 p-2 border rounded-md" data-edit-id value="${escapeHtml(item.title || '')}">
                <input type="datetime-local" class="w-full mb-2 p-2 border rounded-md" data-edit-at value="${item.remind_at ? item.remind_at.replace('Z', '') : ''}">
                <textarea class="w-full mb-2 p-2 border rounded-md" data-edit-msg rows="2">${escapeHtml(item.message || '')}</textarea>
                <div class="flex gap-2">
                    <button data-save-id class="bg-green-600 text-white px-3 py-1 rounded-md text-sm">Save</button>
                    <button data-cancel class="bg-gray-200 text-gray-700 px-3 py-1 rounded-md text-sm">Cancel</button>
                </div>`;
            // replace existing list and attach handlers
            reminderListEl.innerHTML = '';
            reminderListEl.appendChild(li);
            li.querySelector('[data-cancel]').addEventListener('click', () => loadReminderItems());
            li.querySelector('[data-save-id]').addEventListener('click', () => {
                const title = li.querySelector('[data-edit-id]').value;
                const at = li.querySelector('[data-edit-at]').value || null;
                const msg = li.querySelector('[data-edit-msg]').value;
                fetch(`/api/reminders/${id}`, {
                    method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title, message: msg, remind_at: at })
                }).then(res => res.json()).then(() => loadReminderItems()).catch(err => { console.error(err); showToast('Error updating reminder', 'error'); });
            });
        });
    }

    if (createReminderBtn) createReminderBtn.addEventListener('click', (e) => { e.preventDefault(); createReminder(); });

    // load scheduled reminders initially
    loadReminderItems();

    // Reminder delete modal handlers
    function closeDeleteReminderModal() {
        if (!deleteReminderModal) return;
        deleteReminderModal.classList.add('hidden');
        pendingReminderDeleteId = null;
    }

    if (cancelDeleteReminderBtn) cancelDeleteReminderBtn.addEventListener('click', (e) => { e.preventDefault(); closeDeleteReminderModal(); });
    if (confirmDeleteReminderBtn) confirmDeleteReminderBtn.addEventListener('click', (e) => {
        e.preventDefault();
        if (!pendingReminderDeleteId) { closeDeleteReminderModal(); return; }
        deleteReminder(pendingReminderDeleteId);
        closeDeleteReminderModal();
    });

    // --- MODAL & FORM ---
    function openModal(isEdit = false) {
        modal.style.display = 'flex';
        if (isEdit && selectedTaskId) {
            modalTitle.textContent = 'Edit Task';
            const task = fetchedTasks.find(t => t.id === selectedTaskId);
            if (task) {
                document.getElementById('taskId').value = task.id;
                document.getElementById('taskName').value = task.title;
                document.getElementById('startTime').value = task.start_time;
                document.getElementById('duration').value = task.duration;
                document.getElementById('taskColor').value = task.color;
                document.getElementById('isPriority').checked = task.is_priority;
            }
        } else {
            modalTitle.textContent = 'Add New Task';
            taskForm.reset();
            document.getElementById('taskId').value = '';
            document.getElementById('startTime').value = 9;
            document.getElementById('duration').value = 1;
        }
    }

    function closeModal() {
        modal.style.display = 'none';
        selectedTaskId = null;
    }

    closeBtn.addEventListener('click', closeModal);
    window.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    btnAddTask.addEventListener('click', () => {
        if (!selectedDate) { showToast('Please select a date first.', 'info'); return; }
        openModal(false);
    });

    btnEditTask.addEventListener('click', () => {
        if (!selectedTaskId) { showToast('Select a task first!', 'info'); return; }
        openModal(true);
    });

    function openDeleteModal() {
        if (!deleteTaskModal) return;
        deleteTaskModal.classList.remove('hidden');
    }

    function closeDeleteModal() {
        if (!deleteTaskModal) return;
        deleteTaskModal.classList.add('hidden');
    }

    btnDeleteTask.addEventListener('click', () => {
        if (!selectedTaskId) { showToast('Select a task first!', 'info'); return; }
        openDeleteModal();
    });

    if (cancelDeleteTaskBtn) cancelDeleteTaskBtn.addEventListener('click', () => closeDeleteModal());

    if (confirmDeleteTaskBtn) confirmDeleteTaskBtn.addEventListener('click', () => {
        if (!selectedTaskId) { showToast('No task selected', 'error'); closeDeleteModal(); return; }
        fetch(`/api/tasks/${selectedTaskId}`, { method: 'DELETE' })
            .then(async res => {
                const data = await res.json().catch(() => ({}));
                if (!res.ok) {
                    const msg = data.error || `Server ${res.status}`;
                    showToast('Unable to delete task: ' + msg, 'error');
                    closeDeleteModal();
                    return;
                }
                showToast('Task deleted', 'success');
                loadTasks();
                selectedTaskId = null;
                closeDeleteModal();
            }).catch(err => {
                console.error(err);
                showToast('Network error deleting task', 'error');
                closeDeleteModal();
            });
    });

    taskForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const id = document.getElementById('taskId').value;
        const data = {
            title: document.getElementById('taskName').value,
            start_time: parseFloat(document.getElementById('startTime').value),
            duration: parseFloat(document.getElementById('duration').value),
            color: document.getElementById('taskColor').value,
            is_priority: document.getElementById('isPriority').checked,
            task_date: selectedDate.toISOString().split('T')[0]
        };

        if (id) {
            // Edit
            fetch(`/api/tasks/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            }).then(res => res.json()).then(() => {
                closeModal();
                loadTasks();
            });
        } else {
            // Add
            fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            }).then(res => res.json()).then(res => {
                if (res.error) showToast(res.error, 'error');
                else {
                    closeModal();
                    loadTasks();
                }
            }).catch(err => { console.error(err); showToast('Error saving task', 'error'); });
        }
    });

    // --- INIT ---
    renderCalendar(currentDate);
    loadTasks();
});
