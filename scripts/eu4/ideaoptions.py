intValues = (
    1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 33, 40, 50, 60, 75, 100, 150, 200,
    )

floatValues = (
    0.002, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.06, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.33, 0.4, 0.5, 0.6, 0.66, 0.75,
    1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0,
    )

# comments refer to normal value
bonusData = (
    ("(none)",                      1, (None, None)), # special
    ("accepted_culture_threshold",  -0.15, (-0.05, -0.2)), 
    ("adm_tech_cost_modifier",      -0.1, (-0.05, -0.25)), # unused
    ("advisor_cost",                -0.1, (-0.05, -0.25)),
    ("advisor_pool",                1, (1, 2)),
    ("ae_impact",                   -0.1, (-0.05, -0.25)),
    ("army_tradition",              0.5, (0.25, 1.0)), #0.5 to 0.1
    ("army_tradition_decay",        -0.01, (-0.005, -0.01)),
    ("artillery_cost",              -0.2, (-0.05, -0.33)),
    ("artillery_power",             0.1, (0.05, 0.33)),
    ("auto_explore_adjacent_to_colony", 4.0, (True, True)), # bool), cost 1/4
    ("blockade_efficiency",         1/3, (0.33, 0.33)), # Oman only
    ("build_cost",                  -0.2, (-0.05, -0.33)), #-0.1 to -0.2?
    #("build_power_cost",            -0.2, (-0.05, -0.33)), 
    ("caravan_power",                20, (10, 25)),
    ("cavalry_cost",                -0.2, (-0.05, -0.33)), 
    ("cavalry_power",               0.1, (0.05, 0.33)),
    # ("cb_on_government_enemies",    1.0, (True, True)), # obsolete
    ("cb_on_overseas",              1.0, (True, True)), # bool
    ("cb_on_primitives",            1.0, (True, True)), # bool
    ("cb_on_religious_enemies",     1.0, (True, True)), # bool
    ("church_power_modifier",       0.1, (0.05, 0.25)),
    ("colonists",                   1, (1, 1)),
    # ("colonist_time",               -1/3, (-0.1, -0.33)), # obsolete
    ("core_creation",               -0.15, (-0.1, -0.33)),
    ("culture_conversion_cost",     -0.15, (-0.1, -0.33)),
    ("defensiveness",               0.2, (0.1, 0.4)),
    ("development_cost",            -0.1, (-0.05, -0.2)),
    ("devotion",                    0.5, (0.25, 1.0)), 
    ("dip_tech_cost_modifier",      -0.1, (-0.05, -0.25)), # unused
    ("diplomatic_annexation_cost",  -0.15, (-0.1, -0.33)),
    ("diplomatic_reputation",       2, (1, 5)),
    ("diplomatic_upkeep",           2, (1, 3)),
    ("diplomats",                   1, (1, 1)),
    ("discipline",                  0.05, (0.02, 0.1)),
    ("discovered_relations_impact", -0.25, (-0.1, -0.25)),
    ("embargo_efficiency",          1/3, (0.1, 0.33)),
    ("enemy_core_creation",         1.0, (0.5, 2.0)),
    ("envoy_travel_time",           -0.5, (-0.1, -0.25)),
    # ("extra_manpower_at_religious_war", 2.0, (True, True)), # obsolete
    ("fabricate_claims_time",       -0.25, (-0.1, -0.25)),
    ("free_leader_pool",            1, (1, 1)),
    ("fort_maintenance_modifier",   -0.15, (-0.1, -0.25)),
    ("galley_cost",                 -0.2, (-0.1, -0.33)),
    ("galley_power",                0.2, (0.1, 0.5)), #?
    ("garrison_size",               0.1, (0.05, 0.25)),
    ("global_autonomy",             -0.05, (-0.05, -0.05)),
    ("global_colonial_growth",      25, (10, 50)), #?
    ("global_foreign_trade_power",  0.2, (0.05, 0.25)), # cost adjusted downwards
    ("global_manpower_modifier",    1/3, (0.05, 1.0)), # 0.2 to 0.5?
    ("global_garrison_growth",      0.1, (0.05, 0.2)), # UP?
    ("global_missionary_strength",  0.02, (0.01, 0.03)),
    ("global_heretic_missionary_strength",  0.03, (0.01, 0.05)),
    ("global_own_trade_power",      0.2, (0.05, 0.25)), 
    ("global_prov_trade_power_modifier", 0.2, (0.05, 0.25)),
    ("global_regiment_cost",        -0.1, (-0.05, -0.1)), #Poland only
    ("global_regiment_recruit_speed", -0.2, (-0.1, -0.25)), # Prussia only
   
    ("global_ship_cost",            -0.1, (-0.05, -0.1)),
    ("global_ship_recruit_speed",   -0.1, (-0.05, -0.1)),
    ("global_ship_repair",          0.2, (0.05, 0.33)),
    ("global_spy_defence",          0.25, (0.05, 0.5)),
    ("global_tariffs",              0.2, (0.05, 0.2)), # Spain only
    ("global_tax_modifier",         0.1, (0.05, 0.2)),
    ("global_trade_goods_size_modifier",     0.1, (0.05, 0.2)),
    ("global_trade_income_modifier", 0.1, (0.05, 0.2)),
    ("global_trade_power",          0.1, (0.05, 0.2)),
    ("global_unrest",               -1, (-1, -2)),
    ("heavy_ship_cost",             -0.2, (-0.1, -0.33)), # unused
    ("heavy_ship_power",            0.1, (0.05, 0.25)),
    ("heir_chance",                 0.5, (0.25, 1.0)),
    ("hostile_attrition",           1.0, (0.5, 1.0)),
    ("idea_claim_colonies",         1.0, (True, True)), # bool
    ("idea_cost",                   -0.1, (-0.05, -0.1)),
    ("imperial_authority",          0.1, (0.05, 0.25)), #split between 0.1 and 0.05
    ("improve_relation_modifier",   0.25, (0.1, 0.5)), 
    ("infantry_cost",               -0.2, (-0.1, -0.33)), #OP?
    ("infantry_power",              0.1, (0.05, 0.25)), # limit to 0.25
    ("inflation_action_cost",       -0.15, (-0.05, -0.25)),
    ("inflation_reduction",         0.1, (0.05, 0.1)), #split between 0.1 and 0.05
    ("interest",                    -1.0, (-0.5, -1)),
    ("justify_trade_conflict_time", -0.2, (-0.05, -0.2)),
    ("land_attrition",              -0.1, (-0.05, -0.25)),
    ("land_forcelimit_modifier",    0.25, (0.1, 0.5)), # few examples
    ("land_maintenance_modifier",   -0.15, (-0.1, -0.25)), # decrease cost?
    ("land_morale",                 0.1, (0.05, 0.25)),
    ("leader_land_fire",            1, (1, 1)),
    ("leader_land_shock",           1, (1, 1)),
    ("leader_land_manuever",        1, (1, 1)),
    ("leader_naval_fire",           2, (1, 1)),
    ("leader_naval_shock",          2, (1, 1)),
    ("leader_naval_manuever",       2, (1, 2)),
    ("leader_siege",                2/3, (1, 1)), # cost adjusted upwards
    ("legitimacy",                  1.0, (0.25, 1.0)),
    ("light_ship_cost",             -0.2, (-0.1, -0.33)),
    ("light_ship_power",            0.1, (0.05, 0.25)),
    ("loot_amount",                 0.1, (0.05, 0.25)),
    ("manpower_recovery_speed",     0.2, (0.1, 0.33)),
    ("may_explore",                 1.0, (True, True)), # bool
    ("may_force_march",             1.0, (True, True)), # bool
    ("may_infiltrate_administration", 1.0, (True, True)), #bool
    ("may_sabotage_reputation",     1.0, (True, True)), #bool
    ("may_sow_discontent",          1.0, (True, True)), #bool
    ("merc_maintenance_modifier",   -0.25, (-0.1, -0.25)),
    ("mercenary_cost",              -0.25, (-0.1, -0.25)),
    ("merchants",                   1, (1, 1)),
    ("merchant_steering_to_inland", 20, (10, 25)),
    ("migration_cooldown",          -0.2, (-0.05, -0.2)),
    ("mil_tech_cost_modifier",      -0.1, (-0.05, -0.2)),
    ("missionaries",                1, (1, 1)),
    ("monthly_fervor_increase",     0.25, (0.1, 0.5)), 
    ("naval_attrition",             -0.25, (-0.1, -0.25)), # few examples
    ("naval_forcelimit_modifier",   0.25, (0.1, 0.5)), # 0.25 or 0.5?
    ("naval_maintenance_modifier",  -0.25, (-0.1, -0.33)), # -0.2), -0.25), or -0.33?
    ("naval_morale",                0.2, (0.1, 0.5)),
    ("navy_tradition",              0.5, (0.25, 1.0)),
    ("navy_tradition_decay",        -0.01, (-0.005, -0.01)),
    ("no_cost_for_reinforcing",     2.0, (True, True)), # bool
    ("no_religion_penalty",         1.0, (True, True)), # bool
    # ("overseas_income",             0.2, (0.1, 0.3)), # obsolete
    ("papal_influence",             2, (1, 5)), # 2 or 3?
    ("possible_mercenaries",        0.5, (0.25, 1.0)),
    ("prestige",                    2.0, (0.5, 5.0)), # lower cost
    ("prestige_decay",              -0.02, (-0.01, -0.02)),
    ("prestige_from_land",          1.0, (0.5, 1.0)), # Naval only
    ("prestige_from_naval",         1.0, (0.5, 1.0)), # Offensive only
    ("privateer_efficiency",        0.2, (0.1, 0.33)),
    ("production_efficiency",       0.1, (0.05, 0.2)),
    ("province_trade_power_modifier", 0.15, (0.05, 0.2)),
    ("province_warscore_cost",      -0.2, (-0.05, -0.2)),
    ("range",                       0.25, (0.1, 0.33)), # 0.25 or 0.33?
    ("rebel_support_efficiency",    0.25, (0.1, 0.5)),
    ("recover_army_morale_speed",   0.05, (0.02, 0.1)),
    ("recover_navy_morale_speed",   0.05, (0.02, 0.1)),
    ("reduced_native_attacks",      1.0, (True, True)), # bool
    ("reduced_stab_impacts",        1.0, (True, True)), # bool
    ("reinforce_speed",             0.2, (0.1, 0.3)), # 0.15 to 0.30?
    ("relations_decay_of_me",       0.3, (0.1, 0.5)),
    ("religious_unity",             1/3, (0.2, 0.5)),
    ("republican_tradition",        0.005, (0.005, 0.01)), # cost adjusted upwards
    ("sea_repair",                  1.0, (True, True)), # bool
    ("ship_durability",             0.1, (0.05, 0.2)), # FIXME
    ("siege_ability",               0.1, (0.05, 0.2)),
    ("spy_offence",                 0.2, (0.1, 0.25)), # 0.1 to 0.25?
    ("stability_cost_modifier",     -0.1, (-0.05, -0.2)),
    ("technology_cost",             -0.05, (-0.02, -0.1)),
    ("tolerance_heathen",           2, (1, 4)),
    ("tolerance_heretic",           2, (1, 4)),
    ("tolerance_own",               2, (1, 4)),
    ("trade_efficiency",            0.075, (0.05, 0.15)), 
    ("trade_range_modifier",        0.25, (0.1, 0.5)), #0.20 or 0.25?
    ("trade_steering",              0.2, (0.05, 0.5)), # 0.1 to 0.25 ?
    ("transport_cost",              -0.2, (-0.1, -0.33)), # unused
    ("unjustified_demands",         -0.1, (-0.05, -0.25)), # Diplomatic only
    ("vassal_income",               0.2, (0.1, 0.5)), # 0.1 to 0.25 ?
    ("vassal_forcelimit_bonus",     0.25, (0.1, 0.5)),
    ("war_exhaustion",              -0.02, (-0.01, -0.05)), # Innovative only
    ("war_exhaustion_cost",         -0.2, (-0.1, -0.33)), # -0.1 to -0.2?
    ("years_of_nationalism",        -5, (-5, -10)),
    )

