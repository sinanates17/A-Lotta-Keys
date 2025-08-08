/** @type {typeof import("plotly.js-dist-min")} */

const userPageSettings = Object(userSettings)
const dispFav = document.getElementById("favpattern")
const labFav = document.getElementById("favpatternlabel")

if (userPageSettings?.fav) {
    dispFav.textContent = userPageSettings.fav
}

else {
    dispFav.style.display = 'none'
    labFav.style.display = 'none'
}


const beatmaps = Object(beatmapData)
const topPlaysTable = document.getElementById("topPlaysTable")
const tabLabel = document.getElementById("tablabel")
const pbFilter = document.getElementById("filterPB")
const topFilter = document.getElementById("filterTop") 

const Plotly = window.Plotly;
const templateStr = 'Beatmap: %{customdata[0]}<br>' + 
                    'Score: %{customdata[1]}<br>' + 
                    'Accuracy: %{customdata[2]}<br>' + 
                    'PP: %{customdata[3]}<br>' + 
                    'Grade: %{customdata[4]}<br>' + 
                    'Status: %{customdata[5]}<br>' + 
                    'Date: %{customdata[6]}';

let keyFilterElements = document.getElementsByName("filterKey")
let stateFilterElements = document.getElementsByName("filterState")
let tabElements = document.getElementsByName("statsTab")

keyFilterElements = Array.from(keyFilterElements)
stateFilterElements = Array.from(stateFilterElements)
tabElements = Array.from(tabElements)

keyFilterElements.forEach(elem => elem.addEventListener("click", () => clickFilter(elem)))
stateFilterElements.forEach(elem => elem.addEventListener("click", () => clickFilter(elem)))
tabElements.forEach(elem => elem.addEventListener("click", () => clickTab(elem)))
pbFilter.addEventListener("click", () => clickFilter(pbFilter))
topFilter.addEventListener("click", () => clickFilter(topFilter))

function clickFilter(elem) {
  elem.classList.toggle("checked")
  applyFilters()
}

function clickTab(elem) {
  if (elem.classList.contains("checked")) {
    return
  }

  tabElements.forEach(e => {
    e.classList.remove("checked")
    const page = document.getElementById(e.value)
    page.classList.remove("active")
  })

  elem.classList.add("checked")
  tabLabel.textContent = elem.dataset.tabname
  const page = document.getElementById(elem.value)
  page.classList.add("active")
}

