from random import randint
import networkx as nx
import numpy as np

def readGraph(filename):
    file = open(filename, 'r')
    lines = file.readlines()
    file.close()

    header = lines.pop(0).strip().split(' ')
    p = int(header[2])
    G = nx.Graph()
    for line in lines:
        edge = line.strip().split( ' ' )
        vi = int(edge[0])-1
        vj = int(edge[1])-1
        cost = int(edge[2])
        edge = (vi,vj)
            
        G.add_edge(*edge, weight=cost)
   
    distances = nx.floyd_warshall(G)
    file.close()
    return G, p, distances


class TabuSearch:
    def __init__(self, filename):
        self.G, self.p, self.distances = readGraph(filename)

        self.initVariables()

    def initVariables(self):
        self.max_iterations     = max(2*self.G.number_of_nodes(), 100)
        self.stable_iterations  = round(0.2 * self.max_iterations)
        self.iteration          = 0
        self.best_solution      = float('inf')
        self.slack              = 0
        self.add_time           = [ float('-inf') for x in self.G.nodes() ]
        self.freq               = [ 0 for x in self.G.nodes() ]
        self.S                  = set()
        self.NS                 = set( [x for x in self.G.nodes()] )
        self.k                  = max(self.distances)
        self.last_improvement   = self.iteration
        self.tabu_time          = randint(1,self.p+1)
    
    def generateStartingSolution(self):
        while len(self.S) < self.p:
            #print('Generating', len(self.S))
            self.best_solution = self.ADD()
            #print(self.best_solution)


    def evaluate(self, v_candidate, m_type):
        if m_type == 'ADD':
            self.S.add(v_candidate)
            self.NS.remove(v_candidate)
        else:
            self.S.remove(v_candidate)
            self.NS.add(v_candidate)

        cost = 0    
        for v_ns in self.NS:
            min_distance = float('inf')
            closest_facility = 0
            for v_s in self.S:
                if self.distances[v_ns][v_s] < min_distance:
                    min_distance = self.distances[v_ns][v_s]
                    closest_facility = v_s
            
            if min_distance != float('inf'):
                if m_type == 'ADD':
                    cost += self.distances[v_ns][closest_facility] + self.k * self.freq[v_ns]
                else:
                    cost += self.distances[v_ns][closest_facility]
                
        if m_type == 'ADD':
            self.S.remove(v_candidate)
            self.NS.add(v_candidate)
        else:
            self.S.add(v_candidate)
            self.NS.remove(v_candidate)
        
        return cost


    def isTabu(self, v):
        if self.add_time[v] == float('-inf'):
            return False
    
        return self.add_time[v] >= self.iteration - self.tabu_time

    def flip_coin(self):
        return np.random.random() < 0.5
    
    def ADD(self):
        new_solution = float('inf')
        best_candidate = -1
        for v in self.NS:
            if self.isTabu(v):
                continue
            value = self.evaluate(v, 'ADD')
            if value < new_solution:
                new_solution = value
                best_candidate = v
                
        if best_candidate >= 0:
            self.add_time[best_candidate] = self.iteration
            self.S.add(best_candidate)
            self.NS.remove(best_candidate)
            
        return new_solution

    def aspirationCriteria(self,v,value):
        return value < self.best_solution

    def DROP(self):
        new_solution = float('inf')
        best_candidate = -1

        for v in self.S:
            value = self.evaluate(v, 'DROP')
            if ( not self.isTabu(v) or self.aspirationCriteria(v,value) ) and value < new_solution:
                new_solution = value
                best_candidate = v
        
        if best_candidate >= 0:
            self.NS.add(best_candidate)
            self.S.remove(best_candidate)

        return new_solution

    def chooseMove(self):
        if len(self.S) < self.p - self.slack:
            return self.ADD()
        elif len(self.S) > self.p + self.slack:
            return self.DROP()
        elif self.flip_coin() and len(self.S) > 0:
            return self.DROP()
        else:
            return self.ADD()

    def run(self):
        while self.iteration < self.max_iterations:
            new_solution = self.chooseMove()
            self.iteration += 1
            if len(self.S) == self.p and new_solution < self.best_solution:
                self.best_solution = new_solution
                self.slack = 0
                self.last_improvement = self.iteration
                #print('Improvement!', self.best_solution)
            elif self.iteration - self.last_improvement == self.stable_iterations * 2:
                self.slack += 1
                #print('Increasing Slack')
            if self.iteration - self.last_improvement == round(self.stable_iterations / 2):
                self.tabu_time = randint(1,self.p+1)
                #print('Changing Tabu_Time')
            if len(self.S) == self.p and self.iteration - self.last_improvement == self.stable_iterations:
                self.iteration = self.max_iterations
            else:
                self.iteration = self.iteration + 1

        return self.best_solution, self.S
