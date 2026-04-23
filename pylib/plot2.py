import matplotlib.pyplot as plt
import numpy as np
from sklearn.mixture import GaussianMixture

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

def gmm_threshold(arr):
    x = np.asarray(arr).reshape(-1, 1)
    gmm = GaussianMixture(n_components=2, covariance_type='full', random_state=0)
    gmm.fit(x)

    # Find the crossing point where the two component posteriors are equal
    xs = np.linspace(x.min(), x.max(), 4096).reshape(-1, 1)
    logp = gmm._estimate_weighted_log_prob(xs)  # shape (N,2)
    diff = logp[:, 0] - logp[:, 1]
    i = np.argmin(np.abs(diff))
    t = float(xs[i, 0])

    means = gmm.means_.flatten()
    if means[0] > means[1]:
        pass
    return t


arr = np.loadtxt("trace.txt", dtype=int)
real=np.loadtxt("address.txt", dtype=int)
real_trace=np.zeros(4096)
for i in range(128):
    real_trace[real[i]]+=1
print(arr.shape)
arr0=np.zeros([arr.shape[0]//2,arr.shape[1]])
arr1=np.zeros([arr.shape[0]//2,arr.shape[1]])
c=0
for i in range(arr.shape[0]):
    if(i%2==0):
        arr0[i//2]=arr[i+c]
    else:
        arr1[i//2]=arr[i+c]

# Compute the mean difference between even and odd trace rows
result=np.mean(arr0, axis=0)-np.mean(arr1, axis=0)

# Use a simple threshold: mean + 2 standard units above baseline
T=np.mean(result)+2
plt.plot(result)
plt.show()
exit()

acc=[]
for i in range(len(arr)):
    miss=0
    for j in range(2048):
        if(arr[i,j]>3):
            miss+=1
        if(arr[i,j+2048]<3):
            miss+=1
    acc.append(miss/4096)
plt.show()
print(np.mean(acc))
exit()
TP=0
TN=0
FP=0
FN=0

for i in range(4096):
    if real_trace[i] == 1 and exp_result[i] == 1:
        TP += 1
    elif real_trace[i] == 0 and exp_result[i] == 0:
        TN += 1
    elif real_trace[i] == 0 and exp_result[i] == 1:
        FP += 1
    elif real_trace[i] == 1 and exp_result[i] == 0:
        FN += 1

FNR=FN/(TP+FN)
FPR=FP/(TN+FP)
print(FNR, FPR)
