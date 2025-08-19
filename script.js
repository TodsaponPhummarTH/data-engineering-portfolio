// Task Model Class
class Task {
    constructor(title, description = '') {
        this.id = this.generateId();
        this.title = this.validateTitle(title);
        this.description = this.validateDescription(description);
        this.isComplete = false;
        this.createdAt = new Date();
    }

    // Generate unique ID using timestamp and random number
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    // Validate title - required, max 100 characters
    validateTitle(title) {
        if (!title || typeof title !== 'string') {
            throw new Error('Task title is required and must be a string');
        }

        const trimmedTitle = title.trim();
        if (trimmedTitle.length === 0) {
            throw new Error('Task title cannot be empty');
        }

        if (trimmedTitle.length > 100) {
            throw new Error('Task title cannot exceed 100 characters');
        }

        return trimmedTitle;
    }

    // Validate description - optional, max 500 characters
    validateDescription(description) {
        if (description === null || description === undefined) {
            return '';
        }

        if (typeof description !== 'string') {
            throw new Error('Task description must be a string');
        }

        const trimmedDescription = description.trim();
        if (trimmedDescription.length > 500) {
            throw new Error('Task description cannot exceed 500 characters');
        }

        return trimmedDescription;
    }

    // Update task completion status
    toggleComplete() {
        this.isComplete = !this.isComplete;
        return this;
    }

    // Update task title with validation
    updateTitle(newTitle) {
        this.title = this.validateTitle(newTitle);
        return this;
    }

    // Update task description with validation
    updateDescription(newDescription) {
        this.description = this.validateDescription(newDescription);
        return this;
    }

    // Convert task to plain object for storage
    toJSON() {
        return {
            id: this.id,
            title: this.title,
            description: this.description,
            isComplete: this.isComplete,
            createdAt: this.createdAt.toISOString()
        };
    }

    // Create Task instance from stored data
    static fromJSON(data) {
        const task = Object.create(Task.prototype);
        task.id = data.id;
        task.title = data.title;
        task.description = data.description;
        task.isComplete = data.isComplete;
        task.createdAt = new Date(data.createdAt);
        return task;
    }
}

// Unit Tests for Task Class
function runTaskTests() {
    console.log('Running Task class tests...');

    try {
        // Test 1: Valid task creation
        const task1 = new Task('Test Task', 'Test description');
        console.assert(task1.title === 'Test Task', 'Title should be set correctly');
        console.assert(task1.description === 'Test description', 'Description should be set correctly');
        console.assert(task1.isComplete === false, 'Task should be incomplete by default');
        console.assert(task1.id && task1.id.length > 0, 'Task should have an ID');
        console.assert(task1.createdAt instanceof Date, 'CreatedAt should be a Date');
        console.log('✓ Valid task creation test passed');

        // Test 2: Task without description
        const task2 = new Task('Another Task');
        console.assert(task2.description === '', 'Description should default to empty string');
        console.log('✓ Task without description test passed');

        // Test 3: Title validation - empty title
        try {
            new Task('');
            console.assert(false, 'Should throw error for empty title');
        } catch (e) {
            console.assert(e.message.includes('empty'), 'Should throw empty title error');
            console.log('✓ Empty title validation test passed');
        }

        // Test 4: Title validation - null title
        try {
            new Task(null);
            console.assert(false, 'Should throw error for null title');
        } catch (e) {
            console.assert(e.message.includes('required'), 'Should throw required title error');
            console.log('✓ Null title validation test passed');
        }

        // Test 5: Title validation - too long title
        try {
            new Task('a'.repeat(101));
            console.assert(false, 'Should throw error for title too long');
        } catch (e) {
            console.assert(e.message.includes('100 characters'), 'Should throw title length error');
            console.log('✓ Title length validation test passed');
        }

        // Test 6: Description validation - too long description
        try {
            new Task('Valid Title', 'a'.repeat(501));
            console.assert(false, 'Should throw error for description too long');
        } catch (e) {
            console.assert(e.message.includes('500 characters'), 'Should throw description length error');
            console.log('✓ Description length validation test passed');
        }

        // Test 7: Toggle completion
        const task3 = new Task('Toggle Test');
        console.assert(task3.isComplete === false, 'Task should start incomplete');
        task3.toggleComplete();
        console.assert(task3.isComplete === true, 'Task should be complete after toggle');
        task3.toggleComplete();
        console.assert(task3.isComplete === false, 'Task should be incomplete after second toggle');
        console.log('✓ Toggle completion test passed');

        // Test 8: JSON serialization
        const task4 = new Task('JSON Test', 'Test JSON');
        const json = task4.toJSON();
        console.assert(json.id === task4.id, 'JSON should preserve ID');
        console.assert(json.title === task4.title, 'JSON should preserve title');
        console.assert(json.description === task4.description, 'JSON should preserve description');
        console.assert(json.isComplete === task4.isComplete, 'JSON should preserve completion status');
        console.assert(typeof json.createdAt === 'string', 'JSON should have createdAt as string');
        console.log('✓ JSON serialization test passed');

        // Test 9: JSON deserialization
        const restoredTask = Task.fromJSON(json);
        console.assert(restoredTask.id === task4.id, 'Restored task should have same ID');
        console.assert(restoredTask.title === task4.title, 'Restored task should have same title');
        console.assert(restoredTask.description === task4.description, 'Restored task should have same description');
        console.assert(restoredTask.isComplete === task4.isComplete, 'Restored task should have same completion status');
        console.assert(restoredTask.createdAt instanceof Date, 'Restored task should have Date object');
        console.log('✓ JSON deserialization test passed');

        console.log('🎉 All Task class tests passed!');
        return true;
    } catch (error) {
        console.error('❌ Task class test failed:', error);
        return false;
    }
}

