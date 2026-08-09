import importlib
import utils.source_cleaner as s
importlib.reload(s)

print(s.__file__)
print(s.clean_source_url("[https://example.com/test](https://example.com/test)"))
print(s.clean_sources([
    "[https://example.com/a](https://example.com/a)",
    "[https://example.com/b](https://example.com/b)",
    "[https://example.com/a](https://example.com/a)",
]))