async function applyFilters() {

  const filters = []
  const pbOnly = pbFilter.classList.contains("checked")
  const topOnly = topFilter.classList.contains("checked")

  keyFilterElements.map(elem => {
    if (elem.classList.contains("checked")) {
      filters.push(Number(elem.value))
    }
  })
  stateFilterElements.map(elem => {
    if (elem.classList.contains("checked")) {
      filters.push(elem.value)
    }
  })

  let scoreData = Object.values(userData.scores)

  if (pbOnly) {
    scoreData = scoreData.filter(score => score.pb)
  }

  if (topOnly) {
    scoreData = scoreData.filter(score => score.top)
  }

  scoreData = scoreData.filter(score => {
    const keys = beatmaps[score.bid]?.keys
    const state = beatmaps[score.bid]?.status
    return keys !== undefined && ( filters.includes(parseInt(keys)) && filters.includes(state) )
  })

  let rows = Array.from(scoreData).sort((a, b) => b.pp - a.pp)
  rows = rows.filter(r => r.top)

  fillTopPlays(rows)

  let playData = Object.values(userData["beatmap plays history"]);
    let playDataDiffs= playData.slice(1).map((val, i) => val - playData[i]);
    let playDataTimes = Object.keys(userData["beatmap plays history"]);
    let ppTimeData = Object.values(userData["pp history"])

    let seriesStatus = (() => {
        let RLU = ["Ranked", "Loved", "Unranked"];
        let RL = ["Ranked", "Loved"];
        if (RLU.every(el => filters.includes(el))){
            return "RLU";
        }
        else if (RL.every(el => filters.includes(el))){
            return "RL";
        }
        else if (filters.includes("Unranked") && (!filters.includes("Ranked") && !filters.includes("Loved"))) {
            return "U";
        }
        else if (filters.includes("Ranked") && (!filters.includes("Unranked") && !filters.includes("Loved"))) {
            return "R";
        }
        else if (filters.includes("Loved") && (!filters.includes("Ranked") && !filters.includes("Unranked"))) {
            return "L";
        }
        else {
            return null;
        }
    })();

    let seriesKeys = (() => {
        let keyFilters = filters.filter(el => typeof el === "number");

        let _9kp = [9, 10, 12, 14, 16, 18];
        let _10kp = [10, 12, 14, 16, 18];
        let _12kp = [12, 14, 16, 18];
        if (_9kp.every(el => keyFilters.includes(el))) {
            return "9+";
        }
        else if (_10kp.every(el => keyFilters.includes(el))) {
            return "10+";
        }
        else if (_12kp.every(el => keyFilters.includes(el))) {
            return "12+";
        }
        else if (keyFilters.length == 1) {
            return String(keyFilters[0]);
        }
        else {
            return null;
        }
    })();

    let ppTimes = Object.keys(userData["pp history"]).map(time => dateFromTimestamp(time))
    let ppSeries = (() => {
        if (seriesStatus !== null && seriesKeys !== null)
            return ppTimeData.map(point => point[seriesStatus][seriesKeys])
        else {
            return ppTimeData.map(point => 0)
        }
    })();

    let accs = scoreData.map(score => score["acc"]);
    let scores = scoreData.map(score => score["score"]);
    let grades = scoreData.map(score => score["grade"]);
    let pps = scoreData.map(score => score["pp"]);
    let bids = scoreData.map(score => String(score["bid"]));
    let bmnames = bids.map(bid => beatmapData[bid]?.["name"] || "Unknown");
    let states = bids.map(bid => beatmapData[bid]?.["status"] || "Unknown");
    let timesScores = scoreData.map(score => dateFromTimestamp(score["time"]));
    let colors = scoreData.map(score => colorFromSeed(score["bid"]));
    let timesPlays = playDataTimes.map(time => dateFromTimestamp(time))

    let customdata = bmnames.map((b, i) => [b, 
                                            scores[i], 
                                            `${Math.round(accs[i]*10000)/100}%`, 
                                            pps[i],
                                            grades[i],
                                            states[i],
                                            formatDate(timesScores[i])]);


    let traceTimePP = {
        x: timesScores,
        y: pps,
        customdata: customdata,
        colors: colors,
        mode: "markers",
        type: "scatter",
        hovertemplate: templateStr,
        marker: {
            color: colors
        },
        hoverlabel: { namelength: 0 },
    };

    let layoutTimePP = {
        font: {
            family: "ubuntu",
            color: "#efe5f3"
        },
        title: { text: 'PP vs Time'},
        xaxis: { 
            title: { text: 'Time' },
            gridcolor: "#4e4950",
            zerolinecolor: "#efe5f3"
        },
        yaxis: { 
            title: { text: 'PP' },
            gridcolor: "#4e4950",
            zerolinecolor: "#efe5f3"
        },
        hovermode: "closest",
        paper_bgcolor: "#18121b",
        plot_bgcolor: "#18121b"
    };

    Plotly.newPlot("plotTimePP", [traceTimePP], layoutTimePP)

    let traceCumTimePP = {
        x: ppTimes,
        y: ppSeries,
        mode: "line",
        type: "scatter",
        hoverlabel: { namelength: 0 },
    };

    let layoutCumTimePP = {
        font: {
            family: "ubuntu",
            color: "#efe5f3"
        },
        title: { text: 'Cumulative PP vs Time'},
        xaxis: { 
            title: { text: 'Time' },
            gridcolor: "#4e4950",
            zerolinecolor: "#efe5f3"
        },
        yaxis: { 
            title: { text: 'PP' },
            gridcolor: "#4e4950",
            zerolinecolor: "#efe5f3"
        },
        hovermode: "closest",
        paper_bgcolor: "#18121b",
        plot_bgcolor: "#18121b"
    };

    Plotly.newPlot("plotCumTimePP", [traceCumTimePP], layoutCumTimePP)

    let traceTimePlays = {
        x: timesPlays,
        y: playData,
        mode: "line",
        type: "scatter",
        hoverlabel: { namelength: 0 },
    };

    let layoutTimePlays = {
        font: {
            family: "ubuntu",
            color: "#efe5f3"
        },
        title: { text: 'Beatmap Plays vs Time'},
        xaxis: { 
            title: { text: 'Time' },
            gridcolor: "#4e4950",
            zerolinecolor: "#efe5f3"
        },
        yaxis: { 
            title: { text: 'Plays' },
            gridcolor: "#4e4950",
            zerolinecolor: "#efe5f3"
        },
        hovermode: "closest",
        paper_bgcolor: "#18121b",
        plot_bgcolor: "#18121b"
    };

    Plotly.newPlot("plotTimePlays", [traceTimePlays], layoutTimePlays)

        let traceTimePlaysDiffs = {
        x: timesPlays,
        y: playDataDiffs,
        mode: "line",
        type: "scatter",
        hoverlabel: { namelength: 0 },
    };

    let layoutTimePlaysDiffs = {
        font: {
            family: "ubuntu",
            color: "#efe5f3"
        },
        title: { text: 'Daily Beatmap Plays'},
        xaxis: { 
            title: { text: 'Time' },
            gridcolor: "#4e4950",
            zerolinecolor: "#efe5f3"
        },
        yaxis: { 
            title: { text: 'Plays' },
            gridcolor: "#4e4950",
            zerolinecolor: "#efe5f3"
        },
        hovermode: "closest",
        paper_bgcolor: "#18121b",
        plot_bgcolor: "#18121b"
    };

    Plotly.newPlot("plotTimePlaysDiffs", [traceTimePlaysDiffs], layoutTimePlaysDiffs)
}

