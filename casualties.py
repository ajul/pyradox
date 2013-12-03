minResult = -2
dieSize = 10
baseCasualties = [4, 8, 12, 16, 20, 24, 32, 40, 50, 60, 70, 80, 90, 100, 100, 120]

meanBaseCasualties = {}

def computeMeanCasualties(adv):
    total = 0
    for roll in range(dieSize):
        result = adv + roll
        idx = result - minResult
        if idx < 0: idx = 0
        elif idx >= len(baseCasualties): idx = len(baseCasualties) - 1
        total += baseCasualties[idx]
    return total / dieSize

for i in range(minResult - dieSize + 1, minResult + len(baseCasualties)):
    meanBaseCasualties[i] = computeMeanCasualties(i)

w = '{|class = "wikitable"\n'
w += '! Attacker advantage\n'

for i in range(minResult - dieSize + 1, minResult + len(baseCasualties)):
    w += '| %d\n' % i

w += '|-\n'
w += '! Mean base casualties\n'

for i in range(minResult - dieSize + 1, minResult + len(baseCasualties)):
    w += '| %0.1f\n' % meanBaseCasualties[i]

w += '|-\n'
w += '! Marginal proportional increase\n'

for i in range(minResult - dieSize + 1, minResult + len(baseCasualties)):
    if i - 1 in meanBaseCasualties:
        w += '| %0.1f%%\n' % (100.0 * (meanBaseCasualties[i] / meanBaseCasualties[i-1] - 1))
    else:
        w += '| 0.0%\n'

w += '|}\n'

print(w)
