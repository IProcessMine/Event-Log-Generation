import datetime as dt
import logging
import random
from collections import defaultdict
from typing import Any, Union, List, Dict, Optional, Tuple

import dateparser
import numpy as np
import pandas as pd
from faker import Faker

import config_init

fake = Faker()


def initial_capitals(name: str) -> str:
    """
    Return the initial capitals from all words in a given name.

    Args:
        name (str): The name to convert.

    Returns:
        str: The initial capitals of the words in the name.
    """
    return ''.join(word[0].upper() for word in name.split())


# Helper functions
def generate_timestamp(start: Union[dt.date, dt.datetime], end: Union[dt.date, dt.datetime],
                       distribution='uniform') -> dt.datetime:
    """
    Generate a timestamp within a given date range based on a specified distribution.

    Args:
        start (Union[dt.date, dt.datetime]): The start of the date range.
        end (Union[dt.date, dt.datetime]): The end of the date range.
        distribution (str): The type of distribution to use for generating the timestamp. Uniform, normal, exponential, pareto.

    Returns:
        datetime: A randomly generated timestamp within the specified range.
    """
    try:
        if isinstance(start, str) and not isinstance(start, dt.datetime):
            start = dateparser.parse(start)
            start = dt.datetime.combine(start, dt.time.min)
        if isinstance(end, str) and not isinstance(end, dt.datetime):
            end = dateparser.parse(end)
            end = dt.datetime.combine(end, dt.time.max).replace(microsecond=999999)

        delta = (end - start).total_seconds()

        if distribution == 'uniform':
            offset = random.uniform(0, delta)
        elif distribution == 'normal':
            offset = np.random.normal(delta / 2, delta / 6)
        elif distribution == 'exponential':
            offset = np.random.exponential(delta / 2)
        elif distribution == 'pareto':
            offset = (np.random.pareto(3) + 1) * (delta / 4)
        else:
            raise ValueError("Unsupported distribution type")

        offset = max(0, min(delta, offset))  # Ensure offset is within the range
        return start + dt.timedelta(seconds=offset)
    except Exception as e:
        logging.error(f"Error generating timestamp: {str(e)}")
        raise


# Sample utility function to convert working schedule days from string to datetime format
def convert_working_schedule_days(days: List[str]) -> List[int]:
    """
    Convert a list of working days from string format to datetime weekday format.

    Args:
        days (list): List of working days in string format.

    Returns:
        list: List of working days in datetime weekday format.
    """
    days_map = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4,
        'Saturday': 5, 'Sunday': 6, 'workdays': [0, 1, 2, 3, 4], 'weekend': [5, 6],
        'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6
    }
    if not days:
        return []
    if isinstance(days, list):
        try:
            converted_days = [days_map[day] if isinstance(days_map[day], int) else days_map[day] for day in days]
            flattened_days = [item for sublist in converted_days for item in
                              (sublist if isinstance(sublist, list) else [sublist])]
            return list(set(flattened_days))  # Remove duplicates
        except KeyError as e:
            logging.error(f"Unrecognized day in working schedule: {e}")
            return []
    return []


def is_working_time(start_time: dt.datetime, working_days: List[int], working_hours: List[int]) -> bool:
    """
    Check if the given time is within the working schedule.

    Args:
        start_time (dt.datetime): The time to check.
        working_days (List[int]): List of working days.
        working_hours (List[int]): Start and end working hours.

    Returns:
        bool: True if the time is within the working schedule, False otherwise.
    """
    if not working_days or not working_hours:
        return True

    return start_time.weekday() in working_days and working_hours[0] <= start_time.hour < working_hours[1]


def adjust_to_working_schedule(start_date: dt.datetime, end_date: dt.datetime, working_days: List[str],
                               working_hours: List[int]) -> Tuple[dt.datetime, dt.datetime]:
    """
    Adjust the start and end time to fit within the working schedule.

    Args:
        start_date (datetime): Original start date.
        end_date (datetime): Original end date.
        working_days (list): List of working days.
        working_hours (list): Start and end working hours.

    Returns:
        tuple: Adjusted start and end time within the working schedule.
    """
    try:
        working_days = convert_working_schedule_days(working_days)
        if not working_days or not working_hours:
            return start_date, end_date

        working_hours = sorted(working_hours)  # Ensure working hours are in order
        if len(working_hours) == 1:
            working_hours = [working_hours[0], 24]  # Assume end of the day if only start is given

        duration_seconds = (end_date - start_date).total_seconds()
        working_hours_per_day = (working_hours[1] - working_hours[0]) * 3600
        if working_hours_per_day <= 0:
            logging.error("Invalid working hours range")
            return start_date, end_date

        def next_valid_start_time(current_time: dt.datetime) -> dt.datetime:
            if current_time.hour >= working_hours[1] or current_time.hour < working_hours[0]:
                current_time = current_time.replace(hour=working_hours[0])
                current_time += dt.timedelta(days=1)
            while current_time.weekday() not in working_days:
                current_time += dt.timedelta(days=1)
            return current_time

        def add_working_duration(start_time: dt.datetime, duration: float) -> dt.datetime:
            end_time = start_time
            while duration > 0:
                if is_working_time(end_time, working_days, working_hours):
                    available_time = min((end_time.replace(hour=working_hours[1]) - end_time).total_seconds(), duration)
                    end_time += dt.timedelta(seconds=available_time)
                    duration -= available_time
                else:
                    end_time = next_valid_start_time(end_time)
            return end_time

        start_date = next_valid_start_time(start_date)
        end_date = add_working_duration(start_date, duration_seconds)

        return start_date, end_date

    except Exception as e:
        logging.error(f"Error adjusting to working schedule: {e}")
        raise


def generate_random_start_time_within_uom(start_date: dt.datetime, duration_uom: str) -> dt.datetime:
    """
    Generate a random start time within the duration unit of measure.

    Args:
        start_date (datetime.datetime): The base start date.
        duration_uom (str): Unit of measure for duration.

    Returns:
        datetime.datetime: Randomized start date within the duration unit of measure.
    """
    if duration_uom == 'days':
        return start_date + dt.timedelta(hours=random.randint(0, 23))
    elif duration_uom == 'hours':
        return start_date + dt.timedelta(minutes=random.randint(0, 59))
    elif duration_uom == 'minutes':
        return start_date + dt.timedelta(seconds=random.randint(0, 59))
    elif duration_uom == 'seconds':
        return start_date + dt.timedelta(milliseconds=random.randint(0, 999))
    else:
        return start_date