bonusTypes, bonusNormalValues, bonusRanges = zip(*bonusData)

nonPercentFloats = set([
    "army_tradition",
    "hostile_attrition",
    "inflation_reduction",
    "interest",
    "legitimacy",
    # "republican_tradition",
    "navy_tradition",
    "prestige",
    "war_exhaustion",
    ])

def isPercentBonus(bonusName):
    if bonusName in nonPercentFloats: return False
    if bonusName not in bonusTypes: print(bonusName)
    idx = bonusTypes.index(bonusName)
    lowerBound = bonusRanges[idx][0]
    return isinstance(lowerBound, float)

def isReversed(bonusName):
    idx = bonusTypes.index(bonusName)
    return bonusNormalValues[idx] < 0.0

disallowPositiveDuplicates = set([
    "hostile_attrition",
    ])

allowNegativeDuplicates = set([
    "artillery_cost",
    "cavalry_cost",
    "global_regiment_cost",
    "global_revolt_risk",
    "infantry_cost",
    "war_exhaustion",
    ])

def allowDuplicate(bonusType):
    normalValue = bonusNormalValues[bonusTypes.index(bonusType)]
    if normalValue > 0: return bonusType not in disallowPositiveDuplicates
    else: return bonusType in allowNegativeDuplicates

def isBeneficial(bonusName, value):
    if isinstance(value, bool):
        return True
    else:
        idx = bonusTypes.index(bonusName)
        normalValue = bonusNormalValues[idx]
        return (normalValue > 0) == (value > 0)

