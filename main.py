# main.py
import tkinter as tk
from gui import WumpusGameGUI_Auto

# Main entry point: create a Tkinter window and run the Wumpus World game.
if __name__ == '__main__':
    root = tk.Tk()
    root.state("zoomed")  # Launch the window in maximized state.
    app = WumpusGameGUI_Auto(root, size=20, pit_prob=0.2)
    root.mainloop()
