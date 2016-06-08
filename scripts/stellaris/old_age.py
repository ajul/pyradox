result = 0.0
survival = 1.0
for year in range(1000):
    for month in range(12):
        survival *= (1.0 - 1.0e-4 * (year + month / 12.0))
        result += survival / 12.0

print(result)
