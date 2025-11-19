import vfbquery as vfb
import json
import numpy as np

# Custom JSON encoder to handle NumPy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

results = []
results.append(vfb.get_term_info('FBbt_00003748', force_refresh=True))
results.append(vfb.get_term_info('VFB_00000001', force_refresh=True))
results.append(vfb.get_term_info('VFB_00101567', force_refresh=True))
results.append(vfb.get_instances('FBbt_00003748', return_dataframe=False, force_refresh=True))
results.append(vfb.get_templates(return_dataframe=False))

for i, result in enumerate(results):
    print(f"Example {i+1}:")
    print(json.dumps(result, indent=2, cls=NumpyEncoder))
    print()
