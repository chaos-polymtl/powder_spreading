
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import argparse

parser = argparse.ArgumentParser(description='Arguments to plot a graph')
parser.add_argument("-i", "--input", type=str, help="Name of the input file", required=True)
args, leftovers=parser.parse_known_args()


filename=args.input

colors = ['#1b9e77', '#d95f02', '#7570b3', '#e7298a', '#66a61e', '#e6ab02']

from cycler import cycler

colors=['#7570b3','#1b9e77','#d95f02','#e7298a','#66a61e','#e6ab02']

plt.rcParams['axes.prop_cycle'] = cycler(color = colors)
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['figure.figsize'] = (10,8)
plt.rcParams['lines.linewidth'] = 4
plt.rcParams['lines.markersize'] = '11'
plt.rcParams['markers.fillstyle'] = "none"
plt.rcParams['lines.markeredgewidth'] = 2
plt.rcParams['legend.columnspacing'] = 2
plt.rcParams['legend.handlelength'] = 3
plt.rcParams['legend.handletextpad'] = 0.2
plt.rcParams['legend.frameon'] = True
plt.rcParams['legend.fancybox'] = False
plt.rcParams['xtick.major.width'] = 2
plt.rcParams['xtick.major.size'] = 5
plt.rcParams['ytick.major.size'] = 5
plt.rcParams['ytick.major.width'] = 2
plt.rcParams['font.size'] = '25'
plt.rcParams['font.family']='DejaVu Serif'
plt.rcParams['font.serif']='cm'
plt.rcParams['savefig.bbox']='tight'
plt.rcParams['legend.handlelength']=1

files = ["output.data"]
labels = [ "DMT with LB"]
markers = ["o", "^", "s", "<", ">"]

for i in range(len(files)):
    t, energy = np.loadtxt(files[i], skiprows=1, unpack=True)
    plt.semilogy(t,energy,label=labels[i])
   

# Customize the first y-axis
#plt.legend()
plt.xlabel("Time (s)")
plt.ylabel("Kinetic energy [min]")


# Optionally, adjust title padding for the second x-axis

#plt.ylim(1E-11,3E-4)
plt.subplots_adjust(left=0.15, right=0.95,top=0.95)
#plt.savefig("results.pdf", dpi=300)
plt.show()
