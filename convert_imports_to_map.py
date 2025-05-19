import json

with open("temp_mails/__init__.py", "r") as f:
    s = f.read().split("if TYPE_CHECKING:")[1]

_provider_map = {}
_import_map = {}

for line in s.splitlines():
    if line.strip().startswith("from .providers."):
        
        file_name, class_names = line.split(".providers.", 1)[1].split(" import ", 1)
        class_names = [class_name.strip() for class_name in class_names.split(",")]

        _import_map[file_name] = class_names
        for class_name in class_names:
            _provider_map[class_name] = file_name.strip()


sorted_provider_map = dict(sorted(_provider_map.items()))
sorted_import_map = dict(sorted(_import_map.items()))

for file_name, class_names in sorted_import_map.items():
    print(f"\tfrom .providers.{file_name} import {', '.join(class_names)}")


print(f"\n_provider_map = {json.dumps(sorted_provider_map, indent=4)}")