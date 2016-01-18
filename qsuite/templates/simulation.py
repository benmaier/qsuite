#change the following according to your needs
from your_simulation_module import your_simulation_function

def simulation_code(kwargs):

    result = your_simulation_function(**kwargs)

    #do stuff with the result
    #if you create an object carrying out the simulation like so:
    #
    #result = sim.your_simulation_function(**kwargs)
    #
    #consider deleting your object afterwards in order to free memory:
    #
    #del sim
    #
    #(be aware that the results from the simulation have to be a deep copy of
    # of data in the simulation object, or else the resultdata will get deleted, too)
    
    return result
