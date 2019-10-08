from subprocess import check_call
from tempfile import NamedTemporaryFile


def to_binary(num, length):
    return ("{0:0%sb}" % length).format(num)


def encode(total_length, *items):
    s = ''
    curr_pos = 0
    # TODO sanity check or sort
    for num, pos, length in items:
        s += '0' * (pos - curr_pos)
        s += to_binary(num, length)
        curr_pos = pos + length
    if curr_pos < total_length:
        s += '0' * (total_length - curr_pos)
    return s


def encode_electra(mode, temp, speed, power_cycle):
    return encode(34, (int(power_cycle), 0, 1), (mode + 1, 1, 3), (speed, 4, 2), (temp - 15, 11, 4), (1, 32, 1))


def manchester(bits):
    return ''.join(['10' if bit == '0' else '01' for bit in bits])


def write_state(bits):
    return (('111000' + bits) * 3) + '1111'


def length_encode(bits, clock):
    curr = 1
    length = 0
    ret = []
    for i in bits:
        i = int(i)
        if i == curr:
            length += 1000
        else:
            ret.append((curr, length))
            curr = i
            length = 1000
    if length:
        ret.append((curr, length))
    return ret


def write_as_bits(mode, temp, speed, power_cycle):
    return write_state(manchester(encode_electra(mode, temp, speed, power_cycle)))


def write_to_text(mode, temp, speed, power_cycle):
    state = length_encode(write_state(manchester(encode_electra(mode, temp, speed, power_cycle))), 1000)
    ret = ''
    for value, time in state:
        ret += '%s %s\n' % ('pulse' if value == 1 else 'space', time)
    return ret


def write_once(mode, temp, speed, power_cycle, device='/dev/lirc0'):
    txt = write_to_text(mode, temp, speed, power_cycle)
    with NamedTemporaryFile() as fp:
        fp.write(txt.encode('utf-8'))
        fp.flush()
        return check_call('ir-ctl -s %s -d %s' % (fp.name, device), shell=True, universal_newlines=True)
