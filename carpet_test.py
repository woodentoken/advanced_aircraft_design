# import plotly.graph_objects as go

# # Original values
# a = np.array([0.444, 0.468, 0.482, 0.486, 0.491])
# b = np.array([8, 10, 12, 14, 16])
# y = np.array([24552, 200407, 17852.4, 17162.3, 16618])
# x = np.array([100.11, 94.91, 92.3, 91.43, 90.6])

# # Min-max normalization function
# def normalize(arr):
#     return (arr - np.min(arr)) / (np.max(arr) - np.min(arr))

# # Normalize all arrays
# a_norm = normalize(a)
# b_norm = normalize(b)
# y_norm = normalize(y)
# x_norm = normalize(x)

# # Print normalized arrays
# print("a_norm:", a_norm)
# print("b_norm:", b_norm)
# print("y_norm:", y_norm)
# print("x_norm:", x_norm)

# fig = go.Figure(go.Contour(
#     a = [0.444, 0.468, 0.482, 0.486, 0.491],
#     b = [8, 10, 12, 14, 16],
#     y = [24552, 200407, 17852.4, 17162.3, 16618],
#     x = [100.11, 94.91, 92.3, 91.43, 90.6],

# ))

# fig.show()










import numpy as np
import matplotlib.pyplot as plt

# Provided data
AR = np.array([ 8, 10, 12, 14, 16])
WS = np.array([ 100.11, 94.91, 92.3, 91.43, 90.6])
TW = np.array([ 0.444, 0.468, 0.482, 0.486, 0.491])

plt.figure(figsize=(10,6))

# Plot data as a carpet: each AR gets a point, but connect W/S ↔ T/W
plt.plot(WS, TW, marker='o', linestyle='-', color='black', label="Carpet Line")

# Annotate each point with AR value
for i in range(len(AR)):
    plt.text(WS[i] + 0.5, TW[i] + 0.002, f"AR={AR[i]}", fontsize=10)

plt.grid(True, alpha=0.3)
plt.xlabel("Wing Loading (W/S)")
plt.ylabel("Thrust-to-Weight (T/W)")
plt.title("Carpet Plot: T/W vs W/S for Given Aspect Ratios")
plt.legend()
plt.tight_layout()
plt.show()

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d, griddata

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# -----------------------------------------------------------
# Original Data
# -----------------------------------------------------------
AR = np.array([ 8, 10, 12, 14, 16])
WS = np.array([ 100.11, 94.91, 92.3, 91.43, 90.6])
TW = np.array([ 0.444, 0.468, 0.482, 0.486, 0.491])

# -----------------------------------------------------------
# Interpolation for smooth curve
# -----------------------------------------------------------
AR_fine = np.linspace(min(AR), max(AR), 300)
WS_interp = interp1d(AR, WS, kind='cubic')
TW_interp = interp1d(AR, TW, kind='cubic')

WS_smooth = WS_interp(AR_fine)
TW_smooth = TW_interp(AR_fine)

# -----------------------------------------------------------
# Plot
# -----------------------------------------------------------
plt.figure(figsize=(10,7))

# Plot the smooth interpolated T/W vs W/S curve
plt.plot(WS_smooth, TW_smooth, linewidth=2, color='black', label="Interpolated AR curve")

# Plot original points
plt.scatter(WS, TW, c='red', s=60, zorder=3)
for i in range(len(AR)):
    plt.text(WS[i] + 0.6, TW[i], f"AR={AR[i]}", fontsize=9, va='center')

# -----------------------------------------------------------
# ISO–T/W HORIZONTAL LINES (correct behavior)
# -----------------------------------------------------------
y_min = min(TW) - 0.02
y_max = max(TW) + 0.02
WS_min = min(WS) - 5
WS_max = max(WS) + 5

iso_levels = np.linspace(min(TW), max(TW), 6)

