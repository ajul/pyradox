import pyradox.load

parse_techs, get_techs = pyradox.load.load_functions('HoI3', 'technologies', 'technologies', mode="merge")

def get_tech_level(tech, year):
    if year < tech["start_year"]: return 0
    elif "max_level" not in tech.keys(): return 1
    else:
        result = 2 + (year - tech["first_offset"]) // tech["additional_offset"]
        result = max(0, result)
        result = min(tech["max_level"], result)
        return result
