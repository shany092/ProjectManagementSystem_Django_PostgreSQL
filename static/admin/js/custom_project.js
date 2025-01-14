// document.addEventListener('DOMContentLoaded', () => {
//     const teamMemberSelect = document.getElementById('id_team_members');
//     const selectedList = document.getElementById('selected-team-members');

//     // Update displayed list when team members are selected
//     const updateSelectedList = () => {
//         const selectedOptions = Array.from(teamMemberSelect.selectedOptions);
//         selectedList.innerHTML = selectedOptions.map(option => `<li>${option.text}</li>`).join('');
//     };

//     // Attach listener to update list dynamically
//     if (teamMemberSelect && selectedList) {
//         teamMemberSelect.addEventListener('change', updateSelectedList);
//         updateSelectedList();  // Initial update
//     }
// });
