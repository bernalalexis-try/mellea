# Copyright IBM Corp. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Keep the hook reference in docs/docs/concepts/plugins.mdx in sync with HookType.

The reference presents itself as exhaustive, so a hook added to ``HookType``
without a section, a policy-table row and the right count would make it
silently wrong again (#1743).
"""

import re
from pathlib import Path

import pytest

from mellea.plugins.types import HookType

DOC = Path(__file__).resolve().parents[2] / "docs" / "docs" / "concepts" / "plugins.mdx"


def _reference_section(text: str) -> str:
    start = text.index("## Hook types reference")
    end = text.index("### Hook payload policy table")
    return text[start:end]


def _policy_table(text: str) -> dict[str, str]:
    start = text.index("### Hook payload policy table")
    end = text.index("## Execution modes deep dive")
    rows = re.findall(r"^\| `([a-z_]+)` \| (.+?) \|\s*$", text[start:end], re.MULTILINE)
    return dict(rows)


@pytest.fixture(scope="module")
def doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_every_hook_type_has_a_reference_section(doc_text):
    documented = set(
        re.findall(r"^#### `([a-z_]+)`", _reference_section(doc_text), re.MULTILINE)
    )
    assert documented == {hook.value for hook in HookType}


def test_every_hook_type_has_a_policy_table_row(doc_text):
    assert set(_policy_table(doc_text)) == {hook.value for hook in HookType}


def test_the_stated_hook_count_matches_the_enum(doc_text):
    match = re.search(r"Enum with all (\d+) hook types", doc_text)
    assert match is not None
    assert int(match.group(1)) == len(HookType)


def test_policy_table_writable_fields_match_the_policies(doc_text):
    pytest.importorskip("cpex", reason="cpex not installed")
    from mellea.plugins.policies import MELLEA_HOOK_PAYLOAD_POLICIES

    for hook, cell in _policy_table(doc_text).items():
        documented = set(re.findall(r"`([a-z_]+)`", cell))
        policy = MELLEA_HOOK_PAYLOAD_POLICIES.get(hook)
        expected = set(policy.writable_fields) if policy is not None else set()
        assert documented == expected, hook
