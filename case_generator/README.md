# Multilayer Powder Spreading -- Parameter File Generation and Simulation Workflow

This directory contains the scripts used to generate the parameter files
required by the `lethe-particles` executable to reproduce the multilayer
powder spreading simulations from the article:

"Increased packing density during multi-layer powder spreading: An
experimental and numerical study"

------------------------------------------------------------------------

## 1. Generating the Parameter Files

To generate the parameter files for the following simulations:

-   PS1-L1\
-   PS2-L1\
-   PS3-L1\

Run:

``` bash
python3 parameter_sweep.py
```

This will:

-   Create a `prm/` directory\
-   Generate three subdirectories: `PS1/`, `PS2/`, and `PS3/`

### Changing the Domain Length

To generate parameter files for different domain lengths (PSX-LY),
modify the `length_multiplier` variable inside:

``` bash
parameter_sweep.py
```

------------------------------------------------------------------------

## 2. Particle Insertion Strategy

Instead of inserting the full quantity of powder for all 20 layers at
the start of the simulation, we use two Lethe features:

### 2.1 Remove Particles Inside Box

This feature removes all particles inside a user-defined box (defined by
two points).\
The removal occurs immediately before each particle insertion step.

This ensures \no excessive overlap between new and existing particles 
on insertion.

### 2.2 File-Based Particle Insertion

The "file insertion" feature inserts particles from a file containing
the positions, velocities, diameters, etc.\

### Why This Strategy?

-   Only particles required for the current layer are simulated\
-   Significantly reduces computational cost\
-   Particle insertion files can be reused across simulations (e.g.,
    different spreading velocities or particle properties)

------------------------------------------------------------------------

## 3. Directory Structure

    case_generator/
    |
    |-- extract_particle_inputs.py
    |-- template_loading.prm
    |-- template_spreading.prm
    |-- template.sh
    |-- prm/
        |
        |-- PS1/
        |   |-- 00_loading/
        |   |   |
        |   |   |-- gmsh/
        |   |   |-- PS1_LOADING_XX.prm
        |   |   |-- PS1_LOADING_XX.sh
        |   |
        |   |-- gmsh/ 
        |   |-- PS1.sh
        |   |-- PS1.prm
        |
        |-- PS2/
        |   |-- 00_loading/
        |   |   |
        |   |   |-- gmsh/
        |   |   |-- PS2_LOADING_XX.prm
        |   |   |-- PS2_LOADING_XX.sh
        |   |
        |   |-- gmsh/ 
        |   |-- PS2.sh
        |   |-- PS2.prm
        |
        |-- PS3/
            |-- 00_loading/
            |   |
            |   |-- gmsh/
            |   |-- PS3_LOADING_XX.prm
            |   |-- PS3_LOADING_XX.sh
            |
            |-- gmsh/ 
            |-- PS3.sh
            |-- PS3.prm

------------------------------------------------------------------------

## 4. Loading Simulations (Required First)

For each domain length (L1, L2, L3, L4), particle insertion files must first
be generated using loading simulations:

    PSZ_LOADING_XX.prm

### Important

For a given domain length, you only need to run one `00_loading/`
directory.

For example, if you run:

    prm/PS1/00_loading/PS1_LOADING_00.prm
    prm/PS1/00_loading/PS1_LOADING_01.prm
    ...

You do NOT need to run:

    prm/PS2/00_loading/...
    prm/PS3/00_loading/...
    ...

etc. 

------------------------------------------------------------------------

## 5. Running Jobs on a SLURM Cluster

Each `.prm` file is paired with a `.sh` script for SLURM job submission.

If you need to modify cluster settings (time, memory, partition, etc.),
edit:

    template.sh

and regenerate the parameter files.

------------------------------------------------------------------------

## 6. Extracting Particle Insertion Files

After all loading simulations are complete:

1.  Go to the appropriate loading directory:

``` bash
cd case_generator/prm/PSZ/00_loading/
```

2.  Copy the extraction script:

``` bash
cp ../../../extract_particle_inputs.py .
```

3.  Run the extraction (default length multiplier = 1):

``` bash
python3 extract_particle_inputs.py -p PSZ -lm 1
```

4.  Move the generated particle input files:

``` bash
mv particle_*.input ../
```

The same `particle_XX.input` files can (and should) be reused for every
PSZ spreading simulation for a given domain length since the particle 
physical properties during loading do not significantly affect the 
spreading simulation.

------------------------------------------------------------------------

## 7. Running the Spreading Simulations

Assuming Lethe is properly installed, you can launch the spreading
simulations using:

``` bash
mpirun -np N_PROC lethe-particles PSZ.prm
```