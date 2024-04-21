from collections import UserDict
from datetime import datetime
from datetime import timedelta
import pickle


class Field:
    """This class turns input into Field object"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """This class saves name given by user"""
    pass


class Phone(Field):
    """This class saves phone number given by user
        validates if the one has 10 digits
        if not set given value to None and print a message"""
    def __init__(self, value: str):
        super().__init__(value)
        if value.isdigit() and (value.__len__() != 10):
            self.value = None
            print("-----Phone number should have 10 digits-----")


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        try:
            self.birthday = datetime.strptime(value, "%d.%m.%Y")
            if self.birthday > datetime.now():
                self.birthday = None
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
    
    
class Record:
    """This class creates record of given contact which contains:
            - name as Name obj
            - list of phone numbers as Phone objects"""
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone)) 

    def add_birthday(self, birthday):
        """add Birthday object (which contains datetime object info) 
        to Record of existing contact"""
        today = datetime.today().date()
        birthday_obj = datetime.strptime(birthday, "%d.%m.%Y").date()
        if birthday_obj > today:
            raise ValueError
        self.birthday = Birthday(birthday)

    def remove_phone(self, phone):
        """remove given phone number from list
        with phone numbers for this contact.
            Cach exception if one is not in the list"""
        try:
            self.phones.remove(phone)
        except ValueError:
            return "Phone not found"
        
    def edit_phone(self, old_phone, new_phone):
        """delete given phone number if in the list
        and add another one.
            If numer not in the list do nothing"""
        for phone in self.phones:
            if phone.__str__().strip() == old_phone.strip():
                self.phones.remove(phone)
                self.phones.append(Phone(new_phone))

    def find_phone(self, phone):
        """Return phone number if in the list
        else return message for user"""
        for p in self.phones:
            if phone.strip() == p.__str__().strip():
                return p
        return "Phone not found"

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    """Class to interact with contact.
        Creates UserDict with Name and Record of given user"""
    def add_record(self, record: Record):
        self.data[record.name.__str__()] = record

    def find(self, name):
        """Return Record of contact if one is in self.data
            requires name of contact"""
        for _, record in self.data.items():
            if name.__str__().lower() == record.name.__str__().lower():
                return record
        return "Contact not found"
    
    def delete(self, name):
        """Delete contact.
            Reauires name to search contact to delete."""
        for name_obj, _ in self.data.items():
            if name_obj.__str__().lower() == name.lower():
                self.data.__delitem__(name_obj)
                break

    def get_upcoming_birthdays(self):
        users = self.data
        today = datetime.today().date()
        birthday_is_in_this_week = None
        congratulation_date = None
        weekdays = range(0, 5)
        to_cogradulate = []

        #parse all given users and their birthdays
        for name in users:
            birthday = users[name].birthday
            if birthday:
                try:
                    birthday_to_datetime_obj = datetime.strptime(birthday.value, "%d.%m.%Y").date()
                except ValueError:
                    return "birthday should be in format: DD.MM.YYYY. Try again"
                birthday_this_year = datetime(year=today.year, month=birthday_to_datetime_obj.month, day=birthday_to_datetime_obj.day).date()
                birthday_is_in_this_week = (today + timedelta(days=7)) > birthday_this_year >= today

                """check for the next seven days if there are any birthdays. 
                If yes check if they are on weekdays and scedule the congradulation.
                If birthday on weekend scedule congradulations for next Monday"""
                if birthday_is_in_this_week:
                        congratulation_date = birthday_this_year
                        if birthday_this_year.weekday in weekdays:
                            to_cogradulate.append({f"{name}" : f"{congratulation_date}"},)
                        else:
                                while congratulation_date.weekday() not in weekdays:
                                        congratulation_date += timedelta(days=1)

                                to_cogradulate.append({f"{name}" : f"{congratulation_date}"},)
        return to_cogradulate
    
    def __str__(self) -> str:
        contacts = []
        for contact in self.data:
            contacts.append(f'{self.data[contact].__str__()}')
        return f'{contacts}'
    

def input_error(func):
    """Decorator, caches ValueError, IndexError, KeyError
        and gives informative message to user acording to error"""
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            if func.__name__ == "add_contact":
                return "To add contact type name and phone number after comand 'add'."
            elif func.__name__ == "change_username_phone":
                return "To change user phone type:change 'Name' 'old phone' 'new phone'"
            elif func.__name__ == "add_birthday":
                return "Birthday should be in DD.MM.YYYY format and can not be in future"
        except IndexError:
            return "Enter name"
        except KeyError:
            return "No user with this name found"
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book:AddressBook):
    name, phone, *_ = args
    record = Record(name)
    if len(phone) != 10:
        return "Phone nummber should contain 10 digits"
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added."

@input_error
def change_username_phone(args, book: AddressBook):
    if not args:
        return "To change user phone type:change 'Name' 'old phone' 'new phone'"
    name, old_phone, new_phone, *_ = args
    for user in book:
        if name == user and len(old_phone) == 10 and len(new_phone) == 10:
            book[name].edit_phone(old_phone, new_phone)
            return "Contact phone updated"
    return "Contact isn't found or incorrect phone input"

@input_error
def phone_username(args, book:AddressBook):
    name = args[0]
    phones = []
    for phone in book[name].phones:
        phones.append(phone.value)
    return f'{name}: {phones}'

@input_error
def show_all_phones(book):
    return book

@input_error
def add_birthday(args, book: AddressBook):
    book[args[0]].add_birthday(args[1])
    return f'Birthday "{args[1]}" is added to {args[0]}'

@input_error
def show_birthday(args, book):
    birthday = book[args[0]].birthday
    if birthday:
        return f"{args[0]}'s birthday is {birthday}"
    return f"No birthday in book for {args[0]}"

@input_error
def birthdays(book: AddressBook):
    if book.get_upcoming_birthdays():
        return book.get_upcoming_birthdays()
    return "No birthdays in upcoming week"

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():
    """Main starts the bot for saving phone numbers"""
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)


        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book)) ##############

        elif command == "change":
            print(change_username_phone(args, book)) ##############

        elif command == "phone":
            print(phone_username(args, book)) ##############

        elif command == "all":
            print(show_all_phones(book)) ##############

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()