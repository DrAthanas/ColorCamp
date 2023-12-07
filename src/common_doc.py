import inspect

COMMON_DOCSTRINGS = dict(
    red={
        'type':float,
        'desc':...,
        'default':...,
    },
    # green:float,
    # blue:float,
    # name:str=None,
    # description:str=None,
    # metadata:Dict[str, Any]=None,
    # alpha:Optional[float]=None
)

def common_doc(*args, **kwargs):
    
    def wrapper(klass):
        # use inspect to find out args in __init__


        return klass
    
    return wrapper