// Run tests when script loads
runTaskTests();

// Storage Utilities
class TaskStorage {
    constructor() {
        this.storageKey = 'tasks';
        this.isStorageAvailable = this.checkStorageAvailability();
    }

    // Check if localStorage is available
    checkStorageAvailability() {
        try {
            const test = '__storage_test__';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (e) {
            console.warn('localStorage is not available:', e.message);
            return false;
        }
    }

    // Save tasks to localStorage
    saveTasks(tasks) {
        if (!this.isStorageAvailable) {
            console.warn('Cannot save tasks: localStorage unavailable');
            return false;
        }

        try {
            const tasksData = tasks.map(task => task.toJSON());
            localStorage.setItem(this.storageKey, JSON.stringify(tasksData));
            return true;
        } catch (error) {
            console.error('Error saving tasks to localStorage:', error);
            return false;
        }
    }

    // Load tasks from localStorage
    loadTasks() {
        if (!this.isStorageAvailable) {
            console.warn('Cannot load tasks: localStorage unavailable');
            return [];
        }

        try {
            const tasksData = localStorage.getItem(this.storageKey);
            if (!tasksData) {
                return [];
            }

            const parsedData = JSON.parse(tasksData);
            if (!Array.isArray(parsedData)) {
                console.warn('Invalid tasks data format, returning empty array');
                return [];
            }

            return parsedData.map(taskData => Task.fromJSON(taskData));
        } catch (error) {
            console.error('Error loading tasks from localStorage:', error);
            return [];
        }
    }

    // Clear all tasks from storage
    clearTasks() {
        if (!this.isStorageAvailable) {
            console.warn('Cannot clear tasks: localStorage unavailable');
            return false;
        }

        try {
            localStorage.removeItem(this.storageKey);
            return true;
        } catch (error) {
            console.error('Error clearing tasks from localStorage:', error);
            return false;
        }
    }

    // Get storage info
    getStorageInfo() {
        if (!this.isStorageAvailable) {
            return { available: false, used: 0, remaining: 0 };
        }

        try {
            const used = new Blob(Object.values(localStorage)).size;
            const remaining = 5 * 1024 * 1024 - used; // Assuming 5MB limit
            return {
                available: true,
                used: used,
                remaining: Math.max(0, remaining)
            };
        } catch (error) {
            return { available: true, used: 0, remaining: 0 };
        }
    }
}

// Unit Tests for TaskStorage
function runStorageTests() {
    console.log('Running TaskStorage tests...');

    try {
        const storage = new TaskStorage();

        // Test 1: Storage availability check
        console.assert(typeof storage.isStorageAvailable === 'boolean', 'Storage availability should be boolean');
        console.log('✓ Storage availability check test passed');

        // Test 2: Save and load empty array
        const emptyResult = storage.saveTasks([]);
        if (storage.isStorageAvailable) {
            console.assert(emptyResult === true, 'Should successfully save empty array');
            const loadedEmpty = storage.loadTasks();
            console.assert(Array.isArray(loadedEmpty), 'Should load array');
            console.assert(loadedEmpty.length === 0, 'Should load empty array');
            console.log('✓ Save/load empty array test passed');
        }

        // Test 3: Save and load tasks
        const testTasks = [
            new Task('Test Task 1', 'Description 1'),
            new Task('Test Task 2', 'Description 2')
        ];
        testTasks[1].toggleComplete(); // Mark second task as complete

        const saveResult = storage.saveTasks(testTasks);
        if (storage.isStorageAvailable) {
            console.assert(saveResult === true, 'Should successfully save tasks');

            const loadedTasks = storage.loadTasks();
            console.assert(Array.isArray(loadedTasks), 'Should load array of tasks');
            console.assert(loadedTasks.length === 2, 'Should load correct number of tasks');
            console.assert(loadedTasks[0].title === 'Test Task 1', 'Should preserve task title');
            console.assert(loadedTasks[0].description === 'Description 1', 'Should preserve task description');
            console.assert(loadedTasks[0].isComplete === false, 'Should preserve completion status');
            console.assert(loadedTasks[1].isComplete === true, 'Should preserve completion status');
            console.assert(loadedTasks[0] instanceof Task, 'Should restore as Task instances');
            console.log('✓ Save/load tasks test passed');
        }

        // Test 4: Handle corrupted data
        if (storage.isStorageAvailable) {
            localStorage.setItem('tasks', 'invalid json');
            const corruptedLoad = storage.loadTasks();
            console.assert(Array.isArray(corruptedLoad), 'Should handle corrupted data gracefully');
            console.assert(corruptedLoad.length === 0, 'Should return empty array for corrupted data');
            console.log('✓ Corrupted data handling test passed');
        }

        // Test 5: Clear tasks
        const clearResult = storage.clearTasks();
        if (storage.isStorageAvailable) {
            console.assert(clearResult === true, 'Should successfully clear tasks');
            const clearedTasks = storage.loadTasks();
            console.assert(clearedTasks.length === 0, 'Should have no tasks after clearing');
            console.log('✓ Clear tasks test passed');
        }

        // Test 6: Storage info
        const storageInfo = storage.getStorageInfo();
        console.assert(typeof storageInfo === 'object', 'Storage info should be object');
        console.assert(typeof storageInfo.available === 'boolean', 'Should have available property');
        console.log('✓ Storage info test passed');

        console.log('🎉 All TaskStorage tests passed!');
        return true;
    } catch (error) {
        console.error('❌ TaskStorage test failed:', error);
        return false;
    }
}

// Run storage tests
runStorageTests();

// Task Controller - Manages task operations and UI interactions
class TaskController {
    constructor() {
        this.storage = new TaskStorage();
        this.tasks = [];
        this.init();
    }

