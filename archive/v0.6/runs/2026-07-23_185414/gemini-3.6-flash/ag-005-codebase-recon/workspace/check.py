import pipeline.mod_09 as m09
print("mod_09 contents:")
print("SECRET_TOKEN:", getattr(m09, "SECRET_TOKEN", None))
print("NEXT:", getattr(m09, "NEXT", None))

import pipeline.entry as entry
print("entry.START:", entry.START)
