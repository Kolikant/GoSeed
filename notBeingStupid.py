import sys
import csv

if len(sys.argv)!=1:
    print('useage: \"python3 notBeingStupid.py\"')
    exit()

filesInOrder = [
    "k_10_001_500_k10_151_075_",
    "k_10_001_500_k10_051_075_",
    "k_10_001_500_k10_331_340_",
    "k_10_001_500_k10_061_070_",
    "k_10_001_500_k10_271_280_",
    "k_10_001_500_k10_351_400_",
    "k_10_001_500_k10_001_200_"
    ]

Traffics_Migrations = [
    "10_5",
    "15_10",
    "20_10",
    "20_15",
    "20_5",
    "25_10",
    "25_15",
    "25_20",
    "25_5",
    "30_10",
    "30_15",
    "30_20",
    "30_25",
    "30_5",
    "40_10",
    "40_15",
    "40_20",
    "40_25",
    "40_30",
    "40_5",
    "50_10",
    "50_15",
    "50_20",
    "50_25",
    "50_30",
    "50_5",
    "60_10",
    "60_15",
    "60_20",
    "60_25",
    "60_30",
    "60_5",
    "70_10",
    "70_15",
    "70_20",
    "70_25",
    "70_30",
    "70_5",
]

for Traffic_Migration in Traffics_Migrations:
    resultFile = "file_to_move_UBC_GoSeedBlocksArielB_heuristic_depth1_k10_001_500.csv_june2020_depth1_cont.csvcocos8_" + Traffic_Migration + "_write_solution_8_21600_10_38_4194304_1_k10_001.csv"
    with open(resultFile, 'r') as f:
        f_csv = csv.reader(f)
        order = 0
        data = []
        for row in f_csv:
            if len(row) > 0 and not str.isdigit(row[0]):
                if len(data)!=0 and data[0] != []:
                    with open('./' + filesInOrder[order] + Traffic_Migration + ".csv", 'w+') as f2:
                        writer = csv.writer(f2)
                        for i in range(int(len(data))):
                            writer.writerow(data[i])
                    order = order + 1
                data = []
                continue
            data.append(row)
