# powder_spreading

This repository contains the case generation tools and post-processing
scripts used the article:

"Increase in packing density during multi-layer powder spreading: An
experimental and numerical study"

------------------------------------------------------------------------

## Overview

The repository is organized into two main components:

-   `case_generator/`\
    Tools to generate simulation parameter files required by the 
    `lethe-particles` executable.

-   `post_processing/`\
    Scripts to analyze simulation outputs and extract relevant metrics
    (e.g., packing density, layer evolution, and comparison with
    experiments).

Additional files:

-   `.gitignore` -- Git ignore rules\
-   `experimental.data` -- Experimental reference data used for
    validation/comparison\
-   `README.txt` (inside subfolders) -- Local documentation for specific
    directories. 


## Requirements

Typical requirements include:

-   Python 3.x\
-   NumPy\
-   Matplotlib\
-   Pandas (optional)
-   [Lethe properly installed](https://chaos-polymtl.github.io/lethe/documentation/installation/regular_installation.html)
-   Lethe-pyvista  (in the lethe repository: lethe/lethe/contrib/postprocessing/lethe_pyvista_tools)

------------------------------------------------------------------------

## Usage

### 1. Case Generation

Generate the parameter file for the loading and spreading simulation

------------------------------------------------------------------------

### 2. Post-Processing

Navigate to:

    cd post_processing

Run the analysis scripts on simulation output files to compute:

-   Packing density\
-   Displacement fields\

------------------------------------------------------------------------

## Citation

If you use this repository in academic work, please cite:

"Increase in packing density during multi-layer powder spreading: An
experimental and numerical study"

(Add DOI and full reference here.)

------------------------------------------------------------------------

## Author

Olivier Gaboriault
