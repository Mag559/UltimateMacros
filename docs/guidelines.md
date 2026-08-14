- use logging from the `logging` library via `getLogger(__name__)`
- class constructors should initialize classes,
which should only start after calling the `start` or `run` method
- end of `start` method execution should mean all threads started by that class
have been joined
- `run` should not block further code execution
- `stop` method should terminate all threads managed by that class
- package `__init__.py` files should feature lazy imports
- imports from outside the package should take the form of `import um.xyz`
at the top of the file, in cases where imported names are used often,
one can additionally use `from um.xyz import XYZ` in the function scope
- the above two guidelines prevent the entire project alongside all dependencies
from being imported at the very start of the programs runtime
(i.e. importing tools and screen match is often unnecessary).
They can however be omitted for small, self-contained packages like `helper_classes`
or ones common in the entire project (and loaded very early regardless) like `profiles`
