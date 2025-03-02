import pickle
import matplotlib.pyplot as plt

# Load the saved iteration results from the pickle file
with open("iteration_results.pkl", "rb") as f:
    results = pickle.load(f)

# ----- Bar Chart: Wins vs Losses -----
wins = sum(1 for outcome in results["outcomes"] if "win" in outcome.lower())
losses = results["iterations"] - wins

fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
bars = ax.bar(["Wins", "Losses"], [wins, losses], color=["green", "red"], edgecolor="black", width=0.5)

# Annotate bars with counts
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{int(height)}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom', fontsize=14)

ax.set_title(f"Win vs Loss Count over {results['iterations']} Iterations", fontsize=18)
ax.set_xlabel("Outcome", fontsize=16)
ax.set_ylabel("Count", fontsize=16)
ax.legend(bars, ["Wins", "Losses"], fontsize=14, loc="upper right")
plt.tight_layout()
plt.savefig("iteration_results_bar.png", dpi=300)
plt.show()

# ----- Scatter Plot: Iteration Times -----
if "iteration_times" in results:
    # Convert each iteration time from seconds to minutes
    iteration_times_minutes = [t / 60 for t in results["iteration_times"]]
    total_time_minutes = sum(results["iteration_times"]) / 60
    iterations = list(range(1, len(iteration_times_minutes) + 1))

    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    scatter = ax.scatter(iterations, iteration_times_minutes, color="blue", s=60, label="Iteration Time (min)")
    ax.plot(iterations, iteration_times_minutes, linestyle="--", color="blue", alpha=0.7)

    ax.set_title(f"Iteration Time per Iteration over {results['iterations']} Iterations\nTotal Time: {total_time_minutes:.2f} minutes", fontsize=18)
    ax.set_xlabel("Iteration Number", fontsize=16)
    ax.set_ylabel("Time (minutes)", fontsize=16)
    ax.legend(fontsize=14, loc="upper right")
    
    # Optionally, annotate the first and last point for clarity
    ax.annotate(f"{iteration_times_minutes[0]:.2f} min", xy=(iterations[0], iteration_times_minutes[0]),
                xytext=(5, 5), textcoords="offset points", fontsize=12)
    ax.annotate(f"{iteration_times_minutes[-1]:.2f} min", xy=(iterations[-1], iteration_times_minutes[-1]),
                xytext=(-40, 5), textcoords="offset points", fontsize=12)

    plt.tight_layout()
    plt.savefig("iteration_times_scatter.png", dpi=300)
    plt.show()
else:
    print("No iteration_times data found in the pickle file.")
