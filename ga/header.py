from __future__ import division, print_function

from ga import genome
from ga.output_adapters import sqlite_retrieve_best_genome

c_header_template = """/*
 * GENERATED HEADER FILE
 * Database: {dbname}
 * Identity: {id}
 * Generations: {generations}
 */

#ifndef GA_H
#define GA_H

#define GA_TOTAL_NODES {total_nodes}
#define GA_TOTAL_SLOTS {total_slots}
#define GA_SOURCE_ID {source_id}
#define GA_SINK_ID {sink_id}

const uint16_t ga_slot_assignments[] = {{{slot_assignments}}};

const uint16_t ga_path_ids_length = {path_ids_length};
const uint16_t ga_path_ids[] = {{{path_ids}}};

int ga_is_in_path(uint16_t id)
{{
    int i;
    for(i = 0; i < ga_path_ids_length; i++) {{
        if(id == ga_path_ids[i]) {{
            return 1;
        }}
    }}
    return 0;
}}

#endif /* GA_H */
"""

def generate_c_header(dbname, id):
    g, generations, slots = sqlite_retrieve_best_genome(dbname, id)
    genome.normalise_slots(g)
    n = g.n
    attacker_path = genome.find_attacker_path(n)
    output = {}
    output['dbname'] = dbname
    output['id'] = id
    output['generations'] = generations
    output['total_nodes'] = len(n.nodes())
    output['total_slots'] = slots
    output['source_id'] = n.graph['source']
    output['sink_id'] = n.graph['sink']
    output['slot_assignments'] = ", ".join([str(n.node[node]['slot']) for node in n.nodes_iter()])
    output['path_ids_length'] = len(attacker_path)
    output['path_ids'] = ", ".join([ str(a) for a in attacker_path ])
    return c_header_template.format(**output)
