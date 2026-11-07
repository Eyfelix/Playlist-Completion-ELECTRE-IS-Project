import matplotlib.pyplot as plt
from modelsAndConstants import *
from createUserTasteAndScores import *
import os
import numpy as np
import plotly.graph_objects as go

    # Configuration for each criterion
criteriaConfig = {
        'tempo': {
            'title': 'Tempo',
            'xlabel': 'Tempo (BPM)',
            'ylabel': 'Moyenne des occurences',
            'data1Color': '#E63946',
            'data2Color': '#457B9D'
        },
        'valence': {
            'title': 'Valence',
            'xlabel': 'Valence (0-100)',
            'ylabel': 'Moyenne des occurences',
            'data1Color': '#F77F00',
            'data2Color': '#06A77D'
        },
        'energy': {
            'title': "Energie",
            'xlabel': 'Energie (0-100)',
            'ylabel': 'Moyenne des occurences',
            'data1Color': '#D62828',
            'data2Color': '#003049'
        },
        'popularity': {
            'title': 'Popularité',
            'xlabel': 'Popularité (0-100)',
            'ylabel': 'Moyenne des occurences',
            'data1Color': '#F4A261',
            'data2Color': '#2A9D8F'
        },
        'instrumentality': {
            'title': 'Instrumentalité',
            'xlabel': 'Instrumentalité (0-100)',
            'ylabel': 'Moyenne des occurences',
            'data1Color': '#EF476F',
            'data2Color': '#118AB2'
        },
        'year': {
            'title': 'Année',
            'xlabel': 'Année de sortie',
            'ylabel': 'Moyenne des occurences',
            'data1Color': '#FF6B6B',
            'data2Color': '#4ECDC4'
        },
            'genres': {
            'title': 'styles musicaux',
            'xlabel': 'Style musical',
            'ylabel': 'Moyenne des occurences',
            'data1Color': '#F54927',
            'data2Color': '#27D3F5'
        }
    }

