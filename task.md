- [ ] **Research & Planning**
    - [x] Check `_info.csv` for captaincy data (Not found) <!-- id: 1 -->
    - [x] Create detailed Implementation Plan <!-- id: 2 -->

- [ ] **Backend Implementation (`data_processor.py`)**
    - [x] Implement `BowlerCareer` tracking (Runs, Wickets, Innings) <!-- id: 3 -->
    - [x] Implement `FastestToWickets` logic (50, 100, 150, 200) <!-- id: 4 -->
        - [x] Overall <!-- id: 5 -->
        - [x] For Team <!-- id: 6 -->
        - [x] Vs Team <!-- id: 7 -->
    - [x] Implement `BestBowlingFigures` logic (4w, 5w) <!-- id: 8 -->
        - [x] Track by Wickets (DESC), Balls (ASC), Runs (ASC) <!-- id: 9 -->

- [ ] **Frontend Implementation (`index.html`, `app.js`)**
    - [x] Create "Bowling Milestones" Section/Tab <!-- id: 10 -->
    - [x] Create "Best Figures" Section/Tab <!-- id: 11 -->
    - [x] Update `app.js` to render new tables <!-- id: 12 -->

- [ ] **Research & Planning**
    - [x] Check `_info.csv` for captaincy data (Re-verify) <!-- id: 16 -->
    - [ ] Update Implementation Plan <!-- id: 17 -->

- [ ] **Backend Implementation (`data_processor.py`)**
    - [x] Export "Most Wickets" lists (Overall, For Team, Vs Team) <!-- id: 18 -->
    - [x] Implement "Most 4w/5w Hauls" (Count) <!-- id: 19 -->
    - [x] **Captaincy Check**: Double check pattern for captain info <!-- id: 20 -->
    - [x] **Innings Milestones (50, 100)**: <!-- id: 26 -->
        - [x] Extract Fastest/Slowest 50/100 from `innings_stats` <!-- id: 27 -->
        - [x] Group by Overall, Team, Vs Opposition <!-- id: 28 -->
        - [x] Sort Ascending (Fastest) and Descending (Slowest) <!-- id: 29 -->

- [ ] **Frontend Implementation (`index.html`, `app.js`)**
    - [x] Create "Most Wickets" Tab/Section <!-- id: 21 -->
    - [x] Add "Most 4w/5w Hauls" view <!-- id: 22 -->
    - [x] Update "Fastest 50s/100s" to handle Captaincy (Skipped - No Data) <!-- id: 23 -->
    - [x] Add "Innings Milestones" Section <!-- id: 30 -->
        - [x] Filters: Metric (Fastest/Slowest 50/100), Group (Overall, Team, Vs Opp) <!-- id: 31 -->

- [ ] **Verification**
    - [x] Verify new bowling stats <!-- id: 24 -->
    - [x] Verify UI filters <!-- id: 25 -->
    - [x] Verify Innings Milestones and Filters <!-- id: 32 -->

- [x] **Advanced Filtering (Team vs Opposition)** <!-- id: 33 -->
    - [x] **Backend (`data_processor.py`)** <!-- id: 34 -->
        - [x] Implement `bowler_team_vs_stats` for Fastest Wickets <!-- id: 35 -->
        - [x] Implement `most_wickets_team_vs` aggregation <!-- id: 36 -->
        - [x] Export new data structures to `data.js` <!-- id: 37 -->
    - [x] **Frontend (`index.html`, `app.js`)** <!-- id: 38 -->
        - [x] Update "Most Wickets" filters to include "Team vs Opposition" <!-- id: 39 -->
        - [x] Update "Fastest Wickets" filters to include "Team vs Opposition" <!-- id: 40 -->
        - [x] Implement logic to show/hide dual dropdowns <!-- id: 41 -->
        - [x] Verify data filtering and display <!-- id: 42 -->
