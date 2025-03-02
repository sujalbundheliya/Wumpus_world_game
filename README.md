# Wumpus World Game with Enhanced Agent

This project is an implementation of the classic Wumpus World game, enhanced with an intelligent agent that uses knowledge representation and inference to navigate the grid world, avoid hazards, and retrieve the gold. The game supports both manual and autonomous modes and includes a graphical user interface (GUI) built with Tkinter.

## Features

- **Game Logic & Inference:**
  - Grid-based world with cells that may contain pits, wumpuses, or gold.
  - A guaranteed safe starting zone at (0, 0) and a mechanism to ensure a winnable board configuration.
  - A knowledge base representing hazard probabilities using inference rules based on percepts.
  - Automated path planning using breadth-first search (BFS) to find safe paths.

- **Graphical User Interface (GUI):**
  - A multi-panel Tkinter interface displaying game statistics, the grid world, and a log of visited cells.
  - Real-time status updates including score, position, orientation, arrow count, and hazard counts.
  - Keyboard controls for manual play (arrow keys for turning/moving, space to shoot, and Enter to grab).
  - Automated mode where the agent uses its inference mechanism to navigate the world.

- **Iteration & Performance Analysis:**
  - An iteration mode to run multiple game simulations.
  - Collection of performance data including win rate, average score, and survival rate.
  - Generation of charts (bar and scatter plots) to visualize iteration outcomes and execution times.

## File Structure

- **logic.py:**  
  Contains the core game logic including the `Cell`, `WumpusWorld`, `Agent`, and `WumpusGame` classes. This file manages the creation and verification of a winnable game board and defines the behavior of the agent within the world.

- **gui.py:**  
  Implements the graphical user interface using Tkinter. This file handles game rendering, user input (manual and automated), performance statistics, and iteration mode functionality.

- **main.py:**  
  The entry point of the application. It creates the Tkinter window and launches the Wumpus World game.

- **README.md:**  
  This file, which provides an overview of the project, installation instructions, usage guidelines, and a description of the main features.

- **requirements.txt:**  
  Lists external dependencies (currently, only `matplotlib` is required).

## Requirements

- **Python 3.x**  
- **Tkinter:** Typically included with Python installations.
- **Matplotlib:** For generating performance charts.

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd <repository-folder>

2. Set Up a Virtual Environment (Recommended):

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```


3. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt

## Running the Game
To launch the game, run the following command:

    python main.py

This will open the game window in maximized mode.

**Manual Mode Controls**

**Arrow Keys:**

- Press an arrow key once to turn the agent.
- Press the same arrow key again to move forward.

**Spacebar:**
- Shoot an arrow in the agent's current direction.

**Enter Key:**
- Grab the gold if it is present in the current cell.

**Autonomous Mode**

- Click the **Automate** button to enable autonomous play.
- The agent will automatically make decisions based on its knowledge base and inference mechanisms.

**Iteration Mode**

- Enter the desired number of iterations in the provided text box.
- Click **Run Iterations** to simulate multiple games.
- After the iterations are completed, performance charts will be generated and saved, and overall statistics will be displayed.

**Code Overview**

**Logic Implementation:**
- `logic.py` manages the creation of the grid, placement of hazards and gold, and provides the game rules including percept generation and action handling for the agent.

**GUI and Automation:**
- `gui.py` builds a multi-panel interface, renders the game state, binds keyboard events for manual control, and implements the automated decision-making logic for the agent.

**Main Entry Point:**
- `main.py` sets up the Tkinter window and starts the game by instantiating the GUI class.

## Results and Analysis

After running the game in iteration mode, performance data is automatically generated and stored as follows:

**Graphs:**  
Performance charts such as the iteration outcomes and iteration times are saved in the `Results/Graphs` folder (e.g., `iteration_result.png` for win/loss bar charts and `iteration_times.png` for timing scatter plots).

**Timing Data:**  
Detailed iteration timing information is available in the generated charts and can be reviewed from the `Results/Timings` folder.

**Iteration Results File:**  
A detailed summary of the simulation is saved in the `iteration_results.pkl` file. This file contains key metrics including:
- **iterations:** Total number of game iterations run.
- **win_rate:** The percentage of iterations won.
- **avg_score:** The average score across all iterations.
- **outcomes:** A list of outcomes (win or loss) for each iteration.
- **iteration_times:** The time taken for each iteration.

**Additional Notes**

- Make sure you have Python 3.x installed with Tkinter and Matplotlib.
- The game supports both manual and automated modes, so feel free to experiment with both to see how the agent navigates and makes decisions.
- Iteration mode is useful for performance analysis and can help in fine-tuning the agent's decision-making process.

