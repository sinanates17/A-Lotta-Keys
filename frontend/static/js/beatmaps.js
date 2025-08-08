const searchBar = document.getElementById("search")
const tableBody = document.getElementById("tablebody")

let filterElements = document.querySelectorAll('[name="filterKey"], [name="filterState"], [id="reverse"]')
let sortElements = document.getElementsByName("sort")

filterElements = Array.from(filterElements)
sortElements = Array.from(sortElements)

filterElements.forEach(elem => elem.addEventListener("click", () => clickFilter(elem)))
sortElements.forEach(elem => elem.addEventListener("click", () => clickSort(elem)))

function clickFilter(elem) {
  elem.classList.toggle("checked")
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

  const selectedStates = Array.from(document.getElementsByName("filterState"))
  .filter(elem => elem.classList.contains("checked"))
  .map(elem => elem.value)

  tableBody.innerHTML = ''

  if (selectedKeys.length === 0 || selectedStates.length === 0) {
    return
  }

  let reverse = document.getElementById("reverse").classList.contains("checked")
  reverse = reverse ? "True" : "False"
  const sort = document.querySelectorAll('.checkbutton.checked[name="sort"]')[0].value
  const queryKeys = selectedKeys.map(key => 'key=' + encodeURIComponent(key)).join('&')
  const queryStates = selectedStates.map(key => 'status=' + encodeURIComponent(key)).join('&')
  const query = [`sort=${encodeURIComponent(sort)}`, queryKeys, queryStates, `reverse=${encodeURIComponent(reverse)}`].join('&')
  const url = API_BASE + 'api/search/beatmaps?' + query
  const response = await fetch(url)
  const rows = await response.json()

  for (const row of rows) {
    const tr = document.createElement('tr');
    tr.id = row["id"];
    tr.onclick = function() { window.location.href = `${API_BASE}api/search/beatmaps/${tr.id}` }
    const time = `${Math.floor(row["length"]/60)}:${(row["length"]%60).toString().padStart(2, '0')}`

    tr.innerHTML = `
      <td style="width: 4%; text-align: left;">${row["pos"]}</td>
      <td style="width: 43%; text-align: left;">${row["name"]}</td>
      <td style="width: 11%;">${row["mapper"]}</td>
      <td style="width: 5%;">${row["keys"]}</td>
      <td style="width: 5%;">${row["sr"]}</td>
      <td style="width: 5%;">${row["plays"]}</td>
      <td style="width: 5%;">${row["passes"]}</td>
      <td style="width: 7%;">${time}</td>
      <td style="width: 7%;">${row["ln perc"]}%</td>
      <td style="width: 7%;">${row["status"]}</td>`
    tableBody.appendChild(tr)
  }
}

searchBar.addEventListener("input", function() {
  const rows = tableBody.getElementsByTagName("tr")
  const subString = searchBar.value.toLowerCase()
  console.log("test")
  if (searchBar.value === '') {
    for (const row of rows) {
      row.style.display = "table-row"
    }
    return;
  }

  for (const row of rows) {
    var cells = row.getElementsByTagName("td");
    var name = cells[1].textContent.toLowerCase()
    var mapper = cells[2].textContent.toLowerCase()

    if (name.includes(subString) | mapper.includes(subString)) {
      row.style.display = "table-row"
    }
    else {
      row.style.display = "none"
    }

  }
})

applyOptions()