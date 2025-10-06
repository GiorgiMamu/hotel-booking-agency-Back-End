import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hotel_bookings.log'),
        logging.StreamHandler()
    ]
)

#since prices change due to seasons
SEASON_MULTIPLIERS = {
    'winter': 0.8,
    'spring': 1.0,
    'summer': 1.3,
    'fall': 1.1
}

def get_current_season():
    return ['winter', 'winter', 'spring', 'spring', 'spring',
            'summer', 'summer', 'summer', 'fall', 'fall', 'fall', 'winter'][datetime.now().month - 1]


class Room:
    def __init__(self, room_number, room_type, price_per_night, max_guests):
        if room_type not in ['Single', 'Double']:
            raise ValueError("room type must be 'Single' or 'Double'")
        if price_per_night <= 0:
            raise ValueError("price must be positive")
        if max_guests <= 0:
            raise ValueError("max guests must be positive")

        self.room_number = room_number
        self.room_type = room_type
        self.price_per_night = price_per_night
        self.is_available = True
        self.max_guests = max_guests

    def book_room(self):
        if not self.is_available:
            raise ValueError(f"room {self.room_number} is not available")
        self.is_available = False

    def release_room(self):
        self.is_available = True

    def calculate_price(self, nights: int) -> float:
        if nights <= 0:
            raise ValueError("nights must be positive")
        multiplier = SEASON_MULTIPLIERS[get_current_season()]
        return self.price_per_night * multiplier * nights

    def __str__(self):
        status = "available" if self.is_available else "booked"
        return (f"room {self.room_number}({self.room_type}) - {self.price_per_night}$ per night."
                f" max guests: {self.max_guests}, status: {status}.")



class Customer:
    def __init__(self, name, budget):
        if not name or not name.strip():
            raise ValueError("name cannot be empty")
        if budget <= 0:
            raise ValueError("budget must be positive")

        self.name = name
        self.budget = budget
        self.booked_rooms = []
        self.loyalty_points = 0

    def add_room(self, room):
        if not isinstance(room, Room):
            raise ValueError("room must be of type 'Room'")
        self.booked_rooms.append(room)

    def remove_room(self, room):
        if not isinstance(room, Room):
            raise ValueError("room must be of type 'Room'")
        self.booked_rooms.remove(room)


    def pay_for_booking(self, total_price: float) -> bool:
        if total_price <= 0:
            raise ValueError("total_price must be positive")
        if self.budget >= total_price:
            self.budget -= total_price
            self.loyalty_points += int(total_price / 100)
            return True
        return False


    def show_booking_summary(self):
        if not self.booked_rooms:
            raise ValueError("no room bookings")

        summary = f"summary for {self.name}\nBooked rooms:\n"
        for r in self.booked_rooms:
            summary += f"{r.room_number}, {r.price_per_night}$ per night\n"

        return summary




class Hotel:
    def __init__(self, name):
        if not name or not name.strip():
            raise ValueError("name cannot be empty")
        self.name = name
        self.rooms = []
        self.bookings_log = []

    def add_room(self, room):
        if not isinstance(room, Room):
            raise ValueError("room must be of type 'Room'")
        if any(r.room_number == room.room_number for r in self.rooms):
            raise ValueError(f"room {room.room_number} already exists")
        self.rooms.append(room)

    def show_available_rooms(self, room_type=None):
        available = [r for r in self.rooms if r.is_available]
        if room_type:
            if room_type not in ['Single', 'Double']:
                raise ValueError("room type must be 'Single' or 'Double'")
            available = [r for r in available if r.room_type == room_type]
        return available

    def _find_room(self, room_number):
        for room in self.rooms:
            if room.room_number == room_number:
                return room
        raise ValueError(f"room {room_number} not found")


    def calculate_total_booking(self, room_number, nights):
        room = self._find_room(room_number)
        return room.calculate_price(nights)

    def log_booking(self, customer, room, total_price, nights):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'customer': customer.name,
            'room_number': room.room_number,
            'room_type': room.room_type,
            'nights': nights,
            'total_price': round(total_price,2),
            'season': get_current_season()
        }
        self.bookings_log.append(log_entry)
        logging.info(f"---Logged booking: {log_entry}")

    def book_room_for_customer(self, customer, room_number, nights, guests) -> bool:
        if nights <= 0:
            raise ValueError("nights must be positive")
        if guests <= 0:
            raise ValueError("guests must be positive")

        room = self._find_room(room_number)
        if not room.is_available:
            logging.warning(f"Booking failed: room {room.room_number} is not available")
            return False

        if guests > room.max_guests:
            logging.warning(f"Booking filed: {guests} guests exceed max guests of {room.max_guests}")
            return False

        total_price = self.calculate_total_booking(room_number, nights)
        if not customer.pay_for_booking(total_price):
            logging.warning(f"Booking failed: customer {customer.name} does not pay for booking - {total_price:.2f}")
            return False

        room.book_room()
        customer.add_room(room)
        logging.info(f"Booking successful: {customer.name} booked room {room.room_number}")
        self.log_booking(customer, room, total_price, nights)
        return True

    def cancel_booking(self, customer, room_number):
        room = self._find_room(room_number)

        if room not in customer.booked_rooms:
            raise ValueError(f"customer {customer.name} has no booking for room {room_number}")

        room.release_room()
        customer.remove_room(room)

        logging.info(f"Booking cancelled: {customer.name} cancelled Room {room_number}")


if __name__ == "__main__":
    hotel = Hotel("The Grand Budapest Hotel")
    hotel.add_room(Room(101, "Single", 100.0, 1))
    hotel.add_room(Room(102, "Double", 170.0, 2))
    hotel.add_room(Room(103, "Double", 130.0, 3))
    hotel.add_room(Room(104, "Single", 110.0, 1))
    hotel.add_room(Room(105, "Double", 230.0, 2))
    hotel.add_room(Room(106, "Double", 260.0, 3))

    customer1 = Customer("gio", 500.0)
    stay_days = int(input("enter how many days you would like to stay: "))
    guests_num = int(input("enter for how many guests you would like to book: "))

    print("available rooms:")
    for room in hotel.show_available_rooms():
        print(room)

    room_num =int(input("enter room number to book: "))
    hotel.book_room_for_customer(customer1, room_num, stay_days, guests_num)
    hotel.cancel_booking(customer1, room_num)