def generateOptions(bonusTypeIndex):
    bonusType, normalValue, valueRange = bonusData[bonusTypeIndex]

    if normalValue > 0:
        sign = 1
    else:
        sign = -1
    
    if valueRange[0] is None:
        options = ["(none): 0.00 point(s)"]
        values = [None]
        costs = [0.0]
    elif isinstance(valueRange[0], bool):
        cost = 1.0 / normalValue
        options = ["yes: %0.2f point(s)" % (cost,)]
        values = [True]
        costs = [cost]
    elif isinstance(valueRange[0], int):
        options = []
        values = []
        costs = []

        for value in intValues:
            if value < valueRange[0] * sign: continue
            if value > valueRange[1] * sign: continue
            
            cost = value / normalValue * sign
            options.append("%+d: %0.2f point(s)" % (value * sign, cost))
            values.append(value * sign)
            costs.append(cost)

        # negative option
        negValue = -values[0]
        negCost = -costs[0]
        negOption = "%+d: %0.2f point(s)" % (negValue, negCost)
        options = [negOption] + options
        values = [negValue] + values
        costs = [negCost] + costs
            
    else: # float
        options = []
        values = []
        costs = []

        for value in floatValues:
            if value < valueRange[0] * sign: continue
            if value > valueRange[1] * sign: continue

            cost = value / normalValue * sign

            if bonusType in nonPercentFloats:
                options.append("%+0.3f: %0.2f point(s)" % (value * sign, cost))
            else:
                options.append("%+0.1f%%: %0.2f point(s)" % (value * sign * 100.0, cost))
            values.append(value * sign)
            costs.append(cost)

        # negative option
        negValue = -values[0]
        negCost = -costs[0] * 0.5 # only returns half points
        if bonusType in nonPercentFloats:
            negOption = "%+0.3f: %0.2f point(s)" % (negValue, negCost)
        else:
            negOption = "%+0.1f%%: %0.2f point(s)" % (negValue * 100.0, negCost)
        options = [negOption] + options
        values = [negValue] + values
        costs = [negCost] + costs

    return options, values, costs

def getClosestValueIndex(values, target):
    if values[0] is True or values[0] is None: return 0
    
    difference = abs(values[0] - target)
    result = 0
    for i, value in enumerate(values):
        currDifference = abs(value - target)
        if currDifference < difference:
            difference = currDifference
            result = i
    return result
