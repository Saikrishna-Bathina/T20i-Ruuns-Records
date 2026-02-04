# T20i Stats Dashboard

A comprehensive dashboard for visualizing Men's T20 International cricket statistics, powered by Cricsheet data.

## Features
- **Most Runs**: Top 50 run-scorers in T20i history.
- **Highest Scores**: Top 10 individual scores in an innings (with Not Out indicators).
- **Fastest to Milestones**:
    - Fastest to 1000, 2000, 3000, 4000, and 5000 runs.
    - toggle between **Balls Faced** and **Innings Played**.
- **Country Filter**: Filter milestone records by team.

## How it Works
1.  **Data Source**: The project downloads raw ball-by-ball data from [Cricsheet](https://cricsheet.org/).
2.  **Processing**: A Python script (`data_processor.py`) processes the CSV files and generates a `data.js` file containing the calculated statistics.
3.  **Frontend**: A vanilla HTML/CSS/JS frontend loads `data.js` and displays the interactive dashboard. No backend server is required!

## Setup & Running Locally

### Prerequisites
- Python 3.x (for updating data)

### Steps
1.  **Run the Dashboard**:
    - Simply open `index.html` in your web browser.
    - Since it uses `data.js`, it works directly from the file system.

2.  **Update Data**:
    To fetch the latest match data and update the stats:
    ```bash
    python data_processor.py
    ```
    This script will:
    - Download the latest zip from Cricsheet.
    - Extract and process the CSVs.
    - Regenerate `data.js`.
    - Refresh `index.html` to see the changes.

## Deployment
This project is static and ready for deployment on GitHub Pages or Netlify.
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## Technologies
- **Python**: Data processing and statistical analysis.
- **HTML/CSS**: Responsive UI design.
- **JavaScript**: Dashboard logic and interactivity.