def plotDictToPDF(data: dict[str, float], 
                  outputFilename: str, 
                  title: str = "Data Visualization",
                  xlabel: str = "Categories",
                  ylabel: str = "Values",
                  figsize: tuple = (10, 6),
                  color: str = 'steelblue',
                  plotType: str = 'bar') -> None:

    if not data:
        print("WARNING: Empty dictionary provided, no plot created")
        return
    
    # Ensure filename has .pdf extension
    if not outputFilename.endswith('.pdf'):
        outputFilename += '.pdf'
    
    try:
        # Extract keys and values from dictionary
        keys = list(data.keys())
        values = list(data.values())
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create plot based on type
        if plotType == 'bar':
            ax.bar(keys, values, color=color, edgecolor='black', alpha=0.7)
            ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
            ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            
        elif plotType == 'line':
            ax.plot(keys, values, marker='o', color=color, linewidth=2, markersize=8)
            ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
            ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            ax.grid(True, alpha=0.3)
            
        elif plotType == 'scatter':
            ax.scatter(range(len(keys)), values, color=color, s=100, alpha=0.7, edgecolors='black')
            ax.set_xticks(range(len(keys)))
            ax.set_xticklabels(keys, rotation=45, ha='right')
            ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
            ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
        elif plotType == 'pie':
            ax.pie(values, labels=keys, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            ax.axis('equal')  # Equal aspect ratio ensures pie is circular
            
        else:
            print(f"WARNING: Unknown plot type '{plotType}', using 'bar' instead")
            ax.bar(keys, values, color=color, edgecolor='black', alpha=0.7)
            ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
            ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
        
        # Set title
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save as PDF
        plt.savefig(outputFilename, format='pdf', bbox_inches='tight', dpi=300)
        plt.close()
        
        print(f"✓ Plot saved successfully as '{outputFilename}'")
        
    except Exception as e:
        print(f"Error while creating plot: {e}")
        plt.close()
def plotDataComparison(data1: dict[str, float],
                       data2: dict[str, float],
                       outputFilename: str,
                       title: str = "Data Comparison",
                       xlabel: str = "Categories",
                       ylabel: str = "Values",
                       label1: str = "Data 1",
                       label2: str = "Data 2",
                       color1: str = 'steelblue',
                       color2: str = 'coral',
                       plotType: str = 'merged',
                       figsize: tuple = (14, 7)) -> None:
  
    if not data1 or not data2:
        print(f"WARNING: Empty datasets provided, no plot created for {title}")
        return
    
    # Ensure filename has .pdf extension
    if not outputFilename.endswith('.pdf'):
        outputFilename += '.pdf'
    
    try:
        # Extract keys and values
        keys = list(data1.keys())
        values1 = list(data1.values())
        values2 = [data2.get(k, 0) for k in keys]
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=figsize)
        
        if plotType == 'merged':
            # Bars for data1, line for data2
            ax.bar(keys, values1, color=color1, edgecolor='black',
                   alpha=0.5, label=label1, width=0.8)
            ax.plot(keys, values2, marker='o', color=color2,
                    linewidth=2.5, markersize=7, label=label2, zorder=10)
            
        elif plotType == 'bars':
            # Side-by-side bars
            x = np.arange(len(keys))
            width = 0.35
            ax.bar(x - width/2, values1, width, color=color1, edgecolor='black',
                   alpha=0.7, label=label1)
            ax.bar(x + width/2, values2, width, color=color2, edgecolor='black',
                   alpha=0.7, label=label2)
            ax.set_xticks(x)
            ax.set_xticklabels(keys, rotation=45, ha='right')
            
        elif plotType == 'lines':
            # Both as lines
            ax.plot(keys, values1, marker='o', color=color1,
                    linewidth=2.5, markersize=7, label=label1)
            ax.plot(keys, values2, marker='s', color=color2,
                    linewidth=2.5, markersize=7, label=label2)
            plt.xticks(rotation=45, ha='right')
            ax.grid(True, alpha=0.3)
            
        elif plotType == 'line_filled':
            # Line with filled area for data2
            ax.plot(keys, values2, marker='o', color=color2,
                    linewidth=2, markersize=6, label=label2)
            ax.fill_between(keys, values2, alpha=0.3, color=color2)
            ax.plot(keys, values1, marker='s', color=color1,
                    linewidth=2, markersize=6, label=label1, linestyle='--')
            plt.xticks(rotation=45, ha='right')
            ax.grid(True, alpha=0.3)
            
        else:
            print(f"WARNING: Unknown plot type '{plotType}', using 'merged' instead")
            ax.bar(keys, values1, color=color1, edgecolor='black',
                   alpha=0.5, label=label1, width=0.8)
            ax.plot(keys, values2, marker='o', color=color2,
                    linewidth=2.5, markersize=7, label=label2, zorder=10)
        
        # Set labels and title
        ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Add legend and adjust layout
        ax.legend(fontsize=11, loc='best')
        if plotType != 'line_filled':
            ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        # Save as PDF
        plt.savefig(outputFilename, format='pdf', bbox_inches='tight', dpi=300)
        plt.close()
        
        print(f"✓ Plot saved successfully as '{outputFilename}'")
        
    except Exception as e:
        print(f"Error while creating comparison plot: {e}")
        plt.close()


def createAverageDistribution(minValue: int, maxValue: int, criteriaValues: list[int]) -> dict[int, float]:
    if len(criteriaValues) == 0:
        return {i: 0.0 for i in range(minValue, maxValue + 1)}
    
    # Initialize map with zeros
    baseMap = {i: 0.0 for i in range(minValue, maxValue + 1)}
    
    # Count occurrences of each value
    for value in criteriaValues:
        # Only count values within the valid range
        if minValue <= value <= maxValue:
            baseMap[value] += 1.0
    
    # Normalize: divide by total count to get values in [0, 1]
    totalCount = len(criteriaValues)
    for key in baseMap:
        baseMap[key] /= totalCount
    
    return baseMap

def createGenreDistribution(genresValues:list[dict[str,int]]):
    baseMap = {genre:0 for genre in POSSIBLES_GENRES}
    nbTotalGenre = sum([len(genres) for genres in genresValues])
    for genres in genresValues:
        for genre in genres:
            baseMap[genre] += 1
    
    for genre in POSSIBLES_GENRES:
        baseMap[genre] /= nbTotalGenre
    
    return baseMap

def createBaseInfoMusicRange(musicsList:list[Music]):
    tempoMap = createAverageDistribution(MIN_TEMPO, MAX_TEMPO, [music.tempo for music in musicsList])
    valenceMap = createAverageDistribution(0, 100, [music.valence for music in musicsList])
    energyMap = createAverageDistribution(0, 100, [music.energy for music in musicsList])
    instrumentality = createAverageDistribution(0, 100, [music.instrumentality for music in musicsList])
    yearMap = createAverageDistribution(MIN_YEAR, MAX_YEAR, [music.year for music in musicsList])
    popularityMap = createAverageDistribution(0, 100, [music.popularity for music in musicsList])
    genreMap = createGenreDistribution([music.genres for music in musicsList])
    baseMaps = {
        "tempo": tempoMap,
        "valence": valenceMap,
        "energy": energyMap,
        "popularity": popularityMap,
        "instrumentality": instrumentality,
        "year": yearMap,
        "genres":genreMap,
    }
    return baseMaps


