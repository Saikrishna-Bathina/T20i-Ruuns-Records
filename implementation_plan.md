# Implementation Plan - Fastest/Slowest Innings Milestones

## Goal Description
Implement "Fastest" and "Slowest" 50 and 100 run milestones for an innings.
Support filtering by **Team** and **Vs Team (Opposition)** as requested.
*Note: Captaincy filters cannot be implemented due to missing data in the source files.*

## User Review Required
> [!WARNING]
> Captaincy data is not available in the provided Cricsheet dataset. The "By Captain" filter will be omitted.

## Proposed Changes

### Backend - `data_processor.py`
#### [MODIFY] [data_processor.py](file:///c:/Users/Sai Krishna/OneDrive/Desktop/T20i Runs Stats/data_processor.py)
- **Logic**:
    - Iterate through `innings_stats` to extract batting milestones (50, 100).
    - Data Structure: `innings_stats` already contains `milestones` dict `{50: balls, 100: balls}`.
    - Create aggregation buckets:
        - `Overall`: List of all milestones.
        - `By Team`: Dict `{ "India": [ ... ], ... }`
        - `Vs Team`: Dict `{ "Australia": [ ... ], ... }`
    - For each bucket, create Sorted Lists:
        - `Fastest`: Sort by Balls ASC.
        - `Slowest`: Sort by Balls DESC.
    - Export new structure in `data.json`:
      ```json
      "innings_milestones": {
          "overall": { "fastest": {}, "slowest": {} },
          "team": { "fastest": {}, "slowest": {} },
          "vs": { "fastest": {}, "slowest": {} }
      }
      ```
      (Where inner dicts are keyed by milestone value "50", "100")

### Backend - `data_processor.py`
#### [MODIFY] [data_processor.py](file:///c:/Users/Sai Krishna/OneDrive/Desktop/T20i Runs Stats/data_processor.py)
- **Fastest Wickets**:
    - Add `bowler_team_vs_stats` dict to track career stats per (Team, Opposition) pair.
    - Update `update_bowler_career` to populate this new dict.
    - Export `fastest_wickets_team_vs` structure: `Team -> Opposition -> Milestone -> List`.
- **Most Wickets**:
    - Add `agg_team_vs` aggregation using key `(team, opposition, name)`.
    - Export `most_wickets_team_vs` structure: `Team -> Opposition -> List`.

### Frontend - `index.html` & `app.js`
#### [MODIFY] [index.html](file:///c:/Users/Sai Krishna/OneDrive/Desktop/T20i Runs Stats/index.html)
- Update "Most Wickets" and "Bowling Milestones" controls.
- Add "Team vs Opposition" option to Type select.
- Ensure both "Select Team" and "Select Opposition" dropdowns are available and toggleable.

#### [MODIFY] [app.js](file:///c:/Users/Sai Krishna/OneDrive/Desktop/T20i Runs Stats/app.js)
- Update `updateMostWicketsTable` and `updateBowlingMilestonesTable`.
- Handle `team_vs_team` filter mode:
    - Show both dropdowns.
    - Filter data using `statsData.most_wickets.team_vs[team][opp]` or similar.
    - populate dropdowns dynamically based on available keys.

## Verification Plan

### Automated Tests
- Run `data_processor.py` and inspect `data.json` output for `innings_milestones` keys.
- Check that lists are sorted correctly (Fastest: Low balls first; Slowest: High balls first).

### Manual Verification
- Open `index.html`.
- Navigate to "Innings Milestones".
- Check "Fastest 50 Overall" - Expect known records (e.g. Yuvraj Singh, Dipendra Singh Airee).
- Check "Slowest 50 Overall".
- Filter by Team "India" -> Fastest 50.
- Filter Vs Team "Australia" -> Fastest 50.
