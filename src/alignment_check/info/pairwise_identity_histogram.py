"""Info: distribution of pairwise sequence identities.

This is O(n^2) in the number of sequences, so callers should only run it
when the --n2 CLI option is given.
"""

import itertools
import math
from collections.abc import Callable

from alignment_check.alphabet import DEFAULT_GAP_CHARS
from alignment_check.info.pairwise_identity import default_identity
from alignment_check.sequence import Sequence

IdentityFunction = Callable[[str, str, str], float]


def compute_pairwise_identity_histogram(
    sequences: list[Sequence],
    gap_chars: str = DEFAULT_GAP_CHARS,
    identity_fn: IdentityFunction = default_identity,
) -> dict[str, object]:
    """Compute the identity of every pair of sequences.

    Args:
        sequences: The (equal-length) sequences to compare.
        gap_chars: Characters treated as alignment gaps.
        identity_fn: The pairwise identity function to use; see
            `pairwise_identity.default_identity` for the signature and
            the default definition.

    Returns:
        A dict with:
            "identities": The identity of each pair with at least one
                comparable column, in no particular order.
            "pairs_compared": How many pairs contributed a value.
            "pairs_skipped": How many pairs had no comparable columns
                (identity_fn returned NaN) and were left out.
    """
    identities = []
    pairs_skipped = 0
    for a, b in itertools.combinations(sequences, 2):
        identity = identity_fn(a.seq, b.seq, gap_chars)
        if math.isnan(identity):
            pairs_skipped += 1
        else:
            identities.append(identity)

    return {
        "identities": identities,
        "pairs_compared": len(identities),
        "pairs_skipped": pairs_skipped,
    }
