/** @type {typeof import("plotly.js-dist-min")} */

const isDev = window.location.hostname === "127.0.0.1";

API_BASE = isDev
  ? "http://127.0.0.1:5000/"
  : "https://alottakeys.xyz/";

const Plotly = window.Plotly;
const templateStr = 'Beatmap: %{customdata[0]}<br>' + 
                    'Score: %{customdata[1]}<br>' + 
                    'Accuracy: %{customdata[2]}<br>' + 
                    'PP: %{customdata[3]}<br>' + 
                    'Grade: %{customdata[4]}<br>' + 
                    'Status: %{customdata[5]}<br>' + 
                    'Date: %{customdata[6]}';

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

function colorFromSeed(seed) {
    seed = parseFloat(seed);
    const r =  Math.floor(96 * (Math.sin(seed) + 1)) + 64;
    const g =  Math.floor(96 * (Math.sin(seed/2) + 1)) + 64;
    const b =  Math.floor(96 * (Math.sin(seed/3) + 1)) + 64;

    const color = `rgb(${r}, ${g}, ${b})`
    return color;
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

const pbToggle = document.getElementById("pbButton")
const topPlays = document.getElementById("topPlays")
const beatmaps = Object(beatmapData)

let pbOnly = pbToggle.dataset.value === "true"

function getFilters() {

    let filters = []

    let options = Array.from(document.querySelectorAll(".keymodesCheckbox"))

    for (let option of options) {
        if (option.checked) {
            if (option.name === "key") {
                filters.push(Number(option.value))
            } 
            else {
                filters.push(option.value)
            }
        }
    }

    return filters;

}

function togglePBs() {

    if (pbToggle.dataset.value === "true") {
        pbToggle.dataset.value = "false"
    }

    else {
        pbToggle.dataset.value = "true"
    }

    pbOnly = pbToggle.dataset.value === "true"

    applyFilter()

}

function fillTopPlays(rows) {

    topPlays.innerHTML = "";

    let pos = 1
    for (const row of rows) {
        const tr = document.createElement('tr');
        tr.id = row["bid"];

        let ratio = "-"
        if (row["300"] > 0) {
            ratio = Math.round(row["320"] * 100 / row["300"]) / 100
        }
        const acc = Math.round(row.acc * 10000) / 100

        tr.onclick = function() { window.location.href = `${API_BASE}api/search/beatmaps/${tr.id}` }
        tr.innerHTML = `
                    <td style="width: 4%; text-align: left;">${pos}</td>
                    <td style="width: 40%;">${beatmaps[row.bid].name}</td>
                    <td style="width: 8%;">${row.pp}pp</td>
                    <td style="width: 8%;">${acc}%</td>
                    <td style="width: 12%;">${row.score}</td>
                    <td style="width: 8%;">${ratio}</td>
                    <td style="width: 8%;">${row.combo}</td>
                    <td style="width: 12%;">${formatStrDate(row.time)}</td>`;

        pos = pos + 1

    topPlays.appendChild(tr);
    }
}

function formatStrDate(str) {
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    const year = `20${str.slice(0, 2)}`
    const month = months[parseInt(str.slice(2, 4)) - 1]
    const day = parseInt(str.slice(4, 6))

    return `${day} ${month} ${year}`
}

function applyFilter() {

    let scoreData = Object.values(userData["scores"]);
    if (pbOnly) {
        scoreData = scoreData.filter(score => score["pb"])
    }

    let filters = getFilters()

    scoreData = scoreData.filter(score => {
        const keys = beatmaps[score.bid]?.keys;
        const status = beatmaps[score.bid]?.status;
        return keys !== undefined && (filters.includes(parseInt(keys)) && filters.includes(status));
    });

    let = rows = Array.from(scoreData).sort((a, b) => b.pp - a.pp);
    rows = rows.filter(row => row["top"])
    fillTopPlays(rows);

    let playData = Object.values(userData["beatmap plays history"]);
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
}

applyFilter()