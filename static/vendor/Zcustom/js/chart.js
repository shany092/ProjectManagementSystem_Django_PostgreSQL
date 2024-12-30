<!-- Chart.js Library -->
        document.addEventListener('DOMContentLoaded', function () {
            const ctx = document.getElementById('project-chart').getContext('2d');
            const projectChart = new Chart(ctx, {
                type: 'bar', // Choose 'line', 'pie', etc. for different types
                data: {
                    labels: ['Project A', 'Project B', 'Project C', 'Project D'],
                    datasets: [{
                        label: 'Completed Tasks',
                        data: [12, 19, 3, 5], // Dummy data
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.2)',
                            'rgba(54, 162, 235, 0.2)',
                            'rgba(255, 206, 86, 0.2)',
                            'rgba(75, 192, 192, 0.2)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        });
        
    // <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    // <script>
    // </script>