def plotRawVsSmoothedComparison(musicsList: list, outputFolder: str = "comparison_plots", merged: bool = False) -> None:

    if not musicsList:
        print("WARNING: Empty music list provided, no plots created")
        return
    
    # Create output folder if it doesn't exist
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
        print(f"✓ Created output folder: '{outputFolder}'")
    
    # Get raw (average) distributions
    baseMaps = createBaseInfoMusicRange(musicsList)
    
    # Get smoothed (Gaussian) distributions
    userTaste = createUserTaste(musicsList)
    smoothedMaps = userTaste.criteriaMaps
    
    criteriaToPlot = ['tempo', 'valence', 'energy', 'popularity', 'instrumentality', 'year','genres']
    
    print(f"\nCreating {'merged' if merged else 'separate'} comparison plots for {len(criteriaToPlot)} criteria...")
    
    # Create plots for each criterion
    for criterion in criteriaToPlot:
        if criterion not in baseMaps or criterion not in smoothedMaps:
            print(f"WARNING: Criterion '{criterion}' not found in maps, skipping...")
            continue
        
        config = criteriaConfig[criterion]
        rawData = baseMaps[criterion]
        smoothedData = smoothedMaps[criterion]
        
        if merged:
            plotDataComparison(
                data1=rawData,
                data2=smoothedData,
                outputFilename=os.path.join(outputFolder, f"{criterion}_comparison.pdf"),
                title=f"Distribution Brutes vs Lissées - {config['title']}",
                xlabel=config['xlabel'],
                ylabel=config['ylabel'],
                label1="Raw Average",
                label2="Gaussian Smoothed",
                color1=config['data1Color'],
                color2=config['data2Color'],
                plotType='merged'
            )

            
        else:
            plotDictToPDF(data=rawData,
                          outputFilename=os.path.join(outputFolder, f"{criterion}_raw.pdf"),
                          title=f"Distribution Brutes - {config['title']}",
                          xlabel=config["xlabel"],
                          ylabel=config["ylabel"],
                          figsize=(12,6),
                          color=config["data1Color"])
            
            plotDictToPDF(data=rawData,
                          outputFilename=os.path.join(outputFolder, f"{criterion}_smooth.pdf"),
                          title=f"Lissées - {config['title']}",
                          xlabel=config["xlabel"],
                          ylabel=config["ylabel"],
                          figsize=(12,6),
                          color=config["data2Color"])
            

def plotMusicScores(musicsList: list[Music], outputDirectory: str = ".") -> None:
    
    # Create output folder if it doesn't exist
    if not os.path.exists(outputDirectory):
        os.makedirs(outputDirectory)
        print(f"✓ Created output folder: '{outputDirectory}'")
    

    # Extract score lists
    tempoScoreMap = [music.scores["tempo"] for music in musicsList]
    valenceScoreMap = [music.scores["valence"] for music in musicsList]
    energyScoreMap = [music.scores["energy"] for music in musicsList]
    instrumentalityScoreMap = [music.scores["instrumentality"] for music in musicsList]
    yearScoreMap = [music.scores["year"] for music in musicsList]
    popularityScoreMap = [music.scores["popularity"] for music in musicsList]
    genreScoreMap = [music.scores["genres"] for music in musicsList]
    
    # Define score types with their data
    scoreTypes = {
        "tempo": tempoScoreMap,
        "valence": valenceScoreMap,
        "energy": energyScoreMap,
        "instrumentality": instrumentalityScoreMap,
        "year": yearScoreMap,
        "popularity": popularityScoreMap,
        "genres": genreScoreMap
    }
    
    # Create histogram for each score type
    for scoreType, scoreData in scoreTypes.items():
        # Create bins for histogram (0 to 1 with 0.1 intervals)
        bins = [i / 100 for i in range(101)] 
        
        # Count frequencies in each bin
        histogram, _ = np.histogram(scoreData, bins=bins)
        
        # Create data dictionary for plotting
        binLabels = [f"{bins[i]:.2f}-{bins[i+1]:.2f}" for i in range(len(bins) - 1)]
        histogramData = {binLabels[i]: int(histogram[i]) for i in range(len(binLabels))}
        
        # Create output filename
        outputFilename = f"{outputDirectory}/histogram_{scoreType}.pdf"
        
        # Plot and save
        plotDictToPDF(
            data=histogramData,
            outputFilename=outputFilename,
            title=f"Distribution des Scores - {scoreType.capitalize()}",
            xlabel="Score",
            ylabel="Nombre d'occurence",
            figsize=(25, 6),
            color='steelblue',
            plotType='bar'
        )

