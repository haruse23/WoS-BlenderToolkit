import zipfile
import json
from functools import lru_cache
import os

apk_examples = [
    ("0xEE185533", [0xFC001315, 0xFC0008D4]),
    ("0x33DF189E", [0xFC0003F0, 0xFC000254, 0xFC000376, 0xFC000377, 0xFC00037C, 0xFC000380, 0xFC000383, 0xFC000386, 0xFC000389, 0xFC00038D, 0xFC000390, 0xFC000393, 0xFC000397, 0xFC00039C, 0xFC0003A1, 0xFC000313, 0xFC0003A6, 0xFC0003AA, 0xFC0003AD, 0xFC0003B1, 0xFC0003B6, 0xFC0003BA, 0xFC0003BE, 0xFC0003C2, 0xFC0003C7, 0xFC0003CB, 0xFC0003D0, 0xFC0003D3, 0xFC0003D6, 0xFC0003D9, 0xFC00031B])
]

@lru_cache()
def get_string_lookup(path="stringtable_pcapk.zip"):
    addon_dir = os.path.dirname(__file__)
    zip_path = os.path.join(addon_dir, "stringtable_pcapk.zip")

    zf = zipfile.ZipFile(zip_path)
    namefile = None
    for f in zf.namelist():
        namefile = zf.read(f)
    
    lookup = json.loads(namefile)
    return lookup
    
def lookup_pcapk_string_table(pcapk_hash, p):
    lookup = get_string_lookup()
    string_table = lookup['strings']
    map = lookup['files'][pcapk_hash]['lookup']
    
    idx = p >> 26 # 63 for NAME
    offset = (p & 0x3FFFFFF) * 4
    key = f"{int(offset)}"
    
    i = map[key]
    s = string_table[i]
    return s

if __name__ == "__main__":
    for apk_hash, pointers in apk_examples:
        for p in pointers:
            lookup_pcapk_string_table(apk_hash, p)
        