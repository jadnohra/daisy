from collections import deque
from component_base import ComponentBase

class SteppingComponent:
    def __init__(self):
        self._schedulers = set()
        
    def is_registered_in(self, scheduler):
        return scheduler in self._schedulers
    
    def register(self, scheduler):
        self._schedulers.add(scheduler)
        
    def deregister(self, scheduler):
        self._schedulers.remove(scheduler)


class SteppingScheduler:
    def __init__(self):
        self._steppers = set()
        self._dag = {} # keys are nodes and values are adjacency lists
        self._is_dirty = True
        self._top_sort_list = []

    @staticmethod
    def kahn_topsort(graph):
        in_degree = { u : 0 for u in graph }     # determine in-degree 
        for u in graph:                          # of each node
            for v in graph[u]:
                in_degree[v] += 1
     
        Q = deque()                 # collect nodes with zero in-degree
        for u in in_degree:
            if in_degree[u] == 0:
                Q.appendleft(u)
     
        L = []     # list for order of nodes
         
        while Q:                
            u = Q.pop()          # choose node of zero in-degree
            L.append(u)          # and 'remove' it from graph
            for v in graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    Q.appendleft(v)
     
        if len(L) == len(graph):
            return L
        else:                    # if there is a cycle,  
            return []
        
    def add_stepper(self, stepper):
        if stepper.has_component('stepping') == False:
            stepper.add_component('stepping', SteppingComponent(stepper))
        if stepper.stepping.is_registered_in(self) == False:
            stepper.stepping.register(self)
            self._steppers.add(stepper)
    
    def remove_stepper(self, stepper):
        stepper.stepping.deregister(self)
        self._steppers.remove(stepper)
        self.remove_from_dependencies(stepper)
                
    def remove_from_dependencies(self, stepper):
        if stepper in self._dag:
            self._dag.pop(stepper, None)
            self._is_dirty = True
        for k,v in self._dag: # TODO, this may be too slow
            if stepper in v:
                v.remove(stepper)
                self._is_dirty = True
    
    def add_dependency(self, stepper, dependent_stepper):
        self._dag.get(stepper, set()).add(dependent_stepper)
        self._is_dirty = True
        
    def get_stepping_list(self):
        if self._is_dirty:
            self._top_sort_list = self.kahn_topsort(self._dag)
            self._is_dirty = False
        return self._top_sort_list