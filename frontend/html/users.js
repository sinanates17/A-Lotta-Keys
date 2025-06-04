const isDev = window.location.hostname === "127.0.0.1";

API_BASE = isDev
  ? "http://127.0.0.1:5000/"
  : "https://alottakeys.xyz/";

/////////////////////////////////////////////////////////////////////////

const keymodesContainer = document.getElementById('keymodesParent');
const keymodesButton = document.getElementById('keymodesButton');
const keymodesDropdown = document.getElementById("keymodesDropdown");
const searchBar = document.getElementById("search")
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

const ppContainer = document.getElementById('ppParent');
const ppButton = document.getElementById('ppButton');
const ppDropdown = document.getElementById("ppDropdown");
const pps = Array.from(ppDropdown.children);

function showDropdownPP() {
  ppDropdown.classList.toggle('hidden', false);}

function hideDropdownPP() {
  ppDropdown.classList.toggle('hidden', true);}

ppButton.addEventListener('pointerenter', showDropdownPP);
ppContainer.addEventListener('pointerleave', hideDropdownPP);
pps.forEach(child => child.addEventListener('click', hideDropdownPP));

/////////////////////////////////////////////////////////////////////////

function updateSort(sortKey) {
  sortDropdown.dataset.value = sortKey;
  applyFilter();
}

function updatePP(pp) {
  ppDropdown.dataset.value = pp;
  applyFilter();
}

async function applyFilter() {
  const selectedKeys = Array.from(document.querySelectorAll('input[name="key"]:checked')).map(box => box.value);
  const sort = document.getElementById("sortDropdown").dataset.value;
  const pp = document.getElementById("ppDropdown").dataset.value;
  searchBar.value = '';
  body.innerHTML = '';
  if (selectedKeys.length === 0) {
    return;
  }

  let query = selectedKeys.map(key => 'key=' + encodeURIComponent(key)).join('&');
  query = query + '&sort=' + encodeURIComponent(sort);
  query = query + '&pp=' + encodeURIComponent(pp);
  const url = API_BASE + 'api/search/users?' + query;
  const response = await fetch(url);
  const rows = await response.json();
  
  for (const row of rows) {
    const tr = document.createElement('tr');
    tr.id = row["id"];
    tr.onclick = function() { window.location.href = `${API_BASE}api/search/users/${tr.id}` }
    tr.innerHTML = `
      <td style="width: 4%; text-align: left;">${row["pos"]}</td>
      <td style="width: 12%;" >${row["name"]}</td>
      <td style="width: 7%;" >${row["pp"]}</td>
      <td style="width: 11%;">${row["rscore"]}</td>
      <td style="width: 7%;">${row["rperc"]}%</td>
      <td style="width: 11%;">${row["tscore"]}</td>
      <td style="width: 7%;">${row["tperc"]}%</td>
      <td style="width: 10%;">${row["numscores"]}</td>
      <td style="width: 10%;">${row["beatmap plays"]}</td>
      <td style="width: 6%;">${row["last score"]} d</td>
      <td style="width: 15%;">${row["country"]}</td>
    `;
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

applyFilter()