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
- **Phase Logic**:
    - Update `get_phase` boundaries:
        - Powerplay: 0-5 (Overs 1-6)
        - Middle: 6-14 (Overs 7-15)
        - Death: 15-19 (Overs 16-20)
- **Multi-Context Aggregation (World Cups)**:
    - Identify WC matches via `event` field ("World T20", "T20 World Cup").
    - Logic to map Match -> List of Contexts (e.g., `['all', 'wc', 'wc_2024']`).
    - Refactor global stats variables (`batsman_career_stats`, `most_runs_list`, etc.) into a `StatsContainer` class or dictionary structure.
    - Update processing loop to `update(stats, context)` for every relevant context.
    - Export `statsData` with `tournaments` key containing sub-datasets.

### Frontend - `index.html` & `app.js`
#### [MODIFY] [index.html](file:///c:/Users/Sai Krishna/OneDrive/Desktop/T20i Runs Stats/index.html)
- Add Global Filter: "Select Tournament" (All, World Cup Overall, Specific Years).
- Update UI to reflect the active dataset.

#### [MODIFY] [app.js](file:///c:/Users/Sai Krishna/OneDrive/Desktop/T20i Runs Stats/app.js)
- Maintain `currentData` reference (defaulting to `statsData`).
- On Tournament Filter change:
    - Update `currentData` to point to `statsData.tournaments[key]` (or root for 'all').
    - Re-trigger all active table updates (`updateMostRuns`, etc.).
- Ensure all existing functions read from `currentData` instead of global `statsData`.

## Verification Plan
- **Phase Stats**: Check Phase stats table for known boundary cases (e.g. over 15 should be 'Death').
- **World Cup**:
    - Verify "Overall" stats match ESPN/Cricinfo for a known player (e.g. Kohli WC Runs).
    - Verify "2024 WC" stats match that specific tournament.
- **Performance**: Ensure 10-12x data duplication doesn't crash browser (check `data.js` size).

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
