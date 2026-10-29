import importlib

__all__ = ["forecast", "takeup_path"]


def __getattr__(name):
    # Lazy re-export: an eager import makes `python -m voucher_growth_model.forecast` warn.
    if name in __all__:
        return getattr(importlib.import_module("voucher_growth_model.forecast"), name)
    raise AttributeError(name)
