import os
import pyradox.config
import pyradox.format
import pyradox.primitive
import pyradox.txt
import pyradox.yml

undefinedBonuses = set()

baseBonusValues = {
    "adm_tech_cost_modifier" : -0.1, # unused
    "advisor_cost" : -0.1,
    "advisor_pool" : 1,
    "army_tradition" : 1,
    "army_tradition_decay" : -0.01,
    "artillery_cost" : -0.1,
    "artillery_power" : 0.1,
    "auto_explore_adjacent_to_colony" : 2.0, # bool, cost 1/2
    "blockade_efficiency" : 0.33, #?
    "build_cost" : -0.2, #-0.1 to -0.2?
    "cavalry_cost" : -0.1,
    "cavalry_power" : 0.1,
    "cb_on_government_enemies" : 1.0, # bool
    "cb_on_overseas" : 1.0, # bool
    "cb_on_primitives" : 1.0, # bool
    "cb_on_religious_enemies" : 1.0, # bool
    "colonists" : 1,
    "colonist_time" : -0.33, # Expansion only
    "core_creation" : -0.15,
    "defensiveness" : 0.2,
    "dip_tech_cost_modifier" : -0.1, # unused
    "diplomatic_reputation" : 2,
    "diplomatic_upkeep" : 2,
    "diplomats" : 1,
    "discipline" : 0.1,
    "discovered_relations_impact" : -0.25,
    "embargo_efficiency" : 0.33,
    "enemy_core_creation" : 1.0,
    "extra_manpower_at_religious_war" : 1.0, # bool
    "fabricate_claims_time" : -0.25,
    "free_leader_pool" : 1,
    "galley_cost" : -0.2,
    "galley_power" : 0.2, #?
    "global_colonial_growth" : 25, #?
    "global_foreign_trade_power" : 0.1,
    "global_manpower_modifier" : 0.33, # 0.2 to 0.5?
    "global_garrison_growth" : 0.1,
    "global_missionary_strength" : 0.02,
    "global_own_trade_power" : 0.2,
    "global_prov_trade_power_modifier" : 0.2,
    "global_regiment_cost" : -0.1, #Poland only
    "global_regiment_recruit_speed" : -0.1, # Prussia only
    "global_revolt_risk" : -1,
    "global_ship_cost" : -0.1,
    "global_ship_recruit_speed" : -0.1,
    "global_spy_defence" : 0.25,
    "global_tariffs" : 0.1, # Spain only
    "global_tax_modifier" : 0.1,
    "global_trade_income_modifier" : 0.1,
    "global_trade_power" : 0.1,
    "heavy_ship_power" : 0.1,
    "heir_chance" : 0.5, #0.25 or 0.5?
    "hostile_attrition" : 1.0,
    "idea_claim_colonies" : 1.0, # bool
    "idea_cost" : -0.1,
    "imperial_authority" : 0.1, #split between 0.1 and 0.05
    "infantry_cost" : -0.2, #OP?
    "infantry_power" : 0.1,
    "inflation_action_cost" : -0.15,
    "inflation_reduction" : 0.1, #split between 0.1 and 0.05
    "interest" : -1.0,
    "land_attrition" : -0.1,
    "land_forcelimit_modifier" : 0.33, # few examples
    "land_maintenance_modifier" : -0.1,
    "land_morale" : 0.2, # 0.1 to 0.25? OP?
    "leader_fire" : 2/3, # adjusted upwards
    "leader_land_manuever" : 1,
    "leader_naval_manuever" : 2,
    "leader_shock" : 2/3, # adjusted upwards
    "leader_siege" : 2/3, # adjusted upwards
    "legitimacy" : 1.0,
    "light_ship_cost" : -0.2,
    "light_ship_power" : 0.1,
    "manpower_recovery_speed" : 0.2,
    "may_explore" : 1.0, # bool
    "may_force_march" : 1.0, # bool
    "may_infiltrate_administration" : 1.0, #bool
    "may_sabotage_reputation" : 1.0, #bool
    "may_sow_discontent" : 1.0, #bool
    "merc_maintenance_modifier" : -0.25,
    "mercenary_cost" : -0.25,
    "merchants" : 1,
    "mil_tech_cost_modifier" : -0.1, # Aristocratic only
    "missionaries" : 1,
    "naval_attrition" : -0.25,
    "naval_forcelimit_modifier" : 0.25, # 0.25 or 0.5?
    "naval_maintenance_modifier" : -0.25, # -0.2, -0.25, or -0.33?
    "naval_morale" : 0.2,
    "navy_tradition" : 1.0,
    "navy_tradition_decay" : -0.01,
    "no_cost_for_reinforcing" : 1.0, # bool
    "no_religion_penalty" : 1.0, # bool
    "overseas_income" : 0.2, #0.1 or 0.2?
    "papal_influence" : 2, # 2 or 3?
    "possible_mercenaries" : 1.0,
    "prestige" : 1.0,
    "prestige_decay" : -0.02,
    "prestige_from_land" : 1.0, # Naval only
    "prestige_from_naval" : 1.0, # Offensive only
    "production_efficiency" : 0.1,
    "range" : 0.25, # 0.25 or 0.33?
    "rebel_support_efficiency" : 0.25,
    "recover_army_morale_speed" : 0.05,
    "recover_navy_morale_speed" : 0.05,
    "reduced_native_attacks" : 1.0, # bool
    "reduced_stab_impacts" : 1.0, # bool
    "reinforce_speed" : 0.2, # 0.15 to 0.30?
    "relations_decay_of_me" : 0.3,
    "religious_unity" : 0.25,
    "republican_tradition" : 0.005, # adjusted upwards
    "sea_repair" : 1.0, # bool
    "spy_offence" : 0.2, # 0.1 to 0.25?
    "stability_cost_modifier" : -0.1,
    "technology_cost" : -0.05,
    "tolerance_heathen" : 2,
    "tolerance_heretic" : 2,
    "tolerance_own" : 2,
    "trade_efficiency" : 0.075, 
    "trade_range_modifier" : 0.25, #0.20 or 0.25?
    "trade_steering" : 0.2, # 0.1 to 0.25 ?
    "unjustified_demands" : -0.25, # Diplomatic only
    "vassal_income" : 0.2, # 0.1 to 0.25 ?
    "war_exhaustion" : -0.05, # Innovative only
    "war_exhaustion_cost" : -0.2, # -0.1 to -0.2?
    }

