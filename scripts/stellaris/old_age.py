result = 0.0
survival = 1.0

year = 0

median = False

while survival > 0.0:
    if year <= 20:
        death_chance = year * 0.002
    else:
        death_chance = 20 * 0.002 + (year - 20) * 0.02 # in addition?
    death_chance = min(death_chance, 1.0)
    for month in range(12):
        survival *= (1.0 - death_chance)
        if survival < 0.5 and not median:
            median = True
            print(year, month)
        result += survival
    year += 1

print(int(result // 12), round(result % 12))
