from modelsAndConstants import *
import math as mt



def pseudoGaussian(x:float, mu:float, sigma:float) -> float:
    peak = 1
    return peak * mt.exp(-0.5 * ((x - mu) / sigma) ** 2)

def createGaussianDistribution(minValue: int, maxValue: int, criteriaValue: list[int], contrast_power: float = 1.0):
    if not criteriaValue:
        return {i: 0.0 for i in range(minValue, maxValue + 1)}
    
    # Paramétrage de la largeur (Sigma)
    gaussianSigma = (maxValue - minValue) / GAUSSIAN_SIGMA_FACTOR
    baseMap = {i: 0.0 for i in range(minValue, maxValue + 1)}
    
    for mu in criteriaValue:
        if minValue <= mu <= maxValue:
            for x in range(minValue, maxValue + 1):

                val = pseudoGaussian(x,mu,gaussianSigma)
                
                #* On rajoute l'influence des rebond sur les bords du champs
                val += pseudoGaussian(x,(2*minValue - mu),gaussianSigma)
                val += pseudoGaussian(x,(2*maxValue - mu),gaussianSigma)

                baseMap[x] += val

    # --- NORMALISATION MIN-MAX (0 à 1) ---
    raw_values = list(baseMap.values())
    max_val = max(raw_values)
    min_val = min(raw_values)
    
    range_val = max_val - min_val
    if range_val == 0:
        return {i: 0.0 for i in baseMap}

    for i in baseMap:
        # Normalisation linéaire
        norm_val = (baseMap[i] - min_val) / range_val
        
        # En élevant à une puissance > 1, on écrase les petites valeurs 
        # et on garde les sommets proches de 1.
        baseMap[i] = norm_val ** contrast_power

    return baseMap

def createGenreTasteMap(playlistGenres:list[list[str]]) -> dict[str, list[int]]:
        genreMap = {genre:0 for genre in POSSIBLES_GENRES}

        for genre_list in playlistGenres:
            for genre in genre_list:
                if genre in genreMap:
                    genreMap[genre] += 1

        for genre in genreMap:
            genreMap[genre] /= len(playlistGenres)
        return genreMap

      
def createUserTaste(playlist:list[Music]) -> UserTaste:
    # Create criteria for each attribute
    tempoMap = createGaussianDistribution(MIN_TEMPO, MAX_TEMPO, [music.tempo for music in playlist])
    valenceMap = createGaussianDistribution(0, 100, [music.valence for music in playlist])
    energyMap = createGaussianDistribution(0, 100, [music.energy for music in playlist])
    instrumentality = createGaussianDistribution(0, 100, [music.instrumentality for music in playlist])
    knowns = [music.isrc for music in playlist]
    yearMap = createGaussianDistribution(MIN_YEAR, MAX_YEAR, [music.year for music in playlist])
    popularityMap = createGaussianDistribution(0, 100, [music.popularity for music in playlist])
    genreMap = createGenreTasteMap([music.genres for music in playlist])
    criteriaMaps = {
        "tempo": tempoMap,
        "valence": valenceMap,
        "energy": energyMap,
        "popularity": popularityMap,
        "instrumentality": instrumentality,
        "knowns": knowns,
        "year": yearMap,
        "genres": genreMap,
    }
    return UserTaste(criteriaMaps)

#* Compare a Music against the user taste profile
def createMusicScores(music: Music,userTaste:UserTaste) -> dict[str, float]:
    scores = {}        
    for criteria in LIST_CRITERIAS:

        if criteria == "genres":
            scores["genres"] = max([compareGenre(genre,userTaste) for genre in music.genres] + [0])
        else:
            scores[criteria] = userTaste.criteriaMaps[criteria][getattr(music, criteria)]

    scores["isKnown"] = isKnown(music.isrc,userTaste)
    
    return scores


def isKnown(musicIsrc: str,userTaste:UserTaste) -> bool:
    return int(musicIsrc in userTaste.criteriaMaps["knowns"])

def compareGenre(musicGenre: str,userTaste:UserTaste):
    #* Matrice des distances entre genres
    proximityMatrixData = [
        #*Rap   Pop Jazz Rock Class Metal FrVar Latino Electro
        [1.0, 0.7, 0.5, 0.4,  0.2, 0.3, 0.6, 0.7, 0.6], # Rap
        [0.7, 1.0, 0.6, 0.7,  0.4, 0.3, 0.8, 0.7, 0.7], # Pop
        [0.5, 0.6, 1.0, 0.5,  0.6, 0.2, 0.5, 0.6, 0.5], # Jazz
        [0.4, 0.7, 0.5, 1.0,  0.3, 0.7, 0.6, 0.5, 0.5], # Rock
        [0.2, 0.4, 0.6, 0.3,  1.0, 0.4, 0.5, 0.4, 0.4], # Classical
        [0.3, 0.3, 0.2, 0.7,  0.4, 1.0, 0.3, 0.2, 0.4], # Metal
        [0.6, 0.8, 0.5, 0.6,  0.5, 0.3, 1.0, 0.7, 0.6], # FrVar
        [0.7, 0.7, 0.6, 0.5,  0.4, 0.2, 0.7, 1.0, 0.6], # Latino
        [0.6, 0.7, 0.5, 0.5,  0.4, 0.4, 0.6, 0.6, 1.0]  # Electro
    ]
    proximityMatrix = pd.DataFrame(
        proximityMatrixData,
        index=POSSIBLES_GENRES,
        columns=POSSIBLES_GENRES
    )

    if musicGenre not in POSSIBLES_GENRES:
        raise ValueError(f"Genre '{musicGenre}' non reconnu")
    
    # Calculer la distance pondérée
    proximityTotal = 0
    for genrePlaylist, proportion in userTaste.criteriaMaps["genres"].items():
        # Distance entre le genre candidat et ce genre de la playlist
        proximity = proximityMatrix.loc[musicGenre, genrePlaylist]
        
        # Pondérer par la proportion de ce genre dans la playlist
        proximityTotal += proximity * proportion

    proximityTotal /= len(POSSIBLES_GENRES)

    return proximityTotal