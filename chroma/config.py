from typing import Union, List
from pathlib import Path


PROJECT_PATHS = [
    Path(__file__).parent.parent / 'data'
]

class Config:

    def __init__(
            self, 
            default_color_type:str='Hex', 
            ):
        
        self._default_color_type = default_color_type

    @property
    def default_color_type(self)->str:
        return self._default_color_type
    
    project_paths : List[Union[str,Path]] = PROJECT_PATHS
