import numpy as np
import pandas as pd
from pkg import util

class Base:
    def run(self):
        return 1

class Child(Base):
    def run(self):
        pass

def process(df, other, a, b, c, d):
    if a and b or c and d:
        x = 42
    for _, row in df.iterrows():
        print(row)
    m = df.merge(other)
    if df["x"] == np.nan:
        pass
    v = df["a"]["b"]
    arr = df.values
    try:
        util.helper()
    except Exception:
        pass
    return df.groupby("a").sum().reset_index().head()
