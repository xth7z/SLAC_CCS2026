import matplotlib.pyplot as plt
import numpy as np

def sample(arr,sca,cache_size):
    l0=len(arr)
    l1=l0//sca
    arr_sca=[]
    for i in range(l1):
        arr_sca.append(cache_size-np.max(arr[i*sca:(i+1)*sca]))
    return arr_sca

def sample2(arr,sca):
    l0=len(arr)
    l1=l0//sca
    arr_sca=[]
    for i in range(l1):
        arr_sca.append(np.sum(arr[i*sca:(i+1)*sca]))
    return arr_sca


arr = np.loadtxt("trace.txt", dtype=int)    
print(arr.shape)
arr0=np.zeros([arr.shape[0]//2,arr.shape[1]])
arr1=np.zeros([arr.shape[0]//2,arr.shape[1]])
c=0
for i in range(arr.shape[0]):
    if(i%2==0):
        arr0[i//2]=arr[i+c]
    else:
        arr1[i//2]=arr[i+c]
result=np.mean(arr0, axis=0)-np.mean(arr1, axis=0)
plt.plot(result)
plt.show()
