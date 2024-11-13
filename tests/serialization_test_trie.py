import json
import pickle
import tldextract

extractor = tldextract.TLDExtract(include_psl_private_domains=False)

t = extractor._get_tld_extractor().tlds_incl_private_trie

# Test for whether raw trie can be serialized using json.dumps/loads and whether extractor can be serialized/deserialized
# and used
# important for cluster applications (multi-machine - eg. spark) where extractor could be used as a udf or trie could be
# broadcast to remote nodes for comparison on remote.

def test_serialization():
    assert t.name == 'leetrie'
    t_ser = json.loads(json.dumps(t))
    assert t.matches['us'].matches['nc']  # still nested.
    assert t_ser == t
    p_extractor =  pickle.loads(pickle.dumps(extractor))  # fails, not sure why "NoneType" object is not callable
    assert p_extractor("ths.haywood.com").domain == 'haywood'
