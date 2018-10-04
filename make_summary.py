import pypsa

import pandas as pd

def make_csv():

    scenarios = snakemake.config["run_settings"]["scenario"]

    columns = pd.MultiIndex.from_product((scenarios,
                            snakemake.config["run_settings"]["country"]),
                           names=["scenario","country"])

    stats = pd.DataFrame(columns=columns,dtype=float)

    for scenario in scenarios:
        for ct in snakemake.config["run_settings"]["country"]:
            print(scenario,ct)
            network = pypsa.Network("{}{}-{}.nc".format(snakemake.config["results_dir"],ct,scenario))
            stats.at["cost",(scenario,ct)] = network.buses_t.marginal_price.mean()[ct]

            for g in ["wind","solar"]:
                stats.at[g,(scenario,ct)] = network.generators.p_nom_opt[ct + " " + g]
                stats.at["cost-" + g,(scenario,ct)] = (network.generators.p_nom_opt*network.generators.capital_cost)[ct + " " + g]/network.snapshot_weightings.sum()

            for ls,ll in [("charger","battery charge"),("elec","H2 electrolysis"),("fc","H2 to power")]:
                stats.at[ls,(scenario,ct)] = network.links.p_nom_opt[ct + " " + ll]
                stats.at["cost-" + ls,(scenario,ct)] = (network.links.p_nom_opt*network.links.capital_cost)[ct + " " + ll]/network.snapshot_weightings.sum()

            for es, el in [("batt","battery storage"),("H2","H2 storage")]:
                stats.at[es,(scenario,ct)] = network.stores.e_nom_opt[ct + " " + el]
                stats.at["cost-" + es,(scenario,ct)] = (network.stores.e_nom_opt*network.stores.capital_cost)[ct + " " + el]/network.snapshot_weightings.sum()

            available = network.generators_t.p_max_pu.multiply(network.generators.p_nom_opt).sum()
            used = network.generators_t.p.sum()
            curtailment = (available-used)/available
            load = network.loads_t.p.sum().sum()
            supply = available/load
            stats.loc["wcurt",(scenario,ct)] = curtailment[ct + " wind"]
            stats.loc["scurt",(scenario,ct)] = curtailment[ct + " solar"]
            stats.loc["wsupply",(scenario,ct)] = supply[ct + " wind"]
            stats.loc["ssupply",(scenario,ct)] = supply[ct + " solar"]

    stats.to_csv(snakemake.output[0])

if __name__ == "__main__":


    # Detect running outside of snakemake and mock snakemake for testing
    if 'snakemake' not in globals():
        from pypsa.descriptors import Dict
        import yaml

        snakemake = Dict()

        with open('config.yaml') as f:
            snakemake.config = yaml.load(f)

        snakemake["output"] = ["{}summary.csv".format(snakemake.config["results_dir"])]

    make_csv()
