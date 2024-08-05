import datetime
import random
import yaml
from typing import Any, Dict, List, Union
import logging

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def generate_trace_label(index: int, alphabet_size: int = 26, alphabet_start: str = 'a') -> str:
    """
    Generate a trace label given an index.
    Args:
        index (int): The index to generate the label for.
        alphabet_size (int): The size of the alphabet (default is 26 for 'a' to 'z').
        alphabet_start (str): The starting character of the alphabet (default is 'a').
    Returns:
        str: The generated trace label.
    """
    if index > alphabet_size - 1:
        return generate_trace_label(index // alphabet_size, alphabet_size) + chr(ord(alphabet_start) + index % alphabet_size)
    else:
        return chr(ord(alphabet_start) + index)

def initialize_activity_defaults(activity: Dict[str, Any], index: int, activity_defaults: Dict[str, Any]) -> Dict[
    str, Any]:
    """
    Initialize default values for an activity if they are not present.

    Args:
        activity (Dict[str, Any]): The activity dictionary to initialize.
        index (int): The index of the activity in the list.
        activity_defaults (Dict[str, Any]): The default values for activities.

    Returns:
        Dict[str, Any]: The activity dictionary with defaults applied where necessary.
    """
    activity.setdefault('order', index + 1)
    activity.setdefault('trace', generate_trace_label(index))
    activity.setdefault('min_weight', activity_defaults['min_weight'])
    activity.setdefault('max_weight', activity_defaults['max_weight'])
    activity.setdefault('duration_range', activity_defaults['duration_range'])
    activity.setdefault('duration_uom', activity_defaults['duration_uom'])
    activity.setdefault('transaction_types', activity_defaults['transaction_types'])
    activity.setdefault('activity_attributes', activity_defaults['activity_attributes'])
    for transaction_type in activity['transaction_types']:
        transaction_type.setdefault('order', index + 1)
        transaction_type.setdefault('duration_range', activity_defaults['transaction_duration_range'])
        transaction_type.setdefault('duration_uom', activity_defaults['transaction_duration_uom'])
        transaction_type.setdefault('working_days', activity['working_days'])
        transaction_type.setdefault('working_hours', activity['working_hours'])
    return activity


def initialize_attribute_defaults(attribute: Dict[str, Any], attribute_defaults: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize default values for an attribute if they are not present.

    Args:
        attribute (Dict[str, Any]): The attribute dictionary to initialize.
        attribute_defaults (Dict[str, Any]): The default values for attributes.

    Returns:
        Dict[str, Any]: The attribute dictionary with defaults applied where necessary.
    """
    attribute.setdefault('range', attribute_defaults['range'])
    attribute.setdefault('distribution', attribute_defaults['distribution'])
    attribute.setdefault('type', attribute_defaults['type'])
    attribute.setdefault('as_attribute', attribute_defaults['as_attribute'])
    attribute.setdefault('adjustment_type', attribute_defaults['adjustment_type'])
    attribute.setdefault('generation_level', attribute_defaults['generation_level'])
    attribute.setdefault('categories', attribute_defaults['categories'])
    attribute.setdefault('resource_type', attribute_defaults['resource_type'])
    attribute.setdefault('resource_count', attribute_defaults['resource_count'])

    return attribute


def generate_trace_patterns(activities: List[Dict[str, Any]], num_cases: int, trace_gen_defaults: Dict[str, Any]) -> \
List[str]:
    """
    Generate random trace patterns based on the activities and number of cases.

    Args:
        activities (List[Dict[str, Any]]): List of activities with their details.
        num_cases (int): The number of cases to generate traces for.
        trace_gen_defaults (Dict[str, Any]): Default values for trace generation from the defaults.yaml.

    Returns:
        List[str]: A list of generated trace patterns.
    """
    activity_traces = [activity['trace'] for activity in activities]
    trace_patterns = {}

    # Get ranges from defaults
    additional_trace_patterns_range = trace_gen_defaults['additional_trace_patterns_range']
    replays_range = trace_gen_defaults['replays_range']
    traces_in_pattern_range = trace_gen_defaults['traces_in_pattern_range']

    # Ensure at least one trace pattern is in the order of activity 'order'
    ordered_traces = sorted(activities, key=lambda x: x['order'])
    ordered_pattern = ','.join([activity['trace'] for activity in ordered_traces])
    ordered_replays = random.randint(replays_range[0], replays_range[1])
    trace_patterns[ordered_pattern] = ordered_replays

    # Generate additional random trace patterns
    num_additional_patterns = random.randint(additional_trace_patterns_range[0], additional_trace_patterns_range[1])
    for _ in range(num_additional_patterns):
        random_pattern = random.choices(activity_traces,
                                        k=random.randint(traces_in_pattern_range[0], traces_in_pattern_range[1]))
        random_pattern_sorted = sorted(random_pattern, key=lambda trace: next(
            activity['order'] for activity in activities if activity['trace'] == trace))
        random_pattern_str = ','.join(random_pattern_sorted)
        random_replays = random.randint(replays_range[0], replays_range[1])

        if random_pattern_str in trace_patterns:
            trace_patterns[random_pattern_str] += random_replays
        else:
            trace_patterns[random_pattern_str] = random_replays

    # Convert trace patterns to the required format
    trace_patterns_list = [f"({pattern})^{replays}" for pattern, replays in trace_patterns.items()]

    return trace_patterns_list


def initialize_configuration(config_file: str, defaults_file: str) -> Dict[str, Any]:
    """
    Initialize the configuration by reading from YAML files and setting default values.

    Args:
        config_file (str): Path to the configuration YAML file.
        defaults_file (str): Path to the defaults YAML file.

    Returns:
        Dict[str, Any]: The initialized configuration dictionary.
    """
    try:
        with open(config_file, 'r') as cfg_file:
            config = yaml.safe_load(cfg_file)
        with open(defaults_file, 'r') as dft_file:
            defaults = yaml.safe_load(dft_file)

        general_defaults = defaults['general_defaults']
        process_defaults = defaults['process_defaults']
        activity_defaults = defaults['activity_defaults']
        attribute_defaults = defaults['attribute_defaults']
        object_type_defaults = defaults['object_type_defaults']
        trace_gen_defaults = defaults['trace_generation_defaults']

        today = datetime.date.today()
        default_start_date = today.isoformat()
        default_end_date = (today + datetime.timedelta(days=30)).isoformat()

        general_defaults.setdefault('start_date', default_start_date)
        general_defaults.setdefault('end_date', default_start_date)

        config.setdefault('process_id', general_defaults['process_id_start'])
        config.setdefault('case_id', general_defaults['case_id_start'])
        config.setdefault('attribute_definition_id', general_defaults['attribute_definition_id_start'])
        config.setdefault('case_attribute_id', general_defaults['case_attribute_id_start'])
        config.setdefault('activity_id', general_defaults['activity_id_start'])
        config.setdefault('activity_instance_id', general_defaults['activity_instance_id_start'])
        config.setdefault('event_id', general_defaults['event_id_start'])
        config.setdefault('event_attribute_id', general_defaults['event_attribute_id_start'])
        config.setdefault('object_id', general_defaults['object_id'])
        config.setdefault('object_type_id', general_defaults['object_type_id'])
        config.setdefault('object_attribute_id', general_defaults['object_attribute_id'])

        process_id = config['process_id']

        for process_key, process in config['processes'].items():
            process.setdefault('start_date', general_defaults['start_date'])
            process.setdefault('end_date', general_defaults['end_date'])
            process['process_id'] = process.get('process_id', process_id)
            process_id += 1

            process.setdefault('num_cases', process_defaults['num_cases'])
            process.setdefault('case_attributes', process_defaults['case_attributes'])
            process.setdefault('event_attributes', process_defaults['event_attributes'])
            process.setdefault('object_types', process_defaults['object_types'])
            process.setdefault('description', process_defaults['description'])
            process.setdefault('working_days', process_defaults['working_days'])
            process.setdefault('working_hours', process_defaults['working_hours'])

            # Ensure activities are initialized with defaults
            for index, activity in enumerate(process.get('activities', [])):
                activity.setdefault('working_days', process['working_days'])
                activity.setdefault('working_hours', process['working_hours'])
                process['activities'][index] = initialize_activity_defaults(activity, index, activity_defaults)

                for attr_index, attr in enumerate(activity.get('activity_attributes', [])):
                    activity['activity_attributes'][attr_index] = initialize_attribute_defaults(attr,
                                                                                                attribute_defaults)

            for attr_index, attr in enumerate(process.get('case_attributes', [])):
                process['case_attributes'][attr_index] = initialize_attribute_defaults(attr, attribute_defaults)

            for attr_index, attr in enumerate(process.get('event_attributes', [])):
                process['event_attributes'][attr_index] = initialize_attribute_defaults(attr, attribute_defaults)

            for obj_index, object_type in enumerate(process.get('object_types', [])):
                object_type.setdefault('order', obj_index + 1)
                object_type.setdefault('object_attributes', object_type_defaults['object_attributes'])
                object_type.setdefault('activity_qualifiers', object_type_defaults['activity_qualifiers'])
                for attr_index, attr in enumerate(object_type.get('object_attributes', [])):
                    object_type['object_attributes'][attr_index] = initialize_attribute_defaults(attr,
                                                                                                 attribute_defaults)

            # Generate or use provided trace patterns
            trace_patterns = process.get('traces', [])
            if not process.get('traces') or len(process.get('traces')) == 0:
                trace_patterns = generate_trace_patterns(process['activities'], process['num_cases'], trace_gen_defaults)
                process['traces'] = trace_patterns

            # Calculate trace counts based on patterns
            trace_counts = {}
            total_traces = 0
            for pattern in trace_patterns:
                if '^' in pattern:
                    pattern_cases = int(pattern.split('^')[1])
                    pattern = pattern.split('^')[0].replace('(', '').replace(')', '')
                else:
                    pattern_cases = 1  # Default if no ^ is provided
                    pattern = pattern.replace('(', '').replace(')', '')
                trace_counts[pattern] = pattern_cases
                total_traces += pattern_cases

            # Scale trace patterns to match num_cases
            if total_traces > process['num_cases']:
                process['num_cases'] = total_traces

            scale_factor = process['num_cases'] / total_traces
            scaled_trace_counts = {k: int(v * scale_factor) for k, v in trace_counts.items()}

            # Ensure the total number of cases matches num_cases
            remaining_cases = process['num_cases'] - sum(scaled_trace_counts.values())
            if remaining_cases > 0:
                for k in list(scaled_trace_counts.keys()):
                    if remaining_cases == 0:
                        break
                    scaled_trace_counts[k] += 1
                    remaining_cases -= 1

            process['trace_counts'] = scaled_trace_counts
            config['processes'][process_key] = process

        return config

    except yaml.YAMLError as e:
        logger.error(f"Error reading YAML files: {e}")
        raise
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise