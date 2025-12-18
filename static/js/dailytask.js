
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

    let currentDate = new Date();
    let selectedDate = new Date();
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
            calendarGrid.appendChild(emptyCell);
        }

        // Days
        for (let d = 1; d <= daysInMonth; d++) {
            const dayCell = document.createElement('div');
            dayCell.textContent = d;
            dayCell.className = 'calendar-day';

            // Check if matches selectedDate
            if (d === selectedDate.getDate() && month === selectedDate.getMonth() && year === selectedDate.getFullYear()) {
                dayCell.classList.add('active');
            }

            dayCell.addEventListener('click', () => {
                selectedDate = new Date(year, month, d);
                renderCalendar(currentDate); // re-render to update active class
                loadTasks(); // fetch/filter tasks for this date
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
        // 24 hours
        for (let i = 0; i < 24; i++) {
            const hourDiv = document.createElement('div');
            hourDiv.className = 'timeline-hour';
            hourDiv.setAttribute('data-hour', `${i}:00`);
            timelineGrid.appendChild(hourDiv);
        }

        // Render tasks
        // Filter tasks by selectedDate
        const dateStr = selectedDate.toISOString().split('T')[0]; // YYYY-MM-DD
        const todaysTasks = fetchedTasks.filter(t => t.task_date === dateStr);

        todaysTasks.forEach(task => {
            const taskEl = document.createElement('div');
            taskEl.className = 'task-item';
            if (task.is_priority) taskEl.classList.add('priority');

            // Position
            const startHour = task.start_time; // e.g. 9.5
            const duration = task.duration; // e.g. 1.0

            const top = startHour * 60; // 60px per hour
            const height = duration * 60;

            taskEl.style.top = `${top}px`;
            taskEl.style.height = `${height}px`;
            taskEl.textContent = task.title;
            taskEl.style.backgroundColor = getColor(task.color);

            taskEl.addEventListener('click', (e) => {
                e.stopPropagation();
                selectTask(task.id);
            });

            timelineGrid.appendChild(taskEl);
        });

        // Update counts
        updateStats(todaysTasks);
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
        // Highlight in UI? For now just store ID
        // Maybe border style change
        document.querySelectorAll('.task-item').forEach(el => el.style.opacity = '0.6');
        // Find element?
        // Simple visual feedback: restore opacity for all, dim others? 
        // Or just trust the buttons work.
        alert("Task selected. You can Edit or Delete now.");
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

    btnAddTask.addEventListener('click', () => openModal(false));

    btnEditTask.addEventListener('click', () => {
        if (!selectedTaskId) { alert('Select a task first!'); return; }
        openModal(true);
    });

    btnDeleteTask.addEventListener('click', () => {
        if (!selectedTaskId) { alert('Select a task first!'); return; }
        if (confirm('Delete this task?')) {
            fetch(`/api/tasks/${selectedTaskId}`, { method: 'DELETE' })
                .then(res => res.json())
                .then(res => {
                    loadTasks();
                    selectedTaskId = null;
                });
        }
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
                if (res.error) alert(res.error);
                else {
                    closeModal();
                    loadTasks();
                }
            });
        }
    });

    // --- INIT ---
    renderCalendar(currentDate);
    loadTasks();
});
