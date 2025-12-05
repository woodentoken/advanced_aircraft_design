import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# Change these paths to wherever your files are on Windows
# Example: r"C:\Users\YourName\airfoils\g181-e39_55pts.dat"
# ---------------------------------------------------------
file1 = r"C:\\Users\\tadco\\Desktop\\OptVL Test\\gen_pop\\g181-e39_55pts.dat"
file2 = r"C:\\Users\\tadco\\Desktop\\OptVL Test\\gen_pop\\naca65210.dat"

# ---------------------------------------------------------
# Load files (auto-detect whitespace formatting)
# ---------------------------------------------------------
df1 = pd.read_csv(file1, sep=r" ", header=None, engine="python")
df2 = pd.read_csv(file2, sep=r" ", header=None, engine="python")

# ---------------------------------------------------------
# Plot overlay
# ---------------------------------------------------------
plt.figure(figsize=(10, 5))
plt.plot(df1[0], df1[1], label="g181-e39 (55 pts)")
plt.plot(df2[0], df2[1], label="NACA 65210")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Overlay of Airfoil Shapes")
plt.grid(True)
plt.legend()
plt.axis("equal")  # keeps scaling correct for airfoil shape
plt.tight_layout()
plt.show()
