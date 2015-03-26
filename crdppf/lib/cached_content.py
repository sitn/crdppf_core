
from dogpile.cache.region import make_region

cache_region = make_region()
cache_region.configure("dogpile.cache.memory")

@cache_region.cache_on_arguments()
def get_cached_content():
    d={}
    return d
    
@cache_region.cache_on_arguments()
def get_cached_content_l10n(lang):
    d={}
    return d