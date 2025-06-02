/** @type {typeof import("plotly.js-dist-min")} */
const Plotly = window.Plotly;
const scoreData = Object.values(beatmapData.scores);

const accs = scoreData.map(score => score["acc"]);
const scores = scoreData.map(score => score["score"]);
const users = scoreData.map(score => userLinksData[score["uid"]]);
const times = scoreData.map(score => dateFromTimestamp(score["time"]))
const colors = scoreData.map(score => colorFromSeed(score["uid"]))

const customdata = users.map((u, i) => [u, 
                                        scores[i], 
                                        `${Math.round(accs[i]*10000)/100}%`, 
                                        formatDate(times[i])])
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
    title: 'Acc vs Score',
    xaxis: { title: 'Accuracy' },
    yaxis: { title: 'Score' },
    hovermode: "closest"
};

Plotly.newPlot("plotAccScore", [traceAccScore], layoutAccScore)

const traceTimeScore = {
    x: times,
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
    title: 'Time vs Score',
    xaxis: { title: 'Time' },
    yaxis: { title: 'Score' },
    hovermode: "closest"
};

Plotly.newPlot("plotTimeScore", [traceTimeScore], layoutTimeScore)

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
    const r =  Math.floor(128 * (Math.sin(seed) + 1));
    const g =  Math.floor(128 * (Math.sin(seed/2) + 1));
    const b =  Math.floor(128 * (Math.sin(seed/3) + 1));

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