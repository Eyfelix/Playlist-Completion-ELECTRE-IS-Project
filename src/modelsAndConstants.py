import pandas as pd
from collections import defaultdict

POSSIBLES_GENRES = ["rap", "pop", "jazz", "rock", "classical", "metal", "variété française", "latin", "electro"]
CRITERES_WEIGHTS = {
    "tempo": 0.15, #*Recco
    "valence": 0.15, #*Recco
    "energy": 0.15, #*Recco
    "instrumentality": 0.1, #*Recco
    "year": 0.1, #* Sp, from playlist
    "popularity": 0.15, #* Sp, from playlist
    "genres": 0.2 #* Sp, via call artist
}

LIST_CRITERIAS = list(CRITERES_WEIGHTS.keys())

CRITERES_THRESHOLDS = pd.DataFrame([
                                [0.02, 0.3],     # tempo
                                [0.02, 0.3],  # valence
                                [0.02, 0.3],     # energy
                                [0.02, 0.3],    # instrumentality
                                [0.02, 0.3],      # year
                                [0.02, 0.3],     # popularity
                                [0.02, 0.3]   # genre
],index=LIST_CRITERIAS,columns=["indifference","preference"])

DOMINATION_THRESHOLD = 0.9
MAX_YEAR = 2025
MIN_YEAR = 1950
MAX_TEMPO = 250
MIN_TEMPO = 40
GAUSSIAN_SIGMA_FACTOR = 45

class Music:
    def __init__(self, title:str, artist:str, isrc:str,genres:list[str], tempo:int, valence:int, energy:int, instrumentality:int, year:int, popularity:int):
        self.title = title
        self.artist = artist
        self.isrc = isrc #* International Standard Recording Code
        self.genres = genres
        self.tempo = tempo
        self.valence = valence
        self.energy = energy
        self.instrumentality = instrumentality
        self.year = year
        self.popularity = popularity
    
    def setScore(self, scores:dict[str, float]) -> None:
        self.scores = scores

    def __str__(self) -> str:
        return f"{self.title} - {self.artist}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
class UserTaste:
    def __init__(self, criteriaMaps):
        self.criteriaMaps = criteriaMaps
    
    


class DirectedGraph:
    def __init__(self, vertices: list[str] = None):
        self.vertices = set(vertices) if vertices else set()
        self.arcs = defaultdict(set)  #* arcs[i] = set of j such that i -> j
        
    def addVertex(self, vertex: str):
        self.vertices.add(vertex)
        if vertex not in self.arcs:
            self.arcs[vertex] = set()
    
    def addArc(self, source: str, destination: str):
        if source not in self.vertices:
            self.addVertex(source)
        if destination not in self.vertices:
            self.addVertex(destination)
        self.arcs[source].add(destination)
    
    def removeArc(self, source: str, destination: str):
        if source in self.arcs and destination in self.arcs[source]:
            self.arcs[source].discard(destination)
    
    def getSucessors(self, vertex: str) -> set[str]:
        return self.arcs.get(vertex, set()).copy()
    
    def getPredecessors(self, vertex: str) -> set[str]:
        pred = set()
        for source, destinations in self.arcs.items():
            if vertex in destinations:
                pred.add(source)
        return pred
    
    def getArcs(self) -> list[tuple[str, str]]:
        arcs = []
        for source, destinations in self.arcs.items():
            for dest in destinations:
                arcs.append((source, dest))
        return arcs
    
    def getArcsSize(self) -> int:
        return sum(len(dests) for dests in self.arcs.values())
    
    def __str__(self) -> str:
        arcs = self.getArcs()
        return f"Graphe({len(self.vertices)} nœuds, {len(arcs)} arcs)\nArcs: {arcs}"


    