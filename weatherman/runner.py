"""Weatherman

This module takes path to weatherfiles, report type flags and dates as commandline arguments,
and generates corresponding weather reports.

Example:
    The program is run using the command line interface:

        $ python weatherman.py /path/to/weatherfiles -a 2011/7 -b 2011/7 2012/7 -c 2011/7 -e 2004

Attributes:
    RED (str): ANSI escape sequence for red text color.
    BLUE (str): ANSI escape sequence for blue text color.
    RESET (str): ANSI escape sequence for text color reset.

"""

import argparse
import os
import types
from datetime import datetime
from typing import Union, Optional, Callable
from weatherman.helper import read_csv

RED = '\033[91m'
BLUE = '\033[34m'
RESET = '\033[0m'


class DataReader:
    """A Class to parse txt files and populate the readings dictionary.

        Attributes:
            files_dir (str): The directory pointing to weatherfiles.
            report_date (str): The date to be queried in the files.
            str_headers (list): List of headers which contain only strings.

        Methods:
            get_monthly_readings: Returns weather readings for a month.
            get_yearly_readings: Returns weather readings for a year.
    """

    def __init__(self, files_dir: str, report_date: str) -> None:
        """The constructor for DataReader class.

            Args:
                files_dir (str): The directory pointing to weatherfiles.
                report_date (str): The date to be queried in the files.
        """

        self.str_headers = ['PKT', 'Events']
        self.files_dir = files_dir
        self.report_date = report_date

    def _get_files(self, query_date: str) -> list[str]:
        """Returns names of all the text files in the directory.

            Args:
                query_date (str): A query date to look for in filenames.

            Returns:
                list: List of all txt filenames containing the query.
        """

        files_list = [f'{self.files_dir}/{f}' for f in os.listdir(self.files_dir)
                      if query_date in f and f.endswith('.txt')]

        return files_list

    def _get_daily_readings(self, daily_data: dict[str, str]) -> dict[str, Union[str, float]]:
        """Fills daily values in the readings data structure from csv data.

            Args:
                daily_data (dict): Dictionary containing daily readings
                    corresponding to header values.

            Returns:
                dict: Dictionary containing daily readings with correct
                    data-types.
        """

        daily_readings = {}

        for header in daily_data:
            if header not in self.str_headers and daily_data[header] != '':
                daily_readings[header] = float(daily_data[header])
            else:
                daily_readings[header] = daily_data[header]

        return daily_readings

    def get_monthly_readings(self, independent: Optional[bool] = True,
                             monthly_data: Optional[list] = None) \
            -> dict[int, dict[str, Union[str, float]]]:
        """Fills monthly values in the readings data structure from csv data.

            Args:
                independent (bool, optional): Whether the function is being
                    called independently or from another function within
                    this class. Defaults to True.
                monthly_data (list): List containing daily readings
                    corresponding to header values.

            Returns:
                dict: Dictionary containing monthly readings.
        """

        monthly_readings = {}

        if independent:
            report_date = datetime.strptime(self.report_date, '%Y/%m')
            report_year = str(report_date.year)
            report_month = report_date.strftime('%b')

            file_name = self._get_files(f'{report_year}_{report_month}')[0]

            monthly_data = read_csv(file_name)

        for daily_data in monthly_data:
            day = datetime.strptime(daily_data['PKT'], '%Y-%m-%d').day
            monthly_readings[day] = self._get_daily_readings(daily_data)

        return monthly_readings

    def get_yearly_readings(self) -> dict[str, dict[int, dict[str, Union[str, float]]]]:
        """Fills monthly values in the readings data structure from csv data.

            Returns:
                dict: Dictionary containing monthly readings.
        """

        yearly_readings = {}

        file_list = self._get_files(self.report_date)

        for file_name in file_list:
            monthly_data = read_csv(file_name)

            month = datetime.strptime(monthly_data[0]['PKT'], '%Y-%m-%d').strftime('%B')

            yearly_readings[month] = self.get_monthly_readings(False, monthly_data)

        return yearly_readings


