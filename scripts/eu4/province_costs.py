import math

def provinceCost(province):
    cost = 0
    if 'base_tax' in province:
        if 'trade_goods' in province and province['trade_goods'] == 'gold':
            cost += 4 * province['base_tax']
        else:
            cost += province['base_tax']
            
    if 'manpower' in province:
        cost += province['manpower']

    if 'extra_cost' in province:
        cost += province['extra_cost']

    if cost > 0:
        return math.floor(cost)
    else:
        return None
