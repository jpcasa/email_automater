import os
import json
from colorama import Fore, Style

from .weekly import Weekly

class Automator:
    """Automator Class."""

    def __init__(self, config):
        self.config = config
        self.running = True
        self.options = {
            "a": "Create Weekly Emails",
            "b": "Create Registered Reseller Emails",
            "c": "Approve Newsletter",
            "q": "Quit Program"
        }
        self.regions = {
            "a": "LATAM",
            "b": "NA",
            "c": "Go Back",
            "q": "Quit"
        }


    def program(self):
        """Main Program."""
        while self.running:

            self.welcome_message()
            self.show_menu(self.options)
            choice = input('Enter your choice: ').strip().lower()

            if choice == 'a':
                self.automate_weekly()
                print('\nCongrats! You created 3 newsletters.\n')
                choice2 = input('Do you want to quit? [Y/n]: ').strip().lower()
                if choice2 != 'n':
                    self.quit()

            elif choice == 'b':
                self.automate_weekly('registered')

            elif choice == 'c':
                self.approve_newsletter()

            elif choice == 'q':
                self.quit()

            else:
                input('Please enter a valid option (Hit Enter to continue): ')


    def clear_screen(self):
        """Clears the screen for a better UX."""
        os.system('cls' if os.name == 'nt' else 'clear')


    def welcome_message(self):
        """Welcome Message."""
        self.clear_screen()
        print("Welcome to the email automator. What do you want to do?\n")


    def quit(self):
        """Quit Program."""
        self.clear_screen()
        self.running = False


    def alert(self, msg, type='error'):
        if type == 'error':
            print(Fore.RED + msg)
        elif type == 'success':
            print(Fore.GREEN + msg)

        print(Style.RESET_ALL)


    def show_menu(self, options, title=""):
        """Show a menu."""
        if title != "":
            print(title)
        sorted_menu = sorted(options.items())
        for key, value in sorted_menu:
            print("{}) {}".format(key, value))
        print("\n")


    def automate_weekly(self, type='weekly'):
        """Automates Weekly Emails."""
        filenames = os.walk("../content/{}".format(type))
        weekly = Weekly(self.config[type])

        for option in filenames:
            # If newsletter issue has content
            if len(option[2]):

                if '.DS_Store' in option[2]:
                    os.remove(option[0] + '/.DS_Store')

                # Get path and Newsletter info
                str_path = option[0]
                arr_path = str_path.split('/')

                # Check folders
                self.check_folder(str_path)

                if len(arr_path) > 5:
                    nw_info = {
                        "path": str_path,
                        "html_path": str_path.replace('content', 'html'),
                        "year": arr_path[3],
                        "region": arr_path[4],
                        "month": arr_path[5],
                        "nw_code": arr_path[-1]
                    }

                    # Create Emails
                    weekly.create_emails(type, nw_info)


    def check_folder(self, path):
        """Check Folders in HTML."""
        html_path = path.replace('content', 'html').split('/')
        curr_path = []
        status_file_path = path + '/status.txt'

        if not os.path.exists(status_file_path):
            status_file = open(status_file_path, "w")
            status_file.write('not approved')
            status_file.close()

        for item in html_path:
            curr_path.append(item)
            str_path = '/'.join(curr_path)

            if not os.path.exists(str_path):
                os.makedirs(str_path)


    def approve_newsletter(self):
        self.clear_screen()
        region_verified = False
        error = ''
        self.show_menu(self.regions,
            'Fill in the info to approve a newsletter.\n')

        while region_verified == False:
            if error != '':
                msg = error
            else:
                msg = "Choose the region: "
            answer = input(msg).strip().lower()
            if answer == 'a' or answer == 'b':
                nw_code = input('Enter Newsletter Code: ')
                self.alert('Newsletter {} approved!'.format(nw_code), 'success')
                input("Hit any key to continue: ")
                region_verified = True
            elif answer == 'c':
                region_verified = True
            elif answer == 'q':
                self.quit()
                region_verified = True
            else:
                error = 'Please choose a valid region!\n'
