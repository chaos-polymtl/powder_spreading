#!/bin/bash
#SBATCH --account={{Account}}
#SBATCH --ntasks-per-node={{Proc_per_node}}
#SBATCH --nodes={{Number_of_node}} 
#SBATCH --time={{Time}}          
#SBATCH --mem={{Memory}}         
#SBATCH --job-name={{Job_name}}
####SBATCH --output={{Name}}.out
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-user=oliviergabo@gmail.com

source $HOME/.dealii
srun $HOME/lethe/inst/bin/lethe-particles {{Name}}
