# -*- coding: utf-8 -*-
"""Loan Qualifier Application.

This is a command line application to match applicants with qualifying loans.

Example:
    $ python app.py
"""
import sys
import fire
import questionary
from pathlib import Path

from qualifier.utils.fileio import (
    load_csv,
    save_csv
)

from qualifier.utils.calculators import (
    calculate_monthly_debt_ratio,
    calculate_loan_to_value_ratio
)

from qualifier.filters.max_loan_size import filter_max_loan_size
from qualifier.filters.credit_score import filter_credit_score
from qualifier.filters.debt_to_income import filter_debt_to_income
from qualifier.filters.loan_to_value import filter_loan_to_value


def load_bank_data():
    """Ask for the file path to the latest banking data and load the CSV file.

    Returns:
        The bank data from the data rate sheet CSV file.
    """

    csvpath = questionary.text("Enter a file path to a rate-sheet (.csv):").ask()
    csvpath = Path(csvpath)
    if not csvpath.exists():
        sys.exit(f"Oops! Can't find this path: {csvpath}")

    return load_csv(csvpath)


def get_applicant_info():
    """Prompt dialog to get the applicant's financial information.

    Returns:
        Returns the applicant's financial information.
    """

    credit_score = questionary.text("What's your credit score?").ask()
    debt = questionary.text("What's your current amount of monthly debt?").ask()
    income = questionary.text("What's your total monthly income?").ask()
    loan_amount = questionary.text("What's your desired loan amount?").ask()
    home_value = questionary.text("What's your home value?").ask()

    credit_score = int(credit_score)
    debt = float(debt)
    income = float(income)
    loan_amount = float(loan_amount)
    home_value = float(home_value)

    return credit_score, debt, income, loan_amount, home_value


def find_qualifying_loans(bank_data, credit_score, debt, income, loan, home_value):
    """Determine which loans the user qualifies for.

    Loan qualification criteria is based on:
        - Credit Score
        - Loan Size
        - Debit to Income ratio (calculated)
        - Loan to Value ratio (calculated)

    Args:
        bank_data (list): A list of bank data.
        credit_score (int): The applicant's current credit score.
        debt (float): The applicant's total monthly debt payments.
        income (float): The applicant's total monthly income.
        loan (float): The total loan amount applied for.
        home_value (float): The estimated home value.

    Returns:
        A list of the banks willing to underwrite the loan.

    """

    # Calculate the monthly debt ratio
    monthly_debt_ratio = calculate_monthly_debt_ratio(debt, income)
    print(f"The monthly debt to income ratio is {monthly_debt_ratio:.02f}")

    # Calculate loan to value ratio
    loan_to_value_ratio = calculate_loan_to_value_ratio(loan, home_value)
    print(f"The loan to value ratio is {loan_to_value_ratio:.02f}.")

    # Run qualification filters
    bank_data_filtered = filter_max_loan_size(loan, bank_data)
    bank_data_filtered = filter_credit_score(credit_score, bank_data_filtered)
    bank_data_filtered = filter_debt_to_income(monthly_debt_ratio, bank_data_filtered)
    bank_data_filtered = filter_loan_to_value(loan_to_value_ratio, bank_data_filtered)

    print(f"Found {len(bank_data_filtered)} qualifying loans")

    return bank_data_filtered

def get_save_to_file():
    """Prompt dialog to get the user's intent to save results to file.

    Returns:
        Returns yes or no, yes indicating that the user wants to save results to file.
    """    
    response = questionary.select(
        "Do you want to save qualifying loans to a CSV file?",
        choices=["yes","no"]
        ).ask()
    return response

# define csv suffix and suffix size
suffix = '.csv'
suffix_size = len(suffix)
def get_save_path():
    """Prompt dialog to get path to save the file to.

    Returns:
        Returns Path for csv file
    """    
    path = None
    path_is_valid=False
    # loop until user provides a valid response
    while not path_is_valid:
        # prompt the user for the file path
        path = questionary.text(f"Please enter the file path to save qualifying loans to (must end in `{suffix}`):").ask()
        path_is_valid = is_valid_path(path)
        # a valid file path ending in .csv will break the loop

    return Path(path)

def is_valid_path(path):
    """Validate that the provided path is acceptable.

    Returns:
        Returns True if path is valid, False otherwise
    """   
    # confirm that the file path is acceptable
    if path == None or len(path) <= suffix_size or path[-suffix_size:] != suffix:
        print(f"`{path}` is not a valid path.")
        return False
    
    return True

# define CSV headers
headers = ['Lender','Max Loan Amount','Max LTV','Max DTI','Min Credit Score','Interest Rate']

def save_qualifying_loans(qualifying_loans):
    """Saves the qualifying loans to a CSV file.

    Design / Requirements:
        1 - the user interface for this tool is a CLI which prompts the user for required input
            use questionary to get required info from user
            prompt for intent to save to file
            prompt for path to save to

        2 - When there are no qualifying loans, the tool should notify the user and exit.
            if len(loans) < 1 or None, print no loans and exit

        3 - If there are qualifying loans, the tool offer the user to opt out of saving the file.
               If the user opts out of saving the file, the program should quit
               if save_to_file == no, exit

        4 - If there are qualifying loans and if the user wants to save them to a file, the tool
            should prompt for a file path to save the file. The file name should have a valid format.  
            It sould be longer than `.csv` and it should end in `.csv`.
            The program will prompt the using repeatedly until a valid anser is provided. 
            if len(loans) > 0
               if save_to_file == yes
                  save_file = None
                  while !valid(save_file)
                     save_file=get_save_file()
                  save(loans,save_file)
                  exit

        5 - When saving qualifying loans to a file, the tool should save the results as a CSV file. 
            use csvwriter to save file as CSV
            open file for write
               create csvwriter
               csvwriter.write(headers)
               for each loan
                  csvwriter.write(loan)
            return
              

    Args:
        qualifying_loans (list of lists): The qualifying bank loans.
    """

    # @TODO: Complete the usability dialog for savings the CSV Files.
    
    # first, check to see if there are no qualifying loans
    if qualifying_loans is None or len(qualifying_loans) < 1:
        print("There were no qualifyining loans to save.  GoodBye!")
        return

    # there are qualifying loans, check if user wants to exit without saving to file
    save_to_file = get_save_to_file()

    if save_to_file != 'yes':
        print("You have opted not to save qualifying loans to file.  GoodBye!")
        return

    print("You have selected to save qualifying loans to file.")

    # get path to save qualifying loans to
    csv_path = get_save_path()
    save_csv(csv_path,headers,qualifying_loans)
    print(f"Saved qualifying loans to {csv_path}.  GoodBye!")

def run():
    """The main function for running the script."""

    # Load the latest Bank data
    bank_data = load_bank_data()

    # Get the applicant's information
    credit_score, debt, income, loan_amount, home_value = get_applicant_info()

    # Find qualifying loans
    qualifying_loans = find_qualifying_loans(
        bank_data, credit_score, debt, income, loan_amount, home_value
    )

    # Save qualifying loans
    save_qualifying_loans(qualifying_loans)


if __name__ == "__main__":
    fire.Fire(run)
