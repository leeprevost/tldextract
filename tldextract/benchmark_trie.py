import pandas as pd
import tldextract
import timeit

path = r"C:\Users\lee\Downloads\91f0cb13-8bbd-450b-9413-9e5cae0c4e41.csv"
url = lambda x: ".".join(reversed(x.split(".")))

test_data = pd.read_csv(path).rev_tld.apply(url)
n = len(test_data)
extractor1 = tldextract.TLDExtract(include_psl_private_domains=True)


timeit.timeit('test_data.apply(extractor1)', globals=globals(), number=100)