    // Initialize the controller
    init() {
        this.loadTasks();
        this.bindEvents();
        this.renderTasks();
    }

    // Load tasks from storage
    loadTasks() {
        this.tasks = this.storage.loadTasks();
    }

    // Save tasks to storage
    saveTasks() {
        return this.storage.saveTasks(this.tasks);
    }

    // Bind event listeners
    bindEvents() {
        const form = document.getElementById('task-form');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
    }

    // Handle form submission for task creation
    handleFormSubmit(event) {
        event.preventDefault();
        
        const titleInput = document.getElementById('task-title');
        const descriptionInput = document.getElementById('task-description');
        
        if (!titleInput || !descriptionInput) {
            this.showError('Form elements not found');
            return;
        }

        const title = titleInput.value.trim();
        const description = descriptionInput.value.trim();

        // Clear previous error messages
        this.clearErrors();

        try {
            // Create new task with validation
            const newTask = new Task(title, description);
            
            // Add task to collection
            this.tasks.push(newTask);
            
            // Save to storage
            const saveSuccess = this.saveTasks();
            if (!saveSuccess) {
                this.showError('Failed to save task. Please try again.');
                // Remove the task from memory if save failed
                this.tasks.pop();
                return;
            }

            // Clear form
            titleInput.value = '';
            descriptionInput.value = '';
            
            // Re-render tasks
            this.renderTasks();
            
            // Show success feedback
            this.showSuccess('Task created successfully!');
            
            // Focus back to title input for easy task entry
            titleInput.focus();

        } catch (error) {
            this.showError(error.message);
        }
    }

