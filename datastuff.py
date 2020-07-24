import helpData as hd
import pandas as pd
import ast
import csv
import matplotlib.pyplot as plt
import copy
import hunger as h

def linearRunGraph(filename, param, n_steps, cautiousFile=None):
    labelsize = 18
    legendsize = 14
    titlesize = 20
    ticksize = 16

    data = pd.read_csv(filename)
    plt.style.use('ggplot')
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
        
    df0 = hd.filterDataFrame(data, [["targetedAware", True], ["proximityAware", True]])
    df1 = hd.filterDataFrame(data, [["targetedAware", False], ["proximityAware", True]])
    df2 = hd.filterDataFrame(data, [["targetedAware", False], ["proximityAware", False]])

    dfs = [df0, df1, df2]

    modes = [r"Proximity + Attention", r"Proximity Only", r"Unaware"]

    if cautiousFile:
        df3 = pd.read_csv(cautiousFile)
        dfs.append(df3)
        modes.append(r"Cautious")

    colorIter = iter(['#4FADAC', '#5386A6', '#2F5373', '#C59CE6'])
    
    fig = plt.figure(figsize=(5,5))

    for i in range(3 + (cautiousFile != None)):
        df = dfs[i]
        paramValues = []
        survival = []
        up_ci = []
        low_ci = []

        for val, group in df.groupby(param):
            groupLifeTimes = []
            for index, run in group.iterrows():
                counts = run["preyCountOverTime"]
                foodPerPrey = run["foodPerPrey"]
                preyPerPred = run["preyPerPred"]
                revisedCounts, preyStarved = h.getNewPreyCountOverTimeList(foodPerPrey, counts, preyPerPred, n_steps)
                lifetimes = hd.lifeTimes(revisedCounts)
                groupLifeTimes += lifetimes
            
            avg, std, ci = hd.listStats(groupLifeTimes)

            paramValues.append(val)
            survival.append(avg)
            low_ci.append(ci[0])
            up_ci.append(ci[1])

        color = next(colorIter)
        plt.plot(paramValues, survival, label=modes[i], color=color, linewidth=2)
        plt.fill_between(paramValues, low_ci, up_ci, color=color, alpha=.15)
    
    ax = fig.gca()
    ax.set(ylim=(0, 10000))
    ax.set_ylabel(r"prey lifespan (time steps)", fontsize=labelsize, fontweight='bold')
    ax.set_xlabel(r"ppr", fontsize=labelsize, fontweight='bold')
    ax.tick_params(axis='both', which='major', labelsize=ticksize, direction='in')
    plt.legend(prop={"size":legendsize})
    plt.title(r"ppr " + str(n_steps), fontsize=titlesize, fontweight='bold')
    fig.tight_layout()
    fig.savefig(param + str(n_steps), bbox_inches='tight', pad_inches=0)
    plt.close('all')


def hungerGraph(filename, cautiousFile=None):

    labelsize = 18
    legendsize = 14
    titlesize = 20
    ticksize = 16

    data = pd.read_csv(filename)
    plt.style.use('ggplot')
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
        
    df0 = hd.filterDataFrame(data, [["targetedAware", True], ["proximityAware", True], ["predSightAngle", 90]])
    df1 = hd.filterDataFrame(data, [["targetedAware", False], ["proximityAware", True], ["predSightAngle", 90]])
    df2 = hd.filterDataFrame(data, [["targetedAware", False], ["proximityAware", False], ["predSightAngle", 90]])

    dfs = [df0, df1, df2]
    modes = [r"Proximity + Attention", r"Proximity Only", r"Unaware"]

    colorIter = iter(['#4FADAC', '#5386A6', '#2F5373', '#C59CE6'])

    intention_list = []
    proximity_list = []
    unaware_list = []
    all_lists = [intention_list, proximity_list, unaware_list]

    if cautiousFile:
        dfs.append(pd.read_csv(cautiousFile))
        modes.append(r"Cautious")
        cautious_list = []
        all_lists.append(cautious_list)

    fig = plt.figure(figsize=(5,5))
    
    x = [step for step in range(1, 10000+2, 500)]
    for n_steps in x:
        print("step:",n_steps)
        for i in range(3 + (cautiousFile != None)):
            df = dfs[i]
            groupLifeTimes = []
            for index, run in df.iterrows():
                counts = run["preyCountOverTime"]
                foodPerPrey = run["foodPerPrey"]
                preyPerPred = run["preyPerPred"]
                revisedCounts, preyStarved = h.getNewPreyCountOverTimeList(foodPerPrey, counts, preyPerPred, n_steps)
                lifetimes = hd.lifeTimes(revisedCounts)
                groupLifeTimes += lifetimes
            avg, std, ci = hd.listStats(groupLifeTimes)
            all_lists[i].append([avg, ci[0], ci[1]])

    for i in range(len(all_lists)):
        tier = all_lists[i]
        val = []
        l_ci = []
        u_ci = []
        for point in tier:
            a, lc, uc = point
            val.append(a)
            l_ci.append(lc)
            u_ci.append(uc)
        
        color = next(colorIter)
        fig.gca().plot(x, val, label=modes[i], color=color, linewidth=2)
        fig.gca().fill_between(x, l_ci, u_ci, color=color, alpha=.15)
    
    ax = fig.gca()
    ax.set(ylim=(0, 10000), xlim=(0,10000-1))
    ax.set_ylabel(r"prey lifespan (time steps)", fontsize=labelsize, fontweight='bold')
    ax.set_xlabel(r"maximum fasting interval (time steps)", fontsize=labelsize, fontweight='bold')
    ax.tick_params(axis='both', which='major', labelsize=ticksize, direction='in')
    plt.legend(prop={"size":legendsize})
    plt.title(r"Maximum Fasting Interval", fontsize=titlesize, fontweight='bold')
    fig.savefig("hunger", bbox_inches='tight', pad_inches=0)
    plt.close('all')

def getCautiousSeedData(filename, newfilename, param):
    data = pd.read_csv(filename)
    df = hd.filterDataFrame(data, [["targetedAware", True], ["proximityAware", True]])
    paramDict = {}
    for val, group in df.groupby(param):
        groupProbs = []
        groupLengths = []
        for i, run in group.iterrows():
            probs, lengths = ast.literal_eval(run["targetInfo"])
            groupProbs += probs
            groupLengths += lengths
        avg, std, ci = hd.listStats(groupProbs)
        paramDict[str(val)] = [avg, groupLengths]
    with open(newfilename, 'w', newline='') as csvfile:
        fieldnames = ["val", "hist"]
        writer = csv.writer(csvfile)
        writer.writerow(["keys", "values"])
        for key, value in paramDict.items():
            writer.writerow([key, value])


#linearRunGraph("cpreysd.csv", "preySightDistance", 10000, cautiousFile="cpysd.csv")
#linearRunGraph("cpredsd.csv", "predSightDistance", 10000, cautiousFile="cpdsd.csv")
#linearRunGraph("cpredsa.csv", "predSightAngle", 10000, cautiousFile="cpdsa.csv")
linearRunGraph("cppratio.csv", "preyPredRatio", 4000, cautiousFile="cppr.csv")
#linearRunGraph("cspdfrac.csv", "speedFrac", 10000, cautiousFile="cspd.csv")
#hungerGraph("cpredsa.csv", "cpdsa.csv")

for steps in range(1000, 10000+1, 1000):
    linearRunGraph("cppratio.csv", "preyPredRatio", steps, cautiousFile="cppr.csv")
    print(steps, "done")
