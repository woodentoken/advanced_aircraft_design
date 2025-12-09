# Advanced Aircraft Design - SARDINES

This repository contains the course materials and assignments for Team D (SARDINES) design process for the Advanced Aircraft Design course offered at UC Davis during Fall of 2025. leb by Dr. Christina Harvey.

The course focuses on the principles and practices of designing advanced aircraft, covering topics such as aerodynamics, structures, propulsion, and systems integration. And relies on Aviary (https://github.com/OpenMDAO/Aviary), NASA's multidisciplinary aircraft design and optimization tool.

## Contributors and Roles

- Propulsion: Joshua Booth
- Mission Analysis: Kaleb Bordner
- Aerodynamics: Nick Rusali
- Mass/Cost: Sherwin Shi
- Geometry: Xingmin Han

## Project Mission

Search and Rescue redesign of a NASA single aisle passenger aircraft to focus on efficiency and emissions reduction. Our mission requirements are shown below:
<p align="center">
<img width="800" alt="image" src="https://github.com/user-attachments/assets/7f931e05-7380-481d-867a-9a8e2d67c146" />
</p>

## Analysis

primary analysis script resides in the `sardines` directory. running `SARDINE_optimization.py` will optimize an aircraft design and mission simultaneously, subject to provided assumptions and subdiscipline optimizations applied.

## Results

Our final optimized aircraft, which integrates the Propulsion, Mission Analysis, Mass/Cost, and Geometry subdisciplines allowed a 30% reduction in fuel burn relative to our baseline. We present this large increase in flight efficiency with some skepticism. Because we were fully reliant on the fidelity offered by the height_energy method for mission simulation, we suspect that our values are quite low. Additionally, our optimization is forward looking and optimistic in terms of future composite materials and their availability for our aircraft.

The final, integrated and optimized trajectory of our flight plan is shown below.
<p align="center">
<img width="800" alt="integrated_mission_profile" src="https://github.com/user-attachments/assets/dcd51bb1-231d-40ae-a1db-dcbef05a3be3" />
</p>

This resulted in a total mission fuel burn value of 12353 lbm, which represented a 30% reduction from our baseline. Additional details are available in our PDR, which is avaliable upon request.

# Dependencies and Setup

## Tooling
We manage dependencies using [`uv`](https://docs.astral.sh/uv/). With `uv` installed, please run this update_submodules.sh script in the base directory.
```
./update_submodules.sh
```
which will update various git submodules and install the dependencies for pyoptsparse and the IPOPT optimizer.

## Acknowledgements and external tools
- Aviary
- PyOptSparse
- IPOPT
- FAST
