## Optimal Wind+Hydrogen+Other+Battery+Solar Electricity Systems for European countries
#
#Required data:
#
#i) Solar time series "ninja_pv_europe_v1.1_sarah.csv" from "PV v1.1 Europe" https://www.renewables.ninja/downloads
#
#ii) Wind time series "ninja_wind_europe_v1.1_current_on-offshore.csv" from "Wind v1.1 Europe" https://www.renewables.ninja/downloads

## Copyright 2018 Tom Brown (KIT)

## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
## License, or (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.



import pypsa

import pandas as pd

idx = pd.IndexSlice

from pyomo.environ import Constraint

#read in renewables.ninja solar time series
solar_pu = pd.read_csv('ninja_pv_europe_v1.1_sarah.csv',
                       index_col=0,parse_dates=True)

#read in renewables.ninja wind time series
wind_pu = pd.read_csv('ninja_wind_europe_v1.1_current_on-offshore.csv',
                       index_col=0,parse_dates=True)

def annuity(lifetime,rate):
    if rate == 0.:
        return 1/lifetime
    else:
        return rate/(1. - 1. / (1. + rate)**lifetime)


add_hydrogen = True

def prepare_assumptions(Nyears=1,usd_to_eur=1/1.2,assumptions_year=2020):
    """set all asset assumptions and other parameters"""

    assumptions = pd.read_csv("assumptions.csv",index_col=list(range(3))).sort_index()

    #correct units to MW and EUR
    assumptions.loc[assumptions.unit.str.contains("/kW"),"value"]*=1e3
    assumptions.loc[assumptions.unit.str.contains("USD"),"value"]*=usd_to_eur

    assumptions = assumptions.loc[idx[:,assumptions_year,:],"value"].unstack(level=2).groupby(level="technology").sum(min_count=1)

    #fill defaults
    assumptions = assumptions.fillna({"FOM" : assumptions.at["default","FOM"],
                                      "discount rate" : assumptions.at["default","discount rate"],
                                      "lifetime" : assumptions.at["default","lifetime"]})

    #annualise investment costs, add FOM
    assumptions["fixed"] = [(annuity(v["lifetime"],v["discount rate"])+v["FOM"]/100.)*v["investment"]*Nyears for i,v in assumptions.iterrows()]

    return assumptions

def solve_network(ct,scenario):

    #years for weather data (solar is 1985-2015 inclusive, wind is 1980-2016)
    year_start = snakemake.config['year_start']
    year_end = snakemake.config['year_end']

    Nyears = year_end - year_start + 1

    assumptions_year = int(scenario[:4])

    assumptions = prepare_assumptions(Nyears=Nyears,
                                      assumptions_year=assumptions_year)

    if "steel_tanks" in scenario:
        assumptions.loc["H2 storage"] = assumptions.loc["H2 steel tank storage"]
    else:
        assumptions.loc["H2 storage"] = assumptions.loc["H2 underground storage"]

    print(assumptions)

    frequency = snakemake.config['frequency']

    network = pypsa.Network()

    snapshots = pd.date_range("{}-01-01".format(year_start),"{}-12-31 23:00".format(year_end),
                              freq=str(frequency)+"H")

    network.set_snapshots(snapshots)

    network.snapshot_weightings = pd.Series(float(frequency),index=network.snapshots)

    network.add("Bus",ct)
    network.add("Load",ct,
                bus=ct,
                p_set=snakemake.config['load'])

    network.add("Generator",ct+" solar",
                bus=ct,
                p_max_pu = solar_pu[ct],
                p_nom_extendable = True,
                marginal_cost = 0.01, #Small cost to prefer curtailment to destroying energy in storage, solar curtails before wind
                capital_cost = assumptions.at['utility solar PV','fixed'])

    network.add("Generator",ct+" wind",
                bus=ct,
                p_max_pu = wind_pu[ct+"_ON"],
                p_nom_extendable = True,
                marginal_cost = 0.02, #Small cost to prefer curtailment to destroying energy in storage, solar curtails before wind
                capital_cost = assumptions.at['onshore wind','fixed'])

    network.add("Bus",ct + " battery")

    network.add("Store",ct + " battery storage",
                bus = ct + " battery",
                e_nom_extendable = True,
                e_cyclic=True,
                capital_cost=assumptions.at['battery storage','fixed'])

    network.add("Link",ct + " battery charge",
                bus0 = ct,
                bus1 = ct + " battery",
                efficiency = assumptions.at['battery inverter','efficiency'],
                p_nom_extendable = True,
                capital_cost=assumptions.at['battery inverter','fixed'])

    network.add("Link",ct + " battery discharge",
                bus0 = ct + " battery",
                bus1 = ct,
                p_nom_extendable = True,
                efficiency = assumptions.at['battery inverter','efficiency'])

    def extra_functionality(network,snapshots):
        def battery(model):
            return model.link_p_nom[ct + " battery charge"] == model.link_p_nom[ct + " battery discharge"]*network.links.at[ct + " battery charge","efficiency"]

        network.model.battery = Constraint(rule=battery)

    if add_hydrogen:

        network.add("Bus",
                     ct + " H2",
                     carrier="H2")

        network.add("Link",
                    ct + " H2 electrolysis",
                    bus1=ct + " H2",
                    bus0=ct,
                    p_nom_extendable=True,
                    efficiency=assumptions.at["H2 electrolysis","efficiency"],
                    capital_cost=assumptions.at["H2 electrolysis","fixed"])

        network.add("Link",
                     ct + " H2 to power",
                     bus0=ct + " H2",
                     bus1=ct,
                     p_nom_extendable=True,
                     efficiency=assumptions.at["H2 CCGT","efficiency"],
                     capital_cost=assumptions.at["H2 CCGT","fixed"]*assumptions.at["H2 CCGT","efficiency"])  #NB: fixed cost is per MWel

        network.add("Store",
                     ct + " H2 storage",
                     bus=ct + " H2",
                     e_nom_extendable=True,
                     e_cyclic=True,
                     capital_cost=assumptions.at["H2 storage","fixed"])

    solver_name = "gurobi"

    if solver_name == "gurobi":
        solver_options = {"threads" : 4,
                          "method" : 2,
                          "crossover" : 0,
                          "BarConvTol": 1.e-5,
                          "FeasibilityTol": 1.e-6 }
    else:
        solver_options = {}


    network.consistency_check()

    network.lopf(solver_name=solver_name,
                 solver_options=solver_options,
                 extra_functionality=extra_functionality)

    network.export_to_netcdf(snakemake.output[0])

    return network

if __name__ == "__main__":

    # Detect running outside of snakemake and mock up snakemake for testing
    if 'snakemake' not in globals():
        from pypsa.descriptors import Dict
        import yaml

        snakemake = Dict()

        with open('config.yaml') as f:
            snakemake.config = yaml.load(f)

        snakemake["wildcards"] = Dict({ "country" : "DE",
                                        "scenario" : "2020"})

        snakemake["output"] = ["results/{}-{}.nc".format(snakemake.wildcards.country,
                                                         snakemake.wildcards.scenario)]

    network = solve_network(snakemake.wildcards.country,
                            snakemake.wildcards.scenario)
