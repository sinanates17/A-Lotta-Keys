const isDev = window.location.hostname === "127.0.0.1";

API_BASE = isDev
  ? "http://127.0.0.1:5000/"
  : "https://alottakeys.xyz/";

/////////////////////////////////////////////////////////////////////////

const keymodesContainer = document.getElementById('keymodesParent');
const keymodesButton = document.getElementById('keymodesButton');
const keymodesDropdown = document.getElementById("keymodesDropdown");
const searchBar = document.getElementById("search");
const body = document.getElementById("leaderboard");

function showDropdownKeymodes() {
  keymodesDropdown.classList.toggle('hidden', false);}

function hideDropdownKeymodes() {
  keymodesDropdown.classList.toggle('hidden', true);}

keymodesButton.addEventListener('pointerenter', showDropdownKeymodes);
keymodesContainer.addEventListener('pointerleave', hideDropdownKeymodes);

/////////////////////////////////////////////////////////////////////////

const sortContainer = document.getElementById('sortParent');
const sortButton = document.getElementById('sortButton');
const sortDropdown = document.getElementById("sortDropdown");
const sorts = Array.from(sortDropdown.children);

function showDropdownSort() {
  sortDropdown.classList.toggle('hidden', false);}

function hideDropdownSort() {
  sortDropdown.classList.toggle('hidden', true);}

sortButton.addEventListener('pointerenter', showDropdownSort);
sortContainer.addEventListener('pointerleave', hideDropdownSort);
sorts.forEach(child => child.addEventListener('click', hideDropdownSort));

/////////////////////////////////////////////////////////////////////////

const statusContainer = document.getElementById('statusParent');
const statusButton = document.getElementById('statusButton');
const statusDropdown = document.getElementById("statusDropdown");

function showDropdownStatus() {
  statusDropdown.classList.toggle('hidden', false);}

function hideDropdownStatus() {
  statusDropdown.classList.toggle('hidden', true);}

statusButton.addEventListener('pointerenter', showDropdownStatus);
statusContainer.addEventListener('pointerleave', hideDropdownStatus);

/////////////////////////////////////////////////////////////////////////

function updateSort(sortKey) {
  sortDropdown.dataset.value = sortKey;
  applyFilter();
}

async function applyFilter() {
  const selectedKeys = Array.from(document.querySelectorAll('input[name="key"]:checked')).map(box => box.value);
  const selectedStates = Array.from(document.querySelectorAll('input[name="status"]:checked')).map(box => box.value);
  searchBar.value = '';
  body.innerHTML = '';
  if (selectedKeys.length === 0 || selectedStates.length === 0) {
    return;
  }
  const sort = document.getElementById("sortDropdown").dataset.value;
  const queryKeys = selectedKeys.map(key => 'key=' + encodeURIComponent(key)).join('&');
  const queryStates = selectedStates.map(key => 'status=' + encodeURIComponent(key)).join('&');

  const query = [`sort=${encodeURIComponent(sort)}`, queryKeys, queryStates].join('&');
  const url = API_BASE + 'api/search/beatmaps?' + query;
  const response = await fetch(url);
  const rows = await response.json();
  
  for (const row of rows) {
    const tr = document.createElement('tr');
    tr.id = row["id"];
    tr.onclick = function() { window.location.href = `${API_BASE}api/search/beatmaps/${tr.id}` }
    const time = `${Math.floor(row["length"]/60)}:${(row["length"]%60).toString().padStart(2, '0')}`

    tr.innerHTML = `
      <td style="width: 4%; text-align: left;">${row["pos"]}</td>
      <td style="width: 41%;">${row["name"]}</td>
      <td style="width: 13%;">${row["mapper"]}</td>
      <td style="width: 5%;">${row["keys"]}</td>
      <td style="width: 5%;">${row["sr"]}</td>
      <td style="width: 5%;">${row["plays"]}</td>
      <td style="width: 5%;">${row["passes"]}</td>
      <td style="width: 7%;">${time}</td>
      <td style="width: 7%;">${row["ln perc"]}%</td>
      <td style="width: 7%;">${row["status"]}</td>`;
    body.appendChild(tr);
  }
}

/////////////////////////////////////////////////////////////////////////

searchBar.addEventListener("input", function() {
  const rows = body.getElementsByTagName("tr")
  const subString = searchBar.value.toLowerCase()

  if (searchBar.value === '') {
    for (const row of rows) {
      row.style.display = "table-row"
    }
    return;
  }

  for (const row of rows) {
    var cells = row.getElementsByTagName("td");
    var name = cells[1].textContent.toLowerCase()

    if (name.includes(subString)) {
      row.style.display = "table-row"
    }
    else {
      row.style.display = "none"
    }

  }
})

/////////////////////////////////////////////////////////////////////////


applyFilter();