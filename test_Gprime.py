
import mymodule
import matplotlib.pyplot as plt
import time
import numpy as np
import subprocess


if __name__ == "__main__":
    size=512
    stride=16
    groups=1
    
    subprocess.run(["sudo", "pmset", "displaysleepnow"])
    attacker = mymodule.Attacker()
    attacker.Gprime_build_evic_set()

    
    result=[]
    
    for i in range(500):
        for j in range(groups):
            attacker.Gprime()
            t=attacker.probe(True)

    attacker.print(4096,True)
    for i in range(1000):
        size=512
        for k in range(1):
            for j in range(groups):
                start=time.time()
                attacker.Gprime()
                end=time.time()
                attacker.gpu_read(0,512*(i%2))
                t=attacker.probe(True)
                result.append(t)
        attacker.print(4096,False)
    del attacker
    subprocess.run(["caffeinate", "-u", "-t", "1"])
    plt.plot(result)
    plt.show()