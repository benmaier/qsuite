from tauleapevo import fluctuating_fitness_SSA

def simulation_code(kwargs):
    sim = fluctuating_fitness_SSA(**kwargs)
    sim.simulate()

    return None
