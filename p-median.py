import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from TabuSearch import TabuSearch
from pathlib import Path
from natsort import natsorted

pathlist = natsorted(Path("test-data\\").glob('*.txt'), key=str)

for path in pathlist:
    path_in_str = str(path)
    #nx.draw(G, pos=nx.spring_layout(G))
    #plt.draw()
    #plt.show()
    print(path_in_str, end=' ')
    TS = TabuSearch(path_in_str)
    solution_val, solution = TS.run()
    print(solution_val, solution)

