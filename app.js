
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
    if (statsData.most_runs) updateMostRunsTable();
    if (statsData.highest_scores) renderHighestScores();
    populateCountryDropdown();
    updateFastestTable();
    updateFastestInningsTable();
    updatePhaseStatsTable();
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    document.querySelector(`button[onclick="switchTab('${tabId}')"]`).classList.add('active');
}

function updateMostRunsTable() {
    const positionFilter = document.getElementById('mostRunsPositionSelect').value;
    const searchInput = document.getElementById('mostRunsSearch');
    const searchQuery = searchInput ? searchInput.value.toLowerCase() : '';
    const tbody = document.querySelector('#mostRunsTable tbody');
    tbody.innerHTML = '';

    let data;
    if (positionFilter === 'All') {
        data = statsData.most_runs;
    } else {
        data = statsData.most_runs_by_position?.[positionFilter] || [];
    }

    if (searchQuery) {
        data = data.filter(p => p.name.toLowerCase().includes(searchQuery));
    }

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">No records found.</td></tr>';
        return;
    }

    data.slice(0, 50).forEach((player, index) => {
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
    const oppositionSet = new Set();

    // Collect all countries from fastest milestones data
    for (const milestone in statsData.fastest_milestones) {
        statsData.fastest_milestones[milestone].forEach(p => countrySet.add(p.team));
    }

    // Also collect from fastest innings for opposition
    for (const milestone in statsData.fastest_innings_milestones) {
        statsData.fastest_innings_milestones[milestone].forEach(p => {
            countrySet.add(p.team);
            if (p.minq) oppositionSet.add(p.minq);
        });
    }

    const select = document.getElementById('countrySelect');
    const selectInnings = document.getElementById('inningsCountrySelect');
    const selectOpposition = document.getElementById('inningsOppositionSelect');
    const phaseCountrySelect = document.getElementById('phaseCountrySelect');
    const phaseOppositionSelect = document.getElementById('phaseOppositionSelect');

    const sortedCountries = [...countrySet].sort();
    const sortedOppositions = [...oppositionSet].sort();

    // Populate main country dropdown
    sortedCountries.forEach(country => {
        const option = document.createElement('option');
        option.value = country;
        option.textContent = country;
        select.appendChild(option);
    });

    // Populate innings country dropdown
    if (selectInnings) {
        sortedCountries.forEach(country => {
            const option = document.createElement('option');
            option.value = country;
            option.textContent = country;
            selectInnings.appendChild(option);
        });
    }

    // Populate Phase Stats Country Dropdown
    if (phaseCountrySelect) {
        sortedCountries.forEach(country => {
            const option = document.createElement('option');
            option.value = country;
            option.textContent = country;
            phaseCountrySelect.appendChild(option);
        });
    }

    if (selectOpposition) {
        sortedOppositions.forEach(opp => {
            const option = document.createElement('option');
            option.value = opp;
            option.textContent = opp;
            selectOpposition.appendChild(option);
        });
    }

    // Populate Phase Stats Opposition Dropdown
    if (phaseOppositionSelect) {
        sortedOppositions.forEach(opp => {
            const option = document.createElement('option');
            option.value = opp;
            option.textContent = opp;
            phaseOppositionSelect.appendChild(option);
        });
    }
}

function updateFastestTable() {
    const milestone = document.getElementById('milestoneSelect').value;
    const countryFilter = document.getElementById('countrySelect').value;
    const metric = document.getElementById('metricSelect').value;
    const searchInput = document.getElementById('fastestSearch');
    const searchQuery = searchInput ? searchInput.value.toLowerCase() : '';
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

    if (searchQuery) {
        data = data.filter(p => p.name.toLowerCase().includes(searchQuery));
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
    const oppositionFilter = document.getElementById('inningsOppositionSelect').value;
    const positionFilter = document.getElementById('inningsPositionSelect').value;
    const searchInput = document.getElementById('fastestInningsSearch');
    const searchQuery = searchInput ? searchInput.value.toLowerCase() : '';
    const tbody = document.querySelector('#fastestInningsTable tbody');
    tbody.innerHTML = '';

    let data = statsData.fastest_innings_milestones?.[milestone] || [];

    if (countryFilter && countryFilter !== 'All') {
        data = data.filter(p => p.team === countryFilter);
    }

    if (oppositionFilter && oppositionFilter !== 'All') {
        data = data.filter(p => p.minq === oppositionFilter);
    }

    if (positionFilter && positionFilter !== 'All') {
        data = data.filter(p => p.position === positionFilter);
    }

    if (searchQuery) {
        data = data.filter(p => p.name.toLowerCase().includes(searchQuery));
    }

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9">No records found.</td></tr>';
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
                <td>${record.position || 'N/A'}</td>
                <td>${record.minq}</td>
                <td>${record.venue}</td>
                <td>${record.balls}</td>
                <td>${record.date}</td>
                <td>${record.runs}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

function updatePhaseStatsTable() {
    const phase = document.getElementById('phaseSelect').value;
    const category = document.getElementById('phaseCategorySelect').value;
    const countryFilter = document.getElementById('phaseCountrySelect') ? document.getElementById('phaseCountrySelect').value : 'All';
    const oppositionFilter = document.getElementById('phaseOppositionSelect') ? document.getElementById('phaseOppositionSelect').value : 'All';
    const sortOrder = document.getElementById('sortOrder') ? document.getElementById('sortOrder').value : 'desc';

    const searchInput = document.getElementById('phaseSearch');
    const searchQuery = searchInput ? searchInput.value.toLowerCase() : '';
    const tbody = document.querySelector('#phaseStatsTable tbody');
    const thead = document.querySelector('#phaseStatsTable thead');

    tbody.innerHTML = '';
    thead.innerHTML = '';

    // Set Headers based on category
    let headers = '';
    if (category === 'team_innings_highs') {
        headers = `
            <tr>
                <th>Rank</th>
                <th>Team</th>
                <th>Opposition</th>
                <th>Venue</th>
                <th>Score</th>
                <th>Date</th>
            </tr>
        `;
    } else if (category === 'batsman_runs') {
        headers = `
            <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Team</th>
                <th>Runs</th>
                <th>Balls</th>
            </tr>
        `;
    } else if (category === 'bowler_wickets') {
        headers = `
             <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Team</th>
                <th>Wickets</th>
            </tr>
        `;
    } else if (category === 'batsman_innings_highs') {
        headers = `
             <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Team</th>
                <th>Opposition</th>
                <th>Venue</th>
                <th>Runs</th>
                <th>Balls</th>
                <th>Date</th>
            </tr>
        `;
    } else if (category === 'bowler_innings_wickets') {
        headers = `
             <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Team</th>
                <th>Opposition</th>
                <th>Venue</th>
                <th>Wickets</th>
                <th>Runs Conceded</th>
                <th>Date</th>
            </tr>
        `;
    }
    thead.innerHTML = headers;

    // Get Data
    if (!statsData.phase_stats || !statsData.phase_stats[category] || !statsData.phase_stats[category][phase]) {
        tbody.innerHTML = '<tr><td colspan="5">Data not available (Run data_processor.py to update).</td></tr>';
        return;
    }

    let data = [...statsData.phase_stats[category][phase]]; // Copy array to avoid mutating original

    // Apply Dropdown Filters
    if (countryFilter && countryFilter !== 'All') {
        data = data.filter(item => item.team === countryFilter);
    }
    if (oppositionFilter && oppositionFilter !== 'All') {
        // Opposition not present in career stats, safe to check
        data = data.filter(item => item.opposition && item.opposition === oppositionFilter);
    }

    if (searchQuery) {
        if (category === 'team_innings_highs') {
            data = data.filter(item => item.team.toLowerCase().includes(searchQuery) || item.opposition.toLowerCase().includes(searchQuery));
        } else if (category === 'batsman_innings_highs' || category === 'bowler_innings_wickets') {
            data = data.filter(item => item.name.toLowerCase().includes(searchQuery) || item.team.toLowerCase().includes(searchQuery) || item.opposition.toLowerCase().includes(searchQuery));
        } else {
            data = data.filter(item => item.name.toLowerCase().includes(searchQuery));
        }
    }

    // Sort Data
    data.sort((a, b) => {
        let valA, valB;
        if (category === 'team_innings_highs' || category === 'batsman_innings_highs') {
            valA = a.runs;
            valB = b.runs;
        } else if (category === 'bowler_innings_wickets') {
            valA = a.value;
            valB = b.value;
        } else if (category === 'batsman_runs' || category === 'bowler_wickets') {
            valA = a.value;
            valB = b.value;
        }

        if (sortOrder === 'asc') {
            return valA - valB;
        } else {
            return valB - valA;
        }
    });


    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">No records found.</td></tr>';
        return;
    }

    data.slice(0, 50).forEach((item, index) => {
        let row = '';
        if (category === 'team_innings_highs') {
            row = `
                <tr>
                    <td>${index + 1}</td>
                    <td>${item.team}</td>
                    <td>${item.opposition}</td>
                    <td>${item.venue ? item.venue : 'N/A'}</td>
                    <td>${item.runs}/${item.wickets !== undefined ? item.wickets : 0}</td>
                    <td>${item.date}</td>
                </tr>
            `;
        } else if (category === 'batsman_runs') {
            row = `
                <tr>
                    <td>${index + 1}</td>
                    <td>${item.name}</td>
                    <td>${item.team}</td>
                    <td>${item.value}</td>
                    <td>${item.balls}</td>
                </tr>
            `;
        } else if (category === 'bowler_wickets') {
            row = `
                <tr>
                    <td>${index + 1}</td>
                    <td>${item.name}</td>
                    <td>${item.team}</td>
                    <td>${item.value}</td>
                </tr>
            `;
        } else if (category === 'batsman_innings_highs') {
            row = `
                <tr>
                    <td>${index + 1}</td>
                    <td>${item.name}</td>
                    <td>${item.team}</td>
                    <td>${item.opposition}</td>
                    <td>${item.venue ? item.venue : 'N/A'}</td>
                    <td>${item.runs}</td>
                    <td>${item.balls}</td>
                    <td>${item.date}</td>
                </tr>
            `;
        } else if (category === 'bowler_innings_wickets') {
            row = `
                <tr>
                    <td>${index + 1}</td>
                    <td>${item.name}</td>
                    <td>${item.team}</td>
                    <td>${item.opposition}</td>
                    <td>${item.venue ? item.venue : 'N/A'}</td>
                    <td>${item.value}</td>
                    <td>${item.runs}</td>
                    <td>${item.date}</td>
                </tr>
            `;
        }
        tbody.innerHTML += row;
    });
}
