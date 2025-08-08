const searchBarUsers = document.getElementById("searchusers")
const searchBarCountry = document.getElementById("searchcountry")
const tableBody = document.getElementById("tablebody")

let keyFilterElements = document.querySelectorAll('[name="filterKey"], [id="reverse"]')
let stateFilterElements = document.getElementsByName("filterState")
let sortElements = document.getElementsByName("sort")

keyFilterElements = Array.from(keyFilterElements)
stateFilterElements = Array.from(stateFilterElements)
sortElements = Array.from(sortElements)

keyFilterElements.forEach(elem => elem.addEventListener("click", () => clickKeyFilter(elem)))
stateFilterElements.forEach(elem => elem.addEventListener("click", () => clickStateFilter(elem)))
sortElements.forEach(elem => elem.addEventListener("click", () => clickSort(elem)))

function clickKeyFilter(elem) {
  elem.classList.toggle("checked")
  applyOptions()
}

function clickStateFilter(elem) {
if (elem.classList.contains("checked")) {
    return
  }

  stateFilterElements.forEach(e => e.classList.remove("checked"))
  elem.classList.add("checked")

  applyOptions()
}

function clickSort(elem) {
  if (elem.classList.contains("checked")) {
    return
  }

  sortElements.forEach(e => e.classList.remove("checked"))
  elem.classList.add("checked")

  applyOptions()
}

async function applyOptions() {
  const selectedKeys = Array.from(document.getElementsByName("filterKey"))
    .filter(elem => elem.classList.contains("checked"))
    .map(elem => elem.value)

  const pp = document.querySelectorAll('.checkbutton.checked[name="filterState"]')[0].value

  tableBody.innerHTML = ''
  searchBarUsers.value = ''

  if (selectedKeys.length === 0) {
    return
  }

  let reverse = document.getElementById("reverse").classList.contains("checked")
  reverse = reverse ? "True" : "False"

  const country = document.getElementById("searchcountry").value
  const sort = document.querySelectorAll('.checkbutton.checked[name="sort"]')[0].value
  const queryKeys = selectedKeys.map(key => 'key=' + encodeURIComponent(key)).join('&')
  const query = [`sort=${encodeURIComponent(sort)}`, `country=${encodeURIComponent(country)}`, queryKeys, `pp=${encodeURIComponent(pp)}`, `reverse=${encodeURIComponent(reverse)}`].join('&')
  const url = API_BASE + 'api/search/users?' + query
  const response = await fetch(url)
  const rows = await response.json()

  for (const row of rows) {
    const tr = document.createElement('tr');
    tr.id = row["id"];
    tr.onclick = function() { window.location.href = `${API_BASE}api/search/users/${tr.id}` }
    const time = `${Math.floor(row["length"]/60)}:${(row["length"]%60).toString().padStart(2, '0')}`

    tr.innerHTML = `
      <td style="width: 4%; text-align: left;">${row["pos"]}</td>
      <td style="width: 12%;" >${row["name"]}</td>
      <td style="width: 7%;" >${row["pp"]}pp</td>
      <td style="width: 11%;">${row["rscore"]}</td>
      <td style="width: 7%; text-align: left; padding-left: 1em;">${row["rperc"]}%</td>
      <td style="width: 11%;">${row["tscore"]}</td>
      <td style="width: 7%; text-align: left; padding-left: 1em;">${row["tperc"]}%</td>
      <td style="width: 10%;">${row["numscores"]}</td>
      <td style="width: 10%;">${row["beatmap plays"]}</td>
      <td style="width: 9%;">${row["last score"]} d</td>
      <td style="width: 12%;">${row["country"]}</td>`
    tableBody.appendChild(tr)
  }
}

searchBarUsers.addEventListener("input", function() {
  const rows = tableBody.getElementsByTagName("tr")
  const subString = searchBarUsers.value.toLowerCase()
  if (searchBarUsers.value === '') {
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

searchBarCountry.addEventListener("input", () => timerInterrupt())

let timerId = null;

function timerInterrupt() {
  if (timerId !== null) {
    clearTimeout(timerId);
  }

  timerId = setTimeout(() => applyOptions(), 250); 
}

applyOptions()