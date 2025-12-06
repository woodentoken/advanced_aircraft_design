import matplotlib.pyplot as plt
import ipdb
import polars as pl
import numpy as np


captured_data = [
    {
        "cruise_alt": 40000,
        "payload": 0,
        "design_mass": 72715.0619652152,
        "fuel_burn": 19557.81315955217,
        "final_mass": 53157.24880566304,
        "flown_range": 3837.008567755921,
        "payload_total": 0.0,
    },
    {
        "cruise_alt": 40000,
        "payload": 3000,
        "design_mass": 75842.246860212,
        "fuel_burn": 19557.813159557285,
        "final_mass": 56284.43371857376,
        "flown_range": 3787.546721535523,
        "payload_total": 3000.0,
    },
    {
        "cruise_alt": 40000,
        "payload": 6000,
        "design_mass": 78967.87273699592,
        "fuel_burn": 19557.813159553494,
        "final_mass": 59410.05958210556,
        "flown_range": 3734.9161073313085,
        "payload_total": 6000.0,
    },
    {
        "cruise_alt": 35000,
        "payload": 0,
        "design_mass": 72715.06196521522,
        "fuel_burn": 19557.813159552163,
        "final_mass": 53157.24880566305,
        "flown_range": 3268.1049283181273,
        "payload_total": 0.0,
    },
    {
        "cruise_alt": 35000,
        "payload": 3000,
        "design_mass": 75842.24682937455,
        "fuel_burn": 19557.813159553676,
        "final_mass": 56284.433660666335,
        "flown_range": 3098.3941520949234,
        "payload_total": 3000.0,
    },
    {
        "cruise_alt": 35000,
        "payload": 6000,
        "design_mass": 78967.87273167084,
        "fuel_burn": 19557.813159552163,
        "final_mass": 59410.05957211866,
        "flown_range": 3077.6990358490193,
        "payload_total": 6000.0,
    },
    {
        "cruise_alt": 30000,
        "payload": 0,
        "design_mass": 72715.06196517636,
        "fuel_burn": 19557.81315955219,
        "final_mass": 53157.24880558994,
        "flown_range": 2929.033335802929,
        "payload_total": 0.0,
    },
    {
        "cruise_alt": 30000,
        "payload": 3000,
        "design_mass": 75842.24684041194,
        "fuel_burn": 19557.81315955255,
        "final_mass": 56284.43368139726,
        "flown_range": 3005.0175470993,
        "payload_total": 3000.0,
    },
    {
        "cruise_alt": 30000,
        "payload": 6000,
        "design_mass": 78967.8727298638,
        "fuel_burn": 19557.81315955425,
        "final_mass": 59410.05956872461,
        "flown_range": 2773.1691120994237,
        "payload_total": 6000.0,
    },
    {
        "cruise_alt": 25000,
        "payload": 0,
        "design_mass": 72715.06196679338,
        "fuel_burn": 19557.81315955337,
        "final_mass": 53157.248808627766,
        "flown_range": 2489.962518258742,
        "payload_total": 0.0,
    },
    {
        "cruise_alt": 25000,
        "payload": 3000,
        "design_mass": 75842.24684120854,
        "fuel_burn": 19557.81315955329,
        "final_mass": 56284.43368289192,
        "flown_range": 2483.8525187570217,
        "payload_total": 3000.0,
    },
    {
        "cruise_alt": 25000,
        "payload": 6000,
        "design_mass": 78967.87273167084,
        "fuel_burn": 19557.813159552155,
        "final_mass": 59410.05957211867,
        "flown_range": 2462.637228906148,
        "payload_total": 6000.0,
    },
    {
        "cruise_alt": 20000,
        "payload": 0,
        "design_mass": 72715.06196526467,
        "fuel_burn": 19557.813159552228,
        "final_mass": 53157.24880576358,
        "flown_range": 2239.822154407245,
        "payload_total": 0.0,
    },
    {
        "cruise_alt": 20000,
        "payload": 3000,
        "design_mass": 75842.24683979628,
        "fuel_burn": 19557.813159552163,
        "final_mass": 56284.43368024179,
        "flown_range": 2223.7306027118443,
        "payload_total": 3000.0,
    },
    {
        "cruise_alt": 20000,
        "payload": 6000,
        "design_mass": 78967.87273185074,
        "fuel_burn": 19557.813159552214,
        "final_mass": 59410.05957245962,
        "flown_range": 2214.1195198296623,
        "payload_total": 6000.0,
    },
]

# ipdb.set_trace()


fig, ax = plt.subplots(figsize=(10, 6))
altitudes = sorted(set(data["cruise_alt"] for data in captured_data))
payloads = sorted(set(data["payload_total"] for data in captured_data))
for payload in payloads:
    ranges = [
        data["flown_range"]
        for data in captured_data
        if data["payload_total"] == payload
    ]
    ax.plot(altitudes, ranges, marker="o", label=f"Payload: {payload} lbs")
ax.set_xlabel("Cruise Altitude (ft)")
ax.set_ylabel("Flown Range (nmi)")
ax.set_title("Sensitivity of Flown Range to Cruise Altitude and Payload")
ax.legend()
ax.grid(True)
plt.savefig("sensitivity_plot.png")
plt.show()