class Calculator:
    """A Class to parse txt files and populate the readings dictionary.

        Attributes:
            readings (str): Dictionary containing weather readings.
            func (callable): A function to replace the object's compute() function.
                Defaults to None.

        Methods:
            compute: Computes max temperature, min temperature and max humidity for a date.
    """

    def __init__(self,
                 readings: Union[
                     dict[str, Union[str, float]],
                     dict[str, dict[int, dict[str, Union[str, float]]]]
                 ],
                 func: Callable[[], dict[str, int]] = None) -> None:
        """The constructor for Calculator class.

            Args:
                readings (dict): Dictionary containing weather readings.
                func (callable): A function to replace the object's compute function.
                    Defaults to None.
        """

        self.readings = readings
        if func is not None:
            self.compute = types.MethodType(func, self)

    def compute(self) -> dict[str, int]:
        """Computes max temperature, min temperature and max humidity for a date.

            Returns:
                dict: Dictionary containing dates, max temperature, min temperature
                    and max humidity.
        """

        computations = {
            'max_temp': None,
            'max_date': None,
            'min_temp': None,
            'min_date': None,
            'max_humidity': None,
            'humidity_date': None,
        }

        max_temps_readings = {}
        min_temps_readings = {}
        max_humidity_readings = {}

        for month, monthly_readings in self.readings.items():
            for day, daily_data in monthly_readings.items():
                if daily_data['Max TemperatureC'] != '':
                    max_temps_readings[f'{day} {month}'] = int(daily_data['Max TemperatureC'])
                if daily_data['Min TemperatureC'] != '':
                    min_temps_readings[f'{day} {month}'] = int(daily_data['Min TemperatureC'])
                if daily_data['Max Humidity'] != '':
                    max_humidity_readings[f'{day} {month}'] = int(daily_data['Max Humidity'])

        max_temp_date = max(max_temps_readings, key=lambda key: max_temps_readings[key])
        min_temp_date = min(min_temps_readings, key=lambda key: min_temps_readings[key])
        max_humidity_date = max(max_humidity_readings, key=lambda key: max_humidity_readings[key])

        computations['max_temp'] = max_temps_readings[max_temp_date]
        computations['max_date'] = max_temp_date

        computations['min_temp'] = min_temps_readings[min_temp_date]
        computations['min_date'] = min_temp_date

        computations['max_humidity'] = max_humidity_readings[max_humidity_date]
        computations['humidity_date'] = max_humidity_date

        return computations


def compute_monthly_average(self) -> dict[str, int]:
    """Computes averages for max temperature, min temperature and mean humidity for a month.

    A strategy function for the Calculator class which replaces the compute() function in a
    Calculator object.

        Returns:
            dict: Dictionary containing averages for max temperature, min temperature and mean
                humidity for a month.
    """

    computations = {
        'max_temp_avg': None,
        'min_temp_avg': None,
        'mean_humidity_avg': None
    }

    total_max_temp = 0
    max_temp_count = 0
    total_min_temp = 0
    min_temp_count = 0
    total_mean_humidity = 0
    mean_humidity_count = 0

    for day in self.readings.values():
        if day['Max TemperatureC'] != '':
            total_max_temp += day['Max TemperatureC']
            max_temp_count += 1
        if day['Min TemperatureC'] != '':
            total_min_temp += day['Min TemperatureC']
            min_temp_count += 1
        if day['Mean Humidity'] != '':
            total_mean_humidity += day['Mean Humidity']
            mean_humidity_count += 1

    computations['max_temp_avg'] = round(total_max_temp / max_temp_count)
    computations['min_temp_avg'] = round(total_min_temp / min_temp_count)
    computations['mean_humidity_avg'] = round(total_mean_humidity / mean_humidity_count)

    return computations


def compute_min_max(self) -> dict[int, dict[str, int]]:
    """Computes minimum and maximum temperature values for each day in a month.

    A strategy function for the Calculator class which replaces the compute() function in a
    Calculator object.

        Returns:
            dict: Dictionary containing dates and average values of maximum and minimum
                temperatures.
    """

    computations = {}

    for day, daily_reading in self.readings.items():
        max_temp = daily_reading['Max TemperatureC']
        min_temp = daily_reading['Min TemperatureC']

        if daily_reading['Max TemperatureC'] != '' and daily_reading['Min TemperatureC'] != '':
            computations[day] = {
                'max_temp': int(max_temp),
                'min_temp': int(min_temp)
            }

    return computations


class ReportGenerator:
    """A Class to parse txt files and populate the readings dictionary.

        Attributes:
            results (dict): Dictionary containing computations.
            report_date (str): Date to generate the report for.
            func (callable): A function to replace the object's generate_report() function.
                Defaults to None.

        Methods:
            generate_report: Generates and prints report from computations.
    """

    def __init__(self, results: Union[dict[str, int], dict[str, dict[str, int]]],
                 report_date: str, func: Callable[[], None] = None) -> None:
        """The constructor for ReportGenerator class.

            Args:
                results (dict): Dictionary containing computations.
                report_date (str): Date to generate the report for.
                func (callable): A function to replace the object's generate_report() function.
                    Defaults to None.
        """

        self.results = results
        self.report_date = report_date

        if func is not None:
            self.generate_report = types.MethodType(func, self)

    def generate_report(self) -> dict:
        """Generates and prints report from yearly computations."""

        print(f'Highest: {self.results["max_temp"]}C on {self.results["max_date"]}')
        print(f'Lowest: {self.results["min_temp"]}C on {self.results["min_date"]}')
        print(f'Humidity: {self.results["max_humidity"]}% on {self.results["humidity_date"]}')

        return {
            'date': self.report_date,
            'highest_temp': {
                'value': f'{self.results["max_temp"]}C',
                'date': self.results["max_date"],
            },
            'lowest_temp': {
                'value': f'{self.results["min_temp"]}C',
                'date': self.results["min_date"],
            },
            'max_humidity': {
                'value': f'{self.results["max_humidity"]}%',
                'date': self.results["humidity_date"],
            }
        }


