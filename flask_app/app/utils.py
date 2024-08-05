import yaml
import os
from flask import current_app, flash
from datetime import datetime
from glob import glob
from typing import Any, Dict, List, Union, Tuple


def validate_structure(data: Any, schema: Dict[str, Any], path: str = '') -> List[str]:
    errors = []
    if isinstance(data, dict):
        for key, value in schema.items():
            current_path = f"{path}.{key}" if path else key
            if value['mandatory'] and key not in data:
                errors.append(f"Mandatory field '{current_path}' is missing.")
                continue

            if key in data:
                if 'contents' in value and isinstance(data[key], dict):
                    errors.extend(validate_structure(data[key], value['contents'], current_path))
                elif 'contents' in value and isinstance(data[key], list):
                    for i, item in enumerate(data[key]):
                        errors.extend(validate_structure(item, value['contents'], f"{current_path}[{i}]"))
                elif not isinstance(data[key], value['type']):
                    errors.append(f"Field '{current_path}' should be of type {value['type'].__name__}.")

    elif isinstance(data, list):
        for item in data:
            validate_structure(item, schema['contents'])

    return errors


def validate_yaml(file_path: str, schema: str) -> tuple[bool, ValueError] | tuple[bool, str]:
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    errors = []
    if schema == 'defaults':
        validation_schema = current_app.config['DEFAULT_SCHEMA']
        errors.append(validate_structure(data, validation_schema))
    else:
        validation_schema = current_app.config['SETTINGS_SCHEMA']
        for process_key, process in data['processes'].items():
            process['process'] = process
            result = validate_structure(process, validation_schema)
            if result:
                errors.append(({process_key: result}))

    if errors:
        return False, ValueError("Validation errors:\n" + "\n".join({k: v for d in errors for k, v in d.items()}))
    else:
        return True, f'{file_path} is valid.'


def list_defaults():
    directories = [
        current_app.config['DEFAULTS_DOWNLOAD_FOLDER'],
        current_app.config['DEFAULTS_UPLOAD_FOLDER']
    ]

    # Ensure that the directories exist and create them if they don't
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    # Get the allowed file extensions
    allowed_extensions = tuple(current_app.config['ALLOWED_EXTENSIONS'])

    # Initialize an empty list to hold the configuration file details as tuples
    configs = []

    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(allowed_extensions):
                    filepath = os.path.join(root, file)
                    configs.append((filepath, file))

    # Return the list of configuration files as tuples
    return configs


def list_configs():
    # Define the directories to scan
    directories = [
        current_app.config['DEFAULTS_DOWNLOAD_FOLDER'],
        current_app.config['DEFAULTS_UPLOAD_FOLDER'],
        current_app.config['SETTINGS_DOWNLOAD_FOLDER'],
        current_app.config['SETTINGS_UPLOAD_FOLDER']
    ]

    # Ensure that the directories exist and create them if they don't
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    # Get the allowed file extensions
    allowed_extensions = tuple(current_app.config['ALLOWED_EXTENSIONS'])

    # Initialize the list to hold the configuration file details
    configs = []

    # Scan the directories for files with the allowed extensions
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(allowed_extensions):
                    filepath = os.path.join(root, file)
                    created = datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                    file_type = 'Defaults' if 'defaults' in filepath else 'Settings'
                    configs.append({
                        'filename': file,
                        'created': created,
                        'type': file_type
                    })

    # Return the list of configuration files
    return configs


def load_strings(filename='strings.yaml'):
    try:
        with open(os.path.join(current_app.config['CONFIG_FOLDER'], filename), 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return {}


def load_defaults(filename='defaults.yaml'):
    try:
        with open(os.path.join(current_app.config['CONFIG_FOLDER'], filename), 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return {}


def save_defaults(data):
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'defaults_{timestamp}.yaml'
    os.makedirs(current_app.config['DEFAULTS_DOWNLOAD_FOLDER'], exist_ok=True)
    with open(os.path.join(current_app.config['DEFAULTS_DOWNLOAD_FOLDER'], filename), 'w') as file:
        yaml.safe_dump(data, file)
    return filename


def save_settings(data):
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'process_settings_{timestamp}.yaml'
    os.makedirs(current_app.config['SETTINGS_DOWNLOAD_FOLDER'], exist_ok=True)
    with open(os.path.join(current_app.config['SETTINGS_DOWNLOAD_FOLDER'], filename), 'w') as file:
        yaml.safe_dump(data, file)
    return filename


def delete_default(filename):
    file_path = os.path.join(current_app.config['DEFAULTS_DOWNLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.chmod(file_path, 0o777)
        os.remove(file_path)
        flash('File deleted successfully!', 'success')
    else:
        flash('File not found', 'danger')


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
