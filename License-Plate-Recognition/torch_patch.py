import torch

_real_torch_load = torch.load

def patched_torch_load(*args, **kwargs):
    if 'weights_only' in kwargs:
        kwargs['weights_only'] = False
    else:
        kwargs.update({'weights_only': False})
    return _real_torch_load(*args, **kwargs)

torch.load = patched_torch_load
print("✅ torch.load đã được patch với weights_only=False")