def generate_timestamps(start: Union[str, dt.datetime], end: Union[str, dt.datetime], distribution: str,
                        amount: int, orders: Optional[List[int]] = None) -> List[dt.datetime]:
    """
    Generate multiple timestamps within a given date range based on a specified distribution and order.

    Args:
        start (Union[str, dt.datetime]): The start of the date range.
        end (Union[str, dt.datetime]): The end of the date range.
        distribution (str): The type of distribution to use for generating the timestamp. Options are 'uniform', 'normal', 'exponential', 'pareto'.
        amount (int): Number of timestamps to generate.
        orders (list): Optional list of orders to arrange the timestamps. Default is ascending order.

    Returns:
        list: A list of randomly generated timestamps within the specified range, ordered as specified.
    """
    try:
        if isinstance(start, str):
            start = dateparser.parse(start)
            start = dt.datetime.combine(start, dt.time.min)
        if isinstance(end, str):
            end = dateparser.parse(end)
            end = dt.datetime.combine(end, dt.time.max).replace(microsecond=999999)

        timestamps = [generate_timestamp(start, end, distribution) for _ in range(amount)]

        if orders:
            if len(orders) != amount:
                raise ValueError("Length of orders must match the amount of timestamps to generate.")
            ordered_timestamps = sorted(zip(orders, timestamps))
            return [timestamp for _, timestamp in ordered_timestamps]

        return sorted(timestamps)

    except Exception as e:
        logging.error(f"Error generating timestamps: {str(e)}")
        raise


def generate_resource_data(resource_type: str, range_min=1, range_max=10) -> list:
    """
    Generate random resource data using the Faker library.

     Args:
        resource_type (str): The type of resource (e.g., 'machine', 'human').
        range_min (int): Minimum value for resource range.
        range_max (int): Maximum value for resource range.

    Returns:
        list: List of generated resources.
    """
    try:
        resources = []
        for _ in range(range_min, range_max + 1):
            if resource_type == 'machine':
                resources.append(fake.bothify(text='Machine-####'))
            elif resource_type == 'human':
                resources.append(fake.unique.name())
            else:
                raise ValueError(f"Unknown resource type: {resource_type}")
        return resources
    except Exception as e:
        logging.error(f"Error generating resource data: {str(e)}")
        raise


def generate_attribute_value(attribute_type: str, distribution='uniform', categories=None, range_min=0, range_max=100,
                             prev_value=None) -> Union[int, float, str]:
    """
    Generate a value for a given attribute based on its type and distribution.

    Args:
        attribute_type (str): The type of the attribute ('Character', 'Numeric', 'Categorical', etc.).
        distribution (str): The distribution type for generating the value (uniform, normal, exponential, pareto).
        categories (List[str]): List of categories for categorical attributes.
        range_min (int): Minimum value for range-based attributes.
        range_max (int): Maximum value for range-based attributes.
        prev_value (Union[int, float, str]): The previous attribute value to consider in some distributions.

    Returns:
        Union[int, str]: The generated attribute value.
    """
    try:
        if attribute_type in ['Categorical', 'Resource']:
            if categories:
                return np.random.choice(categories)
            else:
                raise ValueError("Categories must be provided for Categorical attribute type")
        elif attribute_type == 'Numeric':
            if distribution == 'uniform':
                if prev_value is not None:
                    return np.random.uniform(prev_value, range_max)
                return np.random.uniform(range_min, range_max)
            elif distribution == 'normal':
                mu = (range_max + range_min) / 2
                sigma = (range_max - range_min) / 6
                if prev_value is not None:
                    mu = (range_max + prev_value) / 2
                    sigma = (range_max - prev_value) / 6
                return np.random.normal(mu, sigma)
            elif distribution == 'exponential':
                scale = (range_max - range_min) / 2
                if prev_value is not None:
                    scale = (range_max - prev_value) / 2
                return np.random.exponential(scale)
            elif distribution == 'pareto':
                shape = 2.62
                return np.random.pareto(shape)
            else:
                raise ValueError(f"Unknown distribution: {distribution}")
        elif attribute_type == 'Character':
            return fake.word()
        elif attribute_type == 'Geo':
            return fake.geo()
        elif attribute_type == 'Company':
            return fake.company()
        elif attribute_type == 'PhoneNumber':
            return fake.phone_number()
        elif attribute_type == 'Email':
            return fake.email()
        elif attribute_type == 'Address':
            return fake.address()
        elif attribute_type == 'UUID':
            return fake.uuid4()
        elif attribute_type == 'DateTime':
            return fake.date_time()
        else:
            raise ValueError(f"Unknown attribute type: {attribute_type}")
    except Exception as e:
        logging.error(f"Error generating attribute value: {str(e)}")
        raise


def adjust_attribute_value(value, adjustment_type, range_min, range_max, categories=None):
    """
    Adjust attribute value based on the adjustment type.

    Args:
        value (Union[int, float, str]): The current attribute value.
        adjustment_type (str): The adjustment type (slight_change, moderate_change, significant_change).
        range_min (int): Minimum value for numeric adjustments.
        range_max (int): Maximum value for numeric adjustments.
        categories (List[str]): List of categories for categorical attributes.

    Returns:
        Union[int, float, str]: The adjusted attribute value.
    """
    if isinstance(value, (int, float)):
        change_percent = {
            'slight_change': 0.10,
            'moderate_change': 0.30,
            'significant_change': 1.00
        }.get(adjustment_type, 0)

        change = value * change_percent
        new_value = value + random.uniform(-change, change)

        if adjustment_type == 'significant_change':
            new_value = max(range_min, min(new_value, range_max))
        else:
            new_value = max(range_min, min(new_value, range_max))
            if adjustment_type == 'moderate_change':
                if new_value - value < 0.30 * value:
                    new_value = value * 1.3 if value < new_value else value * 0.7

        return round(new_value)

    elif isinstance(value, str) and categories:
        change_probability = {
            'slight_change': 0.20,
            'moderate_change': 0.50,
            'significant_change': 1.00
        }.get(adjustment_type, 0)

        if random.random() < change_probability:
            return random.choice([cat for cat in categories if cat != value])

        return value

    return value


def generate_attribute_values(attribute_type: str, distribution='uniform', categories=None, range_min=0, range_max=100,
                              num_values=10, order: list = None) -> list:
    """
    Generate an array of values for a given attribute based on its type and distribution.

    Args:
        attribute_type (str): The type of the attribute ('Character', 'Numeric', 'Categorical', etc.).
        distribution (str): The distribution type for generating the value (uniform, normal, exponential, pareto).
        categories (List[str]): List of categories for categorical attributes.
        range_min (int): Minimum value for range-based attributes.
        range_max (int): Maximum value for range-based attributes.
        num_values (int): Number of values to generate.
        order (List[int], optional): A list of indices specifying the order in which to sort the generated values. Defaults to None.

    Returns:
        list: The generated attribute values, sorted based on the `order` argument if provided.
    """
    values = [generate_attribute_value(attribute_type, distribution, categories, range_min, range_max) for _ in
              range(num_values)]

    if order is not None:
        # Ensure that `order` is a list of integers and has the same length as `num_values`
        if len(order) != num_values or any(not isinstance(i, int) for i in order):
            raise ValueError(
                "Invalid `order` argument. It should be a list of integers with the same length as `num_values`.")

        # Use `zip` to pair each value with its corresponding index, then sort based on `order`
        sorted_values = sorted(zip(order, values), key=lambda x: x[0])
        return [value for _, value in sorted_values]

    else:
        return values


