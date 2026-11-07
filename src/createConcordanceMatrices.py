from modelsAndConstants import * 
from concurrent.futures import ProcessPoolExecutor
from createChart import * 

def computeConcordanceOnCriteria(criteria1:float,criteria2:float,criteriaTresholds:dict[str,float]) -> float:
    indiff = criteriaTresholds["indifference"]
    pref = criteriaTresholds["preference"]

    if criteria1 >= criteria2 - indiff:
        return 1
    elif criteria1 <= criteria2 - pref:
        return 0
    else:
        return (pref + criteria1 - criteria2 ) / (pref - indiff)

def createCriteriaConcordanceMatrix( musicList:list[Music], criteriaTresholds:dict[str,float], criteriaName:str) -> pd.DataFrame:
    print(f"creation de la matrice de concordance du crière {criteriaName}")
    n = len(musicList)
    matrix = np.zeros((n, n))
    labels = [f"{m.title} - {m.artist} - {m.isrc}" for m in musicList]

    for i in range(n):
        for j in range(i+1):
            if i == j:
                matrix[i, j] = 1
            else:
                criteriaMusic1 = musicList[i].scores.get(criteriaName)
                criteriaMusic2 = musicList[j].scores.get(criteriaName)
                matrix[i, j] = computeConcordanceOnCriteria(criteriaMusic1, criteriaMusic2, criteriaTresholds)
                matrix[j, i] = computeConcordanceOnCriteria(criteriaMusic2, criteriaMusic1, criteriaTresholds)

    #* Création du DataFrame avec labels en lignes et colonnes pour plus de clarté
    dfConcordance = pd.DataFrame(matrix, index=labels, columns=labels)

    return dfConcordance

def createOverallConcordanceMatrix(musicList: list[Music]) -> pd.DataFrame:
    n = len(musicList)
    overallMatrix = np.zeros((n, n))
    labels = [f"{m.title} - {m.artist} - {m.isrc}" for m in musicList]
    #* Muli process to speed up things
    with ProcessPoolExecutor() as executor:
        futures = {
            criteria: executor.submit(
                createCriteriaConcordanceMatrix, 
                musicList,
                CRITERES_THRESHOLDS.loc[criteria], 
                criteria
            )
            for criteria in LIST_CRITERIAS
        }

        # On récupère les résultats au fur et à mesure qu'ils se terminent
        matrixCriteria = {criteria: futures[criteria].result() for criteria in LIST_CRITERIAS}

    for criteria in LIST_CRITERIAS:
        
        plotInteractiveHeatmap(matrixCriteria[criteria], 1, f"{criteria}MatriceHeatMap")
        plotMatrixDistribution(matrixCriteria[criteria], f"{criteria}MatriceDistribution")
        overallMatrix += matrixCriteria[criteria].to_numpy() * CRITERES_WEIGHTS[criteria]

    dfConcordance = pd.DataFrame(overallMatrix, index=labels, columns=labels)

    return dfConcordance
