from unittest import TestCase
from unittest.mock import Mock, patch, call

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot
from src.cleaning_robot import CleaningRobotError

class TestCleaningRobot(TestCase):

    @patch.object(GPIO, "input")
    def test_something(self, mock_object: Mock):
        # This is an example of test where I want to mock the GPIO.input() function
        pass

    def test_initialize_robot(self):
        cr = CleaningRobot()
        cr.initialize_robot()
        self.assertEqual(cr.pos_x, 0)
        self.assertEqual(cr.pos_y, 0)
        self.assertEqual(cr.heading, CleaningRobot.N)

    def test_robot_status(self):
        cr= CleaningRobot()
        cr.initialize_robot()
        self.assertEqual(cr.robot_status(),"(0,0,N)")

    def test_initialize_robot_error(self):
        cr = CleaningRobot()
        with patch.object(cr, "robot_status", return_value="(1,0,N)"):
            with self.assertRaises(CleaningRobotError):
                cr.initialize_robot()

    @patch.object(GPIO, "output")
    @patch.object(IBS, "get_charge_left")
    def test_manage_cleaning_system_w_11_percent_battery(self, mock_get_charge_left, mock_gpio_output):
        cr = CleaningRobot()
        mock_get_charge_left.return_value = 11
        cr.manage_cleaning_system()
        mock_gpio_output.assert_has_calls([
            call(cr.CLEANING_SYSTEM_PIN, True),
            call(cr.RECHARGE_LED_PIN, False)
        ])
        self.assertTrue(cr.cleaning_system_on)
        self.assertFalse(cr.recharge_led_on)

    @patch.object(GPIO, "output")
    @patch.object(IBS, "get_charge_left")
    def test_manage_cleaning_system_w_10_percent_battery(self, mock_get_charge_left, mock_gpio_output):
        cr = CleaningRobot()
        mock_get_charge_left.return_value = 10
        cr.manage_cleaning_system()
        mock_gpio_output.assert_has_calls([
            call(cr.RECHARGE_LED_PIN, True),
            call(cr.CLEANING_SYSTEM_PIN, False)
        ])
        self.assertTrue(cr.recharge_led_on)
        self.assertFalse(cr.cleaning_system_on)

    @patch.object(IBS, "get_charge_left")
    def test_charge_more_than_100(self, mock_get_charge_left):
        cr = CleaningRobot()
        mock_get_charge_left.return_value = 101
        with self.assertRaises(CleaningRobotError) as context:
            cr.manage_cleaning_system()
        self.assertEqual(str(context.exception), "charge value must be between 0 and 100")

    @patch.object(IBS, "get_charge_left")
    def test_charge_less_than_0(self, mock_get_charge_left):
        cr = CleaningRobot()
        mock_get_charge_left.return_value = -1
        with self.assertRaises(CleaningRobotError) as context:
            cr.manage_cleaning_system()
        self.assertEqual(str(context.exception), "charge value must be between 0 and 100")

    def test_execute_command_forward(self):
        cr = CleaningRobot()
        cr.initialize_robot()
        with patch.object(cr, "activate_wheel_motor") as mock_wheel_motor:
            new_state = cr.execute_command("f")
            mock_wheel_motor.assert_called_once()
            self.assertEqual(new_state, "(0,1,N)")
            self.assertEqual(cr.robot_status(), "(0,1,N)")

    def test_execute_command_turn_right(self):
        cr = CleaningRobot()
        cr.initialize_robot()
        with patch.object(cr, "activate_rotation_motor") as mock_rotation_motor:
            new_state = cr.execute_command("r")
            mock_rotation_motor.assert_called_once_with("r")
            self.assertEqual(new_state, "(0,0,E)")
            self.assertEqual(cr.robot_status(), "(0,0,E)")

    def test_execute_command_turn_left(self):
        cr = CleaningRobot()
        cr.initialize_robot()
        with patch.object(cr, "activate_rotation_motor") as mock_rotation_motor:
            new_state = cr.execute_command("l")
            mock_rotation_motor.assert_called_once_with("l")
            self.assertEqual(new_state, "(0,0,W)")
            self.assertEqual(cr.robot_status(), "(0,0,W)")

    def test_execute_command_error(self):
        cr = CleaningRobot()
        cr.initialize_robot()
        with self.assertRaises(ValueError) as context:
            cr.execute_command("b")  # Invalid command
        self.assertEqual(str(context.exception), "Invalid command")
        self.assertEqual(cr.robot_status(), "(0,0,N)")

    def test_robot_movement_3_2_E(self):
        cr = CleaningRobot()
        cr.initialize_robot()
        cr = CleaningRobot()
        cr.initialize_robot()
        cr.execute_command("f")
        cr.execute_command("f")
        cr.execute_command("r")
        cr.execute_command("f")
        cr.execute_command("f")
        cr.execute_command("f")
        final_state = cr.robot_status()

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(CleaningRobot, "activate_rotation_motor")
    def test_robot_full_rotation_returns_to_start(self, mock_rotation_motor, mock_wheel_motor):
        cr = CleaningRobot()
        cr.initialize_robot()

        cr.execute_command("f")
        cr.execute_command("r")
        cr.execute_command("f")
        cr.execute_command("r")
        cr.execute_command("f")
        cr.execute_command("r")
        cr.execute_command("f")
        cr.execute_command("r")

        self.assertEqual(cr.robot_status(), "(0,0,N)")
        mock_wheel_motor.assert_called()
        mock_rotation_motor.assert_called()

    @patch.object(GPIO,"input")
    def test_obstacle_found(self, mock_obstacle: Mock):
        cr = CleaningRobot()
        mock_obstacle.return_value = True
        self.assertTrue(cr.obstacle_found())