def add_duration(start_date: Union[dt.date, dt.datetime], duration: float, duration_uom: str) -> dt.datetime:
    """
    Add a specified amount of time to a start date and return the resulting date/time.

    Args:
        start_date (Union[datetime.date, datetime.datetime]): The starting date/time.
        duration (float): Amount of time to add (can be positive or negative).
        duration_uom (str): Unit of measurement for the duration ('days', 'hours', 'minutes', 'seconds').

    Returns:
        datetime: Resulting date/time after adding the specified duration.
    """
    if duration_uom == 'days':
        return start_date + dt.timedelta(days=duration)
    elif duration_uom == 'hours':
        return start_date + dt.timedelta(hours=duration)
    elif duration_uom == 'minutes':
        return start_date + dt.timedelta(minutes=duration)
    elif duration_uom == 'seconds':
        return start_date + dt.timedelta(seconds=duration)
    else:
        raise ValueError(f"Unsupported duration_uom: {duration_uom}")


def generate_process_data(process_config_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Generate process data from YAML configuration and update 'process_id' back to the input configuration.

    Args:
        process_config_data (dict): Dictionary containing process configuration.

    Returns:
        pd.DataFrame: DataFrame representing process data.
    """
    try:
        process_rows = []
        for process_key, process in process_config_data['processes'].items():
            if isinstance(process, dict) and 'process_id' in process:
                process_rows.append({
                    'process_id': process['process_id'],
                    'process_name': process['process_name'],
                    'description': process['description'],
                    'start_date': process['start_date'],
                    'end_date': process['end_date'],
                    'num_cases': process['num_cases'],
                    'traces': process['traces'],
                    'traces_scaled': process['trace_counts']
                })
        process_df = pd.DataFrame(process_rows, columns=['process_id', 'process_name', 'process_description',
                                                         'start_date', 'end_date', 'num_cases', 'traces',
                                                         'traces_scaled'])
        return process_df
    except Exception as e:
        logging.error(f"Error generating process data: {str(e)}")
        raise


def generate_activity_data(process_config_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Generate activity data for each process.

    Args:
        process_config_data (dict): Dictionary containing process configuration.

    Returns:
        pd.DataFrame: DataFrame representing activity data.
    """
    try:
        activity_rows = []
        activity_id = process_config_data['activity_id']
        for process_key, process in process_config_data['processes'].items():
            if isinstance(process, dict) and 'process_id' in process:
                for activity in process['activities']:
                    activity_rows.append({
                        'activity_id': activity.get('activity_id', activity_id),
                        'activity_name': activity['name'],
                        'process_id': process['process_id'],
                        'trace': activity['trace'],
                        'order': activity['order'],
                        'min_weight': activity['min_weight'],
                        'max_weight': activity['max_weight'],
                        'distribution': activity['distribution'],
                        'duration_range': activity['duration_range'],
                        'duration_uom': activity['duration_uom'],
                        'working_days': activity['working_days'],
                        'working_hours': activity['working_hours']
                    })
                    activity_id += 1
        activities_df = pd.DataFrame(activity_rows, columns=['activity_id', 'activity_name', 'process_id', 'trace',
                                                             'order', 'min_weight', 'max_weight', 'distribution',
                                                             'duration_range', 'duration_uom', 'working_days',
                                                             'working_hours'])
        return activities_df
    except Exception as e:
        logging.error(f"Error generating activity data: {e}")
        raise


def create_attribute_definitions(process_config_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Create a DataFrame of attribute definitions from the process configuration.

    Args:
        process_config_data (dict): Dictionary containing process configuration.

    Returns:
        pd.DataFrame: DataFrame representing attribute definitions.
    """
    try:
        attribute_rows = []
        attribute_definition_id = process_config_data['attribute_definition_id']
        case_attribute_id = process_config_data['case_attribute_id']
        event_attribute_id = process_config_data['event_attribute_id']
        object_attribute_id = process_config_data['object_attribute_id']

        for process in process_config_data['processes'].values():
            for attribute in process.get('case_attributes', []):
                attribute_rows.append({
                    'process_id': process['process_id'],
                    'attribute_definition_id': attribute_definition_id,
                    'attribute_type': 'case',
                    'attribute_id': case_attribute_id,
                    'attribute_name': attribute['name'],
                    'attribute_value_type': attribute['type'],
                    'distribution': attribute['distribution'],
                    'range': attribute['range'],
                    'categories': attribute['categories'],
                    'resource_type': attribute['resource_type'],
                    'resource_count': attribute['resource_count'],
                    'as_attribute': attribute['as_attribute'],
                    'adjustment_type': attribute['adjustment_type'],
                    'generation_level': attribute['generation_level']
                })
                attribute_definition_id += 1
                case_attribute_id += 1
            for attribute in process.get('event_attributes', []):
                attribute_rows.append({
                    'process_id': process['process_id'],
                    'attribute_definition_id': attribute_definition_id,
                    'attribute_type': 'event',
                    'attribute_id': event_attribute_id,
                    'attribute_name': attribute['name'],
                    'attribute_value_type': attribute['type'],
                    'distribution': attribute['distribution'],
                    'range': attribute['range'],
                    'categories': attribute['categories'],
                    'resource_type': attribute['resource_type'],
                    'resource_count': attribute['resource_count'],
                    'as_attribute': attribute['as_attribute'],
                    'adjustment_type': attribute['adjustment_type'],
                    'generation_level': attribute['generation_level']
                })
                attribute_definition_id += 1
                event_attribute_id += 1
            for attribute in process.get('activity_instance_attributes', []):
                attribute_rows.append({
                    'process_id': process['process_id'],
                    'attribute_definition_id': attribute_definition_id,
                    'attribute_type': 'activity',
                    'attribute_id': event_attribute_id,
                    'attribute_name': attribute['name'],
                    'attribute_value_type': attribute['type'],
                    'distribution': attribute['distribution'],
                    'range': attribute['range'],
                    'categories': attribute['categories'],
                    'resource_type': attribute['resource_type'],
                    'resource_count': attribute['resource_count'],
                    'as_attribute': attribute['as_attribute'],
                    'adjustment_type': attribute['adjustment_type'],
                    'generation_level': attribute['generation_level']
                })
                attribute_definition_id += 1
                event_attribute_id += 1
            for attribute in process.get('object_attributes', []):
                attribute_rows.append({
                    'process_id': process['process_id'],
                    'attribute_definition_id': attribute_definition_id,
                    'attribute_type': 'object',
                    'attribute_id': event_attribute_id,
                    'attribute_name': attribute['name'],
                    'attribute_value_type': attribute['type'],
                    'distribution': attribute['distribution'],
                    'range': attribute['range'],
                    'categories': attribute['categories'],
                    'resource_type': attribute['resource_type'],
                    'resource_count': attribute['resource_count'],
                    'as_attribute': attribute['as_attribute'],
                    'adjustment_type': attribute['adjustment_type'],
                    'generation_level': attribute['generation_level']
                })
                attribute_definition_id += 1
                object_attribute_id += 1
        attribute_definitions_df = pd.DataFrame(attribute_rows, columns=['process_id', 'attribute_definition_id',
                                                                         'attribute_type', 'attribute_id',
                                                                         'attribute_name', 'attribute_value_type',
                                                                         'distribution', 'range', 'categories',
                                                                         'resource_type', 'resource_count',
                                                                         'as_attribute', 'adjustment_type',
                                                                         'generation_level'])
        return attribute_definitions_df
    except Exception as e:
        logging.error(f"Error creating attribute definitions: {str(e)}")
        raise


def generate_case_data(process_config_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Generate case data for each process.

    Args:
        process_config_data (dict): Dictionary containing process configuration.

    Returns:
        pd.DataFrame: DataFrame representing case data.
    """
    try:
        case_rows = []
        case_id = process_config_data['case_id']
        for process_key, process in process_config_data['processes'].items():
            if isinstance(process, dict) and 'process_id' in process:
                process_id = process['process_id']
                num_cases = process['num_cases']
                process_start_date = pd.to_datetime(process['start_date'])
                process_end_date = pd.to_datetime(process['end_date'])
                working_hours = process['working_hours']
                working_days = process['working_days']

                for i in range(num_cases):
                    start_date = generate_timestamp(process_start_date, process_end_date)
                    end_date = generate_timestamp(start_date, process_end_date)
                    start_date, end_date = adjust_to_working_schedule(start_date, end_date, working_days, working_hours)

                    for key, value in process['trace_counts'].items():
                        case_trace_patterns = []
                        if value <= 0:
                            break
                        else:
                            case_trace_patterns.append(key)
                            process['trace_counts'][key] -= 1

                            case_rows.append({
                                'case_id': case_id,
                                'process_id': process_id,
                                'case_name': f"Case_{case_id}",
                                'start_date': start_date,
                                'end_date': end_date,
                                'trace_pattern': case_trace_patterns,
                                'working_days': working_days,
                                'working_hours': working_hours,
                            })
                            case_id += 1

        cases_df = pd.DataFrame(case_rows, columns=['case_id', 'process_id', 'case_name',
                                                    'start_date', 'end_date', 'trace_pattern', 'working_days',
                                                    'working_hours'])
        return cases_df
    except Exception as e:
        logging.error(f"Error generating case data: {str(e)}")
        raise


def generate_activity_instance_data(process_config_data: Dict[str, Any], cases_df: pd.DataFrame,
                                    activities_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate activity instance data for each case in the process.

    Args:
        process_config_data (dict): Dictionary containing process configuration.
        cases_df (pd.DataFrame): DataFrame representing cases.
        activities_df (pd.DataFrame): DataFrame representing activities.

    Returns:
        pd.DataFrame: DataFrame representing activity instance data.
    """
    try:
        activity_instance_rows = []
        activity_instance_id = process_config_data['activity_instance_id']

        for _, case in cases_df.iterrows():
            trace_patterns = case['trace_pattern'][0].split(',')  # Assuming trace_pattern is a list of strings
            current_time = case['start_date']

            for position, trace in enumerate(trace_patterns):
                filtered_activities = activities_df[(activities_df['process_id'] == case['process_id'])
                                                    & (activities_df['trace'] == trace)]
                for _, activity in filtered_activities.iterrows():
                    start_date = current_time
                    duration_range = activity['duration_range']
                    duration_uom = activity['duration_uom']

                    start_date = generate_random_start_time_within_uom(start_date, duration_uom)
                    end_date = add_duration(start_date, random.randint(duration_range[0], duration_range[1]),
                                            duration_uom)

                    start_date, end_date = adjust_to_working_schedule(start_date, end_date, activity['working_days'],
                                                                      activity['working_hours'])

                    activity_instance_rows.append({
                        'activity_instance_id': activity_instance_id,
                        'case_id': case['case_id'],
                        'activity_id': activity['activity_id'],
                        'start_date': start_date,
                        'end_date': end_date,
                        'activity_name': activity['activity_name'],
                        'position_in_trace': position,
                        'trace': activity['trace'],
                        'order': activity['order'],
                        'working_days': activity['working_days'],
                        'working_hours': activity['working_hours']
                    })

                    activity_instance_id += 1
                    current_time = end_date  # Update current time to the end of the activity for the next one

        activity_instances_df = pd.DataFrame(activity_instance_rows, columns=['activity_instance_id', 'case_id',
                                                                              'activity_id', 'start_date', 'end_date',
                                                                              'activity_name', 'position_in_trace',
                                                                              'trace', 'order', 'working_days',
                                                                              'working_hours'])
        return activity_instances_df
    except Exception as e:
        logging.error(f"Error generating activity instance data: {e}")
        raise


def generate_event_data(process_config_data: Dict[str, Any], activity_instances_df: pd.DataFrame,
                        activities_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate event data for each activity instance according to transaction types.

    Args:
        process_config_data (dict): Dictionary containing process configuration.
        activity_instances_df (pd.DataFrame): DataFrame representing activity instance data.
        activities_df (pd.DataFrame): DataFrame representing activities.

    Returns:
        pd.DataFrame: DataFrame representing event data.
    """
    try:
        event_rows = []
        event_id = process_config_data['event_id']

        for _, instance in activity_instances_df.iterrows():
            activity = activities_df[activities_df['activity_id'] == instance['activity_id']].iloc[0]
            transaction_types = activity.get('transaction_types', [])
            start_date = instance['start_date']
            end_date = instance['end_date']
            if transaction_types:
                for tt in transaction_types:
                    # Check if working_schedule_days and working_schedule_time are specified
                    duration_range = tt['duration_range']
                    duration_uom = tt['duration_uom']
                    event_start_time = generate_random_start_time_within_uom(start_date, tt['duration_uom'])
                    event_end_time = add_duration(event_start_time,
                                                  random.randint(duration_range[0], duration_range[1]),
                                                  duration_uom)

                    event_start_time, event_end_time = adjust_to_working_schedule(event_start_time, event_end_time,
                                                                                  tt['working_days'],
                                                                                  tt['working_hours'])

                    event_rows.append({
                        'event_id': event_id,
                        'activity_instance_id': instance['activity_instance_id'],
                        'case_id': instance['case_id'],
                        'activity_id': instance['activity_id'],
                        'start_date': event_start_time,
                        'end_date': event_end_time,
                        'transaction_name': tt['name'],
                        'transaction_order': tt['order']
                    })

                    start_date = event_end_time
                    event_id += 1
            else:
                event_rows.append({
                    'event_id': event_id,
                    'activity_instance_id': instance['activity_instance_id'],
                    'case_id': instance['case_id'],
                    'activity_id': instance['activity_id'],
                    'start_date': start_date,
                    'end_date': end_date,
                    'transaction_name': '',
                    'transaction_order': ''
                })
                event_id += 1

        events_df = pd.DataFrame(event_rows, columns=['event_id', 'activity_instance_id', 'case_id', 'activity_id',
                                                      'start_date', 'end_date', 'transaction_name',
                                                      'transaction_order'])
        return events_df
    except Exception as e:
        logging.error(f"Error generating event data: {e}")
        raise


def generate_activity_attribute_data(attribute_definitions: pd.DataFrame, activities: pd.DataFrame) -> pd.DataFrame:
    """
    Generate activity attribute data based on the activities and attribute definitions.

    Args:
        attribute_definitions (pd.DataFrame): DataFrame representing attribute definitions.
        activities (pd.DataFrame): DataFrame representing activities.

    Returns:
        pd.DataFrame: DataFrame representing activity attribute data.
    """

    activity_attribute_rows = []
    activity_definitions = attribute_definitions[attribute_definitions['attribute_type'] == 'activity']
    attribute_values_cache = defaultdict(list)
    as_attribute_mapping = {}

    for activity in activities.itertuples():
        process_id = activity.process_id
        for attribute in activity_definitions[activity_definitions['process_id'] == process_id].itertuples():
            generation_level = attribute.generation_level
            adjustment_type = attribute.adjustment_type
            as_attribute = attribute.as_attribute

            if as_attribute:
                if as_attribute not in as_attribute_mapping:
                    as_attribute_mapping[as_attribute] = []
                as_attribute_mapping[as_attribute].append((activity, attribute))
                continue

            if generation_level == 'process':
                key = process_id
            elif generation_level == 'activity_instance':
                key = activity.activity_id
            else:
                key = activity.activity_instance_id

            if not attribute_values_cache[key]:
                num_values = (
                    len(activities[activities['process_id'] == process_id]) if generation_level == 'process' else
                    len(activities[activities[
                                       'activity_id'] == activity.activity_id]) if generation_level == 'activity_instance' else
                    1
                )
                attribute_values_cache[key] = generate_attribute_values(
                    attribute.attribute_value_type,
                    attribute.distribution,
                    attribute.categories,
                    attribute.range[0],
                    attribute.range[1],
                    num_values=num_values
                )

            value = attribute_values_cache[key].pop(0)
            value = adjust_attribute_value(value, adjustment_type, attribute.range[0], attribute.range[1],
                                           attribute.categories)

            activity_attribute_rows.append({
                'attribute_definition_id': attribute.attribute_id,
                'activity_attribute_id': attribute.attribute_id,
                'activity_id': activity.activity_id,
                'process_id': process_id,
                'generation_level': generation_level,
                'attribute_name': attribute.attribute_name,
                'attribute_value': value
            })

    # Process as_attribute at the end
    for attr_name, attr_list in as_attribute_mapping.items():
        for activity, attribute in attr_list:
            process_id = activity.process_id
            matched_attr = next((attr for attr in activity_definitions.itertuples() if
                                 attr.attribute_name == attr_name and attr.process_id == process_id), None)
            if matched_attr:
                value = next((row['attribute_value'] for row in activity_attribute_rows if
                              row['attribute_name'] == attr_name and row['activity_id'] == activity.activity_id), None)
                if value is not None:
                    activity_attribute_rows.append({
                        'attribute_definition_id': attribute.attribute_id,
                        'activity_attribute_id': attribute.attribute_id,
                        'activity_id': activity.activity_id,
                        'process_id': process_id,
                        'generation_level': attribute.generation_level,
                        'attribute_name': attribute.attribute_name,
                        'attribute_value': value
                    })
                else:
                    raise ValueError(f"Attribute '{attr_name}' value not found for activity ID {activity.activity_id}.")
            else:
                raise ValueError(
                    f"Attribute '{attr_name}' not found in attribute definitions for process ID {process_id}.")

    activity_attribute_df = pd.DataFrame(activity_attribute_rows,
                                         columns=['attribute_definition_id', 'activity_attribute_id', 'activity_id',
                                                  'process_id', 'generation_level', 'attribute_name',
                                                  'attribute_value'])

    return activity_attribute_df


def generate_event_attribute_data(attribute_definitions: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """
    Generate event attribute data based on the events and attribute definitions.

    Args:
        attribute_definitions (pd.DataFrame): DataFrame representing attribute definitions.
        events (pd.DataFrame): DataFrame representing events.

    Returns:
        pd.DataFrame: DataFrame representing event attribute data.
    """

    event_attribute_rows = []
    event_definitions = attribute_definitions[attribute_definitions['attribute_type'] == 'event']
    attribute_values_cache = defaultdict(list)
    as_attribute_mapping = {}

    for event in events.itertuples():
        process_id = event.process_id
        for attribute in event_definitions[event_definitions['process_id'] == process_id].itertuples():
            generation_level = attribute.generation_level
            adjustment_type = attribute.adjustment_type
            as_attribute = attribute.as_attribute

            if as_attribute:
                if as_attribute not in as_attribute_mapping:
                    as_attribute_mapping[as_attribute] = []
                as_attribute_mapping[as_attribute].append((event, attribute))
                continue

            if generation_level == 'process':
                key = process_id
            elif generation_level == 'case':
                key = event.case_id
            else:
                key = (event.activity_instance_id, attribute.attribute_id)

            if not attribute_values_cache[key]:
                num_values = (
                    len(events[events['process_id'] == process_id]) if generation_level == 'process' else
                    len(events[events['case_id'] == event.case_id]) if generation_level == 'case' else
                    1
                )
                attribute_values_cache[key] = [generate_attribute_value(
                    attribute.attribute_value_type,
                    attribute.distribution,
                    attribute.categories,
                    attribute.range[0],
                    attribute.range[1]
                ) for _ in range(num_values)]

            value = attribute_values_cache[key].pop(0)
            value = adjust_attribute_value(value, adjustment_type, attribute.range[0], attribute.range[1],
                                           attribute.categories)

            event_attribute_rows.append({
                'attribute_definition_id': attribute.attribute_id,
                'event_attribute_id': attribute.attribute_id,
                'event_id': event.event_id,
                'activity_instance_id': event.activity_instance_id,
                'generation_level': generation_level,
                'attribute_name': attribute.attribute_name,
                'attribute_value': value
            })

    # Process as_attribute at the end
    for attr_name, attr_list in as_attribute_mapping.items():
        for event, attribute in attr_list:
            process_id = event.process_id
            matched_attr = next((attr for attr in event_definitions.itertuples() if
                                 attr.attribute_name == attr_name and attr.process_id == process_id), None)
            if matched_attr:
                value = next((row['attribute_value'] for row in event_attribute_rows if
                              row['attribute_name'] == attr_name and row['event_id'] == event.event_id), None)
                if value is not None:
                    event_attribute_rows.append({
                        'attribute_definition_id': attribute.attribute_id,
                        'event_attribute_id': attribute.attribute_id,
                        'event_id': event.event_id,
                        'activity_instance_id': event.activity_instance_id,
                        'generation_level': attribute.generation_level,
                        'attribute_name': attribute.attribute_name,
                        'attribute_value': value
                    })
                else:
                    raise ValueError(f"Attribute '{attr_name}' value not found for event ID {event.event_id}.")
            else:
                raise ValueError(
                    f"Attribute '{attr_name}' not found in attribute definitions for process ID {process_id}.")

    event_attribute_df = pd.DataFrame(event_attribute_rows,
                                      columns=['attribute_definition_id', 'event_attribute_id', 'event_id',
                                               'activity_instance_id', 'generation_level', 'attribute_name',
                                               'attribute_value'])

    return event_attribute_df


def generate_case_attribute_data(attribute_definitions: pd.DataFrame, cases: pd.DataFrame) -> pd.DataFrame:
    """
    Generate case attribute data based on the cases and attribute definitions.

 Args:
        attribute_definitions (pd.DataFrame): DataFrame representing attribute definitions.
        cases (pd.DataFrame): DataFrame representing cases.

 Returns:
        pd.DataFrame: DataFrame representing case attribute data.
    """

    case_attribute_rows = []
    case_definitions = attribute_definitions[attribute_definitions['attribute_type'] == 'case']
    attribute_values_cache = defaultdict(list)
    as_attribute_mapping = {}

    for case in cases.itertuples():
        process_id = case.process_id
        for attribute in case_definitions[case_definitions['process_id'] == process_id].itertuples():
            generation_level = attribute.generation_level
            adjustment_type = attribute.adjustment_type
            as_attribute = attribute.as_attribute

            if as_attribute:
                if as_attribute not in as_attribute_mapping:
                    as_attribute_mapping[as_attribute] = []
                as_attribute_mapping[as_attribute].append((case, attribute))
                continue

            if generation_level == 'process':
                key = process_id
            else:
                key = case.case_id

            if not attribute_values_cache[key]:
                num_values = (
                    len(cases[cases['process_id'] == process_id]) if generation_level == 'process' else
                    1
                )
                attribute_values_cache[key] = generate_attribute_values(
                    attribute.attribute_value_type,
                    attribute.distribution,
                    attribute.categories,
                    attribute.range[0],
                    attribute.range[1],
                    num_values=num_values
                )
            value = attribute_values_cache[key].pop(0)
            value = adjust_attribute_value(value, adjustment_type, attribute.range[0], attribute.range[1],
                                           attribute.categories)

            case_attribute_rows.append({
                'attribute_definition_id': attribute.attribute_id,
                'case_attribute_id': attribute.attribute_id,
                'case_id': case.case_id,
                'process_id': process_id,
                'generation_level': generation_level,
                'attribute_name': attribute.attribute_name,
                'attribute_value': value
            })


    # Process as_attribute at the end
    for attr_name, attr_list in as_attribute_mapping.items():
        for case, attribute in attr_list:
            process_id = case.process_id
            matched_attr = next((attr for attr in case_definitions.itertuples() if
                                 attr.attribute_name == attr_name and attr.process_id == process_id), None)
            if matched_attr:
                value = next((row['attribute_value'] for row in case_attribute_rows if
                              row['attribute_name'] == attr_name and row['case_id'] == case.case_id), None)
                if value is not None:
                    case_attribute_rows.append({
                        'attribute_definition_id': attribute.attribute_id,
                        'case_attribute_id': attribute.attribute_id,
                        'case_id': case.case_id,
                        'process_id': process_id,
                        'generation_level': attribute.generation_level,
                        'attribute_name': attribute.attribute_name,
                        'attribute_value': value
                    })
                else:
                    raise ValueError(f"Attribute '{attr_name}' value not found for case ID {case.case_id}.")
            else:
                raise ValueError(
                    f"Attribute '{attr_name}' not found in attribute definitions for process ID {process_id}.")

    case_attribute_df = pd.DataFrame(case_attribute_rows,
                                     columns=['attribute_definition_id', 'case_attribute_id', 'case_id', 'process_id',
                                              'generation_level',
                                              'attribute_name', 'attribute_value'])

    return case_attribute_df


def generate_object_attribute_data(attribute_definitions: pd.DataFrame, objects: pd.DataFrame) -> pd.DataFrame:
    """
    Generate object attribute data based on the objects and attribute definitions.

    Args:
        attribute_definitions (pd.DataFrame): DataFrame representing attribute definitions.
        objects (pd.DataFrame): DataFrame representing objects.

    Returns:
        pd.DataFrame: DataFrame representing object attribute data.
    """
    object_attributes = []
    object_definitions = attribute_definitions[attribute_definitions['attribute_type'] == 'object']
    attribute_values_cache = defaultdict(dict)

    for obj in objects.itertuples():
        process_id = obj.process_id

        for attribute in object_definitions[object_definitions['process_id'] == process_id].itertuples():
            generation_level = attribute.generation_level
            adjustment_type = attribute.adjustment_type
            as_attribute = attribute.as_attribute

            if generation_level == 'process':
                key = process_id
            else:
                key = obj.object_id

            if as_attribute and as_attribute in attribute_values_cache[key]:
                attribute_value = attribute_values_cache[key][as_attribute]
            else:
                if key not in attribute_values_cache or attribute.attribute_name not in attribute_values_cache[key]:
                    num_values = (
                        len(objects[objects['process_id'] == process_id]) if generation_level == 'process' else
                        1
                    )
                    attribute_values_cache[key][attribute.attribute_name] = generate_attribute_values(
                        attribute.attribute_value_type,
                        attribute.distribution if attribute.distribution else 'normal',
                        attribute.categories,
                        attribute.range[0],
                        attribute.range[1],
                        num_values=num_values
                    )

                attribute_value = attribute_values_cache[key][attribute.attribute_name].pop(0)

            value = attribute_value
            if adjustment_type == 'slight change':
                value = random.uniform(attribute_value * 0.95, attribute_value * 1.05)
            elif adjustment_type == 'moderate change':
                value = random.uniform(attribute_value * 0.9, attribute_value * 1.1)
            elif adjustment_type == 'significant change':
                value = random.uniform(attribute.range[0], attribute.range[1])

            object_attributes.append({
                'attribute_definition_id': attribute.attribute_id,
                'object_attribute_id': attribute.attribute_id,
                'process_id': process_id,
                'generation_level': generation_level,
                'attribute_name': attribute.attribute_name,
                'attribute_value': value
            })

    return pd.DataFrame(object_attributes)


def generate_object_type_data(process_config_data: Dict) -> pd.DataFrame:
    """
    Create a DataFrame of object types from the process configuration.

    Args:
        process_config_data (dict): Dictionary containing process configuration.

    Returns:
        pd.DataFrame: DataFrame representing object types.
    """
    try:
        object_type_data = []
        object_type_id = 1

        for process_id, process in enumerate(process_config_data['processes'], start=1):
            for object_type in process['object_types']:
                data = {
                    'process_id': process_id,
                    'object_type_id': object_type_id,
                    'object_type': object_type['name'],
                    'object_qualifiers': object_type['object_qualifiers'],
                    'activity_qualifiers': object_type['activity_qualifiers'],
                    'range': object_type['range'],
                }
                object_type_data.append(data)
                object_type_id += 1

        df = pd.DataFrame(object_type_data)
        logging.info("Object type data generated successfully.")
        return df
    except KeyError as e:
        logging.error(f"Configuration key error: {e}")
        raise e


def generate_objects_data(object_types_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a DataFrame of objects from the process configuration based on object types.

    Args:
        object_types_df (pd.DataFrame): DataFrame representing object types.

    Returns:
        pd.DataFrame: DataFrame representing objects.
    """
    try:
        objects_data = []
        object_id = 1

        for _, row in object_types_df.iterrows():
            obj_type_name = row['object_type']
            range_start = row['range'][0]
            range_end = row['range'][1]
            object_type_id = row['object_type_id']

            for obj_id in range(range_start, range_end + 1):
                object_id_code = f"{initial_capitals(obj_type_name)}{obj_id}"
                data = {
                    'object_id': object_id,
                    'object_type': obj_type_name,
                    'object_type_id': object_type_id,
                    'object_id_code': object_id_code
                }
                objects_data.append(data)
                object_id += 1

        df = pd.DataFrame(objects_data)
        logging.info("Objects data generated successfully.")
        return df
    except KeyError as e:
        logging.error(f"Data key error: {e}")
        raise e


def generate_event_object_data(object_types_df: pd.DataFrame, objects_df: pd.DataFrame,
                               events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a DataFrame of event to object relationships and set qualifier name for such relationships.

    Args:
        object_types_df (pd.DataFrame): DataFrame representing object types.
        objects_df (pd.DataFrame): DataFrame representing objects.
        events_df (pd.DataFrame): DataFrame representing events.

    Returns:
        pd.DataFrame: DataFrame representing event_to_object relationships.
    """
    try:
        event_object_data = []

        for _, event in events_df.iterrows():
            to_activity = event['to_activity']
            for _, obj in objects_df.iterrows():
                if obj['object_type'] == to_activity:
                    qualifier = object_types_df[object_types_df['object_type_id'] == obj['object_type_id']].iloc[0].get(
                        'activity_qualifiers', '')
                    data = {
                        'event_id': event['id'],
                        'object_id': obj['object_id'],
                        'qualifier': qualifier
                    }
                    event_object_data.append(data)

        df = pd.DataFrame(event_object_data)
        logging.info("Event to object data generated successfully.")
        return df
    except KeyError as e:
        logging.error(f"Data key error: {e}")
        raise e


def generate_object_to_object_data(object_types_df: pd.DataFrame, objects_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a DataFrame of object to object relationships and set qualifier name for such relationships.

    Args:
        object_types_df (pd.DataFrame): DataFrame representing object types.
        objects_df (pd.DataFrame): DataFrame representing objects.

    Returns:
        pd.DataFrame: DataFrame representing object_to_object relationships.
    """
    try:
        object_to_object_data = []

        for _, obj in objects_df.iterrows():
            object_id_code = obj['object_id_code']
            for _, related_obj in objects_df.iterrows():
                if obj['object_type'] == related_obj['object_type'] and obj['object_id'] != related_obj['object_id']:
                    qualifier = object_types_df[object_types_df['object_type_id'] == obj['object_type_id']].iloc[0].get(
                        'object_qualifiers', '')
                    data = {
                        'object_id': obj['object_id'],
                        'object_id_code': object_id_code,
                        'related_object_id': related_obj['object_id'],
                        'qualifier': qualifier
                    }
                    object_to_object_data.append(data)

        df = pd.DataFrame(object_to_object_data)
        logging.info("Object to object data generated successfully.")
        return df
    except KeyError as e:
        logging.error(f"Data key error: {e}")
        raise e


def write_data_to_csv(directory, processes, cases=None, attribute_definitions=None, case_attributes=None,
                      activities=None, activity_instances=None, events=None, event_attributes=None):
    """
    Writes the provided process data to CSV files.

    Args:
        directory (str): The directory where the output CSV files will be saved.
        processes (pd.DataFrame): DataFrame representing processes.
        cases (pd.DataFrame): DataFrame representing cases.
        attribute_definitions (pd.DataFrame): DataFrame representing attribute definitions.
        case_attributes (pd.DataFrame): DataFrame representing case attributes.
        activities (pd.DataFrame): DataFrame representing activities.
        activity_instances (pd.DataFrame): DataFrame representing activity instances.
        events (pd.DataFrame): DataFrame representing events.
        event_attributes (pd.DataFrame): DataFrame representing event attributes.
    """
    table_mappings = {
        'attribute_definitions': 'AttributeDefinitions.csv',
        'processes': 'Processes.csv',
        'cases': 'Cases.csv',
        'case_attributes': 'CaseAttributes.csv',
        'activities': 'Activities.csv',
        'activity_instances': 'ActivityInstances.csv',
        'events': 'Events.csv',
        'event_attributes': 'EventAttributes.csv'
    }

    try:
        for df, key in [(attribute_definitions, 'attribute_definitions'), (processes, 'processes'), (cases, 'cases'),
                        (case_attributes, 'case_attributes'), (activities, 'activities'),
                        (activity_instances, 'activity_instances'), (events, 'events'),
                        (event_attributes, 'event_attributes')]:
            if df is not None:
                filepath = f"{directory}/{table_mappings[key]}"
                try:
                    df.to_csv(filepath, index=False)
                    logging.info(f"Successfully wrote {key} data to {filepath}")
                except Exception as e:
                    logging.error(f"Error writing {key} data to {filepath}: {e}")

    except Exception as e:
        logging.critical(f"Failed to write CSV files to directory {directory}: {e}")


def write_data_to_combined_csv(filename, processes, cases=None, attribute_definitions=None, case_attributes=None,
                               activities=None, activity_instances=None, events=None, event_attributes=None):
    """
    Write data to a combined CSV file.

    Args:
        filename (str): The prefix for the output files.
        processes (pd.DataFrame): DataFrame representing processes.
        cases (pd.DataFrame): DataFrame representing cases.
        attribute_definitions (pd.DataFrame): DataFrame representing attribute definitions.
        case_attributes (pd.DataFrame): DataFrame representing case attributes.
        activities (pd.DataFrame): DataFrame representing activities.
        activity_instances (pd.DataFrame): DataFrame representing activity instances.
        events (pd.DataFrame): DataFrame representing events.
        event_attributes (pd.DataFrame): DataFrame representing event attributes.
    """
    try:
        # Merge cases with case attributes
        if cases is not None and case_attributes is not None:
            case_attributes_merged = case_attributes.pivot(index='case_id', columns='case_attribute_name',
                                                           values='case_attribute_value')
            cases = cases.merge(case_attributes_merged, on='case_id', how='left')

        # Merge events with event attributes
        if events is not None and event_attributes is not None:
            event_attributes_merged = event_attributes.pivot(index='event_id', columns='event_attribute_name',
                                                             values='event_attribute_value')
            events = events.merge(event_attributes_merged, on='event_id', how='left')

        # Merge events with activity instances
        if events is not None and activity_instances is not None:
            events = events.merge(activity_instances, on='activity_instance_id', how='left',
                                  suffixes=('', '_activity_instance'))

        # Merge events with activities
        if events is not None and activities is not None:
            events = events.merge(activities, on='activity_id', how='left', suffixes=('', '_activity'))

        # Merge events with cases
        if events is not None and cases is not None:
            events = events.merge(cases, on='case_id', how='left', suffixes=('', '_case'))

        # Merge events with processes
        if events is not None and processes is not None:
            events = events.merge(processes, on='process_id', how='left', suffixes=('', '_process'))

        # Flatten the data to the required columns
        if events is not None:
            combined_data = events[['process_id', 'case_id', 'event_id', 'transaction_type', 'position_in_trace',
                                    'start_time_case', 'end_time_case', 'timestamp', 'end_time',
                                    'activity_name', 'activity_id']]

            # Add case attribute columns
            if case_attributes is not None:
                case_attribute_columns = case_attributes['case_attribute_name'].unique()
                for col in case_attribute_columns:
                    combined_data[col] = events[col]

            # Add event attribute columns
            if event_attributes is not None:
                event_attribute_columns = event_attributes['event_attribute_name'].unique()
                for col in event_attribute_columns:
                    combined_data[col] = events[col]

            output_file = f"combined_{filename}.csv"
            combined_data.to_csv(output_file, index=False)
            logging.info(f"Successfully wrote combined CSV data to {output_file}")

    except Exception as e:
        logging.critical(f"Failed to write combined CSV file: {e}")


def write_data_to_sql(filename, processes, cases=None, attribute_definitions=None, case_attributes=None,
                      activities=None,
                      activity_instances=None, events=None, event_attributes=None):
    """
    Writes the provided process data to an SQL file with INSERT INTO statements.

    Args:
        filename (str): The name of the output SQL file.
        processes (pd.DataFrame): DataFrame representing processes.
        cases (pd.DataFrame): DataFrame representing cases.
        attribute_definitions (pd.DataFrame): DataFrame representing attribute definitions.
        case_attributes (pd.DataFrame): DataFrame representing case attributes.
        activities (pd.DataFrame): DataFrame representing activities.
        activity_instances (pd.DataFrame): DataFrame representing activity instances.
        events (pd.DataFrame): DataFrame representing events.
        event_attributes (pd.DataFrame): DataFrame representing event attributes.
    """
    table_mappings = {
        'processes': {
            'table_name': 'Process',
            'columns': ['process_id', 'process_name', 'description']
        },
        'cases': {
            'table_name': 'Cases',
            'columns': ['case_id', 'process_id', 'timestamp', 'end_time']
        },
        'activities': {
            'table_name': 'Activity',
            'columns': ['activity_id', 'activity_name', 'process_id']
        },
        'activity_instances': {
            'table_name': 'ActivityInstance',
            'columns': ['activity_instance_id', 'activity_id', 'case_id']
        },
        'events': {
            'table_name': 'Event',
            'columns': ['event_id', 'case_id', 'activity_instance_id', 'timestamp', 'end_time', 'position_in_trace',
                        'transaction_type']
        },
        'attribute_definitions': {
            'table_name': 'AttributeDefinition',
            'columns': ['attribute_id', 'attribute_name', 'attribute_type', 'attribute_value_type']
        }
    }

    processed_ids = defaultdict(set)

    try:
        with open(filename, 'w') as f:
            for df, key in [(processes, 'processes'), (cases, 'cases'), (activities, 'activities'),
                            (activity_instances, 'activity_instances'), (events, 'events'),
                            (attribute_definitions, 'attribute_definitions')]:
                if df is not None:
                    table_info = table_mappings[key]
                    table_name = table_info['table_name']
                    columns = table_info['columns']

                    for record in df.itertuples(index=False):
                        primary_key = columns[0]
                        primary_key_value = getattr(record, primary_key)

                        if primary_key_value not in processed_ids[table_name]:
                            processed_ids[table_name].add(primary_key_value)
                            values = ', '.join(f"'{str(getattr(record, col))}'" for col in columns)
                            try:
                                f.write(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({values});\n")
                                logging.info(
                                    f"Successfully wrote record to {table_name} with {primary_key}={primary_key_value}")
                            except Exception as e:
                                logging.error(
                                    f"Error writing record to {table_name} with {primary_key}={primary_key_value}: {e}")
    except Exception as e:
        logging.critical(f"Failed to write to file {filename}: {e}")


def main(config_file, defaults_file, output_type, output_file, logging_file):
    global process_data
    logging.basicConfig(filename=logging_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        process_data = config_init.initialize_configuration(config_file, defaults_file)
        logging.info("Configuration initialized and saved to 'merged_config.yaml'.")
        processes_df = generate_process_data(process_data)
        logging.info("Process data generated")
        activities_df = generate_activity_data(process_data)
        logging.info("Activity data generated")
        attribute_definitions_df = create_attribute_definitions(process_data)
        logging.info("Attribute definitions generated")
        cases_df = generate_case_data(process_data)
        logging.info("Case data generated")
        activity_instances_df = generate_activity_instance_data(process_data, cases_df, activities_df)
        logging.info("Activity instance data generated")
        events_df = generate_event_data(process_data, activity_instances_df, activities_df)
        logging.info("Event data generated")
        case_attributes = generate_case_attribute_data(attribute_definitions_df, cases_df)
        # event_attributes = generate_event_attribute_data(attribute_definitions_df, events_df, activities_df)

        # if output_type == 'csv':
        #     write_data_to_csv(output_file, attribute_definitions_df, processes_df, cases_df, case_attributes,
        #                       activities_df,
        #                       activity_instances_df, events_df,
        #                       event_attributes)
        # elif output_type == 'combined_csv':
        #     write_data_to_combined_csv(output_file, processes_df, cases_df, case_attributes, activities_df,
        #                                activity_instances_df,
        #                                events_df, event_attributes)
        # elif output_type == 'sql':
        #     write_data_to_sql(output_file, processes_df, cases_df, attribute_definitions_df, case_attributes,
        #                       activities_df,
        #                       activity_instances_df, events_df,
        #                       event_attributes)
    except Exception as e:
        logging.error(f"Failed to initialize configuration: {str(e)}")


if __name__ == "__main__":
    logging_file = F"Output/Log Files/EventLogGeneration_{int(dt.datetime.now().timestamp() * 1000)}.log"
    config_file = "Config/processes.yaml"
    defaults_file = "Config/defaults.yaml"
    output_type = "sql"  # Choose between 'csv', 'combined_csv', 'sql'
    output_file = "Output/output.sql"
    main(config_file, defaults_file, output_type, output_file, logging_file)
