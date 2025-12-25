from typing import List, Dict
from sklearn.metrics import precision_score, recall_score, f1_score
import numpy as np

def answer_accuracy(preds: List[str], golds: List[str]) -> float:
    # simple token-level overlap heuristic for quick checks (not SOTA)
    def overlap(a,b):
        aset=set(a.lower().split())
        bset=set(b.lower().split())
        if not aset or not bset:
            return 0.0
        return len(aset & bset)/len(bset)
    scores=[overlap(p,g) for p,g in zip(preds,golds)]
    return float(np.mean(scores))

def binary_precision(preds_labels: List[int], golds_labels: List[int]) -> Dict:
    p=precision_score(golds_labels, preds_labels, zero_division=0)
    r=recall_score(golds_labels, preds_labels, zero_division=0)
    f1=f1_score(golds_labels, preds_labels, zero_division=0)
    return {"precision":p,"recall":r,"f1":f1}