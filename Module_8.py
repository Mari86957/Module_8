from datetime import datetime, date, timedelta
from collections import UserDict
import pickle

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

class Field:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)
    

class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not (len(value) == 10 and value.isdigit()):
            raise ValueError("Phone number must be 10 digits and contain only numbers.")
        super().__init__(value)
		

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))
    def remove_phone(self, phone_number):
        phone_to_remove = self.find_phone(phone_number)
        if phone_to_remove:
             self.phones.remove(phone_to_remove)
    def edit_phone(self, old_number, new_number):
        phone_to_edit = self.find_phone(old_number)
        if not phone_to_edit:
            raise ValueError("Old phone not found")
        self.add_phone(new_number)
        self.remove_phone(old_number)
    def find_phone(self, phone_number):
         for phone in self.phones:
              if phone.value == phone_number:
                   return phone 
         else:
            return None
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    def add_birthday(self, birthday):
            self.birthday = Birthday(birthday)


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
    def find(self, name):
        return self.data.get(name)
    def delete(self, name):
        del self.data[name]
    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())
    def find_next_weekday(self, start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)
    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday
    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()
        
        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_date.replace(year=today.year + 1)

                if 0 <= (birthday_this_year - today).days <= days:
                    congratulation_date = birthday_this_year
                    adjusted_date = self.adjust_for_weekend(congratulation_date)
                    
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": adjusted_date.strftime("%d.%m.%Y") 
                    })

        return upcoming_birthdays if upcoming_birthdays else "No upcoming birthdays."




def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(add_contact):
    def inner(*args, **kwargs):
        try:
            return add_contact(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "This contact does not exist."
        except IndexError:
            return "Enter user name."
    return inner


book = AddressBook()

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            self.value = value
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

       

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return f"Phone number changed for {name}."

@input_error
def phone_username(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    phones = ', '.join(phone.value for phone in record.phones)
    return f"{name}: {phones}."

@input_error
def add_birthday(args, book):
    name, date, *_ = args
    record = book.find(name)
    if record is None:
            raise KeyError
    record.add_birthday(date)
    return f"Birthday added for {name}."

@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError("This contact does not exist.")
    if record.birthday is None:
        return f"No birthday information for {name}."
    return f"{name}'s birthday is on {record.birthday.value}."

@input_error
def birthdays(args, book):
    return book.get_upcoming_birthdays()

@input_error
def show_all(contacts):
    return "\n".join(f"{name}: {phone}" for name, phone in contacts.items())


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print (change_contact(args, book))
        elif command == "phone":
            print(phone_username(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")
    save_data(book)  
if __name__ == "__main__":
    main()