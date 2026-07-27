# {title}

Generate the learner-facing landing page after `project.yaml`, project assets,
code and validation links are complete:

```sh
python3 tools/generate_project_discovery.py
python3 tools/generate_project_discovery.py --check
```

The generated page must expose the breadboard map, electrical schematic, code,
build path, expected result, validation checklist and evidence status without
duplicating canonical engineering content.
