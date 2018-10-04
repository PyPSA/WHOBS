configfile: "config.yaml"

wildcard_constraints:
    scenario="[a-z0-9\.\-\_]+",
    country="[a-zA-Z]+"

rule solve_all:
    input:
        config['results_dir'] + "summary.csv"

rule solve:
    output: config['results_dir'] + "{country}-{scenario}.nc"
    threads: 4
    resources:
        mem_mb=20000
    script: "whobs.py"

rule make_summary:
    input:
        expand(config['results_dir'] + "{country}-{scenario}.nc",
	       **config['run_settings'])
    output:
        summary=config['results_dir'] + "summary.csv"
    threads: 2
    resources:
        mem_mb=2000
    script: "make_summary.py"
