from mock.board import I2C

class IBS:

    def __init__(self, i2c: I2C, address: int = 0x77):
        pass

    def get_charge_left(self) -> int:
        """
        Returns the charge left.
        :return: the charge left (i.e., a percentage value from 0 to 100)
        """
        pass

    def get_water_level(self) -> int:
        pass


    def get_dirty_level(self) -> int:
        pass


