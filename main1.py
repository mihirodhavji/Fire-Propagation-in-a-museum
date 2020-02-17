from main import Problem
from main import solver
import probability
import sys
import time
start_time = time.time()
f2 = open("saida_pt.txt","w")
for i in range(1, len(sys.argv),1):
    f1 = open(sys.argv[i], "r")
    result = solver(f1)
    f2.write(""+ sys.argv[i] + str(result))
    f2.write("\n")
    f1.close()
f2.close()
finish_time = time.time()
print("--- %s seconds ---" % (finish_time - start_time))