
let statsData = {};

document.addEventListener('DOMContentLoaded', () => {
    if (typeof t20Data !== 'undefined') {
        statsData = t20Data;
        initDashboard();
    } else {
        console.error('Data not found. Ensure data.js is loaded.');
    }
});

function initDashboard() {
    renderMostRuns();
    renderHighestScores();
    populateCountryDropdown();
    updateFastestTable();
    updateFastestInningsTable();
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    document.querySelector(`button[onclick="switchTab('${tabId}')"]`).classList.add('active');
}

function renderMostRuns() {
    const tbody = document.querySelector('#mostRunsTable tbody');
    tbody.innerHTML = '';

    statsData.most_runs.forEach((player, index) => {
        const row = `
            <tr>
                <td>${index + 1}</td>
                <td>${player.name}</td>
                <td>${player.team}</td>
                <td>${player.runs}</td>
                <td>${player.balls}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

function renderHighestScores() {
    const tbody = document.querySelector('#highestScoreTable tbody');
    tbody.innerHTML = '';

    statsData.highest_scores.forEach((innings, index) => {
        const strikeRate = ((innings.runs / innings.balls) * 100).toFixed(2);
        // Format date slightly better if needed, currently YYYY-MM-DD
        const date = innings.date;

        // Add * if not out
        const scoreDisplay = innings.is_out ? innings.runs : `${innings.runs}*`;

        const row = `
            <tr>
                <td>${index + 1}</td>
                <td>${innings.name}</td>
                <td>${innings.team}</td>
                <td>${scoreDisplay}</td>
                <td>${innings.balls}</td>
                <td>${strikeRate}</td>
                <td>${date}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

function populateCountryDropdown() {
    const countrySet = new Set();

    // Collect all countries from fastest milestones data
    for (const milestone in statsData.fastest_milestones) {
        statsData.fastest_milestones[milestone].forEach(p => countrySet.add(p.team));
    }

    const select = document.getElementById('countrySelect');
    [...countrySet].sort().forEach(country => {
        const option = document.createElement('option');
        option.value = country;
        option.textContent = country;
        select.appendChild(option);
    });

    const selectInnings = document.getElementById('inningsCountrySelect');
    if (selectInnings) {
        [...countrySet].sort().forEach(country => {
            const option = document.createElement('option');
            option.value = country;
            option.textContent = country;
            selectInnings.appendChild(option);
        });
    }
}

function updateFastestTable() {
    const milestone = document.getElementById('milestoneSelect').value;
    const countryFilter = document.getElementById('countrySelect').value;
    const metric = document.getElementById('metricSelect').value;
    const tbody = document.querySelector('#fastestTable tbody');
    const headerRow = document.querySelector('#fastestTable thead tr');

    tbody.innerHTML = '';

    // Update Header
    if (metric === 'balls') {
        headerRow.innerHTML = `
            <th>Rank</th>
            <th>Player</th>
            <th>Team</th>
            <th>Balls Faced</th>
        `;
    } else {
        headerRow.innerHTML = `
            <th>Rank</th>
            <th>Player</th>
            <th>Team</th>
            <th>Innings Played</th>
        `;
    }

    let data;
    if (metric === 'balls') {
        data = statsData.fastest_milestones[milestone] || [];
    } else {
        data = statsData.fastest_milestones_innings[milestone] || [];
    }

    if (countryFilter !== 'All') {
        data = data.filter(p => p.team === countryFilter);
    }

    // Sort just in case (though python script sorts)
    if (metric === 'balls') {
        data.sort((a, b) => a.balls - b.balls);
    } else {
        data.sort((a, b) => a.innings - b.innings);
    }

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4">No records found for this milestone.</td></tr>';
        return;
    }

    data.slice(0, 50).forEach((player, index) => {
        let value = metric === 'balls' ? player.balls : player.innings;
        const row = `
            <tr>
                <td>${index + 1}</td>
                <td>${player.name}</td>
                <td>${player.team}</td>
                <td>${value}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

function updateFastestInningsTable() {
    const milestone = document.getElementById('inningsMilestoneSelect').value;
    const countryFilter = document.getElementById('inningsCountrySelect').value;
    const tbody = document.querySelector('#fastestInningsTable tbody');
    tbody.innerHTML = '';

    let data = statsData.fastest_innings_milestones?.[milestone] || [];

    if (countryFilter && countryFilter !== 'All') {
        data = data.filter(p => p.team === countryFilter);
    }

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6">No records found for this milestone.</td></tr>';
        return;
    }

    // Show top 50 (or filtered list)
    // Data is already sorted by balls from python script
    data.slice(0, 100).forEach((record, index) => {
        const row = `
            <tr>
                <td>${index + 1}</td>
                <td>${record.team}</td>
                <td>${record.name}</td>
                <td>${record.balls}</td>
                <td>${record.date}</td>
                <td>${record.runs}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}
