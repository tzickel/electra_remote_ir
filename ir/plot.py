import matplotlib.pyplot as plt


def seq_to_xy(seq):
    line = [(0, 0)]
    i = 0
    for pnt in seq:
        i += pnt[1]
        if line[-1][1] == 0:
            line.append((line[-1][0], 1))
            line.append((i, 1))
        else:
            line.append((line[-1][0], 0))
            line.append((i, 0))
    return line


def plot(seqs):
    for seq in seqs:
        xy = seq_to_xy(seq)
        plt.plot([x[0] for x in xy], [x[1] for x in xy])
