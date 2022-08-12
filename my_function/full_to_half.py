import pandas as pd

def h2f(dataseries):
    full_cha = ['０', '１','２','３','４','５','６','７','８','９']
    num = 0
    for c in full_cha:
        dataseries = dataseries.str.replace(str(c),str(num))
        num = num + 1
    return dataseries