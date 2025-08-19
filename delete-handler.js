// Delete functionality handler
document.addEventListener('DOMContentLoaded', function() {
    // Add global handlers for delete operations
    window.handleDeleteTask = function(taskId) {
        console.log('Delete handler called for task:', taskId);
        
        // Find the task in the controller
        const task = taskController.tasks.find(t => t.id === taskId);
        if (!task) {
            console.error('Task not found');
            return;
        }
        
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
                        <strong>"${escapeHtml(task.title)}"</strong>
                        ${task.description ? `<br><small>${escapeHtml(task.description)}</small>` : ''}
                    </div>
                </div>
                <div class="delete-confirmation-actions">
                    <button class="btn btn-cancel" id="cancel-delete">No</button>
                    <button class="btn btn-confirm-delete" id="confirm-delete">Yes</button>
                </div>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(dialog);
        
        // Add event listeners
        document.getElementById('cancel-delete').addEventListener('click', function() {
            dialog.remove();
        });
        
        document.getElementById('confirm-delete').addEventListener('click', function() {
            // Remove task from array
            const taskIndex = taskController.tasks.findIndex(t => t.id === taskId);
            taskController.tasks.splice(taskIndex, 1);
            
            if (taskController.saveTasks()) {
                // Close dialog
                dialog.remove();
                
                // Re-render tasks
                taskController.renderTasks();
                
                // Show countdown deletion message
                showDeletionCountdown(task.title);
            } else {
                // Restore the task if save failed
                taskController.tasks.splice(taskIndex, 0, task);
                taskController.showError('Failed to delete task. Please try again.');
                dialog.remove();
            }
        });
        
        // Focus on No button by default for safety
        setTimeout(() => {
            const cancelBtn = document.getElementById('cancel-delete');
            if (cancelBtn) cancelBtn.focus();
        }, 100);
    };
    
    // Helper function to escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Show deletion countdown with progress bar
    function showDeletionCountdown(taskTitle) {
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
                <span class="countdown-text">Task "${escapeHtml(taskTitle)}" deleted successfully</span>
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
});