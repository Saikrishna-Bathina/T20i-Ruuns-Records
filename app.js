
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
    updateFastestTable();
    updateFastestInningsTable();
    updatePhaseStatsTable();
    updateBowlingMilestonesTable();
    updateInningsMilestonesTable(); // New
    updateBestBowlingTable();
    updateMostWicketsTable();
    updateMostHaulsTable();
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
                <th>Balls</th>
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
            let scoreDisplay = `${item.runs}/${item.wickets !== undefined ? item.wickets : 0}`;
            if (item.result === "No Result" || item.result === "Abandoned") {
                scoreDisplay += ` <span style="color: #ffcc00; font-size: 0.8em;">(N/R)</span>`;
            }

            row = `
                <tr>
                    <td>${index + 1}</td>
                    <td>${item.team}</td>
                    <td>${item.opposition}</td>
                    <td>${item.venue ? item.venue : 'N/A'}</td>
                    <td>${scoreDisplay}</td>
                    <td>${item.balls !== undefined ? item.balls : '-'}</td>
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

function updateBowlingMilestonesTable() {
    const milestone = document.getElementById('bowlingMilestoneSelect').value;
    const type = document.getElementById('bowlingTypeSelect').value;
    const teamSelect = document.getElementById('bowlingTeamSelect');
    const teamLabel = document.getElementById('bowlingTeamSelectLabel');
    const oppSelect = document.getElementById('bowlingOppSelect');
    const oppLabel = document.getElementById('bowlingOppSelectLabel');
    const searchInput = document.getElementById('bowlingSearch');
    const searchQuery = searchInput ? searchInput.value.toLowerCase() : '';
    const tbody = document.querySelector('#bowlingMilestonesTable tbody');
    const thead = document.querySelector('#bowlingMilestonesTable thead tr');

    tbody.innerHTML = '';

    // Handle Dropdown Visibility
    if (type === 'for_team' || type === 'vs_team') {
        teamSelect.style.display = 'inline-block';
        teamLabel.style.display = 'inline-block';
        oppSelect.style.display = 'none';
        oppLabel.style.display = 'none';
        if (type === 'for_team') teamLabel.innerText = "Select Team:";
        else teamLabel.innerText = "Select Opposition:";
    } else if (type === 'team_vs') {
        teamSelect.style.display = 'inline-block';
        teamLabel.style.display = 'inline-block';
        teamLabel.innerText = "Select Team:";
        oppSelect.style.display = 'inline-block';
        oppLabel.style.display = 'inline-block';
    } else {
        teamSelect.style.display = 'none';
        teamLabel.style.display = 'none';
        oppSelect.style.display = 'none';
        oppLabel.style.display = 'none';
    }

    // Dynamic Headers
    let teamHeader = "Team";
    if (type === 'for_team') teamHeader = "Team";
    if (type === 'vs_team') teamHeader = "Opposition";
    if (type === 'team_vs') teamHeader = "Opposition"; // In Team vs Opp, show Opp name? Or both? Lists are specific. Context is clear.

    thead.innerHTML = `
        <th>Rank</th>
        <th>Player</th>
        <th>${teamHeader}</th>
        <th>Innings</th>
        <th>Date</th>
    `;

    // Fetch Data
    let data = [];
    if (!statsData.fastest_wickets) {
        tbody.innerHTML = '<tr><td colspan="5">Data not loaded.</td></tr>';
        return;
    }

    if (type === 'overall') {
        data = statsData.fastest_wickets.overall[milestone] || [];
    } else if (type === 'for_team') {
        const team = teamSelect.value;
        if (team === 'All') {
            let all = [];
            Object.values(statsData.fastest_wickets.for_team).forEach(arr => {
                if (arr[milestone]) all = all.concat(arr[milestone]);
            });
            data = all;
        } else {
            data = statsData.fastest_wickets.for_team[team]?.[milestone] || [];
        }
    } else if (type === 'vs_team') {
        const team = teamSelect.value;
        if (team === 'All') {
            let all = [];
            Object.values(statsData.fastest_wickets.vs_team).forEach(arr => {
                if (arr[milestone]) all = all.concat(arr[milestone]);
            });
            data = all;
        } else {
            data = statsData.fastest_wickets.vs_team[team]?.[milestone] || [];
        }
    } else if (type === 'team_vs') {
        // Populate Team Dropdown if empty
        if (teamSelect.options.length <= 1) {
            const keys = Object.keys(statsData.fastest_wickets.team_vs || {}).sort();
            keys.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t;
                opt.innerText = t;
                teamSelect.appendChild(opt);
            });
            if (keys.length > 0) teamSelect.value = keys[0];
        }

        const team = teamSelect.value;
        // Populate Opp Dropdown based on Team
        if (team && team !== 'All') {
            const oppNodes = statsData.fastest_wickets.team_vs[team] || {};
            // Check if oppSelect needs update (simple check: if only 1 option or first option is not relevant)
            // Better: Clear and repopulate if team changed.
            // We need a way to detect if we should repopulate.
            // Let's doing it if oppSelect has only "All" or match current team?
            // Actually, we should trigger repopulate on change.
            // Here we assume if empty, populate.
            if (oppSelect.options.length <= 1 || oppSelect.getAttribute('data-team') !== team) {
                oppSelect.innerHTML = ''; // Remote 'All' since specific pair? Or keep? 'All' oppositions? 
                // If 'All' oppositions, that's just 'for_team' effectively.
                // So for 'team_vs', let's force selection or default to first.

                const oppKeys = Object.keys(oppNodes).sort();
                oppKeys.forEach(o => {
                    const opt = document.createElement('option');
                    opt.value = o;
                    opt.innerText = o;
                    oppSelect.appendChild(opt);
                });
                oppSelect.setAttribute('data-team', team);
                if (oppKeys.length > 0) oppSelect.value = oppKeys[0];
            }
        }

        const opp = oppSelect.value;
        if (team && opp && statsData.fastest_wickets.team_vs[team] && statsData.fastest_wickets.team_vs[team][opp]) {
            data = statsData.fastest_wickets.team_vs[team][opp][milestone] || [];
        }
    }

    // Filter Search
    if (searchQuery) {
        data = data.filter(p => p.name.toLowerCase().includes(searchQuery));
    }

    // Sort (Innings ASC, Date ASC)
    data.sort((a, b) => {
        if (a.innings !== b.innings) return a.innings - b.innings;
        return new Date(a.date) - new Date(b.date);
    });

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">No records found.</td></tr>';
        return;
    }

    data.slice(0, 50).forEach((player, index) => {
        const displayTeam = (type === 'vs_team' || type === 'team_vs') ? player.team : player.team;
        // Logic: 
        // Overall: Show Team
        // For Team: Show Team (Redundant but okay)
        // Vs Team: Show Team (The player's team)
        // Team Vs Opp: Show Team? Or Opp?
        // Header says "Opposition" for type vs_team.
        // If header is "Opposition", we should show 'opposition' data? 
        // But 'player' object might not have 'opposition' field in 'fastest_wickets' structure (check data).
        // Format: {name, innings, date, match_id, team}. It does NOT have opposition in the record usually.
        // For 'team_vs', we know the opposition is 'opp'. 

        let col3 = player.team;
        if (type === 'vs_team') col3 = player.team; // Show player's team
        if (type === 'team_vs') col3 = oppSelect.value; // Show Opposition? Header is Opposition.

        const row = `
            <tr>
                <td>${index + 1}</td>
                <td>${player.name}</td>
                <td>${col3}</td>
                <td>${player.innings}</td>
                <td>${player.date}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });

    // Check if dropdown needs populating (Legacy types)
    if (type !== 'overall' && type !== 'team_vs' && teamSelect.options.length <= 1) {
        let keys = [];
        if (type === 'for_team') keys = Object.keys(statsData.fastest_wickets.for_team).sort();
        else if (type === 'vs_team') keys = Object.keys(statsData.fastest_wickets.vs_team).sort();

        keys.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t;
            opt.innerText = t;
            teamSelect.appendChild(opt);
        });
    }
}