for tw_level in iso_levels:
    plt.hlines(tw_level, WS_min, WS_max, colors='gray', linestyles='--', linewidth=1)
    plt.text(WS_max + 1, tw_level, f"T/W={tw_level:.3f}",
             fontsize=8, va='center', color='gray')

# -----------------------------------------------------------
# ISO–AR Carpet Lines (vertical-ish)
# -----------------------------------------------------------
for a in AR:
    ws_a = WS_interp(a)
    plt.vlines(ws_a, y_min, y_max, colors='black', linewidth=1)
    # Label the AR line at the top
    plt.text(ws_a, y_max + 0.005, f"AR={a}", fontsize=9, ha='center')

# -----------------------------------------------------------
# Formatting
# -----------------------------------------------------------
plt.xlim(WS_min, WS_max)
plt.ylim(y_min, y_max)

plt.xlabel("Wing Loading W/S")
plt.ylabel("Thrust-to-Weight Ratio (T/W)")
plt.title("Corrected Carpet Plot: T/W vs W/S with Iso-T/W (Horizontal) and Iso-AR Lines")
plt.grid(alpha=0.25)
plt.legend()
plt.tight_layout()
plt.show()

# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.interpolate import interp1d

# # -----------------------------
# # Input Data
# # -----------------------------
# AR = np.array([ 8, 10, 12, 14, 16])
# WS = np.array([ 100.11, 94.91, 92.3, 91.43, 90.6])   # Wing loading
# TW = np.array([ 0.444, 0.468, 0.482, 0.486, 0.491])  # Thrust-to-weight

# # Sort the data by W/S so interpolation works cleanly
# sort_idx = np.argsort(WS)
# WS_sorted = WS[sort_idx]
# TW_sorted = TW[sort_idx]
# AR_sorted = AR[sort_idx]

# # -----------------------------
# # Interpolation Setup
# # -----------------------------
# # Range for smooth curves
# WS_grid = np.linspace(min(WS)-5, max(WS)+5, 200)

# # Interpolate AR → T/W relationship
# TW_interp = interp1d(WS_sorted, TW_sorted, kind='cubic', fill_value="extrapolate")
# TW_grid = TW_interp(WS_grid)


# # -----------------------------
# # Create Carpet Lines (iso-AR)
# # -----------------------------
# plt.figure(figsize=(10, 7))

# # Plot main T/W vs W/S curve
# plt.plot(WS_sorted, TW_sorted, 'ko', label="Data Points")
# plt.plot(WS_grid, TW_grid, 'k--', linewidth=1.5, label="Interpolated Trend")

# # Generate diagonal iso-AR curves by shifting T/W
# # Each AR line is offset so they visually spread like a carpet
# offset_scale = 0.006  # Controls diagonal spacing

# for i, ar in enumerate(AR_sorted):
#     TW_line = TW_grid + (i - len(AR_sorted)/2) * offset_scale
#     plt.plot(WS_grid, TW_line, label=f"AR = {ar}")

#     # Label each line near right side
#     label_x = WS_grid[-1]
#     label_y = TW_line[-1]
#     plt.text(label_x + 0.5, label_y, f"AR={ar}", fontsize=10, va="center")

# # -----------------------------
# # Plot Formatting
# # -----------------------------
# plt.xlabel("Wing Loading W/S (lb/ft²)")
# plt.ylabel("Thrust-to-Weight T/W")
# plt.title("Carpet Plot: T/W vs W/S with Diagonal Iso-AR Lines")
# plt.grid(True, which='both', linestyle='--', alpha=0.5)
# plt.xlim(min(WS)-5, max(WS)+10)

# plt.show()

# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.interpolate import interp1d

# # -----------------------------
# # Input Data
# # -----------------------------
# AR = np.array([ 8, 10, 12, 14, 16])
# WS = np.array([ 100.11, 94.91, 92.3, 91.43, 90.6])
# TW = np.array([ 0.444, 0.468, 0.482, 0.486, 0.491])

