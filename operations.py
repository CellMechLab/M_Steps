import numpy as np
from scipy.signal import savgol_filter as savgol 

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

def steps(x,sy):
    baseline = np.median(sy)
    thresh = baseline+np.std(sy)
    up = False
    if sy[0]>thresh:
        up=True
    segments = []
    segment = [sy[0]]
    xsegment=[x[0]]
    for i in range(1,len(sy)):
        cur = sy[i]>thresh
        if cur is up:
            segment.append(sy[i])
            xsegment.append(x[i])    
        else:            
            segments.append([xsegment,segment,up])
            up = cur
            segment=[sy[i]]
            xsegment=[x[i]]
        
    segments.append([list(xsegment),list(segment),up])
    return segments

def fuse(steps,delta):
    newsteps=[]
    jjj=0
    while(jjj<len(steps)):    
        if len(steps[jjj][0])>delta:
            newsteps.append(steps[jjj])
            break
        jjj+=1
    jjj+=1
    while(jjj<len(steps)):    
        xi,yi,post= steps[jjj]
        xold,yold,pre = newsteps[-1]
        if len(xi)<delta:
            if jjj==len(steps)-1:
                if post == False:
                    newsteps.append([xi,yi,False])
                jjj+=1
            else:
                fxi = np.append(np.append(xold,xi),steps[jjj+1][0])
                fyi = np.append(np.append(yold,yi),steps[jjj+1][1])
                newsteps[-1]=[list(fxi),list(fyi),pre]
                jjj+=2            
        else:
            newsteps.append([list(xi),list(yi),post])  
            jjj+=1                  
    return newsteps

def flatten(stx):
    flat=[]
    for st in stx:
        flat.append([st[0],np.average(st[1])*np.ones_like(st[0]),st[2]])
    return flat

def create_steps(x,y,win=101,dth=0.1,memory=100):
    dy = savgol(y,win,1,1)        
    sy = savgol(y,win,1)
    if max(np.abs(dy))<dth:
        return [[x,np.median(sy)*np.ones_like(sy),False]]
    stx = steps(x,sy)
    stx = fuse(stx,memory)    
    return flatten(stx)

def count_steps(stats):
    howmany = 0
    for s in stats:
        if s[2] == True:
            howmany+=1
    return howmany

def intensity(stats,relative = False):
    values = []
    for i in range(len(stats)):
        s = stats[i]
        if s[2] == True:
            if relative is False:
                values.append(s[1][0])
            else:
                if i==0:
                    baseline = stats[i+1][1][0]
                elif i==len(stats)-1:
                    baseline = stats[i-1][1][0]
                else:
                    baseline = (stats[i-1][1][0]+stats[i+1][1][0])/2
                values.append(s[1][0]-baseline)
    return values

def duration(stats):
    values = []
    for s in stats:
        if s[2] == True:
            values.append(s[0][-1]-s[0][0])
    return values