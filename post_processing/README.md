# Multilayer Powder Spreading -- Post-Processing workflow

This directory contains the scripts used to post-process the simulation 
results. Please refer to the powder_spreading/case_generator directory
to run powder spreading simulation. 

------------------------------------------------------------------------

## 1. Directory Structure

Assuming that you have launched the simulations in the 
/powder_spreading/casegenerator/prm/ directory, your file structure should 
look like this:

powder_spreading/
|
|-- experimental.data
|-- case_generator/
|   |
|   |-- extract_particle_inputs.py
|   |-- template_loading.prm
|   |-- template_spreading.prm
|   |-- template.sh
|   |-- prm/
|       |
|       |-- PS1/
|       |   |-- 00_loading/
|       |   |-- gmsh/ 
|       |   |-- out_PS1_2026-02-19/
|       |   |-- PS1.sh
|       |   |-- PS1.prm
|       |
|       |-- PS2/
|       |   |-- 00_loading/
|       |   |-- gmsh/ 
|       |   |-- out_PS2_2026-02-19/
|       |   |-- PS1.sh
|       |   |-- PS1.prm
|       |
|       |-- PS3/
|       |   |-- 00_loading/
|       |   |-- gmsh/ 
|       |   |-- out_PS3_2026-02-19/
|       |   |-- PS1.sh
|       |   |-- PS1.prm
|
|-- post_processing/
    |
    |-- graph_rel_density.py
    |-- graph_vector_density.py
    |-- post_rel_density.py
    |-- post_vector_density.py

The date of the "out_PSZ_YYYY-MM-SS" directories will be different. 

------------------------------------------------------------------------

## 2. Post-process for relative density 

To post-process the effective layer relative density (LRD) and the 
cummulative relative density (CRD) of the "PS1" simulation, the following 
python command needs to be used in the 
"powder_spreading/case_generator/prm/" directory:

``` bash
python3 ../../post_processing/post_rel_density.py -prm PS1.prm

```
The same command can be used for the "PS2" and "PS3" simulations. The 
python script will create a "00_binary/" directory which will store the 
processed data. To plot the three simulations ("PS1", "PS2", "PS3"), 
the following command: 

``` bash
python3 ../../post_processing/graph_rel_density.py 

```

The "graph_rel_density.py" script can be easily modified if you only want 
to plot the results of one simulation. The python script will create a 
"00_figure/" directory which will store the graph associated with the LRD 
and the CRD.

------------------------------------------------------------------------

## 3. Post-process for vector-fields

Similarly to the relative density post-processing script, you first need 
to use the following command in the
"powder_spreading/case_generator/prm/" directory:

``` bash
python3 ../../post_processing/post_vector_field.py -prm PS1.prm

```

To generate every displacement field for every layer, the following 
command can be use: 

``` bash
python3 ../../post_processing/graph_vector_field.py 

```

The graphs will be stored in the "00_figure/" directory.