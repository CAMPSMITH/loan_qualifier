# -*- coding: utf-8 -*-
"""Helper functions to load and save CSV data.

This contains a helper function for loading and saving CSV files.

"""
import csv


def load_csv(csvpath):
    """Reads the CSV file from path provided.

    Args:
        csvpath (Path): The csv file path.

    Returns:
        A list of lists that contains the rows of data from the CSV file.

    """
    with open(csvpath, "r") as csvfile:
        data = []
        csvreader = csv.reader(csvfile, delimiter=",")

        # Skip the CSV Header
        next(csvreader)

        # Read the CSV data
        for row in csvreader:
            data.append(row)
    return data

def save_csv(csvpath, header, records):
    """Saves the data to the specified CSV path

    Args:
        csvpath (Path): The csv file path.
        header  (list): a list of strings providing the field names for the CSV file
        records (list): a list of records to save

    Returns:
        

    """
    with open(csvpath, "w") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=",")

        csvwriter.writerow(header)

        for record in records:
            csvwriter.writerow(record)

    return 