# # Sort data by AR for smooth interpolation
# sort_idx = np.argsort(AR)
# AR_sorted = AR[sort_idx]
# WS_sorted = WS[sort_idx]
# TW_sorted = TW[sort_idx]

# # -----------------------------
# # Interpolation for diagonal iso-AR curves
# # -----------------------------
# # Define a fine parameter along the AR axis
# AR_fine = np.linspace(min(AR_sorted), max(AR_sorted), 200)

# # Interpolate W/S and T/W as functions of AR
# WS_interp = interp1d(AR_sorted, WS_sorted, kind='cubic', fill_value="extrapolate")
# TW_interp = interp1d(AR_sorted, TW_sorted, kind='cubic', fill_value="extrapolate")

# WS_fine = WS_interp(AR_fine)
# TW_fine = TW_interp(AR_fine)

# # For the carpet: generate several diagonal lines
# num_diagonals = len(AR_sorted)
# offset_scale = 0.006  # Controls spacing between diagonal lines

# # -----------------------------
# # Plotting
# # -----------------------------
# plt.figure(figsize=(10, 7))

# # Optional: create a heatmap of AR across the WS/TW plane
# WS_grid = np.linspace(min(WS_sorted)-5, max(WS_sorted)+5, 200)
# TW_grid_vals = np.linspace(min(TW_sorted)-0.02, max(TW_sorted)+0.02, 200)
# WS_2D, TW_2D = np.meshgrid(WS_grid, TW_grid_vals)

# # Simple heatmap: interpolate AR values
# from scipy.interpolate import griddata
# AR_grid = griddata(
#     (WS_sorted, TW_sorted),
#     AR_sorted,
#     (WS_2D, TW_2D),
#     method='cubic'
# )

# plt.contourf(WS_2D, TW_2D, AR_grid, levels=40, cmap='viridis', alpha=0.6)
# plt.colorbar(label="Aspect Ratio (AR)")

# # -----------------------------
# # Diagonal Iso-AR Carpet Lines
# # -----------------------------
# for i, ar in enumerate(AR_sorted):
#     # Offset each diagonal line slightly to create the carpet effect
#     TW_line = TW_fine + (i - len(AR_sorted)/2) * offset_scale
#     plt.plot(WS_fine, TW_line, linewidth=1.5, label=f"AR={ar}")
#     plt.scatter(WS_sorted[i], TW_sorted[i], c='red', s=50)
#     plt.text(WS_fine[-1]+0.5, TW_line[-1], f"{ar}", fontsize=9, va='center')

# # -----------------------------
# # Formatting
# # -----------------------------
# plt.xlabel("Wing Loading W/S")
# plt.ylabel("Thrust-to-Weight T/W")
# plt.title("Carpet Plot: Diagonal Iso-AR Lines")
# plt.grid(True, alpha=0.3)
# plt.legend(loc='upper right')
# plt.tight_layout()
# plt.show()


# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.interpolate import interp1d

# # -----------------------------
# # Input Data
# # -----------------------------
# AR = np.array([ 8, 10, 12, 14, 16])
# WS = np.array([ 100.11, 94.91, 92.3, 91.43, 90.6])
# TW = np.array([ 0.444, 0.468, 0.482, 0.486, 0.491])

# # Sort data by AR for interpolation
# sort_idx = np.argsort(AR)
# AR_sorted = AR[sort_idx]
# WS_sorted = WS[sort_idx]
# TW_sorted = TW[sort_idx]

# # -----------------------------
# # Interpolation for diagonal iso-AR lines
# # -----------------------------
# AR_fine = np.linspace(min(AR_sorted), max(AR_sorted), 200)
# WS_interp = interp1d(AR_sorted, WS_sorted, kind='cubic', fill_value="extrapolate")
# TW_interp = interp1d(AR_sorted, TW_sorted, kind='cubic', fill_value="extrapolate")

# WS_fine = WS_interp(AR_fine)
# TW_fine = TW_interp(AR_fine)

