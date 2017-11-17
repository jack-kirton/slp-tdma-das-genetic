# SLP TDMA DAS Genetic

The purpose of this project is to generate SLP-aware time division multiple access data aggregation scheduling time slot schedules for a network of a given configuration.

## Usage
The majority of the usage instructions can be discovered by running the `main.py` script with the `-h` option at any stage to retrieve lists of options and arguments.

The main functions of the application can be executed by running `main.py` followed by one of the following:
* `run`
* `run-multiple`
* `plot`
* `c-header`

`run` will execute a single run of the genetic algorithm with the provided parameters.
`run-multiple` will execute the specified number of runs of the genetic algorithm. In this case database records will be given the ID provided appended by a number beginning from 0.
`plot` gives a number of options for the various plots that can be created from either single runs or averages over multiple runs. **WARNING:** `slots-average` and especially `pareto` can take a long time to run depending on the amount of runs stored in the database.
`c-header` will output a C header file that can be included and used as part of an algorithm. One such algorithm can be found [here](https://bitbucket.org/jack-kirton/slp-algorithms-tinyos/) named `slp_tdma_das_ga`.


## Creating Content
**NOTE:** It is advised that you fork the repository if you are creating new content.

### Topologies
In the file `ga/topology.py` you have the ability to create custom topologies to suit the network you are generating solutions for.
Simply create a new class that is a subclass of `Topology` in the same file and make sure to add all nodes first using `add_node` (use the same numerical ID as the node in the real network) and then connect nodes that are within communication range of each other using `add_edge`.
Use the `GridTopology` class as an example to build your own topology.

### Fitness Functions
In the file `ga/fitness.py` are examples of the fitness functions used. To create your own simply create the function in this file and add it to the `_fitness_functions` dictionary at the end of the file.
Ensure the function produces a result in the range 0-1 as this is the behaviour of the existing fitness functions.

