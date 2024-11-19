import numpy as np
from skimage.restoration import denoise_tv_chambolle
from scipy.signal import find_peaks

def track(number,data):
    filter = data[:,1]==number
    time = data[:,0][filter]
    intensity = data[:,2][filter]
    return time,intensity

def svm(data):
    filter = data[:,3]==3
    tracks = set(data[:,1][filter])
    return tracks

def openFile(filename):
    data = []
    f = open(filename)
    f.readline()
    for line in f:
        elements = line.strip().split(',')
        info = [int(elements[0]),int(float(elements[1])),float(elements[4]),int(float(elements[19]))]
        data.append(info)
    data = np.array(data)
    f.close()
    
    numbers = list(svm(data))
    
    tr = []
    for n in numbers:
        tr.append(track(n,data))

    return tr

def filter(y,win=11):
    return denoise_tv_chambolle(y,max_num_iter=200,weight=win)

def corners(sy,win=121):
    buffer = int((win-1)/2)
    x = np.zeros_like(sy)
    for i in range(buffer,len(sy)-buffer):
        delta = np.average(sy[i:i+buffer+1])-np.average(sy[i-buffer:i])
        x[i]=delta
    return x

def cliffs(dy,height,distance):
    return find_peaks(dy,height,distance=distance)

def delta(segments,jump):
    while True:        
        for j in range(len(segments)-1):
            yright = np.average(segments[j+1][1])
            yleft = np.average(segments[j][1])
            if np.abs(yright-yleft)<jump:
                x = np.append(segments[j][0],segments[j+1][0])
                y = np.append(segments[j][1],segments[j+1][1])
                segments[j]=([x,y,True])
                segments.pop(j+1)
                break
        else:
            break
    return segments

def create_steps(x,y,ppoints,npoints,memory=0):
    segments=[]
    corners = np.append(ppoints,npoints)
    corners.sort()
    up=False
    start = 0
    for k in corners:
        xsegment = x[start:k]
        ysegment = np.ones_like(xsegment)*np.average(y[start:k])
        segments.append([list(xsegment),list(ysegment),up])    
        up = not up
        start=k
    segments.append([list(x[start:]),list(y[start:]),up])
    if memory>0:
        segments = delta(segments,memory)
    return segments

def baseline(y):
    y10 = np.percentile(y,10)
    return y10
            
def count_steps(stats,baseline,isbaseline):
    if isbaseline is False:
        return len(stats)
    howmany = 0
    for s in stats:        
        if baseline-isbaseline<np.average(s[1])< baseline+isbaseline:
            howmany+=1
    return howmany

def intensity(stats,baseline = None,isbaseline=None):
    values = []
    for i in range(len(stats)):
        s = stats[i]
        if baseline is None:
            values.append(np.average(s[1]))
        else:
            if baseline-isbaseline<np.average(s[1])< baseline+isbaseline:
                values.append(np.average(s[1])-baseline)
    return values

def duration(stats,baseline,isbaseline):
    values = []
    for s in stats:
        if baseline-isbaseline<np.average(s[1])< baseline+isbaseline:
            values.append(s[0][-1]-s[0][0])
    return values