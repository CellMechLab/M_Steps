import numpy as np
import matplotlib.pyplot as plt
import ruptures as rpt
from scipy.signal import savgol_filter as savgol 

frame = 0
track = 1
intensity = 4
svm = 19

data = []
f = open('example.csv')
f.readline()
for line in f:
    elements = line.strip().split(',')    
    info = [int(elements[0]),int(float(elements[1])),float(elements[4]),int(float(elements[19]))]
    data.append(info)
data = np.array(data)
f.close()

def track(number):
    filter = data[:,1]==number
    time = data[:,0][filter]
    intensity = data[:,2][filter]
    return time,intensity

def svm():
    filter = data[:,3]==3
    tracks = set(data[:,1][filter])
    return tracks

stationary = list(svm())

noiselevel = 10
threshold = noiselevel

time,signal = track(stationary[0])

# detection
algo = rpt.Pelt(model="rbf").fit(signal)
result = algo.predict(pen=10)

# display
rpt.display(signal, result, result)
plt.show()