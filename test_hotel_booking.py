import unittest
from hotel_booking import Room, Customer, Hotel

class TestRoom(unittest.TestCase):
    def setUp(self):
        self.room = Room(101, "Single", 100.0, 1)

    def test_invalid_room_type(self):
        with self.assertRaises(ValueError):
            Room(102, "Triple", 100.0, 3)

    def test_book_room(self):
        self.room.book_room()
        self.assertFalse(self.room.is_available)

    def test_book_already_booked_room(self):
        self.room.book_room()
        with self.assertRaises(ValueError):
            self.room.book_room()


class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.customer = Customer("lasha", 500.0)
        self.room = Room(101, "Single", 100.0, 1)

    def test_invalid_name(self):
        with self.assertRaises(ValueError):
            Customer("", 500.0)
        with self.assertRaises(ValueError):
            Customer("   ", 500.0)

    def test_remove_nonexistent_room(self):
        with self.assertRaises(ValueError):
            self.customer.remove_room(self.room)

    #asked in task
    def test_pay_for_booking_sufficient_budget(self):
        initial_budget = self.customer.budget
        result = self.customer.pay_for_booking(200.0)
        self.assertTrue(result)
        self.assertEqual(self.customer.budget, initial_budget - 200.0)
        self.assertEqual(self.customer.loyalty_points, 2)

    def test_pay_for_booking_insufficient_budget(self):
        initial_budget = self.customer.budget
        result = self.customer.pay_for_booking(600.0)
        self.assertFalse(result)
        self.assertEqual(self.customer.budget, initial_budget)
        self.assertEqual(self.customer.loyalty_points, 0)


class TestHotel(unittest.TestCase):
    def setUp(self):
        self.hotel = Hotel("Hotel")
        self.room1 = Room(101, "Single", 100.0, 1)
        self.room2 = Room(102, "Double", 150.0, 2)
        self.hotel.add_room(self.room1)
        self.hotel.add_room(self.room2)
        self.customer = Customer("lasha", 500.0)

    def test_add_duplicate_room(self):
        with self.assertRaises(ValueError):
            self.hotel.add_room(Room(101, "Single", 100.0, 1))

    def test_calculate_total_booking(self):
        total = self.hotel.calculate_total_booking(101, 2)
        expected = self.room1.calculate_price(2)
        self.assertEqual(total, expected)

    #asked in task
    def test_book_room_for_customer_success(self):
        result = self.hotel.book_room_for_customer(self.customer, 101, 2, 1)
        self.assertTrue(result)
        self.assertFalse(self.room1.is_available)
        self.assertIn(self.room1, self.customer.booked_rooms)
        self.assertEqual(len(self.hotel.bookings_log), 1)

    def test_book_room_for_customer_unavailable(self):
        self.room1.book_room()
        result = self.hotel.book_room_for_customer(self.customer, 101, 2, 1)
        self.assertFalse(result)