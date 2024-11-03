import numpy as np
import matplotlib.pyplot as plt

f = open('analysis\EventsPerCell_StandardMode.csv','r',encoding='UTF-8')

header = f.readline().strip().split(',')

data=[[] for _ in header]
k=2
for line in f:
    if line.strip()=='':
        break
    k+=1
    slices = line.strip().split(',')
    for i in range(len(header)):
        if slices[i]!='':
            data[i].append(int(slices[i]))
f.close()
    
fig,ax = plt.subplots(1,1)

for k in range(4):
    # Count the occurrences of each number
    counts = [data[k].count(m)/len(data[k]) for m in range(5)]

    # Generate x values for step plot (0, 1, 2, 3, 4)
    x = np.arange(len(counts))

    # Plot the stepwise graph
    ax.step(x, counts, where='mid', label=header[k], marker='o')
plt.xlabel('Number')
plt.ylabel('Count')
plt.legend()
plt.xticks(x)  # Ensure ticks are placed at each integer position
plt.grid(True)

plt.show()