# # -----------------------------
# # Plotting
# # -----------------------------
# plt.figure(figsize=(11, 8))

# # --- Diagonal Iso-AR Carpet Lines ---
# offset_scale = 0.006
# for i, ar in enumerate(AR_sorted):
#     TW_line = TW_fine + (i - len(AR_sorted)/2) * offset_scale
#     plt.plot(WS_fine, TW_line, linewidth=1.5, color='blue')
#     plt.scatter(WS_sorted[i], TW_sorted[i], c='red', s=50, zorder=5)
#     plt.text(WS_fine[-1]+0.5, TW_line[-1], f"{ar}", fontsize=10, va='center', color='blue')

# # --- Horizontal Iso-T/W Lines ---
# num_tw_lines = 6
# TW_min, TW_max = min(TW_sorted)-0.02, max(TW_sorted)+0.02
# WS_min, WS_max = min(WS_sorted)-5, max(WS_sorted)+5
# TW_levels = np.linspace(TW_min, TW_max, num_tw_lines)

# for tw in TW_levels:
#     plt.hlines(tw, WS_min, WS_max, colors='gray', linestyles='--', linewidth=1)
#     plt.text(WS_max + 0.5, tw, f"{tw:.3f}", color='gray', fontsize=8, va='center')

# # --- Gridlines ---
# plt.grid(True, linestyle='--', alpha=0.3)

# # --- Labels and Title ---
# plt.xlabel("Wing Loading W/S")
# plt.ylabel("Thrust-to-Weight T/W")
# plt.title("Carpet Plot: Diagonal Iso-AR Lines + Horizontal Iso-T/W Lines")
# plt.xlim(WS_min, WS_max)
# plt.ylim(TW_min, TW_max)

# plt.tight_layout()
# plt.show()

# # import plotly.graph_objects as go

# # fig = go.Figure(go.Carpet(
# #     a = [8, 10, 12, 14, 16],
# #     b = [100.11, 94.91, 92.3, 91.43, 90.6],
# #     y = [0.444, 0.468, 0.482, 0.486, 0.491],

# # ))

# # fig.show()

# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.interpolate import interp1d

# # -----------------------------
# # Input Data
# # -----------------------------
# AR = np.array([ 8, 10, 12, 14, 16])
# WS = np.array([ 100.11, 94.91, 92.3, 91.43, 90.6])
# TW = np.array([ 0.444, 0.468, 0.482, 0.486, 0.491])

# # Sort data by AR for interpolation
# sort_idx = np.argsort(AR)
# AR_sorted = AR[sort_idx]
# WS_sorted = WS[sort_idx]
# TW_sorted = TW[sort_idx]

# # -----------------------------
# # Interpolation for diagonal iso-AR lines
# # -----------------------------
# # Each AR line passes through its original point and extends diagonally
# # Use linear interpolation between the original points for simplicity
# # This gives true carpet-style diagonals

# num_points = 200
# WS_grid = np.linspace(min(WS_sorted)-5, max(WS_sorted)+5, num_points)

# # Create a function to interpolate T/W as a function of W/S using the points
# TW_interp = interp1d(WS_sorted, TW_sorted, kind='linear', fill_value='extrapolate')
# TW_grid = TW_interp(WS_grid)

# # -----------------------------
# # Plotting
# # -----------------------------
# plt.figure(figsize=(11, 8))

# # Plot original points
# plt.scatter(WS_sorted, TW_sorted, c='red', s=50, zorder=5)
# for i in range(len(AR_sorted)):
#     plt.text(WS_sorted[i]+0.5, TW_sorted[i], f"AR={AR_sorted[i]}", color='blue', fontsize=10, va='center')

# # Plot diagonal iso-AR lines
# for i, ar in enumerate(AR_sorted):
#     # Each line is linear between min and max W/S
#     # Passes through the original point
#     slope = 0.0  # For perfect linear, adjust if you want more tilt
#     intercept = TW_sorted[i] - slope*WS_sorted[i]
#     TW_line = slope*WS_grid + intercept
#     plt.plot(WS_grid, TW_line, color='blue', linewidth=1.5)

