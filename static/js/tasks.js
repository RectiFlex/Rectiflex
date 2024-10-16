document.addEventListener('DOMContentLoaded', function() {
    const statusButtons = document.querySelectorAll('.status-btn');
    statusButtons.forEach(button => {
        button.addEventListener('click', function() {
            const taskId = this.getAttribute('data-task-id');
            const newStatus = this.getAttribute('data-status');
            updateTaskStatus(taskId, newStatus);
        });
    });
});

function updateTaskStatus(taskId, newStatus) {
    fetch('/api/update_task_status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task_id: taskId, status: newStatus }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Failed to update task status');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred while updating the task status');
    });
}