// Hook to repopulate dropdown on type change
document.getElementById('bowlingTypeSelect')?.addEventListener('change', function () {
    const type = this.value;
    const teamSelect = document.getElementById('bowlingTeamSelect');
    const oppSelect = document.getElementById('bowlingOppSelect');
    teamSelect.innerHTML = '<option value="All">All Teams</option>';
    oppSelect.innerHTML = '';
    updateBowlingMilestonesTable();
});

document.getElementById('bowlingTeamSelect')?.addEventListener('change', function () {
    const type = document.getElementById('bowlingTypeSelect').value;
    if (type === 'team_vs') {
        document.getElementById('bowlingOppSelect').innerHTML = '';
    }
    updateBowlingMilestonesTable();
});

document.getElementById('bowlingOppSelect')?.addEventListener('change', updateBowlingMilestonesTable);


function updateBestBowlingTable() {
    const type = document.getElementById('bestBowlingTypeSelect').value;
    const teamFilter = document.getElementById('bestBowlingTeamSelect').value;
    const searchInput = document.getElementById('bestBowlingSearch');
    const searchQuery = searchInput ? searchInput.value.toLowerCase() : '';
    const tbody = document.querySelector('#bestBowlingTable tbody');

    tbody.innerHTML = '';

    if (!statsData.best_figures) return;

    let data = statsData.best_figures[type] || [];

    if (teamFilter !== 'All') {
        data = data.filter(p => p.team === teamFilter);
    }

    if (searchQuery) {
        data = data.filter(p => p.name.toLowerCase().includes(searchQuery));
    }

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8">No records found.</td></tr>';
        return;
    }

    data.slice(0, 50).forEach((item, index) => {
        const row = `
            <tr>
                <td>${index + 1}</td>
                <td>${item.name}</td>
                <td>${item.wickets}/${item.runs}</td>
                <td>${item.balls}</td>
                <td>${item.team}</td>
                <td>${item.opposition}</td>
                <td>${item.venue}</td>
                <td>${item.date}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });

    // Lazy Populate Dropdown
    const sel = document.getElementById('bestBowlingTeamSelect');
    if (sel && sel.options.length <= 1) {
        const teams = new Set();
        ['4_wickets', '5_wickets'].forEach(key => {
            if (statsData.best_figures[key]) {
                statsData.best_figures[key].forEach(p => teams.add(p.team));
            }
        });
        [...teams].sort().forEach(t => {
            const opt = document.createElement('option');
            opt.value = t;
            opt.innerText = t;
            sel.appendChild(opt);

        });
    }
}

function updateMostWicketsTable() {
    const type = document.getElementById('mostWicketsTypeSelect').value;
    const teamSelect = document.getElementById('mostWicketsTeamSelect');
    const teamLabel = document.getElementById('mostWicketsTeamSelectLabel');
    const oppSelect = document.getElementById('mostWicketsOppSelect');
    const oppLabel = document.getElementById('mostWicketsOppSelectLabel');
    const searchInput = document.getElementById('mostWicketsSearch');
    const searchQuery = searchInput ? searchInput.value.toLowerCase() : '';
    const tbody = document.querySelector('#mostWicketsTable tbody');

    tbody.innerHTML = '';

    // Visibility
    if (type === 'for_team' || type === 'vs_team') {
        teamSelect.style.display = 'inline-block';
        teamLabel.style.display = 'inline-block';
        oppSelect.style.display = 'none';
        oppLabel.style.display = 'none';
        if (type === 'for_team') teamLabel.innerText = "Select Team:";
        else teamLabel.innerText = "Select Opposition:";
    } else if (type === 'team_vs') {
        teamSelect.style.display = 'inline-block';
        teamLabel.style.display = 'inline-block';
        teamLabel.innerText = "Select Team:";
        oppSelect.style.display = 'inline-block';
        oppLabel.style.display = 'inline-block';
    } else {
        teamSelect.style.display = 'none';
        teamLabel.style.display = 'none';
        oppSelect.style.display = 'none';
        oppLabel.style.display = 'none';
    }

    if (!statsData.most_wickets) return;

    let data = [];
    if (type === 'overall') {
        data = statsData.most_wickets.overall || [];
    } else if (type === 'for_team') {
        const team = teamSelect.value;
        if (team === 'All') {
            Object.values(statsData.most_wickets.for_team).forEach(arr => {
                data = data.concat(arr);
            });
        } else {
            data = statsData.most_wickets.for_team[team] || [];
        }
    } else if (type === 'vs_team') {
        const team = teamSelect.value;
        if (team === 'All') {
            Object.values(statsData.most_wickets.vs_team).forEach(arr => {
                data = data.concat(arr);
            });
        } else {
            data = statsData.most_wickets.vs_team[team] || [];
        }
    } else if (type === 'team_vs') {
        // Populate Team Dropdown
        if (teamSelect.options.length <= 1) {
            const keys = Object.keys(statsData.most_wickets.team_vs || {}).sort();
            keys.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t;
                opt.innerText = t;
                teamSelect.appendChild(opt);
            });
            if (keys.length > 0) teamSelect.value = keys[0];
        }

        const team = teamSelect.value;
        // Populate Opp Dropdown
        if (team && team !== 'All') {
            const oppNodes = statsData.most_wickets.team_vs[team] || {};
            if (oppSelect.options.length <= 1 || oppSelect.getAttribute('data-team') !== team) {
                oppSelect.innerHTML = '';
                const oppKeys = Object.keys(oppNodes).sort();
                oppKeys.forEach(o => {
                    const opt = document.createElement('option');
                    opt.value = o;
                    opt.innerText = o;
                    oppSelect.appendChild(opt);
                });
                oppSelect.setAttribute('data-team', team);
                if (oppKeys.length > 0) oppSelect.value = oppKeys[0];
            }
        }

        const opp = oppSelect.value;
        if (team && opp && statsData.most_wickets.team_vs[team] && statsData.most_wickets.team_vs[team][opp]) {
            data = statsData.most_wickets.team_vs[team][opp] || [];
        }
    }

    if (searchQuery) {
        data = data.filter(p => p.name.toLowerCase().includes(searchQuery));
    }

    // Sort by Wickets DESC
    data.sort((a, b) => b.wickets - a.wickets);

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7">No records found.</td></tr>';
        return;
    }

    data.slice(0, 50).forEach((item, index) => {
        const avg = item.wickets > 0 ? (item.runs / item.wickets).toFixed(2) : '-';
        const econ = item.balls > 0 ? (item.runs / (item.balls / 6)).toFixed(2) : '-';

        // Col3 Logic
        let col3 = item.team;
        if (type === 'vs_team') col3 = item.team; // Opp Name is context
        if (type === 'team_vs') col3 = oppSelect.value; // Opp Name

        const row = `
            <tr>
                <td>${index + 1}</td>
                <td>${item.name}</td>
                <td>${col3}</td>
                <td>${item.wickets}</td>
                <td>${item.innings}</td>
                <td>${avg}</td>
                <td>${econ}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });

    // Helper for dropdown population logic (Legacy)
    if (type !== 'overall' && type !== 'team_vs' && teamSelect.options.length <= 1) {
        let keys = [];
        if (type === 'for_team') keys = Object.keys(statsData.most_wickets.for_team).sort();
        else if (type === 'vs_team') keys = Object.keys(statsData.most_wickets.vs_team).sort();

        keys.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t;
            opt.innerText = t;
            teamSelect.appendChild(opt);
        });
    }
}