# # Plot horizontal iso-T/W lines
# TW_min, TW_max = min(TW_sorted)-0.02, max(TW_sorted)+0.02
# num_tw_lines = 6
# TW_levels = np.linspace(TW_min, TW_max, num_tw_lines)
# for tw in TW_levels:
#     plt.hlines(tw, WS_grid[0], WS_grid[-1], colors='gray', linestyles='--', linewidth=1)
#     plt.text(WS_grid[-1]+0.5, tw, f"{tw:.3f}", color='gray', fontsize=8, va='center')

# # Grid
# plt.grid(True, linestyle='--', alpha=0.3)

# # Labels
# plt.xlabel("Wing Loading W/S")
# plt.ylabel("Thrust-to-Weight T/W")
# plt.title("Carpet Plot: Diagonal Iso-AR Lines Passing Through Points")

# plt.xlim(min(WS_grid)-0.5, max(WS_grid)+5)
# plt.ylim(TW_min, TW_max)

# plt.tight_layout()
# plt.show()

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# -----------------------------
# Input Data
# -----------------------------
AR = np.array([ 8, 10, 12, 14, 16])
WS = np.array([ 100.11, 94.91, 92.3, 91.43, 90.6])
TW = np.array([ 0.444, 0.468, 0.482, 0.486, 0.491])


# Sort by W/S for CubicSpline
sort_idx = np.argsort(WS)
WS_sorted = WS[sort_idx]
TW_sorted = TW[sort_idx]
AR_sorted = AR[sort_idx]

# Interpolation
WS_fine = np.linspace(min(WS_sorted)-5, max(WS_sorted)+5, 300)
cs = CubicSpline(WS_sorted, TW_sorted, extrapolate=True)
TW_fine = cs(WS_fine)

# Plot
plt.figure(figsize=(11,8))

# Original points
plt.scatter(WS_sorted, TW_sorted, c='red', s=50, zorder=5)
for i in range(len(AR_sorted)):
    plt.text(WS_sorted[i]+0.5, TW_sorted[i], f"AR={AR_sorted[i]}", color='blue', fontsize=10, va='center')

# Smooth diagonal iso-AR lines
offset_scale = 0.006
for i, ar in enumerate(AR_sorted):
    TW_line = TW_fine + (i - len(AR_sorted)/2) * offset_scale
    plt.plot(WS_fine, TW_line, color='blue', linewidth=1.5)

# Horizontal iso-T/W lines
TW_min, TW_max = min(TW_sorted)-0.02, max(TW_sorted)+0.02
num_tw_lines = 6
TW_levels = np.linspace(TW_min, TW_max, num_tw_lines)
for tw in TW_levels:
    plt.hlines(tw, WS_fine[0], WS_fine[-1], colors='gray', linestyles='--', linewidth=1)
    plt.text(WS_fine[-1]+0.5, tw, f"{tw:.3f}", color='gray', fontsize=8, va='center')

# Gridlines
plt.grid(True, linestyle='--', alpha=0.3)

# Labels
plt.xlabel("Wing Loading W/S")
plt.ylabel("Thrust-to-Weight T/W")
plt.title("Carpet Plot: Smooth Curved Diagonal Iso-AR Lines + Horizontal Iso-T/W Lines")

plt.xlim(min(WS_fine)-0.5, max(WS_fine)+5)
plt.ylim(TW_min, TW_max)

plt.tight_layout()
plt.show()

import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Input Data
# -----------------------------
AR = np.array([ 8, 10, 12, 14, 16])
WS = np.array([ 100.11, 94.91, 92.3, 91.43, 90.6])
TW = np.array([ 0.444, 0.468, 0.482, 0.486, 0.491])
# Plotting grid
WS_min, WS_max = min(WS)-5, max(WS)+5
TW_min, TW_max = min(TW)-0.02, max(TW)+0.02
WS_grid = np.linspace(WS_min, WS_max, 300)

