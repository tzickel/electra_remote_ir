import signal
from threading import Thread

from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_AIR_CONDITIONER
from pyhap.characteristic import PROP_MIN_VALUE, PROP_MAX_VALUE, PROP_MIN_STEP


class AirConditioner(Accessory):
    category = CATEGORY_AIR_CONDITIONER
    common_properties = {PROP_MIN_VALUE: 16,
                        PROP_MAX_VALUE: 30,
                        PROP_MIN_STEP: 1}

    def set_temp(self, value):
        self.setter('temp', value)
    
    def set_mode(self, value):
        self.setter('mode', value)

    def get_temp(self):
        return self.getter('temp') or 0

    def get_mode(self):
        return self.getter('mode') or 0

    def __init__(self, getter, setter, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.getter = getter
        self.setter = setter

        thermostat = self.add_preload_service('Thermostat')
        thermostat.configure_char(
            'CurrentTemperature',
            getter_callback=self.get_temp,
            properties=self.common_properties
        )

        thermostat.configure_char(
            'TargetTemperature',
            setter_callback=self.set_temp,
            getter_callback=self.get_temp,
            properties=self.common_properties
        )

        thermostat.configure_char(
            'CurrentHeatingCoolingState',
            getter_callback=self.get_mode,
        )

        thermostat.configure_char(
            'TargetHeatingCoolingState',
            setter_callback=self.set_mode,
            getter_callback=self.get_mode,
        )

        thermostat.configure_char(
            'TemperatureDisplayUnits',
            value=0,  # Celsius
        )


def main(getter, setter, port):
    driver = AccessoryDriver(port=port)
    driver.add_accessory(accessory=AirConditioner(getter, setter, driver, 'ElectraAirConditioner'))
    signal.signal(signal.SIGTERM, driver.signal_handler)
    return driver


def threaded(getter, setter, port=51827):
    driver = main(getter, setter, port)
    t = Thread(target=driver.start)
    t.daemon = True
    t.start()


if __name__ == "__main__":
    def getter(name):
        print(name)
        return 0
    
    def setter(name, value):
        pass

    threaded(getter, setter)
    while True:
        import time
        time.sleep(1)