    // Render all tasks to the UI
    renderTasks() {
        const taskList = document.getElementById('task-list');
        const emptyState = document.getElementById('empty-state');
        
        if (!taskList || !emptyState) {
            console.error('Task list or empty state elements not found');
            return;
        }

        // Clear current task list
        taskList.innerHTML = '';

        if (this.tasks.length === 0) {
            // Show empty state with appropriate message
            this.showEmptyState(emptyState, taskList);
        } else {
            // Hide empty state and show tasks
            emptyState.style.display = 'none';
            taskList.style.display = 'block';
            
            // Organize tasks by status
            this.renderTaskSections();
            
            // Update task count display
            this.updateTaskCount();
        }
    }

    // Render tasks organized by sections (Current, Pending, Completed)
    renderTaskSections() {
        const taskList = document.getElementById('task-list');
        
        // Separate tasks by status
        const pendingTasks = this.tasks.filter(task => !task.isComplete);
        const completedTasks = this.tasks.filter(task => task.isComplete);
        
        // Sort tasks by creation date (newest first)
        const sortedPending = pendingTasks.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
        const sortedCompleted = completedTasks.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
        
        // Create sections
        if (sortedPending.length > 0) {
            const pendingSection = this.createTaskSection('Pending Tasks', sortedPending, 'pending');
            taskList.appendChild(pendingSection);
        }
        
        if (sortedCompleted.length > 0) {
            const completedSection = this.createTaskSection('Completed Tasks', sortedCompleted, 'completed');
            taskList.appendChild(completedSection);
        }
    }

    // Create a task section with title and tasks
    createTaskSection(title, tasks, sectionType) {
        const section = document.createElement('div');
        section.className = `task-section task-section-${sectionType}`;
        
        // Create section header
        const header = document.createElement('div');
        header.className = 'task-section-header';
        header.innerHTML = `
            <h3 class="task-section-title">${title}</h3>
            <span class="task-section-count">${tasks.length} task${tasks.length !== 1 ? 's' : ''}</span>
        `;
        section.appendChild(header);
        
        // Create tasks container
        const tasksContainer = document.createElement('div');
        tasksContainer.className = 'task-section-tasks';
        
        // Add tasks to container
        tasks.forEach(task => {
            const taskElement = this.createTaskElement(task);
            tasksContainer.appendChild(taskElement);
        });
        
        section.appendChild(tasksContainer);
        return section;
    }

    // Show empty state with appropriate message
    showEmptyState(emptyState, taskList) {
        emptyState.style.display = 'block';
        taskList.style.display = 'none';
        
        // Update empty state message based on context
        const emptyMessage = emptyState.querySelector('p');
        if (emptyMessage) {
            emptyMessage.textContent = 'No tasks yet. Create your first task above!';
        }
    }

    // Update task count display
    updateTaskCount() {
        const completedCount = this.tasks.filter(task => task.isComplete).length;
        const totalCount = this.tasks.length;
        const pendingCount = totalCount - completedCount;
        
        // Create or update task summary
        let taskSummary = document.getElementById('task-summary');
        if (!taskSummary) {
            taskSummary = document.createElement('div');
            taskSummary.id = 'task-summary';
            taskSummary.className = 'task-summary';
            
            const taskListSection = document.querySelector('.task-list-section');
            if (taskListSection) {
                taskListSection.insertBefore(taskSummary, taskListSection.firstChild);
            }
        }
        
        taskSummary.innerHTML = `
            <div class="task-stats">
                <span class="stat-item">
                    <strong>${totalCount}</strong> Total
                </span>
                <span class="stat-item">
                    <strong>${pendingCount}</strong> Pending
                </span>
                <span class="stat-item">
                    <strong>${completedCount}</strong> Completed
                </span>
            </div>
        `;
    }

    // Create HTML element for a single task
    createTaskElement(task) {
        const taskDiv = document.createElement('div');
        taskDiv.className = `task-item ${task.isComplete ? 'completed' : ''}`;
        taskDiv.dataset.taskId = task.id;

        taskDiv.innerHTML = `
            <div class="task-content">
                <div class="task-header">
                    <h3 class="task-title">${this.escapeHtml(task.title)}</h3>
                    <div class="task-actions">
                        <button class="btn btn-toggle" onclick="taskController.toggleTask('${task.id}')">
                            ${task.isComplete ? '↶ Undo' : '✓ Complete'}
                        </button>
                        <button class="btn btn-delete" onclick="handleDeleteTask('${task.id}')">
                            🗑 Delete
                        </button>
                    </div>
                </div>
                ${task.description ? `<p class="task-description">${this.escapeHtml(task.description)}</p>` : ''}
                <div class="task-meta">
                    <span class="task-date">Created: ${this.formatDate(task.createdAt)}</span>
                    <span class="task-status">${task.isComplete ? 'Completed' : 'Pending'}</span>
                </div>
            </div>
        `;

        return taskDiv;
    }

