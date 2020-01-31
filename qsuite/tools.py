"""
A collection of useful tools.
"""

from qsuite import qconfig
import numpy as np

def change_result_parameter_order(results, new_order, old_order=None, ignore_measurement_axis=False):
    """
    Take the result array and move around the axes such that it corresponds to 
    the order of parameters in `new_order` (a list of the parameter names as
    defined in `external_parameters` and `internal_parameters`).
    """

    res = results
    is_list = type(results) is list
    if is_list:
        res = np.array(res)

    if old_order is None:
        cf = qconfig()
        params = [ _[0] for _ in cf.external_parameters + cf.internal_parameters ]
    else:
        params = old_order

    if ignore_measurement_axis and None in params:
        params.pop(params.index(None))
    
    new_indices = np.array([new_order.index(p) for p in params])
    if not np.all(np.sort(new_indices) == np.arange(len(params))):
        raise ValueError("Every element in the list `new order` needs to have a corresponding element in the parameter configuration.")

    res = np.moveaxis(res, np.arange(len(params)), new_indices)

    if is_list:
        res = res.tolist()

    return res



def change_meanerr_parameter_order(meanerr, new_order, old_order=None):
    return change_result_parameter_order(meanerr, new_order, old_order=old_order, ignore_measurement_axis=True)
