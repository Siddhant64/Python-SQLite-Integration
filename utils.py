import re
import getpass

def printData(data):
    header = data[0]
    rows = data[1]
    for item in header:
        print(item, end = ' ')
    print("\n------------------")
    for row in rows:
        for rowvalue in row:
            print(rowvalue, end=' ')
        print()


'''
get_username_from_user

Prompts user for email, makes sure it is valid and returns the email

Returns:
    email: String representing user email
'''
def get_username_from_user():
    email = input("Email: ")
    # http://regexlib.com/Search.aspx?k=email&c=-1&m=-1&ps=20
    while(not re.match("^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$", email)):
        email = input("Enter valid email: ")
    return email
 

'''
get_password_from_user

Prompts user for password, makes sure it is valid and returns the password

Returns:
    password: String representing password
'''    
def get_password_from_user():
    password = getpass.getpass("Password: ")
    while(not re.match("^[A-Za-z0-9_]*$", password)):
        password = input("Enter valid password: ")
    return password


'''
notnullinput

Prompts user for input, makes sure user enters something and returns the string

Args: prompt
      
Returns:
    input: String 
'''
def notnullinput(prompt):
    text = input(prompt)
    while (not text):
        print("You must enter something")
        input(prompt)
    return text


'''
showMenu

    Helper function to print out menus.
    
    Arguments:
        menuOptions: List of string representing menu options
        taskList: callback functions for each menu option. Callback functions
                  must return True if they want the menu to not show again

'''
def showMenu(menuOptions, taskList):
    while (True):
        for i in range(len(menuOptions)):
            print(str(i + 1) + ": " + menuOptions[i])
        option = input("Enter a choice: ")
        try:
            int(option)
        except:
            continue
        if not int(option) - 1 in range(len(menuOptions)):
            continue
        if (taskList[int(option) - 1]()):
            break
