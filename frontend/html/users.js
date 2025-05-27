const isDev = window.location.hostname === "127.0.0.1";

API_BASE = isDev
  ? "http://127.0.0.1:5000/"
  : "https://alottakeys.xyz/";

/////////////////////////////////////////////////////////////////////////

const keymodesContainer = document.getElementById('keymodesParent');
const keymodesButton = document.getElementById('keymodesButton');
const keymodesDropdown = document.getElementById("keymodesDropdown");

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

function updateSort(sortKey) {
  sortDropdown.dataset.value = sortKey;
  applyFilter();
}

async function applyFilter() {
  const selectedKeys = Array.from(document.querySelectorAll('input[name="key"]:checked')).map(box => box.value);
  const sort = document.getElementById("sortDropdown").dataset.value;
  let query = selectedKeys.map(key => 'key=' + encodeURIComponent(key)).join('&');
  query = query + '&sort=' + encodeURIComponent(sort);
  const url = API_BASE + 'api/search/users?' + query;
  console.log(url);
  

  const response = await fetch(url);
  const rows = await response.json();

  const body = document.getElementById("leaderboard");
  body.innerHTML = '';
  for (const row of rows) {
    const tr = document.createElement('tr')
    tr.innerHTML = `
      <td style="width: 4%; text-align: left;">${row["pos"]}</td>
      <td style="width: 15%;">${row["name"]}</td>
      <td style="width: 11%;">${row["rscore"]}</td>
      <td style="width: 7%;">${row["rperc"]}%</td>
      <td style="width: 11%;">${row["tscore"]}</td>
      <td style="width: 7%;">${row["tperc"]}%</td>
      <td style="width: 10%;">${row["numscores"]}</td>
      <td style="width: 10%;">${row["beatmap plays"]}</td>
      <td style="width: 10%;">${row["last score"]} d</td>
      <td style="width: 15%;">${row["country"]}</td>
    `;
    body.appendChild(tr)
  }
}

applyFilter()