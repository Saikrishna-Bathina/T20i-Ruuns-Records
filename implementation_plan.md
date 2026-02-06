# Implementation Plan: Correct Phase Definitions

## Goal
Update the phase definitions for T20 stats to align with the standard 6-10-4 split:
-   **Powerplay**: Overs 0.1 - 6.0 (First 6 overs) -> Unchanged.
-   **Middle**: Overs 6.1 - 16.0 (Next 10 overs). Currently seems to be 6.1 - 15.0 (9 overs).
-   **Death**: Overs 16.1 - 20.0 (Last 4 overs). Currently seems to be 15.1 - 20.0 (5 overs).

## Proposed Changes

### Backend (`data_processor.py`)

#### [MODIFY] [data_processor.py](file:///c:/Users/Sai%20Krishna/OneDrive/Desktop/T20i%20Runs%20Stats/data_processor.py)
*   Update `get_phase(over)` function:
    *   `if over < 6: return "Powerplay"` (0 to 5.x) -> Correct.
    *   `elif over < 16: return "Middle"` (6.x to 15.x) -> **CHANGE to `over < 16`**.
        *   Currently it is likely `over < 15`.
    *   `else: return "Death"` (16.x to 19.x).

### Frontend (`index.html`)

#### [MODIFY] [index.html](file:///c:/Users/Sai%20Krishna/OneDrive/Desktop/T20i%20Runs%20Stats/index.html)
*   Update dropdown labels:
    *   "Middle Overs (7-15)" -> "Middle Overs (7-16)"
    *   "Death Overs (16-20)" -> "Death Overs (17-20)"

## Verification Plan
*   Run `data_processor.py`.
*   Verify `index.html` dropdowns.
*   Notify user.
