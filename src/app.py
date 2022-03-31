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


# define CSV headers
header = ['Lender','Max Loan Amount','Max LTV','Max DTI','Min Credit Score','Interest Rate']

def save_qualifying_loans(qualifying_loans):
    """Saves the qualifying loans to a CSV file.

    Requirements:
        1 - the user interface for this tool is a CLI which prompts the user for required input

        2 - When there are no qualifying loans, the tool should notify the user and exit.

        3 - If there are qualifying loans, the tool offer the user to opt out of saving the file.

        4 - If there are qualifying loans and if the user wants to save them to a file, the tool
            should prompt for a file path to save the file.

        5 - When saving qualifying loans to a file, the tool should save the results as a CSV file.    

    Args:
        qualifying_loans (list of lists): The qualifying bank loans.
    """

    # @TODO: Complete the usability dialog for savings the CSV Files.
    
    # first, check to see if there are no qualifying loans
    if qualifying_loans is None or len(qualifying_loans) < 1:
        print("There were no qualifyining loans to save.  GoodBye!")
        return

    # there are qualifying loans, check if user wants to exit without saving to file
    save_to_file = None
    # define allowed answers
    allowed_answers = ['yes','no']
    while save_to_file == None:
        # prompt for intent to save
        save_to_file = questionary.text("Do you want to save qualifying loans to a CSV file (yes or no)?:").ask()
        # normalize the data by 
        save_to_file = save_to_file.lower()
        # check if answer was valid
        if save_to_file not in allowed_answers:
            print(f"{save_to_file} is not a valid answer.  Only yes or no are allowed.")
            save_to_file = None   # this will cause the question to be asked again
        # a valid answer of yes or no will break the loop

    if save_to_file != 'yes':
        print("You have opted not to save qualifying loans to file.  GoodBye!")
        return

    print("You have selected to save qualifying loans to file.")
    csv_path = None
    suffix = '.csv'
    suffix_size = len(suffix)
    while csv_path == None:
        # prompt the user for the file path
        csv_path = questionary.text(f"Please enter the file path to save qualifying loans to (must end in `{suffix}`):").ask()
        # confirm that the file path is acceptable
        if csv_path == None or len(csv_path) <= suffix_size or csv_path[-suffix_size:] != suffix:
            print(f"`{csv_path}` is not a valid path.")
            csv_path = None    # this will cause the question to be asked again
        # a valid file path ending in .csv will break the loop
    csv_path = Path(csv_path)
    save_csv(csv_path,header,qualifying_loans)
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
