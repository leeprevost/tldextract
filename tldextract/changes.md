# Changes 11/13/2024
by: Lee Prevost

Changes to tldextract (commit: 100da81)

1. Added tldextract/leetrie.py
- New TrieLeaf which is a subclass of a pure Python dict and dot accessor methods.   Added a __set_state__ method to support serialization
- New LeeTrie which is a subclass of TrieLeaf and with added methods to support creation and adding nodes.

2. Changes to tldextract.tldextract.py
- override Trie class (old Trie) to new LeeTrie

3. Benchmarks
- Added tldextract/benchmark_trie.py to generate benchmark_results.txt

4. Test support
- added tests/serialization_test_trie.py -- tests for case where trie is serialized with json.dumps/loads and where extractor is pickled.

# First pass:
- Full test ran successfully including serialization tests.  This could be important as I see evidence of tldextract getting used in massive scale situations such as CommonCrawl.org where extraction is performed across clusters of machines using spark.   In these cases, its important that both the extractor and the Trie can be serialized as the extractor could be used as a user defined function on remote nodes or the Trie could be broadcast to nodes for lookup.   
- Initial performance was worse using 10 loops on extraction from approximately 15K urls
-- 60ms vs. 37.9ms

# Second pass
- refactored the _PublicSuffixListTLDExtractor class to use a new suffix_index method which uses dict key assessors rather than dot assessors.
- Speed improved substantially to roughly the same as base -- 40.3 ms ± 214 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)

# Conclusions/Thoughts
Even though I think this provides a net gain as it makes your extractor and the Trie serializable (important for multi-cluster applications), I was surprised that a pure Python dictionary didn't provide faster lookup over the custom class.   

[Benchmark Results](benchmark_results.txt)


I could see further optimization as follows:
1. Collapse 'matches' on itself.   Rather than add new leafs to matches, just add the leaf keys directly to the leaf.   The result would be that each leaf would have 'end' and 'is_private' plus all the label keys.  This would likely have an exponential effect in terms of size and speed.  I didn't do this as I would also need to refactor the new suffix_index and possibly other places in the code.??
2. Get rid of 'end' by testing for number of labels in the leaf or by adding a property to the TrieLeaf that tests for this.  If only 'is_private' is in the leaf, then we have reached 'end.'
3. I chose to subclass dict in my Trie.   I did that in spite of our conversation John about using UserDict as UserDict seems more backward compatible than is subclassing dict.   But, the UserDict.__repr__() method complained about my added dot assessors so I chose the simpler path.