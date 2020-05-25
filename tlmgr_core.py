# Core helper functions

def ask_user_confirmation():
    """ Ask for user confirmation """
    user_confirm = str(input("Are you sure you wanna proceed? (YES/n)"))
    while user_confirm != "YES" and user_confirm != "n":
        user_confirm = str(input("Not a valid answer!. Proceed? (YES/n)"))
    if user_confirm == 'n':
        logging.info("\nOperation has been canceled!!\n")
        user_confirm = False
    else:
        user_confirm = True
    return user_confirm
