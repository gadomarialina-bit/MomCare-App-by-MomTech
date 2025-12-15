document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const timelineGrid = document.getElementById('timelineGrid');
    const calendarGrid = document.getElementById('calendarGrid');
    const currentMonthDisplay = document.getElementById('currentMonthDisplay');
    const prevMonthBtn = document.getElementById('prevMonthBtn');
    const nextMonthBtn = document.getElementById('nextMonthBtn');
    const addTaskBtn = document.getElementById('addTaskBtn');
    const taskModal = document.getElementById('taskModal');
    const closeBtn = document.querySelector('.close-btn');
    const taskForm = document.getElementById('taskForm');
    const deleteSelectedTaskBtn = document.getElementById('deleteSelectedTaskBtn');
    const headerDateDisplay = document.getElementById('currentDateDisplay');
    const priorityList = document.getElementById('priorityList');
    const editTaskBtn = document.getElementById('editTaskBtn');
    const modalTitle = document.getElementById('modalTitle');

    // Form Fields for quick reference
    const taskIdInput = document.getElementById('taskId');
    const taskNameInput = document.getElementById('taskName');
    const startTimeInput = document.getElementById('startTime');
    const durationInput = document.getElementById('duration');
    const taskColorInput = document.getElementById('taskColor');
    const isPriorityInput = document.getElementById('isPriority');

    // Calendar State
    let currentDate = new Date(); // Tracks the month being displayed
    let selectedDate = new Date(); // Tracks the single day selected by the user
    let selectedTaskId = null; // Tracks the ID of the task currently selected for editing/deletion

    // Normalize selected date to today for a better initial experience
    selectedDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate());

    const monthNames = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];

    // --- Core Data Storage ---
    // Tasks are stored with a 'dateKey' (YYYY-MM-DD)
    let tasks = JSON.parse(sessionStorage.getItem('momcareTasks')) || [
        // Default tasks for the initial selected day (today)
        { id: 1, name: 'Breakfast', start: 8, duration: 1, color: 'orange', dateKey: getISODate(selectedDate), isPriority: false },
        { id: 2, name: 'Go to school!', start: 10, duration: 1, color: 'yellow-green', dateKey: getISODate(selectedDate), isPriority: true },
        { id: 3, name: 'Pick up groceries', start: 16, duration: 0.5, color: 'orange', dateKey: getISODate(selectedDate), isPriority: true },
    ];

    // --- Helper Functions ---

    // Formats date as YYYY-MM-DD string
    function getISODate(date) {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    const saveTasks = () => {
        sessionStorage.setItem('momcareTasks', JSON.stringify(tasks));
    };


    // --- Calendar Functions ---

    const renderCalendar = () => {
        calendarGrid.innerHTML = '';

        const currentMonth = currentDate.getMonth();
        const currentYear = currentDate.getFullYear();

        currentMonthDisplay.textContent = `${monthNames[currentMonth]} ${currentYear}`;
        headerDateDisplay.textContent = `${monthNames[selectedDate.getMonth()]} ${selectedDate.getDate()}, ${selectedDate.getFullYear()}`;

        // 1. Add Day Labels (Sun-Sat)
        const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        daysOfWeek.forEach(day => {
            const label = document.createElement('span');
            label.className = 'day-label';
            label.textContent = day;
            calendarGrid.appendChild(label);
        });

        const firstDayOfMonth = new Date(currentYear, currentMonth, 1).getDay();
        const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

        // 2. Add empty slots
        for (let i = 0; i < firstDayOfMonth; i++) {
            calendarGrid.appendChild(document.createElement('span'));
        }

        // 3. Add Dates
        for (let day = 1; day <= daysInMonth; day++) {
            const dateSpan = document.createElement('span');
            dateSpan.className = 'date-number';
            dateSpan.textContent = day;

            const dateKey = getISODate(new Date(currentYear, currentMonth, day));

            if (tasks.some(task => task.dateKey === dateKey)) {
                dateSpan.classList.add('has-task');
            }

            if (dateKey === getISODate(selectedDate)) {
                dateSpan.classList.add('active-date');
            }

            dateSpan.addEventListener('click', () => {
                selectedDate = new Date(currentYear, currentMonth, day);
                renderCalendar();
                renderTimeline();
            });

            calendarGrid.appendChild(dateSpan);
        }
    };

    // --- Priority Rendering ---

    const renderPriorityList = () => {
        priorityList.innerHTML = '';
        const selectedDateKey = getISODate(selectedDate);

        const priorityTasks = tasks
            .filter(task => task.dateKey === selectedDateKey && task.isPriority)
            .sort((a, b) => a.start - b.start);

        if (priorityTasks.length === 0) {
            priorityList.innerHTML = '<li>No high priority tasks today!</li>';
            return;
        }

        priorityTasks.forEach(task => {
            const listItem = document.createElement('li');
            const startHour = Math.floor(task.start);
            const startMin = (task.start % 1) * 60;
            const timeStr = `${startHour % 12 || 12}:${String(startMin).padStart(2, '0')}`;

            listItem.textContent = `${timeStr} - ${task.name}`;
            priorityList.appendChild(listItem);
        });
    };


    // --- Timeline/Task Functions ---
    const timeToGridRow = (time) => {
        return (time - 8) * 2 + 1;
    };

    const renderTimeline = () => {
        timelineGrid.innerHTML = '';

        headerDateDisplay.textContent = `${monthNames[selectedDate.getMonth()]} ${selectedDate.getDate()}, ${selectedDate.getFullYear()}`;

        const selectedDateKey = getISODate(selectedDate);
        const filteredTasks = tasks.filter(task => task.dateKey === selectedDateKey);

        // 1. Generate Time Slots (8:00 AM to 9:00 PM)
        for (let hour = 8; hour <= 21; hour += 0.5) {
            if (hour % 1 === 0) {
                const timeSlotDiv = document.createElement('div');
                const ampm = hour >= 12 ? 'PM' : 'AM';
                const displayHour = hour % 12 || 12;

                timeSlotDiv.className = 'time-slot';
                timeSlotDiv.textContent = `${displayHour}:00 ${ampm}`;
                timeSlotDiv.style.gridRowStart = timeToGridRow(hour);
                timeSlotDiv.style.gridRowEnd = timeToGridRow(hour) + 2;
                timelineGrid.appendChild(timeSlotDiv);
            }
        }

        // 2. Render Task Bars
        filteredTasks.forEach(task => {
            const taskDiv = document.createElement('div');
            taskDiv.className = `task-bar ${task.color}`;
            taskDiv.textContent = task.name;
            taskDiv.dataset.taskId = task.id;

            if (task.isPriority) {
                taskDiv.classList.add('priority-task');
            }

            const startRow = timeToGridRow(task.start);
            const spanRows = task.duration * 2;

            taskDiv.style.gridRowStart = startRow;
            taskDiv.style.gridRowEnd = startRow + spanRows;
            taskDiv.style.gridColumn = '2 / 3';

            taskDiv.addEventListener('click', (e) => {
                e.stopPropagation();
                selectTask(task.id);
            });

            timelineGrid.appendChild(taskDiv);
        });

        // 3. Render the Priority List
        renderPriorityList();

        // Clear selection visuals after render
        document.querySelectorAll('.task-bar').forEach(bar => {
            bar.classList.remove('selected-for-edit');
        });
        selectedTaskId = null;
    };

    const selectTask = (id) => {
        document.querySelectorAll('.task-bar').forEach(bar => {
            bar.classList.remove('selected-for-edit');
        });

        const selectedBar = document.querySelector(`[data-task-id="${id}"]`);
        if (selectedBar) {
            selectedBar.classList.add('selected-for-edit');
            selectedTaskId = id;
        }
    };


    // --- Modal/Form Logic ---

    const openModalForNewTask = () => {
        taskForm.reset();
        taskIdInput.value = '';
        modalTitle.textContent = 'Add New Task';
        taskModal.style.display = 'block';
    };

    const openModalForEdit = () => {
        if (selectedTaskId === null) {
            alert('Please click on a task in the schedule to select it for editing.');
            return;
        }

        const taskToEdit = tasks.find(t => t.id === selectedTaskId);
        if (!taskToEdit) return;

        modalTitle.textContent = `Edit Task: ${taskToEdit.name}`;
        taskIdInput.value = taskToEdit.id;
        taskNameInput.value = taskToEdit.name;
        startTimeInput.value = taskToEdit.start;
        durationInput.value = taskToEdit.duration;
        taskColorInput.value = taskToEdit.color;
        isPriorityInput.checked = taskToEdit.isPriority;

        taskModal.style.display = 'block';
    };

    // Event Listeners
    addTaskBtn.onclick = openModalForNewTask;
    editTaskBtn.onclick = openModalForEdit;
    closeBtn.onclick = () => { taskModal.style.display = 'none'; };
    window.onclick = (event) => {
        if (event.target == taskModal) { taskModal.style.display = 'none'; }
    };

    // Handle Form Submission (Add or Edit Task)
    taskForm.onsubmit = (event) => {
        event.preventDefault();

        const id = taskIdInput.value ? parseInt(taskIdInput.value) : null;
        const name = taskNameInput.value.trim();
        const start = parseFloat(startTimeInput.value);
        const duration = parseFloat(durationInput.value);
        const color = taskColorInput.value;
        const isPriority = isPriorityInput.checked;

        if (start < 8 || (start + duration) > 22) {
            alert('Task time must be between 8:00 AM and 10:00 PM.');
            return;
        }

        const taskData = { name, start, duration, color, isPriority, dateKey: getISODate(selectedDate) };

        if (id) {
            // EDIT existing task
            const index = tasks.findIndex(t => t.id === id);
            if (index !== -1) {
                tasks[index] = { ...tasks[index], ...taskData };
            }
        } else {
            // ADD new task
            const newId = Date.now();
            tasks.push({ id: newId, ...taskData });
        }

        tasks.sort((a, b) => a.start - b.start);
        saveTasks();
        renderCalendar();
        renderTimeline();
        taskModal.style.display = 'none';
    };

    // Delete Selected Task
    deleteSelectedTaskBtn.onclick = () => {
        if (selectedTaskId === null) {
            alert('Please select a task on the schedule to delete it.');
            return;
        }

        if (confirm('Are you sure you want to delete the selected task?')) {
            // Filter out the selected task
            tasks = tasks.filter(task => task.id !== selectedTaskId);

            selectedTaskId = null; // Clear selection
            saveTasks();
            renderCalendar();
            renderTimeline();
        }
    };

    // Calendar Navigation
    prevMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1, 1);
        renderCalendar();
    });

    nextMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1, 1);
        renderCalendar();
    });


    // --- Initialization ---
    renderCalendar();
    renderTimeline();
});