// Hook for Most Wickets Dropdown
document.getElementById('mostWicketsTypeSelect')?.addEventListener('change', function () {
    const type = this.value;
    const teamSelect = document.getElementById('mostWicketsTeamSelect');
    const oppSelect = document.getElementById('mostWicketsOppSelect');
    teamSelect.innerHTML = '<option value="All">All Teams</option>';
    oppSelect.innerHTML = '';
    updateMostWicketsTable();
});

document.getElementById('mostWicketsTeamSelect')?.addEventListener('change', function () {
    const type = document.getElementById('mostWicketsTypeSelect').value;
    if (type === 'team_vs') {
        document.getElementById('mostWicketsOppSelect').innerHTML = '';
    }
    updateMostWicketsTable();
});

document.getElementById('mostWicketsOppSelect')?.addEventListener('change', updateMostWicketsTable);


function updateMostHaulsTable() {
    const type = document.getElementById('mostHaulsTypeSelect').value;
    const searchInput = document.getElementById('mostHaulsSearch');
    const searchQuery = searchInput ? searchInput.value.toLowerCase() : '';
    const tbody = document.querySelector('#mostHaulsTable tbody');

    tbody.innerHTML = '';

    if (!statsData.most_hauls) return;

    let data = statsData.most_hauls[type] || [];

    if (searchQuery) {
        data = data.filter(p => p.name.toLowerCase().includes(searchQuery));
    }

    // Already sorted by count DESC

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">No records found.</td></tr>';
        return;
    }

    data.slice(0, 50).forEach((item, index) => {
        const count = type === '4w' ? item['4w'] : item['5w'];
        const row = `
            <tr>
                <td>${index + 1}</td>
                <td>${item.name}</td>
                <td>${item.team}</td>
                <td>${count}</td>
                <td>${item.innings}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

function updateInningsMilestonesTable() {
    const metric = document.getElementById('imMetricSelect').value;
    const milestone = document.getElementById('imMilestoneSelect').value;
    const group = document.getElementById('imGroupSelect').value;
    const teamSelect = document.getElementById('imTeamSelect');
    const teamLabel = document.getElementById('imTeamSelectLabel');
    const searchInput = document.getElementById('imSearch');
    const searchQuery = searchInput ? searchInput.value.toLowerCase() : '';
    const tbody = document.querySelector('#inningsMilestonesTable tbody');

    tbody.innerHTML = '';

    // Handle Team Dropdown Visibility
    if (group === 'team' || group === 'vs') {
        teamSelect.style.display = 'inline-block';
        teamLabel.style.display = 'inline-block';
        teamLabel.innerText = group === 'team' ? "Select Team:" : "Select Opposition:";
    } else {
        teamSelect.style.display = 'none';
        teamLabel.style.display = 'none';
    }

    if (!statsData.innings_milestones) return;

    let data = [];
    if (group === 'overall') {
        if (statsData.innings_milestones.overall[milestone])
            data = statsData.innings_milestones.overall[milestone][metric] || [];
    } else {
        const groupKey = group === 'team' ? 'team' : 'vs';
        const sourceData = statsData.innings_milestones[groupKey];

        if (sourceData) {
            // Populate if empty
            if (teamSelect.options.length === 0) {
                const keys = Object.keys(sourceData).sort();
                keys.forEach(k => {
                    const opt = document.createElement('option');
                    opt.value = k;
                    opt.innerText = k;
                    teamSelect.appendChild(opt);
                });
                if (keys.length > 0) teamSelect.value = keys[0];
            }

            const currentTeam = teamSelect.value;
            if (currentTeam && sourceData[currentTeam] && sourceData[currentTeam][milestone]) {
                data = sourceData[currentTeam][milestone][metric] || [];
            }
        }
    }

    if (searchQuery) {
        data = data.filter(p => p.name.toLowerCase().includes(searchQuery));
    }

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7">No records found.</td></tr>';
        return;
    }

    data.slice(0, 50).forEach((item, index) => {
        const row = `
            <tr>
                <td>${index + 1}</td>
                <td>${item.name}</td>
                <td>${item.team}</td>
                <td>${item.opposition}</td>
                <td>${item.balls}</td>
                <td>${item.runs}${item.is_out === false ? '*' : ''}</td>
                <td>${item.date}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

document.getElementById('imGroupSelect')?.addEventListener('change', function () {
    const teamSelect = document.getElementById('imTeamSelect');
    teamSelect.innerHTML = '';
    updateInningsMilestonesTable();
});