plt.figure(figsize=(11,8))

# -----------------------------
# Plot original red points
# -----------------------------
plt.scatter(WS, TW, c='red', s=50, zorder=5)
for i in range(len(AR)):
    plt.text(WS[i]+0.5, TW[i], f"AR={AR[i]}", color='blue', fontsize=10, va='center')

# -----------------------------
# Diagonal iso-AR lines through each point
# -----------------------------
# We'll use a small slope (or cubic curve) extending across the plot
for i in range(len(AR)):
    # Slope of the line (can adjust for slight curvature)
    slope = 0.002  # small positive slope for diagonal appearance
    TW_line = slope*(WS_grid - WS[i]) + TW[i]  # line passes through red point
    plt.plot(WS_grid, TW_line, color='blue', linewidth=1.5)


for i in range(len(AR)):
    # Slope of the line (can adjust for slight curvature)
    slope = -0.002  # small positive slope for diagonal appearance
    TW_line = slope*(WS_grid - WS[i]) + TW[i]  # line passes through red point
    plt.plot(WS_grid, TW_line, color='blue', linewidth=1.5)
# -----------------------------
# Horizontal iso-T/W lines
# -----------------------------
num_tw_lines = 6
TW_levels = np.linspace(TW_min, TW_max, num_tw_lines)
for tw in TW_levels:
    plt.hlines(tw, WS_min, WS_max, colors='gray', linestyles='--', linewidth=1)
    plt.text(WS_max+0.5, tw, f"{tw:.3f}", color='gray', fontsize=8, va='center')

# -----------------------------
# Gridlines and labels
# -----------------------------
plt.grid(True, linestyle='--', alpha=0.3)
plt.plot(90, 0.48, marker='*', color='red', markersize=15)
plt.xlabel("Wing Loading W/S")
plt.ylabel("Thrust-to-Weight T/W")
plt.title("T/W vs W/S with Aspect Ratio")
plt.xlim(WS_min, WS_max)
plt.ylim(TW_min, TW_max)
plt.tight_layout()
plt.show()

import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Input Data
# -----------------------------
AR = np.array([8, 10, 12, 14, 16])
WS = np.array([100.11, 94.91, 92.3, 91.43, 90.6])
TW = np.array([0.444, 0.468, 0.482, 0.486, 0.491])
FuelBurn = np.array([24500, 20400, 17800, 17000, 16600])

# Plotting grid
WS_min, WS_max = min(WS)-5, max(WS)+5
TW_min, TW_max = min(TW)-0.02, max(TW)+0.02
WS_grid = np.linspace(WS_min, WS_max, 300)

plt.figure(figsize=(11,8))

# -----------------------------
# Plot original red points
# -----------------------------
plt.scatter(WS, TW, c='red', s=50, zorder=5)
for i in range(len(AR)):
    plt.text(WS[i]-0.5, TW[i]+0.002, f"AR={AR[i]}", color='xkcd:dull blue', fontsize=12, va='center')

# -----------------------------
# Diagonal iso-AR lines through each point
# -----------------------------
for i in range(len(AR)):
    slope = 0.0015  # small positive slope for diagonal appearance
    TW_line = slope*(WS_grid - WS[i]) + TW[i]
    plt.plot(WS_grid, TW_line, color='xkcd:dull blue', linewidth=2)

# -----------------------------
# Diagonal iso-FuelBurn lines through each point
# -----------------------------
for i in range(len(FuelBurn)):
    slope = -0.002  # negative slope for fuel burn lines (adjust as needed)
    TW_line = slope*(WS_grid - WS[i]) + TW[i]
    plt.plot(WS_grid, TW_line, color='xkcd:carolina blue', linewidth=2)
    plt.text(WS[i]+3, TW[i]-0.005, f"FB={int(FuelBurn[i])}lbs", color='xkcd:carolina blue', fontsize=12, va='center')

