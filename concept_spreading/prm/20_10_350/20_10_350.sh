#!/bin/bash
#SBATCH --account=rrg-blaisbru
#SBATCH --ntasks-per-node=64
#SBATCH --nodes=1 
#SBATCH --time=167:59:00          
#SBATCH --mem=249G         
#SBATCH --job-name=20_10_350
####SBATCH --output=20_10_350.out
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-user=oliviergabo@gmail.com

source $HOME/.dealii
srun $HOME/lethe/inst/bin/lethe-particles 20_10_350.prm