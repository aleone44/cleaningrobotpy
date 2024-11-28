from unittest import TestCase
from unittest.mock import Mock, patch, call

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot


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

