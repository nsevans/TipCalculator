from itertools import count
#import time
import common.event_logger as logger
import common.settings as settings

class Employees():

    def __init__(self):
        """
        Constructor for the employees object. Just stores a list of all employees that can
        collect tips.
        """        
        self.employees = []

    def generate_employee_info(self, pdf_string):
        """
        Parses the pdf text, and returns a list of employees with their full name and the
        number of hours they worked, according to the payroll sheet. The parser then saves
        the list to this object's employees attribute.

        Args:
            pdf_string (string): The string generated from a pdf that is used 
            to collect all employee information.
        """

        logger.logEvent('Starting PDF parsing to generate list of employees and their info...')

        pdf_list = pdf_string.split(' ')

        #parsing_start_time = time.time()

        for name in settings.user_settings['EMPLOYEE_NAMES']:
            
            # Initialize current employee's stats
            name_index = 0
            employee_id = 0
            employee_hours = 0.0

            # Get first and last name(s) of current employee
            first_name = name.split(' ')[0]
            last_names = []
            if len(name.split(' ')) > 1:
                last_names = name.split(' ')[1:]

            try:
                name_index = self.get_name_index(first_name, last_names, pdf_list)
                # If index is 0, employee wasn't found/not a valid employee name, 
                # so skip finding the rest of the employee data
                if name_index == 0:
                    continue

                employee_id = self.get_employee_id(name_index, pdf_list)

                employee_hours = self.get_employee_hours(name_index, pdf_list)

                employee_name = first_name + ' ' + (' '.join(last_names))
                self.employees.append([employee_name, employee_id, employee_hours, "0%", "$0"])

            except Exception as e:
                data = "Index: {} ID: {} Hours: {} Name: {}".format(name_index ,employee_id, employee_hours, name)
                logger.logTraceback('Data: '+data+'\n---'+str(e)+'---', e)
                logger.logEvent('Failed to add employee: ('+data+')',log_type=logger.logging.ERROR)

    def get_employee_hours(self, index, pdf_list):
        """
        Find the employee's hours worked from the pdf.

        Args:
            index (int): Index in the pdf_list where the employee's name is found.
            pdf_list (list): List of every word/string in the pdf.

        Returns:
            float: Total number of hours worked by an employee.
        """
        hours = 0
        # Start at index where the employee's name was found
        for i in range(index+1, len(pdf_list)):
            # Loop until the string "TOTAL PAY" is found,
            # after that string will show the hours 
            if pdf_list[i] + ' ' + pdf_list[i+1] == "TOTAL PAY":
                try:
                    hours = float(pdf_list[i-1])
                    # Instance where an employee has a driver summary, their total hours
                    # won't appear in the same place, so go ahead the starting index plus 8 positions
                    if hours == 0:
                        hours = float(pdf_list[i+1+8])
                except Exception:
                    # For some reason couldn't get hours so just assign 0 hours
                    hours = 0
                # Exit loop since hours were found
                break


        return hours


    def get_employee_id(self, name_index, pdf_list):
        """
        Find the employee's ID number from the pdf.

        Args:
            name_index (int): Index where the employee's name is located.
            pdf_list (list): List of every word/string in the pdf.

        Returns:
            int: The employee's ID number.
        """
        # Employee ID is found in the index directly before the employee's names
        return int(pdf_list[name_index-1])
                

    def get_name_index(self, first_name, last_names, pdf_list):
        """
        Given an employee's first name, and a list of all last names,
        find the index in the pdf where the name is found.

        Args:
            first_name (string): First name of employee.
            last_names (list): Last names of employee (Middle and Last (Anything but first name)).
            pdf_list (list): List of every word/string in the pdf.

        Returns:
            int: Index where the name of the employee is found in the pdf_list (0 if not found).
        """
        # Find all cases of first name
        name_indexes = [i for i, j in zip(count(), pdf_list) if j == first_name]
        # Loop through and check each case until we have a match
        isMatch = False
        name_index = 0
        # Loop over each index of possible matches
        for index in name_indexes:
            matched_count = 0
            # If there's a last name
            if len(last_names) > 0:
                # Check last name for match by checking each name index
                for i in range(0, len(last_names)):
                    # If the last name isn't a match, break out to check next index
                    if last_names[i] != pdf_list[index+i+1]:
                        break

                    # If the current index of the name is a match, increase match count
                    if last_names[i] == pdf_list[index+i+1]:
                        matched_count += 1

                    if matched_count == len(last_names):
                        isMatch = True
                        break
            # Employee only has first name in system, and hopefully there aren't any duplicates 
            # (EX: "Nick" and "Nick") so it's just a match
            else:
                isMatch = True

            if isMatch:
                name_index = index
                break
        return name_index