def computeBonusCost(bonusType, bonusValue):
    if bonusType in baseBonusValues:
        baseBonusValue = baseBonusValues[bonusType]
        if isinstance(bonusValue, bool): bonusValue = 1.0
        result = bonusValue / baseBonusValue
        if result < 0.0: print("Warning: bonus cost for %s below 0." % bonusType) 
        return result
    else:
        if bonusType not in undefinedBonuses:
            print("Undefined bonus %s" % bonusType)
            undefinedBonuses.add(bonusType)
        return 1.0

def computeGroupCost(groupName, tree):
    groupValue = 0.0
    # if "start" not in tree.keys(): groupValue += 2.0 # compensate for lack of traditions

    #print("== %s ==" %groupName)
    for ideaName, bonuses in tree.items():
        if ideaName in ("category", "trigger", "ai_will_do", "important", "free"): continue
        for bonusType, bonusValue in bonuses.items():
            bonusCost = computeBonusCost(bonusType, bonusValue)
            # if "USA" in groupName: print('%s %s %0.2f' % (bonusType, bonusValue, bonusCost))
            groupValue += bonusCost
    return groupValue
    
result = []

for _, data in pyradox.txt.parseDir(os.path.join(pyradox.config.basedirs['EU4'], 'common', 'ideas')):
    for groupName, tree in data.items():
        if "start" not in tree.keys(): continue
        result.append((computeGroupCost(groupName, tree), groupName))

result.sort(reverse=True)
for i, (cost, groupName) in enumerate(result):
    print("|-\n| %s || %0.2f || %d" % (groupName, cost, i+1))

# cannot into relevant: less than 7
# cannot into stronk: 7 to 9
# normal: 9 to 11
# stronk: 11 to 13
# stronker: 13 to 15
# uberstronk: 15 or more

# top picks
# * republican tradition
# * missionary strength
# * discipline
# * infantry power
# * land morale
# * diplomatic reputation
# * tech cost
# * core cost
# * stability cost
# * advisor pool?
