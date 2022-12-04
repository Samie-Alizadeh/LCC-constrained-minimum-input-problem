from igraph import Graph
import random

def Rule_M(out, In, matched, N, possible_nodes, access):

    change = 0

    for v in range(N):
        if len(out[v])==1:
            change = 1
            y = out[v][0]
            matched[y] = 1
            adjacents = [node for node in In[y]]
            In[y] = []
            for adjacent in adjacents:
                out[adjacent].remove(y)

    for v in possible_nodes:    
        if len(In[v])==1:
            change = 1
            x = In[v][0]
            matched[v] = 1
            adjacents = [node for node in out[x]]
            out[x] = []
            for adjacent in adjacents:
                In[adjacent].remove(x)

    return out, In, matched, change 

def update_from_bG_to_Gl(access, be_access, observed, unmatched_nodes, dominated):

    accessible_nodes = []

    for v in unmatched_nodes:
        dominated[v] = 1
        accessible_nodes += access[v]

    for v in accessible_nodes:
        if observed[v]!=1:
            be_accessible = [i for i in be_access[v]]
            be_access[v] = []
            for node in be_accessible:
                access[node].remove(v)
            observed[v] = 1

    return access, be_access, observed, dominated            

def Rule_DS1_DS2_DS3(access, be_access, observed, dominated, matched, N, out, In):    

    change = 0

    for v in range(N):
        if observed[v] == 0:
            if len(be_access[v])==1:
                change = 1
                dominated[v] = 1

                successors = [n for n in access[v]]
                for successor in successors:               
                    be_accessible = [n for n in be_access[successor]]
                    be_access[successor] = []
                    for node in be_accessible:
                        access[node].remove(successor)
                    observed[successor] = 1

            elif  len(be_access[v])==2 and len(access[v])==1: 
                    predecessors = [k for k in be_access[v]]
                    predecessors.remove(v)
                    predecessor = predecessors[0]

                    if matched[v]==1:

                        change = 1
                        dominated[predecessor] = 1

                        successors = [n for n in access[predecessor]]
                        for successor in successors:
                            be_accessible = [n for n in be_access[successor]]
                            be_access[successor] = []
                            for node in be_accessible:
                                access[node].remove(successor)
                            observed[successor] = 1  

        else:
            if len(access[v])==1:
                    successor = access[v][0]
                    if matched[v]==1:
                        change = 1
                        access[v] = []
                        be_access[successor].remove(v)

    return access, be_access, observed, dominated, change, out, In 

def update_from_Gl_to_bG(dominated, In, out):

    for v in range(N):
        if dominated[v]==1:
            successors = [n for n in In[v]]
            In[v] = []
            for node in successors:
                out[node].remove(v)

    return In, out

def my_algorithm(G, N, LCC):

    access = {}
    be_access = {}
    out = {}
    In = {}
    for v in range(N):
           neighbors = G.neighborhood(v,mode="out",order=LCC)
           access[v] = [n for n in neighbors]

           neighbors = G.neighborhood(v,mode="in",order=LCC)
           be_access[v] = [n for n in neighbors]

           neighbors = G.neighborhood(v,mode="out",order=1)
           neighbors.remove(v)
           out[v] = [n for n in neighbors]        

           neighbors = G.neighborhood(v,mode="in",order=1)
           neighbors.remove(v)
           In[v] = [n for n in neighbors]


    possible_nodes = []

    matched = {}
    observed = {}
    dominated = {}
    for v in range(N):
        matched[v] = 0
        observed[v] = 0     
        dominated[v] = 0     

    while(True):

        out, In, matched, change1 = Rule_M(out, In, matched, N, possible_nodes, access)

        unmatched_nodes = [v for v in range(N) if len(In[v])==0 and matched[v]==0]

        access, be_access, observed, dominated = update_from_bG_to_Gl(access, be_access, observed, unmatched_nodes, dominated)


        access, be_access, observed, dominated, change2, out, In = Rule_DS1_DS2_DS3(access, be_access, observed, dominated, matched, N, out, In)
        possible_nodes = [v for v in range(N) if observed[v]==1 and len(access[v])==0]
        In, out = update_from_Gl_to_bG(dominated, In, out)

        observed_nodes = 0
        matched_nodes = 0
        for v in range(N):
            if observed[v]==1:
                observed_nodes+=1
            if matched[v]==1:
                matched_nodes+=1

        if change1==0 and change2==0:

            if  len(unmatched_nodes)+matched_nodes+observed_nodes==(2*N):
                input_nodes = unmatched_nodes + [v for v in range(N) if dominated[v]==1]
                input_nodes = list(set(input_nodes))
                return len(input_nodes) 

            else:

                if matched_nodes+len(unmatched_nodes)!=N:
                    possible_matchings = [(len(access[v]),v) for v in range(N) if matched[v]==0 and len(In[v])!=0]
                    possible_matchings.sort()

                    y = possible_matchings[0][1]
                    xs = [v for v in In[y]]
                    x = random.choice(xs)

                    matched[y] = 1

                    adjacents = [n for n in In[y]]
                    In[y] = []
                    for adjacent in adjacents:
                        out[adjacent].remove(y)

                    adjacents = [n for n in out[x]]
                    out[x] = []
                    for adjacent in adjacents:
                        In[adjacent].remove(x) 

                    unmatched_nodes = [v for v in range(N) if len(In[v])==0 and matched[v]==0]    
                    access, be_access, observed, dominated = update_from_bG_to_Gl(access, be_access, observed, unmatched_nodes, dominated)


                else:
                    possible_dominatings = [(len(access[v]),v) for v in range(N) if dominated[v]==0]
                    possible_dominatings.sort(reverse=True)

                    node = possible_dominatings[0][1]

                    dominated[node] = 1
                    successors = [n for n in access[node]]
                    for successor in successors:
                        observed[successor] = 1
                        be_accessible = [n for n in be_access[successor]]
                        be_access[successor] = []
                        for bec in be_accessible:
                            access[bec].remove(successor) 

                    In, out = update_from_Gl_to_bG(dominated, In, out)


if __name__ == "__main__": 
   
      
      G  = Graph.Read_Ncol('datset_name.txt', directed=True)
      N = G.vcount()
      
      LCC = 1   # desired LCC
      
      input_nodes = my_algorithm(G, N, LCC) 
      
      print (input_nodes/N)