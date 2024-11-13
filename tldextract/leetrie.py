from collections import UserDict
from collections.abc import Collection
import idna


class TrieLeaf(dict):
    # add dot accessors
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class LeeTrie(TrieLeaf):
    """Pure Python dict Trie for storing eTLDs with their labels in reverse-order.
    Pure dict Trie should be faster and can also be serialized for parallel processing applications (eg. Pyspark).

    by: Lee Prevost
    """
    name = 'leetrie'

    def __init__(self, matches: dict[str, "LeeTrie"] | None = None, end: bool = False, is_private: bool = False) -> None:
        """TODO."""
        super().__init__()
        self.matches = matches if matches else {}
        self.end = end
        self.is_private = is_private

    @staticmethod
    def create(
            public_suffixes: Collection[str],
            private_suffixes: Collection[str] | None = None,
    ) -> "LeeTrie":
        """Create a Trie from a list of suffixes and return its root node."""
        root_node = LeeTrie()

        for suffix in public_suffixes:
            root_node.add_suffix(suffix)

        if private_suffixes is None:
            private_suffixes = []

        for suffix in private_suffixes:
            root_node.add_suffix(suffix, True)

        return root_node

    def add_suffix(self, suffix: str, is_private: bool = False) -> None:
        """Append a suffix's labels to this Trie node."""
        node = self

        labels = suffix.split(".")
        labels.reverse()

        for label in labels:
            if label not in node.matches:
                node.matches[label] = LeeTrie()
            node = node.matches[label]

        node.end = True
        node.is_private = is_private


    # future: could embed search methods into Trie

#slightly modified search removing '.matches' accessor and using pure dict lookup.
def suffix_index(
        self, spl: list[str], include_psl_private_domains: bool | None = None
) -> tuple[int, bool]:
    """Return the index of the first suffix label, and whether it is private.

    Returns len(spl) if no suffix is found.
    """
    if include_psl_private_domains is None:
        include_psl_private_domains = self.include_psl_private_domains

    node = (
        self.tlds_incl_private_trie
        if include_psl_private_domains
        else self.tlds_excl_private_trie
    )
    i = len(spl)
    j = i
    for label in reversed(spl):
        decoded_label = _decode_punycode(label)
        if decoded_label in node['matches']:
            j -= 1
            node = node['matches'][decoded_label]
            if node['end']:
                i = j
            continue

        is_wildcard = "*" in node['matches']
        if is_wildcard:
            is_wildcard_exception = "!" + decoded_label in node['matches']
            if is_wildcard_exception:
                return j, node['matches']["*"].is_private
            return j - 1, node['matches']["*"].is_private

        break

    return i, node['is_private']

def _decode_punycode(label: str) -> str:
    lowered = label.lower()
    looks_like_puny = lowered.startswith("xn--")
    if looks_like_puny:
        try:
            return idna.decode(lowered)
        except (UnicodeError, IndexError):
            pass
    return lowered