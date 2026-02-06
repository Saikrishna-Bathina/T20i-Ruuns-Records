# T20i Stats Dashboard - Project Walkthrough

This guide explains the entire T20i Runs Stats project from the root concepts to the final user interface. It is designed to help a new person understand how the system works "under the hood."

## 1. The Big Picture
**Goal**: Create a web dashboard to view T20 International cricket statistics (like Most Runs, Fastest Centuries, Phase Stats) without needing a complex backend server.

**How it works**:
1.  **Raw Data**: We get ball-by-ball cricket data from [Cricsheet](https://cricsheet.org/).
2.  **Processing**: A Python script (`data_processor.py`) reads this raw data, calculates all the statistics we need, and saves them into a single JavaScript file (`data.js`).
3.  **Display**: The website (`index.html`) loads this `data.js` file and uses a simple JavaScript program (`app.js`) to display the stats in tables and charts.

## 2. The Workflow (Root to End)

### Step 1: The Raw Data (Root)
The project starts with raw data.
*   **Source**: Cricsheet (specifically the "Men's T20 International" dataset).
*   **Format**: A ZIP file containing thousands of CSV files. Each CSV file represents one cricket match.
*   **Content**: Every single ball bowled in history, including who batted, who bowled, runs scored, and extras.

### Step 2: The Processing Engine (Python)
We use a Python script `data_processor.py` to make sense of this massive amount of data.
*   **Download**: It automatically downloads the latest zip file from Cricsheet.
*   **Extract**: It unzips the files into the `t20i_data/` folder.
*   **Analyze**: It loops through every CSV file (every match) and calculates:
    *   Total runs for every player.
    *   Balls faced.
    *   Fastest milestones (e.g., balls to reach 1000 runs).
    *   Phase stats (Powerplay vs Middle vs Death overs).
*   **Export**: Crucially, it saves these calculated stats into a file called `data.js`.
    *   *Why .js and not .json?* By saving it as `const t20Data = { ... }`, we can load it directly in the browser as a script, avoiding "CORS" errors that happen when trying to load JSON files directly from the hard drive.

### Step 3: The Frontend (User Interface)
The user interacts with the `index.html` file.
*   **Structure (`index.html`)**: Defines the layout—tabs for different stats, dropdowns for filters, and empty tables waiting for data.
*   **Styling (`style.css`)**: Makes it look good (colors, layout, responsiveness).
*   **Logic (`app.js`)**: This is the brain of the webpage.
    1.  It waits for the page to load.
    2.  It looks for the `t20Data` variable (loaded from `data.js`).
    3.  It takes that data and populates the HTML tables.
    4.  It handles user interactions like searching for a player, changing a country filter, or sorting columns.

## 3. Key Files Explained

| File | Type | Purpose |
| :--- | :--- | :--- |
| `data_processor.py` | Python Script | **The Worker**: Downloads raw data, calculates stats, and updates `data.js`. Run this to refresh data. |
| `data.js` | JavaScript Data | **The Bridge**: Holds all the processed statistics in a format the browser can understand. |
| `index.html` | HTML | **The Skeleton**: The main webpage structure. |
| `style.css` | CSS | **The Skin**: Stylizes the website. |
| `app.js` | JavaScript | **The Brain**: Runs in the browser, reads `data.js`, and updates the UI based on user actions. |

## 4. How to Explain "Running It"
To a new person, you can say:
1.  **"To see the dashboard, just double-click `index.html`."** It opens in the browser instantly because the data is already pre-packaged in `data.js`.
2.  **"To update the stats with yesterday's matches, run the Python script."** `python data_processor.py` will catch up on the latest games and update `data.js`.
