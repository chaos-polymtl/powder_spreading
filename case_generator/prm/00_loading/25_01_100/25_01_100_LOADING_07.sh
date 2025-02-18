#!/bin/bash
#SBATCH --account=def-damela
#SBATCH --ntasks-per-node=64
#SBATCH --nodes=1 
#SBATCH --time=11:00:00          
#SBATCH --mem=249G         
#SBATCH --job-name=07
####SBATCH --output=25_01_100_LOADING_07.out
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-user=oliviergabo@gmail.com

source $HOME/.dealii
srun $HOME/lethe/inst/bin/lethe-particles 25_01_100_LOADING_07.prm