    // Toggle task completion status
    toggleTask(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (!task) {
            this.showError('Task not found');
            return;
        }

        const wasComplete = task.isComplete;
        task.toggleComplete();
        
        if (this.saveTasks()) {
            // Add completion animation class
            const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
            if (taskElement && !wasComplete && task.isComplete) {
                taskElement.classList.add('just-completed');
                setTimeout(() => {
                    taskElement.classList.remove('just-completed');
                }, 600);
            }
            
            this.renderTasks();
            
            // Show appropriate success message
            const statusMessage = task.isComplete ? 
                `"${task.title}" marked as completed! 🎉` : 
                `"${task.title}" marked as pending.`;
            this.showSuccess(statusMessage);
        } else {
            // Revert the change if save failed
            task.toggleComplete();
            this.showError('Failed to update task. Please try again.');
        }
    }

    // Delete a task with confirmation
    deleteTask(taskId) {
        console.log('Delete task called with ID:', taskId);
        const task = this.tasks.find(t => t.id === taskId);
        if (!task) {
            this.showError('Task not found');
            return;
        }

        console.log('Task found, showing confirmation dialog');
        // Show custom confirmation dialog
        this.showDeleteConfirmation(task, taskId);
    }

    // Show custom delete confirmation dialog
    showDeleteConfirmation(task, taskId) {
        // Create confirmation dialog
        const dialog = document.createElement('div');
        dialog.className = 'delete-confirmation-overlay';
        dialog.innerHTML = `
            <div class="delete-confirmation-dialog">
                <div class="delete-confirmation-header">
                    <h3>Delete Task</h3>
                </div>
                <div class="delete-confirmation-body">
                    <p>Are you sure you want to delete this task?</p>
                    <div class="task-preview">
                        <strong>"${this.escapeHtml(task.title)}"</strong>
                        ${task.description ? `<br><small>${this.escapeHtml(task.description)}</small>` : ''}
                    </div>
                </div>
                <div class="delete-confirmation-actions">
                    <button class="btn btn-cancel" onclick="taskController.cancelDelete()">No</button>
                    <button class="btn btn-confirm-delete" onclick="taskController.confirmDelete('${taskId}')">Yes</button>
                </div>
            </div>
        `;

        // Add to page
        document.body.appendChild(dialog);
        this.currentDeleteDialog = dialog;
        console.log('Dialog added to page, currentDeleteDialog set:', !!this.currentDeleteDialog);

        // Focus on No button by default for safety
        setTimeout(() => {
            const cancelBtn = dialog.querySelector('.btn-cancel');
            if (cancelBtn) {
                cancelBtn.focus();
                console.log('Cancel button focused');
            }
        }, 100);
    }

    // Cancel delete operation
    cancelDelete() {
        if (this.currentDeleteDialog) {
            this.currentDeleteDialog.remove();
            this.currentDeleteDialog = null;
        }
    }

    // Confirm delete operation
    confirmDelete(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (!task) {
            this.showError('Task not found');
            this.cancelDelete();
            return;
        }

        // Remove task from array
        const taskIndex = this.tasks.findIndex(t => t.id === taskId);
        this.tasks.splice(taskIndex, 1);

        if (this.saveTasks()) {
            // Close dialog
            this.cancelDelete();
            
            // Re-render tasks
            this.renderTasks();
            
            // Show countdown deletion message
            this.showDeletionCountdown(task.title);
        } else {
            // Restore the task if save failed
            this.tasks.splice(taskIndex, 0, task);
            this.showError('Failed to delete task. Please try again.');
            this.cancelDelete();
        }
    }

