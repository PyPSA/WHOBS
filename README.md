

# Optimal Wind+Hydrogen+Other+Battery+Solar (WHOBS) electricity systems for European countries

This free software uses open data to calculate what it would cost to
create a constant "baseload" generation profile from a combination of
wind power, solar power and storage (using batteries and the
electrolysis of hydrogen) for different European countries. Total
costs are calculated using projected assumptions for 2020, 2030 and
2050 (see `assumptions.csv`). Hourly weather data over 31 years are
used from the open [renewables.ninja](https://www.renewables.ninja)
project.

Current electricity generation costs (investment and operation) are
around 50-70 EUR/MWh.

Using wind+solar+batteries+hydrogen we get:

2020 assumptions:

![2020](https://raw.githubusercontent.com/PyPSA/whobs/master/img/2020.png)

2030 assumptions:

![2030](https://raw.githubusercontent.com/PyPSA/whobs/master/img/2030.png)

2050 assumptions:

![2050](https://raw.githubusercontent.com/PyPSA/whobs/master/img/2050.png)

## Important assumptions

Discount rates, underground storage of hydrogen.

## Warnings

- Electricity systems with zero direct CO2 emissions can be built more
  cheaply by using additional technology options. The examples here
  are simply a toy model to put an upper bound on the costs for a very
  simple setup. Additional generation technologies which may reduce
  costs include using existing hydroelectric generators, biomass from
  sustainable resources (such as waste and agricultural/forestry
  residues), geothermal, nuclear and fossil/biomass plants with
  CCS. Additional storage technologies include redox flow batteries,
  compressed air energy storage, etc., see [this review](https://doi.org/10.1016/j.apenergy.2014.09.081). Existing and planned
  transmission grid connects between countries can also reduce costs
  by up to 20% by smoothing wind over a larger area. Demand-side
  management can adapt demand to generation profiles. Furthermore,
  flexibility from electric vehicles and electrified heating with
  thermal storage can also reduce costs.

- Costs here are for completely decarbonised electricity
  systems. Reaching lower levels of decarbonisation is much cheaper
  and doesn't necessarily require any storage at all.


- The wind profiles use the current wind turbine fleets. Future
  turbines have higher capacity factors because e.g. they're taller,
  where wind resources are better.

- Electrolysis could be more cost effective if: waste heat is used to
  improve efficiency; oxygen is sold.

- Hydrogen-to-power may be cheaper with future developments in fuel cells.



# Installation

## Software

You'll need to install an environment for the Python programming
language (Version 3.x) along with the library
[PyPSA](https://github.com/PyPSA/PyPSA). You can follow PyPSA's
[installation
instructions](https://www.pypsa.org/doc/installation.html) or just do
`pip install pypsa`.

You'll also need a linear program solver, see the [advice for free
software
solvers](https://www.pypsa.org/doc/installation.html#getting-a-solver-for-linear-optimisation). To
solve 31 years at once, you'll need a commercial solver like Gurobi or CPLEX.

## Weather data

For the wind and solar generation time series, get from the [renewables.ninja download page](https://www.renewables.ninja/downloads):

- Solar time series `ninja_pv_europe_v1.1_sarah.csv` from "PV v1.1 Europe"

- Wind time series `ninja_wind_europe_v1.1_current_on-offshore.csv` from "Wind v1.1 Europe"


# Running a simulation

For short simulations, you can run the notebook `run_single_simulations.ipynb`.

To run them on the command line, use `whobs.py`.

To run many simulations, e.g. on a cluster, use [snakemake](https://snakemake.readthedocs.io/en/stable/).

# Results files

See zenodo.org

# Licence

All code in this repository is copyright 2018 Tom Brown (KIT)

This program is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either [version 3 of the
License](LICENSE.txt), or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
[GNU General Public License](LICENSE.txt) for more details.
