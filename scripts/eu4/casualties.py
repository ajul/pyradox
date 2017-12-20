min_result = -2
die_size = 10
base_casualties = [4, 8, 12, 16, 20, 24, 32, 40, 50, 60, 70, 80, 90, 100, 100, 120]

mean_base_casualties = {}

def compute_mean_casualties(adv):
    total = 0
    for roll in range(die_size):
        result = adv + roll
        idx = result - min_result
        if idx < 0: idx = 0
        elif idx >= len(base_casualties): idx = len(base_casualties) - 1
        total += base_casualties[idx]
    return total / die_size

for i in range(min_result - die_size + 1, min_result + len(base_casualties)):
    mean_base_casualties[i] = compute_mean_casualties(i)

w = '{|class = "wikitable"\n'
w += '! Attacker advantage\n'

for i in range(min_result - die_size + 1, min_result + len(base_casualties)):
    w += '| %d\n' % i

w += '|-\n'
w += '! Mean base casualties\n'

for i in range(min_result - die_size + 1, min_result + len(base_casualties)):
    w += '| %0.1f\n' % mean_base_casualties[i]

w += '|-\n'
w += '! Marginal proportional increase\n'

for i in range(min_result - die_size + 1, min_result + len(base_casualties)):
    if i - 1 in mean_base_casualties:
        w += '| %0.1f%%\n' % (100.0 * (mean_base_casualties[i] / mean_base_casualties[i-1] - 1))
    else:
        w += '| 0.0%\n'

w += '|}\n'

print(w)
