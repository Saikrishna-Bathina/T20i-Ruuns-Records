# Implementation Plan: Advanced Bowling Statistics

## Goal
Add detailed bowling statistics to the platform:
1.  **Fastest to Wicket Milestones (50, 100, 150, 200)**: Ranked by *innings played*.
    *   **Categories**: Overall, For Specific Team, Against Specific Team.
2.  **Best Bowling Figures (Speed)**: Fastest 4-Wicket and 5-Wicket hauls in an innings.
    *   **Ranking**: Fewest Balls -> Fewest Runs -> Date (Most Recent).

> [!NOTE]
> Captaincy data is unavailable in the source CSVs, so "Fastest milestones as Captain" cannot be implemented at this time.

## Proposed Changes

### Backend (`data_processor.py`)

#### [MODIFY] [data_processor.py](file:///c:/Users/Sai%20Krishna/OneDrive/Desktop/T20i%20Runs%20Stats/data_processor.py)

**1. Track Cumulative Wickets & Innings**
*   Create a new tracking structure `bowler_career_stats`:
    *   Key: `bowler_name`
    *   Value:
        *   `innings`: int (Count of innings bowled)
        *   `wickets`: int (Total wickets)
        *   `milestones_reached`: dict (Make sure we only record the FIRST time they cross 50, 100, etc.)
            *   Key: milestone (50, 100) -> Value: {innings: X, match_id: Y, date: Z}
*   **Team/Opposition Splits**:
    *   We also need to track `bowler_team_stats` (For Team) and `bowler_vs_stats` (Against Team) with similar structure to handle "Fastest 50 wickets for India" or "Fastest 50 wickets vs Australia".

**2. Track Fastest 4/5 Wicket Hauls**
*   In the existing `bowler_innings_stats` (or a sidebar calculation during the main loop), check:
    *   If `wickets >= 4`:
        *   Store entry: `{name, team, opposition, venue, date, wickets, runs_conceded, balls_bowled}`.
*   After processing all data, verify sorting:
    *   Sort by: `wickets` (DESC) [implicit for 5 vs 4 lists], `balls` (ASC), `runs` (ASC).

**3. Output Data Structure (`data.js`)**
Add new keys to the exported JSON:
*   `fastest_wickets`:
    *   `overall`: {50: [...], 100: [...], ...} (List sorted by innings)
    *   `for_team`: Dictionary `{TeamName: [ {name, innings, ...} ]}`.
    *   `vs_team`: Dictionary `{OppositionName: [ {name, innings, ...} ]}`.
*   `best_figures_innings`:
    *   `5_fer`: List of `{name, team, opposition, runs, balls, wickets, date}`.
    *   `4_fer`: List ...

### Frontend (`index.html` & `app.js`)

#### [MODIFY] [index.html](file:///c:/Users/Sai%20Krishna/OneDrive/Desktop/T20i%20Runs%20Stats/index.html)
*   Add new Section/Tabs for "Bowling Milestones" and "Best Figures".
*   "Bowling Milestones":
    *   Dropdown: Milestone (50, 100, 150, 200).
    *   Dropdown: Type (Overall, For Team, Vs Team).
    *   Dropdown: Team Filter (Dynamic based on Type).
*   "Best Figures (Speed)":
    *   Dropdown: Type (5 Wickets, 4 Wickets).
    *   Dropdown: Filter Team/Opposition.

#### [MODIFY] [app.js](file:///c:/Users/Sai%20Krishna/OneDrive/Desktop/T20i%20Runs%20Stats/app.js)
*   Render functions for the new tables:
    *   `renderMilestoneTable(data)`
    *   `renderBestFiguresTable(data)`

## Verification Plan
1.  Run `data_processor.py`.
2.  Check `data.js` output.
3.  Open `index.html` and verify tables and filters.
4.  Notify user.
