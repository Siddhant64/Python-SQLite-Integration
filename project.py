import getpass
import functions as fnc
import sys
from utils import *

user = None

def place_bid(sid):
    global user
    amount = notnullinput("Enter bid amount: ")
    if (fnc.place_bid(user, sid, amount)):
        print("Bid placed successfully")
    else:
        print("Bid amount has to be more than the current highest bid")
    return True


def list_seller_sales(seller):
    data = fnc.list_user_sales(seller)
    printData(data)
    show_followup_menu(data)
    return True


def list_seller_reviews(seller):
    printData(fnc.list_user_reviews(seller))
    return True


def show_followup_menu(data):
    while(True):
        suboption = input("Enter Sale ID for Sub Menu or enter b " + 
                                  "to go back: ")
        if (suboption.lower() == "b"):
            break
        else:
            temp = [x[0].lower() for x in data[1]]
            if suboption.lower() not in temp:
                continue
            suboption = data[1][temp.index(suboption.lower())][0]
            rows = fnc.sale_info(suboption)
            printData(rows)
            menuOptions = ["Place a bid", "List Sales of Seller", "List Reviews of Seller"]
            def place_b():
                return place_bid(suboption)
            def list_s():
                return list_seller_sales(rows[1][0][0])
            def list_r():
                return list_seller_reviews(rows[1][0][0])
            tasks = [place_b, list_s, list_r]
            showMenu(menuOptions, tasks)
            break
    


def product_review(pid):
    rtext = input("Review: ")
    rating = input("Rating (Between 1 and 5): ")
    fnc.product_review(pid, user, rating, rtext)
    return True


def list_reviews(pid):
    printData(fnc.list_reviews(pid))
    return True


def list_sales(pid):
    rows = fnc.list_product_sales(pid)
    printData(rows)
    show_followup_menu(rows)
    return True


'''
product_options

Gives user different options to select
Performs task accoringy to options

Args: suboption

'''
def product_options(suboption):
    menuOptions = ["Write Product Review", "List All Reviews",
                   "List All Active Sales", "Go back to Menu"]
    def product_rev():
        return product_review(suboption)
    def list_rev():
        return list_reviews(suboption)
    def list_s():
        return list_sales(suboption)
    tasks=[product_rev, list_rev, list_s, lambda: True] 
    showMenu(menuOptions, tasks)


def list_products():
    rows=fnc.list_products()
    printData(rows)
    while(True):
        suboption = input("Enter Product ID for Sub Menu or enter b " + 
                                  "to go back: ")
        if (suboption.lower() == "b"):
            break
        else:
            temp = [x[0].lower() for x in rows[1]]
            if suboption.lower() not in temp:
                continue
            suboption = rows[1][temp.index(suboption.lower())][0]
            product_options(suboption)
            break
    return False


def search_sales():
    rows = fnc.search_sales(notnullinput("Search for: "))
    printData(rows)
    show_followup_menu(rows)
    return False


def post_sale():
    pid = input("Product Id: ")
    descr = notnullinput("Description: ")
    endtime = notnullinput("Date & Time ('YYYY-MM-DD HH:mm'): ")  
    cond = notnullinput("Condition: ")
    rprice = input("Reserved Price: ")
    fnc.post_sale(user, pid, endtime, descr, cond, rprice)
    return False


def user_review(reviewee):
    global user
    rtext = notnullinput("Review: ")
    rating = notnullinput("Rating (Between 1 and 5): ")
    fnc.user_review(user, reviewee, rtext, rating)
    return True


def search_users():
    keyword = notnullinput("Enter Keyword to search for User: ")
    rows = fnc.search_users(keyword)
    printData(rows)
    while(True):
        suboption = input("Enter user email for Sub Menu or enter b " + 
                                  "to go back: ")
        if (suboption == "b" or suboption == "B"):
            break
        else:
            temp = [x[0].lower() for x in rows[1]]
            if suboption.lower() not in temp:
                continue
            suboption = rows[1][temp.index(suboption.lower())][0]
            menuOptions = ["Write A Review", "List Active Listings", "List All Reviews"]
            def user_rev():
                return user_review(suboption)
            def list_s():
                return list_seller_sales(suboption)
            def list_r():
                return list_seller_reviews(suboption)
            tasks = [user_rev, list_s, list_r]
            showMenu(menuOptions, tasks)
            break
    return False


def log_out():
    global user
    user = None
    return True


def showAfterLoginMenu():
    menuOptions = ["List Products", "Search for Sales", "Post a Sale", "Search for Users", "Logout"]
    tasks = [list_products, search_sales, post_sale, search_users, log_out]
    showMenu(menuOptions, tasks)


'''
login

Gets email and Password from the user 
Checks email and password if it matches or not.

'''
def login():
    global user
    email = get_username_from_user()
    password = getpass.getpass('Password: ')
    while(not fnc.login(email,password)):
        while(True):
            option = input("Login failed. 1 to try again, 2 to go back: ")
            if option == '1':
                email = get_username_from_user()
                password = getpass.getpass('Password: ')
                break
            elif option == '2':
                return 1
            else:
                print("Valid choices are 1 and 2")
    user = email
    showAfterLoginMenu()
    return False


'''
sign_up

Gets email and Password from the user 
Prompts user for name,city,gender makes sure user enters something and returns the string

'''    
def sign_up():
    global user
    while (True):
        email = get_username_from_user()
        password = get_password_from_user()    
        name = input('Name: ')
        gender = input('Gender (M/F): ')
        city = input('City: ')
        if (not fnc.sign_up(email,password,name,gender,city)):
            print("This email is already in use. Try another email: ")
        else:
            user = email
            showAfterLoginMenu()
            return False


def quit():
    print('Thank you')
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        fnc.connect(sys.argv[1])
        showMenu(["Login", "Signup", "Exit"], [login, sign_up, quit])
    else:
        print("DB name required as argument")
    

