import sys
import csv
from os import listdir
from os.path import isfile, join
from decimal import Decimal

solsDir = "./sols/"
dest = "./forCalc/"
solutions = [solsDir + f for f in listdir(solsDir) if ".csv" in f]

def getConfigs(type):
    translateArray = []
    if type == "light":
        translateArray = [
            ["./data/divisions/B_heuristic_depth1_001_050_div_10_20_30_40_50/B_heuristic_depth1_001_050_001_010.csv", 0, 10],
            ["./data/divisions/B_heuristic_depth1_001_050_div_10_20_30_40_50/B_heuristic_depth1_001_050_011_020.csv", 10, 20],
            ["./data/divisions/B_heuristic_depth1_001_050_div_10_20_30_40_50/B_heuristic_depth1_001_050_021_030.csv", 20, 30],
            ["./data/divisions/B_heuristic_depth1_001_050_div_10_20_30_40_50/B_heuristic_depth1_001_050_031_040.csv", 30, 40],
            ["./data/divisions/B_heuristic_depth1_001_050_div_10_20_30_40_50/B_heuristic_depth1_001_050_041_050.csv", 40, 50]
        ] 
    if type == "heavy" or type == "heavy3":
        translateArray = [
            ["./data/divisions/B_heuristic_depth1_001_500_div_100_200_300_400_500/B_heuristic_depth1_001_500_001_100.csv", 0, 100],
            ["./data/divisions/B_heuristic_depth1_001_500_div_100_200_300_400_500/B_heuristic_depth1_001_500_101_200.csv", 100, 200],
            ["./data/divisions/B_heuristic_depth1_001_500_div_100_200_300_400_500/B_heuristic_depth1_001_500_201_300.csv", 200, 300],
            ["./data/divisions/B_heuristic_depth1_001_500_div_100_200_300_400_500/B_heuristic_depth1_001_500_301_400.csv", 300, 400],
            ["./data/divisions/B_heuristic_depth1_001_500_div_100_200_300_400_500/B_heuristic_depth1_001_500_401_500.csv", 400, 500]
        ] 
    
    return translateArray

def getFirstForm(configs):
    configs = getConfigs(type)
    firstForm = {}

    for config in configs:
        firstForm[config[0]] = range(config[1], config[2])
    return firstForm

def printResult(configs, basicModel, finalModel, writePath):
    with open(writePath, 'w+') as csvFile:
        writer = csv.writer(csvFile)
        for config in configs:
            row = []
            row.append(config[0])
            row.append("-".join(map(str, basicModel[config[0]])))
            row.append("-".join(map(str, finalModel[config[0]])))
            row.append(1)
            writer.writerow(row)

if len(sys.argv)!=2:
    print('useage: \"python3 FullMigrationSolToCalc.py <fileType>\"')
    exit()

fileType = sys.argv[1]

if(fileType=="ILP"):
    for solutionPath in solutions:
        solution = solutionPath.split("/")[-1]
        type = solution.split("_")[1]
        configs = getConfigs(type)
        
        basicModel = getFirstForm(configs)
        finalModel = getFirstForm(configs)
        with open(solutionPath, 'r') as csvFile:
        
            csvReader = csv.reader(csvFile)
            for row in csvReader:
                if "->" not in row[0]:
                    break
                fileSn = int(row[0].split(":")[0])
                sourceVolume = int(row[0].split(":")[1].split("->")[0])
                targetVolume = int(row[0].split("->")[1])
                finalModel[configs[int(sourceVolume)][0]].remove(int(fileSn))
                finalModel[configs[int(targetVolume)][0]].append(int(fileSn))
        printResult(configs, basicModel, finalModel, dest + solution)

if(fileType=="Greedy"):
    for solutionPath in solutions:
        solution = solutionPath.split("/")[-1]
        type = solution.split("_")[0]
        configs = getConfigs(type)
        
        basicModel = getFirstForm(configs)
        finalModel = getFirstForm(configs)
        with open(solutionPath, 'r') as csvFile:
            csvReader = csv.reader(csvFile)
            next(csvFile)
            for row in csvReader:
                fileSn = int(row[3])
                sourceVolume = int(row[1])
                targetVolume = int(row[2])
                finalModel[configs[int(sourceVolume)][0]].remove(int(fileSn))
                finalModel[configs[int(targetVolume)][0]].append(int(fileSn))
        printResult(configs, basicModel, finalModel, dest + solution)




# def getBasic(solution):
#     type = solution.split("_")[1]
#     if type == "light":
#         light = {}
#         splitSize = 10
#         splitIndex = 0
#         splitCount = 0
#         for i in range(50):
#             splitCount += 1
#             if(splitCount == splitSize):
#                 splitIndex += 1
#                 splitCount = 0
#             light[i] = splitIndex
#         return light

# def translateToCalc(solution, finalForm):
#     finalForCalc = {}
#     for fileSn in finalForm:
#         path = volumeToPath(solution, finalForm[fileSn])
#         if path not in finalForCalc:
#             finalForCalc[path] = []
#         finalForCalc[path].append(fileSn)
#     return finalForCalc

# for solution in solutions:
#     sol = solution.split("/")[-1]
#     baseForm = getBasic(sol)
#     finalForm = getBasic(sol)
    
#     f_csv = csv.reader(solution)
#     for row in f_csv:
#         if "->" not in row[0]:
#             break
#         fileSn = int(row[0].split(":")[0])
#         targetVolume = int(row[0].split("->")[1])
#         finalForm[fileSn] = targetVolume

#     for fileSn in baseForm:
#         sys.stdout.write(str(fileSn) + "-"),
#     print("")
#     print("")
#     print("")
#     finalForCalc = translateToCalc(sol, finalForm)
#     for path in finalForCalc:
#         print(path)
#         for fileSn in finalForCalc[path]:
#             sys.stdout.write(str(fileSn) + "-"),