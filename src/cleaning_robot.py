import time

DEPLOYMENT = False  # This variable is to understand whether you are deploying on the actual hardware

try:
    import RPi.GPIO as GPIO
    import board
    import IBS
    DEPLOYMENT = True
except:
    import mock.GPIO as GPIO
    import mock.board as board
    import mock.ibs as IBS


class CleaningRobot:

    RECHARGE_LED_PIN = 12
    CLEANING_SYSTEM_PIN = 13
    INFRARED_PIN = 15

    # Wheel motor pins
    PWMA = 16
    AIN2 = 18
    AIN1 = 22

    # Rotation motor pins
    BIN1 = 29
    BIN2 = 31
    PWMB = 32
    STBY = 33

    N = 'N'
    S = 'S'
    E = 'E'
    W = 'W'

    LEFT = 'l'
    RIGHT = 'r'
    FORWARD = 'f'


    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.INFRARED_PIN, GPIO.IN)
        GPIO.setup(self.RECHARGE_LED_PIN, GPIO.OUT)
        GPIO.setup(self.CLEANING_SYSTEM_PIN, GPIO.OUT)

        GPIO.setup(self.PWMA, GPIO.OUT)
        GPIO.setup(self.AIN2, GPIO.OUT)
        GPIO.setup(self.AIN1, GPIO.OUT)
        GPIO.setup(self.PWMB, GPIO.OUT)
        GPIO.setup(self.BIN2, GPIO.OUT)
        GPIO.setup(self.BIN1, GPIO.OUT)
        GPIO.setup(self.STBY, GPIO.OUT)

        ic2 = board.I2C()
        self.ibs = IBS.IBS(ic2)

        self.pos_x = 0
        self.pos_y = 0
        self.heading = "N"

        self.recharge_led_on = False
        self.cleaning_system_on = False

    def initialize_robot(self) -> None:
        self.pos_x = 0
        self.pos_y = 0
        self.heading = self.N
        if self.robot_status() != "(0,0,N)":
            raise CleaningRobotError("error in initialize robot")


    def robot_status(self) -> str:
        return f"({self.pos_x},{self.pos_y},{self.heading})"

    def execute_command(self, command: str) -> str:
        directions = {
            self.N: (0, 1),
            self.S: (0, -1),
            self.E: (1, 0),
            self.W: (-1, 0)
        }
        rotations_left = {
            self.N: self.W,
            self.W: self.S,
            self.S: self.E,
            self.E: self.N
        }
        rotations_right = {
            self.N: self.E,
            self.E: self.S,
            self.S: self.W,
            self.W: self.N
        }
        if self.check_battery() <= 10:
            return "!" + self.robot_status()
        if command == self.FORWARD:
            if self.obstacle_found():
                self.pos_y = int(self.pos_y)
                return f"({self.pos_x},{self.pos_y},{self.heading})({self.pos_x},{self.pos_y + 1})"

            else:
                self.activate_wheel_motor()
                dx, dy = directions[self.heading]
                self.pos_x += dx
                self.pos_y += dy

        elif command == self.LEFT:
            self.activate_rotation_motor(self.LEFT)
            self.heading = rotations_left[self.heading]

        elif command == self.RIGHT:
            self.activate_rotation_motor(self.RIGHT)
            self.heading = rotations_right[self.heading]

        else:
            raise ValueError("Invalid command")

        return self.robot_status()

    def obstacle_found(self) -> bool:
        return GPIO.input(self.INFRARED_PIN)

    def manage_cleaning_system(self) -> None:
        charge_left = self.check_battery()
        if charge_left < 0 or charge_left > 100:
            raise CleaningRobotError("charge value must be between 0 and 100")
        if charge_left > 10:
            GPIO.output(self.CLEANING_SYSTEM_PIN, True)
            GPIO.output(self.RECHARGE_LED_PIN, False)
            self.cleaning_system_on = True
            self.recharge_led_on = False
        else:
            GPIO.output(self.RECHARGE_LED_PIN, True)
            GPIO.output(self.CLEANING_SYSTEM_PIN, False)
            self.recharge_led_on = True
            self.cleaning_system_on = False

    def activate_wheel_motor(self) -> None:
        """
        Let the robot move forward by activating its wheel motor
        """
        # Drive the motor clockwise
        GPIO.output(self.AIN1, GPIO.HIGH)
        GPIO.output(self.AIN2, GPIO.LOW)
        # Set the motor speed
        GPIO.output(self.PWMA, GPIO.HIGH)
        # Disable STBY
        GPIO.output(self.STBY, GPIO.HIGH)

        if DEPLOYMENT: # Sleep only if you are deploying on the actual hardware
            time.sleep(1) # Wait for the motor to actually move

        # Stop the motor
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.LOW)
        GPIO.output(self.PWMA, GPIO.LOW)
        GPIO.output(self.STBY, GPIO.LOW)

    def activate_rotation_motor(self, direction) -> None:
        """
        Let the robot rotate towards a given direction
        :param direction: "l" to turn left, "r" to turn right
        """
        if direction == self.LEFT:
            GPIO.output(self.BIN1, GPIO.HIGH)
            GPIO.output(self.BIN2, GPIO.LOW)
        elif direction == self.RIGHT:
            GPIO.output(self.BIN1, GPIO.LOW)
            GPIO.output(self.BIN2, GPIO.HIGH)

        GPIO.output(self.PWMB, GPIO.HIGH)
        GPIO.output(self.STBY, GPIO.HIGH)

        if DEPLOYMENT:  # Sleep only if you are deploying on the actual hardware
            time.sleep(1)  # Wait for the motor to actually move

        # Stop the motor
        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.LOW)
        GPIO.output(self.PWMB, GPIO.LOW)
        GPIO.output(self.STBY, GPIO.LOW)

    def check_battery(self) -> int:
        charge_left = self.ibs.get_charge_left()
        if charge_left is None:
            return 0
        return charge_left

class CleaningRobotError(Exception):
    pass
