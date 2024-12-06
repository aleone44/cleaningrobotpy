from unittest import TestCase
from unittest.mock import Mock, patch, call

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot
from src.cleaning_robot import CleaningRobotError

class TestCleaningRobot(TestCase):

    def setUp(self):
        self.cr=CleaningRobot()

    @patch.object(GPIO, "input")
    def test_something(self, mock_object: Mock):
        # This is an example of test where I want to mock the GPIO.input() function
        pass

    def test_initialize_robot_x(self):
        self.cr.initialize_robot()
        self.assertEqual(self.cr.pos_x, 0)

    def test_initialize_robot_y(self):
        self.cr.initialize_robot()
        self.assertEqual(self.cr.pos_y, 0)

    def test_initialize_robot_heading(self):
        self.cr.initialize_robot()
        self.assertEqual(self.cr.heading, CleaningRobot.N)

    def test_robot_status(self):
        cr= CleaningRobot()
        cr.initialize_robot()
        self.assertEqual(self.cr.robot_status(),"(0,0,N)")

    @patch("src.cleaning_robot.CleaningRobot.robot_status")
    def test_initialize_robot_error(self, mock_robot_status):
        mock_robot_status.return_value = "(-1,0,N)"
        with self.assertRaises(CleaningRobotError):
            self.cr.initialize_robot()


    @patch.object(IBS, "get_charge_left")
    def test_execute_command_enough_battery_led_off(self, mock_get_charge_left):
        mock_get_charge_left.return_value = 11
        self.cr.manage_cleaning_system()
        self.assertFalse(self.cr.recharge_led_on)

    @patch.object(IBS, "get_charge_left")
    def test_execute_command_enough_battery_cleaning_system_on(self, mock_get_charge_left):
        mock_get_charge_left.return_value = 11
        self.cr.manage_cleaning_system()
        self.assertTrue(self.cr.cleaning_system_on)


    @patch.object(IBS, "get_charge_left")
    def test_execute_command_low_battery_led_on(self, mock_get_charge_left):
        mock_get_charge_left.return_value = 9
        self.cr.manage_cleaning_system()
        self.assertTrue(self.cr.recharge_led_on)

    @patch.object(IBS, "get_charge_left")
    def test_execute_command_low_battery_cleaning_system_off(self, mock_get_charge_left):
        mock_get_charge_left.return_value = 9
        self.cr.manage_cleaning_system()
        self.assertFalse(self.cr.cleaning_system_on)

    @patch.object(IBS, "get_charge_left")
    def test_charge_more_than_100(self, mock_get_charge_left):
        mock_get_charge_left.return_value = 101
        with self.assertRaises(CleaningRobotError) as context:
            self.cr.manage_cleaning_system()
        self.assertEqual(str(context.exception), "charge value must be between 0 and 100")

    @patch.object(IBS, "get_charge_left")
    def test_charge_less_than_0(self, mock_get_charge_left):
        mock_get_charge_left.return_value = -1
        with self.assertRaises(CleaningRobotError) as context:
            self.cr.manage_cleaning_system()
        self.assertEqual(str(context.exception), "charge value must be between 0 and 100")

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(CleaningRobot, "check_battery", return_value=11)
    @patch.object(CleaningRobot, "obstacle_found", return_value=False)
    def test_check_battery_called(self, mock_obstacle_found, mock_check_battery, mock_wheel_motor):
        self.cr.initialize_robot()
        self.cr.execute_command("f")
        mock_check_battery.assert_called_once()

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(CleaningRobot, "check_battery", return_value=11)
    @patch.object(CleaningRobot, "obstacle_found", return_value=True)
    def test_obstacle_found_called(self, mock_obstacle_found, mock_check_battery, mock_wheel_motor):
        self.cr.initialize_robot()
        self.cr.execute_command("f")
        mock_obstacle_found.assert_called_once()

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(CleaningRobot, "check_battery", return_value=11)
    @patch.object(CleaningRobot, "obstacle_found", return_value=False)
    def test_forward_wheel_motor_called(self, mock_obstacle_found, mock_check_battery, mock_wheel_motor):
        self.cr.initialize_robot()
        self.cr.execute_command("f")
        mock_wheel_motor.assert_called_once()

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(CleaningRobot, "check_battery", return_value=11)
    @patch.object(CleaningRobot, "obstacle_found", return_value=False)
    def test_execute_command_forward(self, mock_obstacle_found, mock_check_battery, mock_wheel_motor):
        self.cr.initialize_robot()
        self.cr.execute_command("f")
        self.assertEqual(self.cr.robot_status(), "(0,1,N)")

    @patch.object(CleaningRobot, "activate_rotation_motor")
    @patch.object(CleaningRobot, "check_battery", return_value=99)
    @patch.object(CleaningRobot, "obstacle_found", return_value=False)
    def test_execute_command_turn_right(self, mock_obstacle_found, mock_check_battery, mock_rotation_motor):
        self.cr.initialize_robot()
        self.cr.execute_command("r")
        self.assertEqual(self.cr.robot_status(), "(0,0,E)")

    @patch.object(CleaningRobot, "activate_rotation_motor")
    @patch.object(CleaningRobot, "check_battery", return_value=99)
    @patch.object(CleaningRobot, "obstacle_found", return_value=False)
    def test_execute_command_turn_left(self, mock_obstacle_found, mock_check_battery, mock_rotation_motor):
        self.cr.initialize_robot()
        self.cr.execute_command("l")
        self.assertEqual(self.cr.robot_status(), "(0,0,W)")

    @patch.object(CleaningRobot, "check_battery", return_value=98)
    @patch.object(CleaningRobot, "obstacle_found", return_value=False)
    def test_execute_command_error(self, mock_obstacle_found, mock_check_battery):
        self.cr.initialize_robot()
        with self.assertRaises(ValueError) as context:
            self.cr.execute_command("b")
        self.assertEqual(self.cr.robot_status(), "(0,0,N)")

    @patch.object(CleaningRobot, "activate_rotation_motor")
    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(CleaningRobot, "check_battery", return_value=98)
    @patch.object(CleaningRobot, "obstacle_found", return_value=False)
    def test_robot_movement_3_2_E(self,mock_obstacle_found, mock_check_battery, mock_wheel_motor,mock_rotation_motor):
        self.cr.initialize_robot()
        self.cr.execute_command("f")
        self.cr.execute_command("f")
        self.cr.execute_command("r")
        self.cr.execute_command("f")
        self.cr.execute_command("f")
        self.cr.execute_command("f")
        final_state = self.cr.robot_status()
        self.assertEqual(final_state, "(3,2,E)")

    @patch.object(CleaningRobot, "activate_rotation_motor")
    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(CleaningRobot, "check_battery", return_value=97)
    @patch.object(CleaningRobot, "obstacle_found", return_value=False)
    def test_robot_full_rotation_returns_to_start_wheel_motor_called(self, mock_obstacle_found, mock_check_battery,
                                                                     mock_wheel_motor,
                                                                     mock_rotation_motor):
        self.cr.initialize_robot()
        self.cr.execute_command("f")
        self.cr.execute_command("r")
        self.cr.execute_command("f")
        self.cr.execute_command("r")
        self.cr.execute_command("f")
        self.cr.execute_command("r")
        self.cr.execute_command("f")
        self.cr.execute_command("r")
        mock_wheel_motor.assert_called()

    @patch.object(CleaningRobot, "activate_rotation_motor")
    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(CleaningRobot, "check_battery", return_value=97)
    @patch.object(CleaningRobot, "obstacle_found", return_value=False)
    def test_robot_full_rotation_returns_to_start_rotation_motor_called(self, mock_obstacle_found, mock_check_battery, mock_wheel_motor,
                                                  mock_rotation_motor):
        self.cr.initialize_robot()
        self.cr.execute_command("f")
        self.cr.execute_command("r")
        self.cr.execute_command("f")
        self.cr.execute_command("r")
        self.cr.execute_command("f")
        self.cr.execute_command("r")
        self.cr.execute_command("f")
        self.cr.execute_command("r")
        mock_rotation_motor.assert_called()

    @patch.object(CleaningRobot, "activate_rotation_motor")
    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(CleaningRobot, "check_battery", return_value=97)
    @patch.object(CleaningRobot, "obstacle_found", return_value=False)
    def test_robot_full_rotation_returns_to_start(self,mock_obstacle_found, mock_check_battery, mock_wheel_motor,mock_rotation_motor):
        self.cr.initialize_robot()
        self.cr.execute_command("f")
        self.cr.execute_command("r")
        self.cr.execute_command("f")
        self.cr.execute_command("r")
        self.cr.execute_command("f")
        self.cr.execute_command("r")
        self.cr.execute_command("f")
        self.cr.execute_command("r")
        self.assertEqual(self.cr.robot_status(), "(0,0,N)")

    @patch.object(CleaningRobot, "check_battery", return_value=11)
    @patch.object(GPIO, "input")
    def test_obstacle_found(self, mock_obstacle: Mock, mock_check_battery):
        mock_obstacle.return_value = True
        self.assertTrue(self.cr.obstacle_found())

    @patch.object(CleaningRobot, "check_battery", return_value=11)
    @patch.object(GPIO,"input")
    def test_obstacle_found_check_position(self, mock_obstacle: Mock, mock_check_battery):
        self.cr.initialize_robot()
        mock_obstacle.return_value = True
        self.assertEqual(self.cr.execute_command("f"), "(0,0,N)(0,1)")

    @patch.object(CleaningRobot, "check_battery", return_value=10)
    def test_battery_low_robot_dont_move(self, mock_check_battery):
        self.cr.initialize_robot()
        status = self.cr.robot_status()
        self.cr.execute_command("f")
        self.assertEqual(self.cr.robot_status(), status)



    
