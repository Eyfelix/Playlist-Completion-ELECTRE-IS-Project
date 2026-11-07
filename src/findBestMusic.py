import csv
import json
from createUserTasteAndScores import createUserTaste
from modelsAndConstants import *
from createChart import *
from createConcordanceMatrices import * 
from graphHandler import * 

def loadMusicFromCSV(filename: str) -> list[Music]:
    musicList = []
    seenMusics = set()
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                try:
                    # Parser la liste de genres depuis JSON
                    genres = json.loads(row['genres'])
                    if row['isrc'] in seenMusics:
                        continue
                    seenMusics.add(row['isrc'])
                    # Créer l'objet Music
                    music = Music(
                        title=row['title'],
                        artist=row['artist'],
                        isrc=row['isrc'],
                        genres=genres,
                        tempo=int(row['tempo']),
                        valence=float(row['valence']),
                        energy=float(row['energy']),
                        instrumentality=float(row['instrumentality']),
                        year=int(row['year']),
                        popularity=int(row['popularity'])
                    )
                    
                    musicList.append(music)
                
                except (KeyError, ValueError, json.JSONDecodeError) as e:
                    print(f"Erreur lors du parsing d'une ligne: {e}")
                    print(f"Ligne problématique: {row}")
                    continue
        
        print(f"Done : {len(musicList)} musiques chargées depuis '{filename}'")
        return musicList
    
    except FileNotFoundError:
        print(f"Erreur: Le fichier '{filename}' n'existe pas.")
        return []
    except IOError as e:
        print(f"Erreur lors de la lecture du fichier: {e}")
        return []
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return []





 
if __name__ == "__main__":
    #* Charge les données
    musicsData = loadMusicFromCSV('./data/allMusicData.csv')
    playlist = loadMusicFromCSV('./data/thePlaylistData.csv')

    #* Crée le profil de la playlist
    userTaste = createUserTaste(playlist)

    #* Évalue toutes les musiques par rapport au profil utilisateur
    for music in musicsData:
        scores = createMusicScores(music,userTaste)
        music.setScore(scores)

    #* Filter music to remove the ones already in the playlist
    filteredMusics = list(filter(lambda m: not m.scores["isKnown"],musicsData))
    print(f'Size filtered : {len(filteredMusics)}')
    overallConcordanceMatrix = createOverallConcordanceMatrix(filteredMusics)
    print("Creation of concordance matrice finished, size : ",overallConcordanceMatrix.shape)
    relationGraph = createRelationGraph(overallConcordanceMatrix, DOMINATION_THRESHOLD)
    print(f"Relation graph created : {len(relationGraph.vertices)},{relationGraph.getArcsSize()}")
    reduceGraph = contractCycles(relationGraph)
    print(f"Reduce graph created : {len(reduceGraph.vertices)},{reduceGraph.getArcsSize()}")
    # print(reduceGraph)
    efficaceSet = findEfficaceSet(reduceGraph)
    efficaceMusic = convertVerticesToMusic(efficaceSet,musicsData)
    print(f"Efficace SET {efficaceMusic}")


    kernelSet = findKernel(reduceGraph)
    kernelMusic = convertVerticesToMusic(kernelSet,musicsData)
    print(f"KERNEL : {kernelMusic}")
    print(f'Relation graph size {len(relationGraph.vertices)},{relationGraph.getArcsSize()} Reduce graph : {len(reduceGraph.vertices)},{reduceGraph.getArcsSize()}')
    print(f'Kernel Size :{len(kernelMusic)} | Efficace Set size : {len(efficaceMusic)}')

    plotRawVsSmoothedComparison(filteredMusics,"Raw_filtered",False)

    plotRawVsSmoothedComparison(playlist,"Raw_vs_Smooth_playlist",True)
    plotRawVsSmoothedComparison(playlist,"Raw_and_Smooth_playlist",False)

    plotMusicScores(filteredMusics,"Scores_filtered")


    plotInteractiveHeatmap(overallConcordanceMatrix,1,"concordance_matrice_HeatMap")
    plotMatrixDistribution(overallConcordanceMatrix,"concordance_matrice_Distribution")

    computeStatsAndUserTaste(kernelMusic,userTaste,"Kernel_vs_userTaste")


