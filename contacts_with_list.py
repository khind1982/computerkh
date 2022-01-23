# Each contact will be rendered as a dictionary
# Contacts should include first name, last name, full name, company, phone number, e-mail address
# Contacts can be organised in a dictionary (i.e. dictionary of dictionaries) - each key of the outer dictionary will be the name of the contact
# Add contacts: Go through a list of contact details which is supplied by the user
# Delete contacts: Search the list for 'name' keys with a particular value and delete
# Search contacts: Same functionality as for deletion
# Sort contacts: Sort the keys in the dictionary
# How can the contacts list be saved for later (i.e. to avoid having to add them all again?)

exit = False

contacts = [{
    'first_name' : 'Kevin',
    'last_name' : 'Hind',
    'full_name' : 'Hind, Kevin',
    'company' : 'Clarivate',
    'phone' : '(01223) 271259',
    'e-mail' : 'kevin.hind@proquest.com'
    }]


def menu_of_options():
    print(
        """
        ===== MENU =====
        1 - Print the menu
        2 - Print the contacts list
        3 - Add a contact
        4 - Delete or Edit a contact by name
        5 - Sort the contacts list by key
        6 - Show a list of names
        0 - Exit
        """)


def add_a_contact(contacts):
    first_name = input("Enter the contact's first name: ")
    last_name = input("Enter the contact's last name: ")
    company = input("Enter the name of the company the contact works for: ")
    phone = input("Enter the contact's phone number: ")
    email = input("Enter the contact's e-mail address: ")
    contacts.append({
        'first_name' : first_name,
        'last_name' : last_name,
        'full_name' : last_name + ', ' + first_name,
        'company' : company,
        'phone' : phone,
        'e-mail' : email
        })
    return contacts


def edit_or_delete_contact(contacts):
    # This mixes presentation with logic
    # Should separate user input functions from functions that perform actions on the list
    # The menu should be envisaged as a separate component
    to_edit = input(
            """Enter the name of a contact
            in the form last name, first_name: """).strip()
    action = input(
        """
        Select from one of the following options:
        To delete a contact, type '1'
        To edit a contact, type '2'
        : """)
    while True:
        if action == '1':
            contact_to_delete = filter_contact(contacts, 'full_name', to_edit)[0]
            contacts.remove(contact_to_delete)
            break
        elif action == '2':
            contact_to_edit = filter_contact(contacts, 'full_name', to_edit)[0]
            contacts = edit_contact(contacts, contact_to_edit)
            break
        else:
            print("Unknown action.  Try again")


def edit_contact(contacts, contact_to_edit):
    selection = input(
    """
    Which contact field do you want to edit?
    Select from: first_name, last_name, company, phone, e-mail
    To select 'first_name', type '1'
    To select 'last_name', type '2'
    To select 'company', type '3'
    To select 'phone', type '4'
    To select 'e-mail', type '5'
    : """
    )

    number_to_field = {
        '1' : 'first_name',
        '2' : 'last_name',
        '3' : 'company',
        '4' : 'phone',
        '5' : 'e-mail'
    }

    field_to_edit = number_to_field[selection]

    new_value = input("Type replacement text for this field: ")
    contact_to_edit[field_to_edit] = new_value
    if field_to_edit in ['first_name', 'last_name']:
        contact_to_edit['full_name'] = contact_to_edit['last_name'] + ', ' + contact_to_edit['first_name']
    return contacts


def filter_contact(contacts, field, value):
    return [contact for contact in contacts if contact[field] == value]


while not exit:
    # Where user is required to type words, don't mix case
    # use numbers for basic options
    print(menu_of_options())
    selection = input("Enter a number from the menu: ")

    if selection == '1':
        print(menu_of_options())
    elif selection == '2':
        print(contacts)
    elif selection == '3':
        contacts = add_a_contact(contacts)
    elif selection == '4':
        edit_or_delete_contact(contacts)
    elif selection == '5':
        contacts = dict(sorted(contacts.items()))
    elif selection == '6':
        print(contacts.keys())
    elif selection == '0':
        exit = True
    else:
        "Please enter a number from the menu."
