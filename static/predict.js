tailwind.init();

  // Initialize TailwindCSS components if needed
  // tailwind.init();

  function updateFarmImage() {
      var landSize = document.getElementById('landSizeInput').value;
      var farmImage = document.getElementById('farmImage');

      if (landSize >= 1 && landSize < 10) {
          farmImage.src = 'https://i.postimg.cc/RCw9z1Kv/Screenshot-2024-02-14-205114.png';
          farmImage.classList.remove('hidden');
      } else if (landSize >= 10 && landSize < 20) {
          farmImage.src = 'https://github.com/ombhojane/chalokisaanai/blob/main/assets/mid.png?raw=true';
          farmImage.classList.remove('hidden');
      } else if (landSize >= 20 && landSize < 25) {
          farmImage.src = 'https://github.com/ombhojane/chalokisaanai/blob/main/assets/large.png?raw=true';
          farmImage.classList.remove('hidden');
      } else if (landSize >= 25) {
          farmImage.src = 'https://github.com/ombhojane/chalokisaanai/blob/main/assets/extramid.png?raw=true';
          farmImage.classList.remove('hidden');
      } else {
          farmImage.classList.add('hidden');
      }
  }

  function toggleBudgetInfo(event) {
      event.preventDefault(); // Prevent the default behavior of the button click

      var budgetInfo = document.getElementById('budgetInfo');
      var arrowIcon = document.getElementById('arrowIcon');

      if (budgetInfo.classList.contains('hidden')) {
          budgetInfo.classList.remove('hidden');
          arrowIcon.classList.remove('fa-chevron-down');
          arrowIcon.classList.add('fa-chevron-up');
      } else {
          budgetInfo.classList.add('hidden');
          arrowIcon.classList.remove('fa-chevron-up');
          arrowIcon.classList.add('fa-chevron-down');
      }
  }

function toggleBudgetInfo(event) {
  event.preventDefault();

  var budgetInfo = document.getElementById('budgetInfo');
  var arrowIcon = document.getElementById('arrowIcon');
  var budgetTable = document.getElementById('budgetTable');

  if (budgetInfo.classList.contains('hidden')) {
    budgetInfo.classList.remove('hidden');
    arrowIcon.classList.remove('fa-chevron-down');
    arrowIcon.classList.add('fa-chevron-up');

    // Populate the table with budget information
    populateBudgetTable();
  } else {
    budgetInfo.classList.add('hidden');
    arrowIcon.classList.remove('fa-chevron-up');
    arrowIcon.classList.add('fa-chevron-down');
  }
}

function populateBudgetTable() {
  var budgetTableBody = document.querySelector('#budgetTable tbody');

  // Clear existing rows
  budgetTableBody.innerHTML = '';

  // Budget information data
  var budgetData = [
    { type: 'Economy', audience: 'Budget travelers, local tourists, students.', range: '5,000 to 50,000 Rs.' },
    { type: 'Mid-Range', audience: 'Middle-class tourists, small groups, families.', range: '50,000 to 2,00,000 Rs.' },
    { type: 'Luxury', audience: 'High-end tourists, international visitors, corporate groups.', range: '2,00,000 to 10,00,000 Rs.' }
  ];

  // Populate the table with data
  budgetData.forEach(function (item) {
    var row = budgetTableBody.insertRow();
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var cell3 = row.insertCell(2);

    cell1.textContent = item.type;
    cell2.textContent = item.audience;
    cell3.textContent = item.range;
  });
}

