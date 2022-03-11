import numpy as np
import json


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

# # Your codes .... 
# json.dumps(data, cls=NpEncoder

def state_space(grid_size=13, num_players=2):
    """compute state space of tron game"""
    # each grid location is either free or occupied
    print("Large: {}".format(2**100))

    #