def computeStatsAndUserTaste(listMusics:list[Music],userTaste:UserTaste,outputFolder:str):
    if not listMusics:
        print("WARNING: Empty music list provided, no plots created")
        return
    
    # Create output folder if it doesn't exist
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
        print(f"✓ Created output folder: '{outputFolder}'")
    
    baseMap = createBaseInfoMusicRange(listMusics)
    tasteMaps = userTaste.criteriaMaps
    
    # Criteria to plot (excluding 'knowns', 'mode', and 'genre' as they need special handling)
    criteriaToPlot = ['tempo', 'valence', 'energy', 'popularity', 'instrumentality', 'year','genres']
    

    
    
    # Create plots for each criterion
    for criterion in criteriaToPlot:
        if criterion not in baseMap or  criterion not in tasteMaps:
            print(f"WARNING: Criterion '{criterion}' not found in maps, skipping...")
            continue

        config = criteriaConfig[criterion]
        baseData = baseMap[criterion]
        
        tasteData = tasteMaps[criterion]

        plotDataComparison(
                data1=baseData,
                data2=tasteData,
                outputFilename=f"{outputFolder}/{criterion}_Occurences_Taste.pdf",
                title=f"Moyenne des occurences vs Profil de la playlist - {config['title']}",
                xlabel=config['xlabel'],
                ylabel=config['ylabel'],
                label1="Moyenne des occurences",
                label2="Profil de la playlist",
                color1=config['data1Color'],
                color2=config['data2Color'],
                plotType='merged'
            )
        

def plotInteractiveHeatmap(df, downsampleFactor=1, outputFile="heatmap",outputFolder:str = "concordanceMatrices"):

    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
        print(f"✓ Created output folder: '{outputFolder}'")

    # Downsample data and labels
    if downsampleFactor > 1:
        downsampled = df.iloc[::downsampleFactor, ::downsampleFactor]
    else:
        downsampled = df
    
    # Get row and column labels
    rowLabels = downsampled.index.tolist()
    colLabels = downsampled.columns.tolist()
    
    # Create heatmap with labels
    fig = go.Figure(data=go.Heatmap(
        z=downsampled.values,
        x=colLabels,  # Column labels
        y=rowLabels,  # Row labels
        colorscale='Viridis',
        zmin=0, zmax=1,
        hovertemplate='<b>Row:</b> %{y}<br><b>Col:</b> %{x}<br><b>Value:</b> %{z:.3f}<extra></extra>',
        colorbar=dict(title="Concordance")
    ))
    
    fig.update_layout(
        title=f'Music Concordance Matrix ({df.shape[0]}x{df.shape[1]})',
        xaxis_title='Music (Column)',
        yaxis_title='Music (Row)',
        width=1200, 
        height=1000,
        # Important: allow labels to be visible when zooming
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=8),
            showticklabels=True
        ),
        yaxis=dict(
            tickfont=dict(size=8),
            showticklabels=True
        )
    )
    
    fig.write_html(f'{outputFolder}/{outputFile}.html')
    print(f"✓ Interactive heatmap saved as '{outputFile}'")

def plotMatrixDistribution(df, outputFile="distribution",outputFolder="concordanceMatrices"):

    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
        print(f"✓ Created output folder: '{outputFolder}'")


    values = df.values.flatten()
    roundedValues = np.round(values / 0.01) * 0.01
    bins = np.arange(0, 1.01, 0.01)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    counts, edges, patches = ax.hist(roundedValues, bins=bins, 
                                      color='steelblue', edgecolor='black', 
                                      linewidth=0.5, alpha=0.8)
    
    ax.set_title('Value Distribution (grouped by 0.01)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Value', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Set x-axis to show every 0.1
    ax.set_xticks(np.arange(0, 1.1, 0.1))
    
    plt.tight_layout()
    plt.savefig(os.path.join(outputFolder, f"{outputFile}.pdf"), dpi=300, format='pdf', bbox_inches='tight')
    plt.close()
    
    print(f"Distribution histogram saved as '{outputFile}.pdf'")