def generate_average_report(self) -> dict:
    """Generates and prints report from monthly average computations.

    A strategy function for the ReportGenerator class which replaces the generate_report()
    function in a ReportGenerator object.
    """

    print(f'Highest Average: {self.results["max_temp_avg"]}C')
    print(f'Lowest Average: {self.results["min_temp_avg"]}C')
    print(f'Average Mean Humidity: {self.results["mean_humidity_avg"]}%')

    return {
        'date': self.report_date,
        'highest_avg_temp': f'{self.results["max_temp_avg"]}C',
        'lowest_avg_temp': f'{self.results["min_temp_avg"]}C',
        'avg_mean_humidity': f'{self.results["mean_humidity_avg"]}%',
    }


def generate_multiple_bar_report(self) -> dict:
    """Generates and prints report containing two horizontal bar charts per day from computations.

    A strategy function for the ReportGenerator class which replaces the generate_report()
    function in a ReportGenerator object.
    """

    print(datetime.strptime(self.report_date, '%Y/%m').strftime('%B %Y'))

    for day, readings in self.results.items():
        print(f'{"%02d" % day} {RED}{"+" * readings["max_temp"]} '
              f'{RESET}{readings["max_temp"]}C')

        print(f'{"%02d" % day} {BLUE}{"+" * readings["min_temp"]} '
              f'{RESET}{readings["min_temp"]}C')

    return {}


def generate_single_bar_report(self) -> dict:
    """Generates and prints report containing one horizontal bar chart per day from computations.

    A strategy function for the ReportGenerator class which replaces the generate_report()
    function in a ReportGenerator object.
    """

    print(datetime.strptime(self.report_date, '%Y/%m').strftime('%B %Y'))

    for day, readings in self.results.items():
        print(f'{"%02d" % day} {BLUE}{"+" * readings["min_temp"]}{RED}'
              f'{"+" * readings["max_temp"]} {RESET}'
              f'{readings["min_temp"]}C - {readings["max_temp"]}C')

    return {}


def process_args(dates: list[str], report_num: int, path: str,
                 strategies: Union[
                     dict[str, None],
                     dict[str, Union[
                         Callable[[], dict[str, int]],
                         Callable[[], dict[int, dict[str, int]]],
                         Callable[[], None]]
                     ]
                 ],
                 yearly: bool = False) -> list:
    """Calls methods and creates objects corresponding to arguments passed by user

        Args:
            dates (list): List containing dates entered by user.
            report_num (int): Current report number being generated.
            path (str): Path to weatherfiles directory.
            strategies (dict): Dictionary containing strategy functions for computations
                and report.
            yearly (bool): Flag to specify whether the report is for monthly or yearly data.

        Returns:
            list: List of reports.
    """

    reports = []
    for date in dates:
        print(f'\nReport # {report_num}')
        data_reader = DataReader(path, date)
        if yearly:
            readings = data_reader.get_yearly_readings()
        else:
            readings = data_reader.get_monthly_readings()

        calculator = Calculator(readings, strategies['calc_strategy'])
        computations = calculator.compute()

        report_generator = ReportGenerator(computations, date, strategies['report_strategy'])
        reports.append(report_generator.generate_report())

        report_num += 1

    return reports


def main():
    """Main function.

    The main function parses arguments from commandline and passes the arguments along with
    corresponding strategy functions to process_args() for each report flag. It also keeps
    track of the number of reports being printed.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', help='yearly report', nargs="+")
    parser.add_argument('-a', help='monthly average report', nargs="+")
    parser.add_argument('-c', help='monthly multiple bar chart report', nargs="+")
    parser.add_argument('-b', help='monthly single bar chart report', nargs="+")
    parser.add_argument('path', help='weatherfiles directory')

    args = parser.parse_args()

    report_num = 1

    if args.e:
        strategy = {
            'calc_strategy': None,
            'report_strategy': None
        }
        report_num = process_args(
            args.e, report_num, args.path,
            strategy, yearly=True)

    if args.a:
        strategy = {
            'calc_strategy': compute_monthly_average,
            'report_strategy': generate_average_report
        }
        report_num = process_args(
            args.a, report_num, args.path,
            strategy)

    if args.c:
        strategy = {
            'calc_strategy': compute_min_max,
            'report_strategy': generate_multiple_bar_report
        }
        report_num = process_args(
            args.c, report_num, args.path,
            strategy)

    if args.b:
        strategy = {
            'calc_strategy': compute_min_max,
            'report_strategy': generate_single_bar_report
        }
        report_num = process_args(
            args.b, report_num, args.path,
            strategy)


if __name__ == '__main__':
    main()
