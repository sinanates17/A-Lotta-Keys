/** @type {typeof import("plotly.js-dist-min")} */
const Plotly = window.Plotly;
const scoreData = Object.values(beatmapData.scores);
const playData = Object.values(beatmapData["play history"])
const passData = Object.values(beatmapData["pass history"])
const timeData = Object.keys(beatmapData["play history"])

const accs = scoreData.map(score => score["acc"]);
const scores = scoreData.map(score => score["score"]);
const users = scoreData.map(score => userLinksData[score["uid"]]);
const timesScores = scoreData.map(score => dateFromTimestamp(score["time"]))
const colors = scoreData.map(score => colorFromSeed(score["uid"]))

const plays = Array.from(playData.values())
const passes = Array.from(passData.values())
const timesPlays = timeData.map(ts => dateFromTimestamp(ts))

const customdata = users.map((u, i) => [u, 
                                        scores[i], 
                                        `${Math.round(accs[i]*10000)/100}%`, 
                                        formatDate(timesScores[i])])
const templateStr = 'Player: %{customdata[0]}<br>Score: %{customdata[1]}<br>Accuracy: %{customdata[2]}<br>Date: %{customdata[3]}';

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
};

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
};

Plotly.newPlot("plotAccScore", [traceAccScore], layoutAccScore);

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
};

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
    plot_bgcolor: "#18121b"
};

Plotly.newPlot("plotTimeScore", [traceTimeScore], layoutTimeScore);

const traceTimePlays = {
    x: timesPlays,
    y: plays,
    mode: "lines",
    type: "scatter",
    name: "plays"
};

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
    plot_bgcolor: "#18121b"
};

Plotly.newPlot("plotTimePlays", [traceTimePlays, traceTimePasses], layoutTimePlays)

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