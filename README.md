# Advanced Aircraft Design

This repository contains the course materials and assignments for the Advanced Aircraft Design course offered at UC Davis during Fall of 2025.

The course focuses on the principles and practices of designing advanced aircraft, covering topics such as aerodynamics, structures, propulsion, and systems integration.

The course is taught by Dr. Christina Harvey.

# Contributors

- Joshua Booth
- Kaleb Bordner
- Nick Rusali
- Sherwin Shi
- Xingmin Han

# Project Mission

Search and Rescue redesign of a NASA single aisle passenger aircraft to focus on efficiency and emissions reduction.

# Dependencies and Setup

I'd recommend using a virtual environment defined by the tool `uv`, which is ideal for managing Python dependencies.

You can find documentation for `uv` [here](https://docs.astral.sh/uv/). Look at the installation instructions for your operating system. Once `uv` is installed, you can clone this repository and install the dependencies with the "custom" update script by running:

```
./update_submodules.sh
```

on the command line.

## Explanation of `update_submodules.sh`

This just clones the Aviary submodule into your local repository so you can use it (and modify it if you want).

Then it runs `uv sync` to install the dependencies defined in `pyproject.toml`. This .toml file points to the local Aviary submodule and uses it as a dependency, hence, why we need to clone it first.

once this script is run once, you can then use the development branch of aviary in this virtual enviroment by importing it as needed. I recommend you run

```
aviary check
```

from the command line to ensure everything is working properly.
