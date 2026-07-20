import importlib
import pkgutil
import unittest

import um


class ImportTest(unittest.TestCase):
    def test_importing(self):
        errors = []

        for module_info in pkgutil.walk_packages(
                path=um.__path__,
                prefix=um.__name__ + ".",
        ):
            try:
                mod = importlib.import_module(module_info.name)
                if hasattr(mod, "__all__"):
                    for name in mod.__all__:
                        getattr(mod, name)  # raises AttributeError if missing
            except Exception as e:
                errors.append(f"{module_info.name}: {e!r}")

        if errors:
            self.fail("Failed to import modules:\n" + "\n".join(errors))


if __name__ == '__main__':
    unittest.main()
