- use logging from the `logging` library via `getLogger(__name__)`
- class constructors should initialize classes,
which should only start after calling the `start` or `run` method
- end of `start` method execution should mean all threads started by that class
have been joined
- `run` should not block further code execution
- `stop` method should terminate all threads managed by that class