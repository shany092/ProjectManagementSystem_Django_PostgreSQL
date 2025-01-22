document.addEventListener('DOMContentLoaded', function() {
    const taskElements = document.querySelectorAll('.field-parent_task_id');
    taskElements.forEach((taskElement) => {
        taskElement.addEventListener('click', (event) => {
            const subTasks = event.target.closest('tr').nextElementSibling;
            if (subTasks.style.display === 'none') {
                subTasks.style.display = 'table-row';
            } else {
                subTasks.style.display = 'none';
            }
        });
    });
});
