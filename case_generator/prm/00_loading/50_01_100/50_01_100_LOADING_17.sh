#!/bin/bash
#SBATCH --account=def-damela
#SBATCH --ntasks-per-node=64
#SBATCH --nodes=1 
#SBATCH --time=11:00:00          
#SBATCH --mem=249G         
#SBATCH --job-name=17
####SBATCH --output=50_01_100_LOADING_17.out
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-user=oliviergabo@gmail.com

source $HOME/.dealii
srun $HOME/lethe/inst/bin/lethe-particles 50_01_100_LOADING_17.prm