from modelsAndConstants import * 



def createRelationGraph(matConcordance: pd.DataFrame, seuil: float) -> DirectedGraph:
    
    #* Verifications
    if matConcordance.shape[0] != matConcordance.shape[1]:
        raise ValueError("La matrice de concordance doit être carrée")
    
    if not (0 <= seuil <= 1):
        raise ValueError("Le seuil doit être entre 0 et 1")
    
    musicsLabel = list(matConcordance.index)
    graph = DirectedGraph(musicsLabel)
    
    #* Add all arcs above threshold
    for music1 in matConcordance.index:
        for music2 in matConcordance.columns:
            if music1 != music2:  #* No self-loops
                if matConcordance.loc[music1, music2] > seuil:
                    graph.addArc(music1, music2)
    
    return graph

 
def findStronglyConnectedComponents(graph:DirectedGraph) -> list[set[str]]:
    #* kosaraju algorithm

    def DFS1Iterative(startNode, adj, visited, finishStack):
        stack = [(startNode, False)]  # (node, childrenProcessed)
        
        while stack:
            node, childrenProcessed = stack.pop()
            
            if childrenProcessed:
                finishStack.append(node)
            else:
                if visited[node]:
                    continue
                
                visited[node] = True

                stack.append((node, True))
                
                # Add unvisited children to stack (in reverse order to maintain DFS order)
                for neighbor in adj[node]:
                    if not visited[neighbor]:
                        stack.append((neighbor, False))
    
    
    def DFS2Iterative(startNode, revAdj, visited, scc):
        stack = [startNode]
        
        while stack:
            node = stack.pop()
            
            if visited[node]:
                continue
            
            visited[node] = True
            scc.add(node)
            
            # Add unvisited neighbors to stack
            for neighbor in revAdj[node]:
                if not visited[neighbor]:
                    stack.append(neighbor)

    V = graph.vertices
    visited = {u : False for u in V}
    st = []

    #* Fill stack with finish time order
    for i in V:
        if not visited[i]:
            # DFS1(i, graph.arcs, visited, st)
            DFS1Iterative(i, graph.arcs, visited, st)

    reverseGraph = DirectedGraph(V)
    #* Reverse the graph
    for u in V:
        for v in graph.arcs[u]:
            reverseGraph.addArc(v,u)

    #* Process reversed graph in order of stack
    visited = {u : False for u in V}
    SCCs = []

    while st:
        u = st.pop()
        if not visited[u]:
            scc = set()
            # DFS2(u, revArcs, visited, scc)
            DFS2Iterative(u, reverseGraph.arcs, visited, scc)
            SCCs.append(scc)

    return SCCs


def contractCycles(graphe: DirectedGraph) -> DirectedGraph:

    cycles = findStronglyConnectedComponents(graphe)
    
    # Créer un mapping des nœuds originaux vers les nœuds contractés
    vertexToGroup = {}
    groupToLabel = {}
    

    vertexNotInCycle = set(graphe.vertices)
    for cycle in cycles:
        vertexNotInCycle -= cycle
    
    for vertex in vertexNotInCycle:
        vertexToGroup[vertex] = vertex
        groupToLabel[vertex] = vertex
    
    #* Group cycle
    for idx, cycle in enumerate(cycles):

        groupLabel = " | ".join(cycle)
        groupeId = f"CYCLE_{idx}"
        
        for vertex in cycle:
            vertexToGroup[vertex] = groupeId
        groupToLabel[groupeId] = groupLabel

    reduceGraph = DirectedGraph()
    
    # Ajouter les nœuds du nouveau graphe
    for groupeId, label in groupToLabel.items():
        reduceGraph.addVertex(label)
    
    # Ajouter les arcs du nouveau graphe
    addedArcs = set()
    for source, destinations in graphe.arcs.items():
        groupeSource = groupToLabel[vertexToGroup[source]]
        
        for destination in destinations:
            groupeDest = groupToLabel[vertexToGroup[destination]]
            
            # Éviter les auto-boucles et les doublons
            if groupeSource != groupeDest:
                arc = (groupeSource, groupeDest)
                if arc not in addedArcs:
                    reduceGraph.addArc(groupeSource, groupeDest)
                    addedArcs.add(arc)
    
    return reduceGraph

def findEfficaceSet(relationGraph: DirectedGraph) -> list[str]:
    efficaceSet = []
    for vertex in relationGraph.vertices:
        dominatingSet = relationGraph.getPredecessors(vertex)
        if len(dominatingSet) == 0:
            efficaceSet.append(vertex)
    
    return efficaceSet

def findKernel(graph: DirectedGraph) -> set[str]:

    #* Start with all vertices as candidates
    candidates = set(graph.vertices)
    kernel = set()
    
    #* Greedy algorithm: iteratively select vertices with no predecessors in candidates
    while candidates:
        print(f"Searching kernel {len(candidates)} left")
        #* Find vertices in candidates with no predecessors in candidates
        verticesWithoutPred = set()
        for vertex in candidates:
            predecessors = graph.getPredecessors(vertex)
            if not (predecessors & candidates):  #* No predecessor in candidates
                verticesWithoutPred.add(vertex)
        
        #* Add these vertices to the kernel
        kernel.update(verticesWithoutPred)
        
        #* Remove them from candidates and their neighbors
        toRemove = verticesWithoutPred.copy()
        for vertex in verticesWithoutPred:
            toRemove.update(graph.getSucessors(vertex))
        candidates -= toRemove
    
    return kernel

def convertVerticesToMusic(vertices: list[str], musicsAvailable: list[Music]) -> list[Music]:
    musics_result = []
    isrc_seen = set()  # Pour éviter les doublons
    
    # Créer un dictionnaire pour accéder rapidement aux musiques par ISRC
    music_by_isrc = {music.isrc: music for music in musicsAvailable}
    
    for vertex in vertices:
        # Vérifier si le vertex contient plusieurs labels (mergés avec " | ")
        labels = vertex.split(' | ')
        
        for label in labels:
            # Extraire l'ISRC du label
            # Format attendu: "titre - artiste - ISRC"
            parts = label.strip().split(' - ')
            
            if len(parts) >= 3:
                # L'ISRC est la dernière partie
                isrc = parts[-1].strip()
                
                # Chercher la musique correspondante
                if isrc in music_by_isrc and isrc not in isrc_seen:
                    musics_result.append(music_by_isrc[isrc])
                    isrc_seen.add(isrc)
    
    return musics_result