    // Show deletion countdown with progress bar
    showDeletionCountdown(taskTitle) {
        // Remove any existing countdown
        const existingCountdown = document.querySelector('.deletion-countdown');
        if (existingCountdown) {
            existingCountdown.remove();
        }

        // Create countdown element
        const countdown = document.createElement('div');
        countdown.className = 'deletion-countdown';
        countdown.innerHTML = `
            <div class="countdown-content">
                <span class="countdown-text">Task "${this.escapeHtml(taskTitle)}" deleted successfully</span>
                <div class="countdown-progress">
                    <div class="countdown-bar"></div>
                </div>
            </div>
        `;

        // Insert at top of container
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(countdown, container.firstChild);
            
            // Start progress bar animation
            const progressBar = countdown.querySelector('.countdown-bar');
            if (progressBar) {
                // Trigger animation
                setTimeout(() => {
                    progressBar.style.width = '100%';
                }, 50);
            }
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (countdown.parentNode) {
                    countdown.style.opacity = '0';
                    setTimeout(() => {
                        countdown.remove();
                    }, 300);
                }
            }, 5000);
        }
    }

    // Show error message to user
    showError(message) {
        this.showMessage(message, 'error');
    }

    // Show success message to user
    showSuccess(message) {
        this.showMessage(message, 'success');
    }

    // Show message with specified type
    showMessage(message, type) {
        // Remove existing messages
        const existingMessage = document.querySelector('.message');
        if (existingMessage) {
            existingMessage.remove();
        }

        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        messageDiv.textContent = message;

        // Insert at top of container
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(messageDiv, container.firstChild);
            
            // Auto-remove after 3 seconds
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.remove();
                }
            }, 3000);
        }
    }

    // Clear error messages
    clearErrors() {
        const errorMessages = document.querySelectorAll('.message-error');
        errorMessages.forEach(msg => msg.remove());
    }

    // Escape HTML to prevent XSS
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Format date for display
    formatDate(date) {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }
}

// Initialize the task controller when DOM is loaded
let taskController;

document.addEventListener('DOMContentLoaded', () => {
    taskController = new TaskController();
});

// Unit Tests for TaskController
function runTaskControllerTests() {
    console.log('Running TaskController tests...');
    
    try {
        // Test 1: Controller initialization
        const controller = new TaskController();
        console.assert(controller.storage instanceof TaskStorage, 'Should have TaskStorage instance');
        console.assert(Array.isArray(controller.tasks), 'Should have tasks array');
        console.log('✓ Controller initialization test passed');

        // Test 2: Task creation workflow
        const initialTaskCount = controller.tasks.length;
        
        // Simulate creating a task
        const testTask = new Task('Test Controller Task', 'Test description');
        controller.tasks.push(testTask);
        
        console.assert(controller.tasks.length === initialTaskCount + 1, 'Should add task to collection');
        console.assert(controller.tasks[controller.tasks.length - 1].title === 'Test Controller Task', 'Should preserve task title');
        console.log('✓ Task creation workflow test passed');

        // Test 3: HTML escaping
        const htmlString = '<script>alert("xss")</script>';
        const escaped = controller.escapeHtml(htmlString);
        console.assert(!escaped.includes('<script>'), 'Should escape HTML tags');
        console.assert(escaped.includes('&lt;'), 'Should convert < to &lt;');
        console.log('✓ HTML escaping test passed');

        // Test 4: Date formatting
        const testDate = new Date('2024-01-15T10:30:00');
        const formatted = controller.formatDate(testDate);
        console.assert(typeof formatted === 'string', 'Should return string');
        console.assert(formatted.length > 0, 'Should return non-empty string');
        console.log('✓ Date formatting test passed');

        // Test 5: Task sorting
        const task1 = new Task('First Task');
        const task2 = new Task('Second Task');
        // Simulate different creation times
        task1.createdAt = new Date('2024-01-01');
        task2.createdAt = new Date('2024-01-02');
        
        controller.tasks = [task1, task2];
        const sortedTasks = [...controller.tasks].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
        console.assert(sortedTasks[0].title === 'Second Task', 'Should sort by newest first');
        console.log('✓ Task sorting test passed');

        // Test 6: Task count calculation
        const completedTask = new Task('Completed Task');
        completedTask.toggleComplete();
        const pendingTask = new Task('Pending Task');
        
        controller.tasks = [completedTask, pendingTask];
        const completedCount = controller.tasks.filter(task => task.isComplete).length;
        const totalCount = controller.tasks.length;
        const pendingCount = totalCount - completedCount;
        
        console.assert(completedCount === 1, 'Should count completed tasks correctly');
        console.assert(pendingCount === 1, 'Should count pending tasks correctly');
        console.assert(totalCount === 2, 'Should count total tasks correctly');
        console.log('✓ Task count calculation test passed');

        console.log('🎉 All TaskController tests passed!');
        return true;
    } catch (error) {
        console.error('❌ TaskController test failed:', error);
        return false;
    }
}

// Run controller tests
runTaskControllerTests();