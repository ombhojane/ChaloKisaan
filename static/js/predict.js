tailwind.init();

  // Initialize TailwindCSS components if needed
  // tailwind.init();

  function updateFarmImage() {
      var landSize = document.getElementById('landSizeInput').value;
      var farmImage = document.getElementById('farmImage');

      if (landSize >= 1 && landSize < 10) {
          farmImage.src = 'https://www.wallpaperup.com/uploads/wallpapeassets\small.pngrs/2015/06/13/720738/0c856c888523da6127f5a322edcd8b43.jpg';
          farmImage.classList.remove('hidden');
      } else if (landSize >= 10 && landSize < 20) {
          farmImage.src = 'https://www.wallpaperup.com/uploads/wallpapers/2015/06/13/720738/0c856c888523da6127f5a322edcd8b43.jpg';
          farmImage.classList.remove('hidden');
      } else if (landSize >= 20 && landSize < 25) {
          farmImage.src = '../assets/extramid.png';
          farmImage.classList.remove('hidden');
      } else if (landSize >= 25) {
          farmImage.src = '../assets/large.png';
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

