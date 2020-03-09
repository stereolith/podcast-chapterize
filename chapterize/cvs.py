import numpy as np
import scipy as sp

#def cvs(tokens, boundaries):

def test():
    import json
    with open('/home/lukas/Documents/podcast-chapterize-eval/transcripts/raumzeit-2020.m4a_transcript.json', 'r') as f:
        data = json.load(f)
    
    tokens = [token['token'] for token in data['tokens']]

    splits = cvs(tokens, len(data["chapters"]) -1)

    for split in splits:
        print(f'time: {round(float(data["tokens"][split]["time"])/60, 2)} min')

    print(f'\ngold chapter times: ({len(data["chapters"])} chapters)')
    for gold_chapter in data["chapters"]:
        print(f'time: {round(float(gold_chapter["start_time"])/60, 2)} min')


def cvs(tokens, k):
    # Content Vector Segmentation (CVS)  
    # https://arxiv.org/pdf/1503.05543.pdf
    # https://github.com/alexalemi/segmentation
    import matplotlib.pyplot as plt

    from gensim.models import KeyedVectors
    model = KeyedVectors.load_word2vec_format('/home/lukas/Downloads/german.model',binary=True)

    X = []
    mapper = {}
    count = 0
    for i,word in enumerate(tokens):
        if word in model:
            mapper[i] = count
            count += 1
            X.append( model[word] )

    model = None

    mapperr = { v:k for k,v in mapper.items() }

    X = np.array(X)

    sig = gensig_model(X)

    # splits = greedysplit_optimize_k(X.shape[0], sig)
    splits, s = greedysplit(X.shape[0], k, sig)

    splitsr = refine(splits, sig, 20)

    return [mapperr[split] for split in splitsr[:-1]]
    
def greedysplit_optimize_k(n, sig):
    # score value from sig (gensig_model) correlates with k
    # normalization need, else the score is always lower for a higher k

    bestsplit = [], 0
    for k in range(5,20):
        new = greedysplit(n, k, sig)
        if new[1] < bestsplit[1]:
            bestsplit = new
            best_k = k
        print(f'for k {k} split score is {bestsplit[1]}')
    print(f'chose k={best_k}')
    return bestsplit[0]
    # optimal = max()

def gensig_model(X, minlength=1, maxlength=None, lam=0.0):
    N,D = X.shape
    over_sqrtD = 1./np.sqrt(D)
    cs = np.cumsum(X,0)

    def sigma(a,b):
        length = (b-a)
        if minlength:
            if length < minlength: return np.inf
        if maxlength:
            if length > maxlength: return np.inf

        tot = cs[b-1].copy()
        if a > 0:
            tot -= cs[a-1]
        signs = np.sign(tot)
        return -over_sqrtD*(signs*tot).sum()
    return sigma

def greedysplit(n, k, sigma):
    """ Do a greedy split """
    splits = [n]
    s = sigma(0,n)

    def score(splits, sigma):
        splits = sorted(splits)
        return sum( sigma(a,b) for (a,b) in seg_iter(splits) )

    while k > 0:
        usedinds = set(splits)
        new = min( ( score( splits + [i], sigma), splits + [i] )
                for i in range(1,n) if i not in usedinds )
        splits = new[1]
        s = new[0]
        k -= 1
    return sorted(splits), s

def refine(splits, sigma, n=1):
    """ Given some splits, refine them a step """
    oldsplits = splits[:]
    counter = 0
    n = n or np.inf

    while counter < n:
        splits = [0]+splits
        n = len(splits) - 2
        new = [splits[0]]
        for i in range(n):
            out = bestsplit(splits[i], splits[i+2], sigma)
            new.append(out[2])
        new.append(splits[-1])
        splits = new[1:]

        if splits == oldsplits:
            break
        oldsplits = splits[:]
        counter += 1

    return splits

def bestsplit(low, high, sigma, minlength=1, maxlength=None):
    """ Find the best split inside of a region """
    length = high-low
    if length < 2*minlength:
        return (np.inf, np.inf, low)
    best = min( ((sigma(low,j), sigma(j, high), j) for j in range(low+1,high)), key=lambda x: x[0]+x[1] )
    return best

def pairwise(iterable):
    from itertools import tee
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def seg_iter(splits):
    return pairwise([0] + splits)