# -----------------------------
# Horizontal iso-T/W lines
# # -----------------------------
# num_tw_lines = 6
# TW_levels = np.linspace(TW_min, TW_max, num_tw_lines)
# for tw in TW_levels:
#     plt.hlines(tw, WS_min, WS_max, colors='gray', linestyles='--', linewidth=1)
#     plt.text(WS_max+0.5, tw, f"{tw:.3f}", color='gray', fontsize=8, va='center')

# -----------------------------
# Gridlines and labels
# -----------------------------
plt.grid(True, linestyle='-', alpha=1)
plt.plot(91.5, 0.485, marker='*', color='xkcd:bright blue', markersize=20)
plt.xlabel("Wing Loading W/S (lb/ft^2)")
plt.ylabel("Thrust-to-Weight T/W")
plt.title("T/W vs W/S with Aspect Ratio and Fuel Burn")
plt.xlim(WS_min-1, WS_max+1)
plt.ylim(TW_min-0.005, TW_max+.005)
plt.tight_layout()
plt.show()

import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Input Data
# -----------------------------
AR = np.array([8, 10, 12, 14, 16])
WS = np.array([100.11, 94.91, 92.3, 91.43, 90.6])
TW = np.array([0.444, 0.468, 0.482, 0.486, 0.491])
FuelBurn = np.array([24552, 200407, 17852.4, 17162.3, 16618])

# Plotting grid
WS_min, WS_max = min(WS)-5, max(WS)+5
TW_min, TW_max = min(TW)-0.02, max(TW)+0.02
WS_grid = np.linspace(WS_min, WS_max, 300)

plt.figure(figsize=(12,8))

# -----------------------------
# Plot original red points
# -----------------------------
plt.scatter(WS, TW, c='red', s=50, zorder=5)
for i in range(len(AR)):
    plt.text(WS[i]+0.5, TW[i], f"AR={AR[i]}", color='blue', fontsize=10, va='center')

# -----------------------------
# Smooth diagonal iso-AR lines
# -----------------------------
for i in range(len(AR)):
    x0 = WS[i]
    y0 = TW[i]
    # Create a small curvature around the red point
    TW_curve = y0 + 0.002*(WS_grid - x0) + 0.00003*(WS_grid - x0)**3
    plt.plot(WS_grid, TW_curve, color='blue', linewidth=1.5)

# -----------------------------
# Smooth diagonal iso-FuelBurn lines
# -----------------------------
for i in range(len(FuelBurn)):
    x0 = WS[i]
    y0 = TW[i]
    # Curvature opposite to AR lines for visual separation
    TW_curve = y0 - 0.00002*(WS_grid - x0) + 0.00003*(WS_grid - x0)**3
    plt.plot(WS_grid, TW_curve, color='green', linestyle='--', linewidth=1.5)
    # Label fuel burn at the end
    plt.text(WS_grid[-1]+0.5, TW_curve[-1], f"{int(FuelBurn[i])}", color='green', fontsize=8, va='center')

# -----------------------------
# Horizontal iso-T/W lines
# -----------------------------
num_tw_lines = 6
TW_levels = np.linspace(TW_min, TW_max, num_tw_lines)
for tw in TW_levels:
    plt.hlines(tw, WS_min, WS_max, colors='gray', linestyles='--', linewidth=1)
    plt.text(WS_max+0.5, tw, f"{tw:.3f}", color='gray', fontsize=8, va='center')

# -----------------------------
# Gridlines and labels
# -----------------------------
plt.grid(True, linestyle='--', alpha=0.3)
plt.xlabel("Wing Loading W/S")
plt.ylabel("Thrust-to-Weight T/W")
plt.title("Carpet Plot: Smooth Iso-AR Lines + Smooth Iso-Fuel Burn Lines + Horizontal Iso-T/W Lines")
plt.xlim(WS_min, WS_max)
plt.ylim(TW_min, TW_max)
plt.tight_layout()
plt.show()



