from optvl import OVLSolver
import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------------------------
# FILES FOR THE TWO GEOMETRIES
# --------------------------------------------------------------------
geom1 = "C:\\Users\\tadco\\Desktop\\OptVL Test\\generated_asa_wing.avl"
geom2 = "C:\\Users\\tadco\\Desktop\\OptVL Test\\generated_sardine_wing2.avl"

ovl1 = OVLSolver(geo_file=geom1, debug=False)
ovl2 = OVLSolver(geo_file=geom2, debug=False)
    
# Mach and Reynolds for both
ovl1.set_parameter("Mach", 0.30)
ovl2.set_parameter("Mach", 0.30)

# ovl1.set_parameter("Re", 1e6)
# ovl2.set_parameter("Re", 1e6)

# AoA sweep
alpha_range = np.linspace(-5, 15, 21)

# Storage dictionaries
results = {
    "geom1": {"CL": [], "CD": [], "Cm": []},
    "geom2": {"CL": [], "CD": [], "Cm": []}
}

# --------------------------------------------------------------------
# FUNCTION TO RUN A CASE
# --------------------------------------------------------------------
def run_alpha_sweep(ovl, key_name):
    for alpha in alpha_range:
        ovl.set_variable("alpha", alpha)
        ovl.execute_run()
        data = ovl.get_total_forces()

        results[key_name]["CL"].append(data["CL"])
        results[key_name]["CD"].append(data["CD"])
        results[key_name]["Cm"].append(data["Cm"])

# --------------------------------------------------------------------
# RUN SWEEPS
# --------------------------------------------------------------------
print("Running geometry 1...")
run_alpha_sweep(ovl1, "geom1")

print("Running geometry 2...")
run_alpha_sweep(ovl2, "geom2")

# --------------------------------------------------------------------
# PLOTTING
# --------------------------------------------------------------------
# plt.style.use("seaborn-v0_8")

# Lift Curve
plt.figure(figsize=(8,5))
plt.plot(alpha_range, results["geom1"]["CL"], label="Advanced Single Aisle Wing")
plt.plot(alpha_range, results["geom2"]["CL"], label="SARDINES Wing")
plt.xlabel("Angle of Attack (deg)")
plt.ylabel("CL")
plt.title("Lift Curve (CL vs α)")
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()

# Drag Curve
plt.figure(figsize=(8,5))
plt.plot(alpha_range, results["geom1"]["CD"], label="Advanced Single Aisle Wing")
plt.plot(alpha_range, results["geom2"]["CD"], label="SARDINES Wing")
plt.xlabel("Angle of Attack (deg)")
plt.ylabel("CD")
plt.title("Drag Curve (CD vs α)")
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()

# Polar Plot
plt.figure(figsize=(8,5))
plt.plot(results["geom1"]["CD"], results["geom1"]["CL"], label="Advanced Single Aisle Wing")
plt.plot(results["geom2"]["CD"], results["geom2"]["CL"], label="SARDINES Wing")
plt.xlabel("CD")
plt.ylabel("CL")
plt.title("Lift–Drag Polar (CL vs CD)")
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()
