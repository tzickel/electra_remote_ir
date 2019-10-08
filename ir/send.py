from .pyslinger import IR
from .write import write_as_bits
from .read import FanSpeed, Modes


def args_to_params(args):
    def fromval(cls, something):
        try:
            something = int(something)
        except:
            pass
        if isinstance(something, int):
            return cls(something)
        else:
            return cls[something]

    mode = fromval(Modes, args[0])
    temp = int(args[1])
    speed = fromval(FanSpeed, args[2])
    power_cycle = bool(int(args[3]))
    return mode, temp, speed, power_cycle


def send(gpio_pin, mode, temp, speed, power_cycle):
    protocol = "RAW"
    protocol_config = dict(
        one_duration=1000,
        zero_duration=1000)
    ir = IR(gpio_pin, protocol, protocol_config)
    code = write_as_bits(mode, temp, speed, power_cycle)
    ir.send_code(code)


if __name__ == "__main__":
    from sys import argv
    from os import environ

    gpio_pin = int(environ('GPIO_PIN', 25))

    send(gpio_pin, *args_to_params(argv[1:]))
