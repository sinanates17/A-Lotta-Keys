/** @type {typeof import("plotly.js-dist-min")} */

const Plotly = window.Plotly;
const leaderboard = document.getElementById("leaderboardtable")
const tabLabel = document.getElementById("tablabel")
let tabElements = document.getElementsByName("statsTab")

tabElements = Array.from(tabElements)
tabElements.forEach(elem => elem.addEventListener("click", () => clickTab(elem)))

fillData()

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

function fillData() {
    const scoreData = Object.values(beatmapData.scores)
    const playData = Object.values(beatmapData["play history"])
    const passData = Object.values(beatmapData["pass history"])
    const timeData = Object.keys(beatmapData["play history"])


    let timeRanked = null

    if (rankedDate !== "unranked") {
        timeRanked = dateFromTimestamp(rankedDate)
    }

    const lastUpdated = dateFromTimestamp(beatmapData["updated"])

    const accs = scoreData.map(score => score["acc"])
    const scores = scoreData.map(score => score["score"])
    const users = scoreData.map(score => userLinksData[score["uid"]])
    const timesScores = scoreData.map(score => dateFromTimestamp(score["time"]))
    const colors = scoreData.map(score => colorFromSeed(score["uid"]))

    const plays = Array.from(playData.values())
    const passes = Array.from(passData.values())
    const timesPlays = timeData.map(ts => dateFromTimestamp(ts))

    const customdata = users.map((u, i) => [u, 
                                            scores[i], 
                                            `${Math.round(accs[i]*10000)/100}%`, 
                                            formatDate(timesScores[i])])
    const templateStr = 'Player: %{customdata[0]}<br>Score: %{customdata[1]}<br>Accuracy: %{customdata[2]}<br>Date: %{customdata[3]}'

    const vlines = [
        {
        type: "line",
        x0: timeRanked,
        x1: timeRanked,
        y0: 0,
        y1: 1,
        xref: "x",
        yref: "paper",
        line: { color: "cyan", width: 2 }
        },
        {
        type: "line",
        x0: lastUpdated,
        x1: lastUpdated,
        y0: 0,
        y1: 1,
        xref: "x",
        yref: "paper",
        line: { color: "red", width: 2 }
        }
    ]

    const vlabels = [
        {
        x: timeRanked,
        y: 1,
        xref: "x",
        yref: "paper",
        text: "Ranked",
        showarrow: false,
        font: { color: "cyan" },
        yanchor: "bottom"
        },
        {
        x: lastUpdated,
        y: 1,
        xref: "x",
        yref: "paper",
        text: "Updated",
        showarrow: false,
        font: { color: "red" },
        yanchor: "bottom"
        },
    ]

    if (timeRanked === null) {
        vlines.shift()
        vlabels.shift()
    }

    const traceAccScore = {
        x: accs,
        y: scores,
        customdata: customdata,
        colors: colors,
        mode: "markers",
        type: "scatter",
        hovertemplate: templateStr,
        marker: {
            color: colors
        },
        hoverlabel: { namelength: 0 },
    }

    const layoutAccScore = {
        font: {
            family: "ubuntu",
            color: "#efe5f3"
        },
        title: { text: 'Acc vs Score'},
        xaxis: { 
            title: { text: 'Accuracy' },
            gridcolor: "#4e4950",
            zerolinecolor: "#efe5f3"
        },
        yaxis: { 
            title: { text: 'Score' },
            gridcolor: "#4e4950",
            zerolinecolor: "#efe5f3"
        },
        hovermode: "closest",
        paper_bgcolor: "#18121b",
        plot_bgcolor: "#18121b"
    }

    Plotly.newPlot("plotAccScore", [traceAccScore], layoutAccScore)

    const traceTimeScore = {
        x: timesScores,
        y: scores,
        customdata: customdata,
        mode: "markers",
        type: "scatter",
        hovertemplate: templateStr,
        marker: {
            color: colors
        },
        hoverlabel: { namelength: 0 },
    }

    const layoutTimeScore = {
        font: {
            family: "ubuntu",
            color: "#efe5f3"
        },
        title: { text: 'Time vs Score'},
        xaxis: { 
            title: { text: 'Time' },
            gridcolor: "#4e4950",
            zerolinecolor: "#efe5f3"
        },
        yaxis: { 
            title: { text: 'Score' },
            gridcolor: "#4e4950",
            zerolinecolor: "#efe5f3"
        },
        hovermode: "closest",
        paper_bgcolor: "#18121b",
        plot_bgcolor: "#18121b",
        shapes: vlines,
        annotations: vlabels
    }

    Plotly.newPlot("plotTimeScore", [traceTimeScore], layoutTimeScore)

    const traceTimePlays = {
        x: timesPlays,
        y: plays,
        mode: "lines",
        type: "scatter",
        name: "plays"
    }

    const traceTimePasses = {
        x: timesPlays,
        y: passes,
        mode: "lines",
        type: "scatter",
        name: "passes"
    }

    const layoutTimePlays = {
        font: {
            family: "ubuntu",
            color: "#efe5f3"
        },
        title: { text: 'Plays and Passes over Time'},
        xaxis: { 
            title: { text: 'Time' },
            gridcolor: "#4e4950",
            zerolinecolor: "#efe5f3"
        },
        yaxis: {
            gridcolor: "#4e4950",
            zerolinecolor: "#efe5f3",
            range: [0, null]
        },
        hovermode: "closest",
        paper_bgcolor: "#18121b",
        plot_bgcolor: "#18121b",
        shapes: vlines,
        annotations: vlabels
    }

    Plotly.newPlot("plotTimePlays", [traceTimePlays, traceTimePasses], layoutTimePlays)

    for (const row of pbData) {
    if (row.old) {
            continue
    }
    const tr = document.createElement('tr')
    tr.id = row["uid"]
    tr.onclick = function() { window.location.href = `${API_BASE}api/search/users/${tr.id}` }
    tr.innerHTML = `
        <td style="width: 4%; text-align: left;">${row["pos"]}</td>
        <td style="width: 12%; text-align: right;">${row["player"]}</td>
        <td style="width: 7%; text-align: right;">${row["pp"]}</td>
        <td style="width: 8; text-align: right;">${row["score"]}</td>
        <td style="width: 10%; text-align: right;">${row["acc"]}%</td>
        <td style="width: 8%; text-align: right;">${row["combo"]}</td>
        <td style="width: 6%; text-align: right;">${row["ratio"]}</td>
        <td style="width: 6%; text-align: right;">${row["marv"]}</td>
        <td style="width: 6%; text-align: right;">${row["perf"]}</td>
        <td style="width: 6%; text-align: right;">${row["great"]}</td>
        <td style="width: 6%; text-align: right;">${row["good"]}</td>
        <td style="width: 6%; text-align: right;">${row["bad"]}</td>
        <td style="width: 6%; text-align: right;">${row["miss"]}</td>
        <td style="width: 9%; text-align: right;">${row["date"]}</td>`

    leaderboard.appendChild(tr);
  }
}