function fillTopPlays(rows) {

    topPlaysTable.innerHTML = "";

    let pos = 1
    for (const row of rows) {
        if (row.old) {
            continue
        }
        const tr = document.createElement('tr')
        tr.id = row.bid

        let ratio = "-"
        if (row["300"] > 0) {
            ratio = Math.round(row["320"] * 100 / row["300"]) / 100
        }
        const acc = Math.round(row.acc * 10000) / 100

        tr.onclick = function() { window.location.href = `${API_BASE}api/search/beatmaps/${tr.id}` }
        tr.innerHTML = `
                    <td style="width: 4%; text-align: left;">${pos}</td>
                    <td style="width: 40%; text-align: left;">${beatmaps[row.bid].name}</td>
                    <td style="width: 8%;">${row.pp}pp</td>
                    <td style="width: 8%;">${acc}%</td>
                    <td style="width: 12%;">${row.score}</td>
                    <td style="width: 8%;">${ratio}</td>
                    <td style="width: 8%;">${row.combo}</td>
                    <td style="width: 12%;">${formatStrDate(row.time)}</td>`

        pos = pos + 1

    topPlaysTable.appendChild(tr)
    }
}

function formatStrDate(str) {
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    const year = `20${str.slice(0, 2)}`
    const month = months[parseInt(str.slice(2, 4)) - 1]
    const day = parseInt(str.slice(4, 6))

    return `${day} ${month} ${year}`
}

function formatDate(date) {
    const day = date.getUTCDate();
    const month = date.getUTCMonth();
    const year = date.getUTCFullYear();

    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

    const formatted = `${day} ${monthNames[month]} ${year}`;
    return formatted;
}

function colorFromSeed(seed) {
    seed = parseFloat(seed);
    const r =  Math.floor(96 * (Math.sin(seed) + 1)) + 64;
    const g =  Math.floor(96 * (Math.sin(seed/2) + 1)) + 64;
    const b =  Math.floor(96 * (Math.sin(seed/3) + 1)) + 64;

    const color = `rgb(${r}, ${g}, ${b})`
    return color;
}

function dateFromTimestamp(ts) {
    const year = 2000 + parseInt(ts.slice(0, 2));
    const month = parseInt(ts.slice(2, 4)) - 1;
    const day = parseInt(ts.slice(4, 6));
    const hour = parseInt(ts.slice(6, 8));
    const minute = parseInt(ts.slice(8, 10));
    const second = parseInt(ts.slice(10, 12));

    const date = new Date(year, month, day, hour, minute, second);

    return date;
}

applyFilters()