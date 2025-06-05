/** @type {typeof import("plotly.js-dist-min")} */
const Plotly = window.Plotly;

const scoreData = Object.values(userData["scores"]);
const playData = Object.values(userData["beatmap plays history"]);

const accs = scoreData.map(score => score["acc"]);
const scores = scoreData.map(score => score["score"]);
const grades = scoreData.map(score => score["grade"]);
const pps = scoreData.map(score => score["pp"]);
const beatmaps = scoreData.map(score => score["bid"]);
const timesScores = scoreData.map(score => dateFromTimestamp(score["time"]));
const colors = scoreData.map(score => colorFromSeed(score["bid"]));

const customdata = beatmaps.map((b, i) => [b, 
                                        scores[i], 
                                        `${Math.round(accs[i]*10000)/100}%`, 
                                        pps[i],
                                        grades[i],
                                        formatDate(timesScores[i])]);
const templateStr = 'Beatmap: %{customdata[0]}<br>Score: %{customdata[1]}<br>Accuracy: %{customdata[2]}<br>PP: %{customdata[3]}<br>Grade: %{customdata[4]}<br>Date: %{customdata[5]}';

const traceTimePP = {
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

const layoutTimePP = {
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
