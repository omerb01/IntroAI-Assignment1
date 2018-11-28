import numpy as np
from matplotlib import pyplot as plt

X = np.array([400, 450, 900, 390, 550])

# TODO: Write the code as explained in the instructions

T = np.linspace(0.01,5,100)
P = np.zeros((100,5))
min_x=min(X)


for i in range(len(X)) :
    for t in range(len(T)):
        sum = 0
        for j in range(len(X)):
            sum += np.power(X[j]/min_x,((-1)/T[t]))
        probability = np.power(X[i]/min_x,((-1)/T[t]))/sum
        P[t][i]=probability
print(P)

for i in range(len(X)):
    plt.plot(T, P[:, i], label=str(X[i]))


plt.xlabel("T")
plt.ylabel("P")
plt.title("Probability as a function of the temperature")
plt.legend()
plt.grid()
plt.show()
exit()
