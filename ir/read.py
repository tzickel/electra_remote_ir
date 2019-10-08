from subprocess import check_output
from enum import IntEnum


class WrongDataError(Exception):
    pass


def read_once(device='/dev/lirc0'):
    return check_output('ir-ctl -r -1 -d %s' % device, shell=True, universal_newlines=True).split('\n')


def parse_input(lines):
    ret = []
    seq = []
    for line in lines:
        line = line.strip()
        if not line or line[0] == '#':
            continue
        line = line.split(' ')
        if line[0] == 'timeout':
            ret.append(seq)
            seq = []
            continue
        line = (0 if line[0] == 'space' else 1, int(line[1]))
        seq.append(line)
    if seq:
        ret.append(seq)
    return ret


def round_values(seq, round_to):
    return [(x[0], int(round(float(x[1]) / round_to) * round_to)) for x in seq]


# Signal is 3 high, 3 low, mantcheser encoded 34 bits data copied 3 times, then 4 high
def get_data_from_sequence(seq):
    high_length = 3000
    low_length = 3000
    end_length = 4000
    clock_length = 1000
    state = 0
    datas = []
    data = []
    for bit, length in seq:
        if length == high_length and bit == 1:
            if state == 0:
                state = 1
                continue
            elif state == 2:
                datas.append(data)
                data = []
                state = 1
                continue
        elif length == low_length and bit == 0:
            if state == 1:
                state = 2
                continue
        # This is for the case if the first bit after the low_length is 0
        elif length == low_length + clock_length and bit == 0:
            if state == 1:
                state = 2
                data.append((0, 1000))
                continue
        elif length == end_length and bit == 1:
            if state == 2:
                break
        elif state == 2:
            data.append((bit, length))
            continue
        raise WrongDataError('Invalid state decoding sequence')
    data = set([tuple(x) for x in datas])
    if len(data) != 1:
        raise WrongDataError('Data is not the same on all repeats')
    return data.pop()


def convert_to_bits(seq, clock_cycle=1000):
    bits = []
    for pnt in seq:
        for _ in range(0, pnt[1], clock_cycle):
            bits.append(pnt[0])
    return bits


def decode_manchester(bits):
    data = zip(bits[::2], bits[1::2])
    decoded_bits = []
    for item in data:
        if item[0] == 0 and item[1] == 1:
            decoded_bits.append(1)
        elif item[0] == 1 and item[1] == 0:
            decoded_bits.append(0)
        else:
            raise WrongDataError('Data is not manchester encoded')
    return decoded_bits


def as_string(bits):
    return ''.join([str(x) for x in bits])


def get_state(seq):
    return as_string(decode_manchester(convert_to_bits(get_data_from_sequence(seq))))


class FanSpeed(IntEnum):
    low = 0
    medium = 1
    high = 2
    auto = 3


class Modes(IntEnum):
    cool = 0
    heat = 1
    recycle = 2
    defrost = 3
    air = 4


def decode(bits):
    fan_speed = int(bits[4:6], 2)
    temp = int(bits[11:15], 2) + 15
    mode = int(bits[1:4], 2) - 1
    power_cycle = bool(bits[0] == '1')
    return {'mode': Modes(mode), 'temp': temp, 'speed': FanSpeed(fan_speed), 'power_cycle': power_cycle}


def get_ir_data(lines):
    states = []
    for seq in parse_input(lines):
        try:
            state = decode(get_state(round_values(seq, 1000)))
            states.append(state)
        except WrongDataError:
            pass # We want to ignore bad inputs
    return states


def find_changes_region(seqs):
    first = None
    for i, j in enumerate(zip(*seqs)):
        if len(set(j)) != 1:
            first = i
            break
    if first is None:
        raise Exception('All sequences are the same')
    last = None
    for i, j in enumerate(list(zip(*seqs))[::-1]):
        if len(set(j)) != 1:
            last = len(seqs[0]) - i
            break
    return first, last, [x[first:last] for x in seqs]


if __name__ == "__main__":
    import sys, os, stat

    if len(sys.argv) < 2:
        print('Usage: %s [file or device path]' % sys.argv[0])
        sys.exit(1)

    filename = sys.argv[1]
    regular_file = stat.S_ISREG(os.stat(filename).st_mode)

    if regular_file:
        with open(filename) as f:
            for item in get_ir_data(f.readlines()):
                print(item)
    else:
        while True:
            try:
                lines = read_once(filename)
                state = get_ir_data(lines)
                print(state)
            except KeyboardInterrupt:
                break
            except WrongDataError:
                pass
