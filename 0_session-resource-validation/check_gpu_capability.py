!pip install -q --no-cache-dir torch==2.0.1

import torch
import sys

# Check that the CUDA capability of the GPUs in this workspace meet minimum requirements
version = torch.cuda.get_device_capability()
if version[0] <= 5:
    device = torch.cuda.get_device_name()
    msg = "CUDA Capability (%d.%d) of the GPU device (%s) " \
        "is less than the required (5.0), please use a newer" \
        "GPU instance type" % (version[0], version[1], device)

    sys.exit(msg)
