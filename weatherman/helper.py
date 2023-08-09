"""Helper Functions"""
import csv


def read_csv(file_path: str) -> list:
    """Reads a text file as csv and returns rows in a list.

        Args:
            file_path (str): The path to a txt file.

        Returns:
            list: List of dictionaries containing data from txt file.
    """

    with open(file_path, 'r') as csv_file:
        header = [h.strip() for h in csv_file.readline().split(',')]
        header[0] = 'PKT'
        data = csv.DictReader(csv_file, fieldnames=header)
        return list(data)
