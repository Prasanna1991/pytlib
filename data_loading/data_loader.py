# base class for input generation
# Source provides frames (in order or out of order)
# Source could be a sequence of multiple items
# Transformer takes frames/sequence of frames and turns into samples

class DataLoader:
    def __init__(self,source,transformer):
        self.source = source
        self.transformer = transformer
    
    def __iter__(self):
        return self
    
    def __next__(self):
        pass

#### Data Loader factory for kind of dependency injection
from data_loading.sources.kitti_source import KITTISource
from data_loading.transformers.crop_transformer import CropTransformer

class DataLoaderFactory:

    @classmethod
    def GetKITTILoader(cls):
        source = KITTISource('path/to/source')
        transformer = CropTransformer(['people'])
        return DataLoader(source,transformer)
