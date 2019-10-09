# Erlazio erauzle automatikoa

Bi kontzeptuen arteko erlazio-erauzle automatiko baten inplementazioa.

## Adibidea

```python
from erlazio_erauzlea import ErlazioErauzlea

ee = ErlazioErauzlea.kargatu('path_to_model')

testua = """By the time the earliest plants evolved, animals were already the dominant organisms in the ocean. 
Plants were also contrained to the upper layer of water that received enough sunlight for photosynthesis. 
"""

erlazioak = ee.erlazioak_erauzi(testua)

print(erlazioak)
```

| arg1          | arg2          | rel   | konfiantza |
| ------------- |:-------------:| -----:|:----------:|
| animal        | plant         | IsA   | 0.03       |
| organism      | plant         | IsA   | 0.22       |
| organism      | animal        | IsA   | 0.48       |
| plant         | water         | AtLocation   | 0.87       |
| layer         | water         | AtLocation   | 0.58       |
