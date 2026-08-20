"""
Monkeypatch the ActionCompleter.get_completions from the action_completer library.
Original version calculated the start_position of the completion to be at the start of all parameters i.e.:
for a prompt `view Desktop -1` where `view` is the action, `Desktop` and `-1` are the parameters,
autocompleting `-1` would override the first parameter `Desktop`.

Upstream: https://github.com/stephen-bunn/prompt-toolkit-action-completer
(archived since 2025)
Affects: prompt-toolkit-action-completer==1.1.1
"""
from typing import Generator, Optional, cast

from action_completer import ActionGroup, Action
from prompt_toolkit.completion import Completion, CompleteEvent
from prompt_toolkit.document import Document
from action_completer.completer import ActionCompleter, CompletionIterator_T
from action_completer.utils import extract_context, get_fragments, encode_completion


def _patched_get_completions(
        self, document: Document, complete_event: CompleteEvent
) -> Generator[Completion, None, None]:
    """Generate completions for the given prompt document.

    Args:
        document (~prompt_toolkit.document.Document): The document directly from
            the prompt to generate completions for
        complete_event (~prompt_toolkit.completion.CompleteEvent): The completion
            event for the completions

    Yields:
        prompt_toolkit.completion.Completion:
            A completion for the given prompt document
    """

    _, _, completable, fragments = extract_context(
        self.root, get_fragments(document.text)
    )
    if len(fragments) <= 0:
        return

    # this starting position is NOT the same as len(document.text)
    # BEFORE:
    # start_position = -len(" ".join(fragments))
    # FIXED:
    start_position = -len(fragments[-1])

    completion_iterator: Optional[CompletionIterator_T] = None
    if isinstance(completable, ActionGroup):
        completion_iterator = cast(
            CompletionIterator_T, self._iter_group_completions
        )
    elif isinstance(completable, Action):
        completion_iterator = cast(
            CompletionIterator_T, self._iter_action_completions
        )

    if completion_iterator:
        for completion in completion_iterator(
                completable, fragments, complete_event, start_position=start_position
        ):
            completion.text = encode_completion(completion.text)
            yield completion


ActionCompleter.get_completions = _patched_get_completions
