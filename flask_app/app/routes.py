import os
from datetime import datetime
import yaml
import logging
from flask import render_template, request, redirect, url_for, flash, Blueprint, send_from_directory, \
    current_app, jsonify
from werkzeug.utils import secure_filename
from .forms import ConfigDefaultForm, DeleteFileForm, ConfigSettingsForm, ProcessForm
from .utils import load_defaults, save_defaults, load_strings, list_configs, delete_default, allowed_file, \
    save_settings, validate_yaml
from .init_processes import initialize_configuration


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)


@main.route('/')
def index():
    logger.info('Index returned')
    configs = list_configs()
    return render_template('index.html', configs=configs)


@main.route('/config/settings/form', methods=['GET', 'POST'])
def settings_config_form():
    settings_form = ConfigSettingsForm()
    tooltips = load_strings()

    if settings_form.validate_on_submit():
        # Process the settings form data
        settings = {
            'processes': []
        }
        for process in settings_form.processes.entries:
            process_data = {
                'process_name': process.process_name.data,
                'process_description': process.process_description.data,
                'process_id': process.process_id.data,
                'case_id': process.case_id.data,
                'start_date': process.start_date.data,
                'end_date': process.end_date.data,
                'num_cases': process.num_cases.data,
                'traces': [trace.data for trace in process.traces.entries],
                'case_attributes': [attr.data for attr in process.case_attributes.entries],
                'activities': [act.data for act in settings_form.activities],
                'event_attributes': [attr.data for attr in process.event_attributes.entries],
                'object_types': [obj_type.data for obj_type in process.object_types.entries]
                # Add other loops for activity_attributes, transaction_types, object_attributes, object_qualifiers and activity_qualifiers
            }

            for activity in process.activities.entries:
                activity_data = {
                    'activity_id': activity.activity_id.data,
                    'name': activity.name.data,
                    'trace': activity.trace.data,
                    'order': activity.order.data,
                    'min_weight': activity.min_weight.data,
                    'max_weight': activity.max_weight.data,
                    'distribution': activity.distribution.data,
                    'duration_range_min': activity.duration_range_min.data,
                    'duration_range_max': activity.duration_range_max.data,
                    'duration_uom': activity.duration_uom.data,
                    'working_hours_min': activity.working_hours_min.data,
                    'working_hours_max': activity.working_hours_max.data,
                    'working_days': activity.working_days.data,
                    'transaction_types': [],
                    'activity_attributes': [attr.data for attr in activity.activity_attributes.entries]
                }
                for trans_type in activity.transaction_types.entries:
                    trans_type_data = {
                        'name': trans_type.name.data,
                        'custom_type': trans_type.custom_type.data,
                        'order': trans_type.order.data,
                        'transaction_duration_range_min': trans_type.transaction_duration_range_min.data,
                        'transaction_duration_range_max': trans_type.transaction_duration_range_max.data,
                        'transaction_duration_uom': trans_type.transaction_duration_uom.data
                    }
                    activity_data['transaction_types'].append(trans_type_data)
                process_data['activities'].append(activity_data)

                process_data['activities'].append(activity_data)
            # Add other loops for traces, case_attributes, event_attributes and object_types
            settings['processes'].append(process_data)

        # Save the settings using a utility function
        save_settings(settings)
        flash('Settings updated successfully.', 'success')
        return redirect(url_for('main.index'))

    return render_template('settings_config_form.html', form=settings_form, tooltips=tooltips)


@main.route('/config/defaults/form', methods=['GET', 'POST'])
def defaults_config_form():
    defaults_form = ConfigDefaultForm()
    tooltips = load_strings()

    if request.method == 'GET' and os.path.exists('app/config/defaults.yaml'):
        defaults = load_defaults()
        # Populate the defaults_form with existing data
        defaults_form.process_id_start.data = defaults['general_defaults'].get('process_id_start')
        defaults_form.case_id_start.data = defaults['general_defaults'].get('case_id_start')
        defaults_form.attribute_definition_id_start.data = defaults['general_defaults'].get(
            'attribute_definition_id_start')
        defaults_form.case_attribute_id_start.data = defaults['general_defaults'].get('case_attribute_id_start')
        defaults_form.activity_id_start.data = defaults['general_defaults'].get('activity_id_start')
        defaults_form.activity_instance_id_start.data = defaults['general_defaults'].get('activity_instance_id_start')
        defaults_form.event_id_start.data = defaults['general_defaults'].get('event_id_start')
        defaults_form.event_attribute_id_start.data = defaults['general_defaults'].get('event_attribute_id_start')
        defaults_form.object_id.data = defaults['general_defaults'].get('object_id')
        defaults_form.object_type_id.data = defaults['general_defaults'].get('object_type_id')

        defaults_form.additional_trace_patterns_range_min.data = \
        defaults['trace_generation_defaults']['additional_trace_patterns_range'][0]
        defaults_form.additional_trace_patterns_range_max.data = \
        defaults['trace_generation_defaults']['additional_trace_patterns_range'][1]
        defaults_form.replays_range_min.data = defaults['trace_generation_defaults']['replays_range'][0]
        defaults_form.replays_range_max.data = defaults['trace_generation_defaults']['replays_range'][1]
        defaults_form.traces_in_pattern_range_min.data = defaults['trace_generation_defaults']['traces_in_pattern_range'][
            0]
        defaults_form.traces_in_pattern_range_max.data = defaults['trace_generation_defaults']['traces_in_pattern_range'][
            1]

        defaults_form.num_cases.data = defaults['process_defaults'].get('num_cases')

        defaults_form.min_weight.data = defaults['activity_defaults'].get('min_weight')
        defaults_form.max_weight.data = defaults['activity_defaults'].get('max_weight')
        defaults_form.duration_range_min.data = defaults['activity_defaults']['duration_range'][0]
        defaults_form.duration_range_max.data = defaults['activity_defaults']['duration_range'][1]
        defaults_form.duration_uom.data = defaults['activity_defaults'].get('duration_uom')
        defaults_form.transaction_types.data = defaults['activity_defaults'].get('transaction_types')
        defaults_form.transaction_duration_range_min.data = defaults['activity_defaults']['transaction_duration_range'][0]
        defaults_form.transaction_duration_range_max.data = defaults['activity_defaults']['transaction_duration_range'][1]
        defaults_form.transaction_duration_uom.data = defaults['activity_defaults'].get('transaction_duration_uom')

        defaults_form.attribute_range_min.data = defaults['attribute_defaults']['range'][0]
        defaults_form.attribute_range_max.data = defaults['attribute_defaults']['range'][1]
        defaults_form.distribution.data = defaults['attribute_defaults'].get('distribution')
        defaults_form.adjustment_type.data = defaults['attribute_defaults'].get('adjustment_type')
        defaults_form.generation_level.data = defaults['attribute_defaults'].get('generation_level')
        defaults_form.resource_type.data = defaults['attribute_defaults'].get('resource_type')
        defaults_form.resource_count.data = defaults['attribute_defaults'].get('resource_count')
        defaults_form.object_range_min.data = defaults['object_type_defaults']['range'][0]
        defaults_form.object_range_max.data = defaults['object_type_defaults']['range'][1]

    if defaults_form.validate_on_submit():
        defaults = {
            'general_defaults': {
                'process_id_start': int(defaults_form.process_id_start.data),
                'case_id_start': int(defaults_form.case_id_start.data),
                'attribute_definition_id_start': int(defaults_form.attribute_definition_id_start.data),
                'case_attribute_id_start': int(defaults_form.case_attribute_id_start.data),
                'activity_id_start': int(defaults_form.activity_id_start.data),
                'activity_instance_id_start': int(defaults_form.activity_instance_id_start.data),
                'event_id_start': int(defaults_form.event_id_start.data),
                'event_attribute_id_start': int(defaults_form.event_attribute_id_start.data),
                'object_id': int(defaults_form.object_id.data),
                'object_type_id': int(defaults_form.object_type_id.data),
            },
            'trace_generation_defaults': {
                'additional_trace_patterns_range': [int(defaults_form.additional_trace_patterns_range_min.data),
                                                    int(defaults_form.additional_trace_patterns_range_max.data)],
                'replays_range': [int(defaults_form.replays_range_min.data), int(defaults_form.replays_range_max.data)],
                'traces_in_pattern_range': [int(defaults_form.traces_in_pattern_range_min.data),
                                            int(defaults_form.traces_in_pattern_range_max.data) + 1]
            },
            'process_defaults': {
                'num_cases': int(defaults_form.num_cases.data),
                'case_attributes': [],
                'event_attributes': [],
                'object_types': [],
            },
            'activity_defaults': {
                'min_weight': float(defaults_form.min_weight.data),
                'max_weight': float(defaults_form.max_weight.data),
                'duration_range': [int(defaults_form.duration_range_min.data),
                                   int(defaults_form.duration_range_max.data)],
                'duration_uom': defaults_form.duration_uom.data,
                'transaction_types': [s for s in defaults_form.transaction_types.data if s != ''],
                'transaction_duration_range': [int(defaults_form.transaction_duration_range_min.data),
                                               int(defaults_form.transaction_duration_range_max.data)],
                'transaction_duration_uom': defaults_form.transaction_duration_uom.data,
                'activity_attributes': [],
                'working_days': [],
                'working_hours': [],
            },
            'attribute_defaults': {
                'range': [int(defaults_form.attribute_range_min.data),
                          int(defaults_form.attribute_range_max.data)],
                'distribution': defaults_form.distribution.data,
                'adjustment_type': defaults_form.adjustment_type.data,
                'generation_level': defaults_form.generation_level.data,
            },
            'object_type_defaults': {
                'range': [int(defaults_form.object_range_min.data),
                          int(defaults_form.object_range_max.data)],
                'object_attributes': [],
                'activity_qualifiers': [],
            }
        }

        # Save the defaults to a YAML file
        save_defaults(defaults)
        flash('Defaults saved successfully!', 'success')
        return redirect(url_for('main.index'))

    return render_template('default_config_form.html', form=defaults_form, tooltips=tooltips)

@main.route('/download/<filename>')
def download_config(filename):
    directories = [
        current_app.config['DEFAULTS_DOWNLOAD_FOLDER'],
        current_app.config['DEFAULTS_UPLOAD_FOLDER'],
        current_app.config['SETTINGS_DOWNLOAD_FOLDER'],
        current_app.config['SETTINGS_UPLOAD_FOLDER']
    ]
    for directory in directories:
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path):
            return send_from_directory(directory=directory, path=filename)
    flash('File not found.', 'danger')
    return redirect(url_for('main.available_configs'))


@main.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        config_type = request.form.get('config_type')
        if file and allowed_file(file.filename) and config_type in ['defaults', 'settings']:
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', config_type, filename)
            file.save(file_path)
            is_valid, message = validate_yaml(file_path, config_type)
            if not is_valid:
                os.remove(file_path)
                flash(f'Validation error: {str(message)}')
                return redirect(request.url)
            flash(f'{config_type.capitalize()} file successfully uploaded and validated!', 'success')
            return redirect(url_for('main.index'))
    return render_template('upload_form.html')


@main.route('/delete/<filename>', methods=['POST'])
def delete_config_file(filename):
    directories = [
        current_app.config['DEFAULTS_DOWNLOAD_FOLDER'],
        current_app.config['DEFAULTS_UPLOAD_FOLDER'],
        current_app.config['SETTINGS_DOWNLOAD_FOLDER'],
        current_app.config['SETTINGS_UPLOAD_FOLDER']
    ]
    file_deleted = False
    for directory in directories:
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            file_deleted = True
            break
    if file_deleted:
        flash(f'File {filename} deleted successfully.', 'success')
    else:
        flash(f'File {filename} not found.', 'danger')
    return redirect(url_for('main.index'))


@main.route('/confirm-delete/<filename>', methods=['GET'])
def confirm_delete(filename):
    return render_template('confirm_delete.html', filename=filename)


@main.route('/available_configs')
def available_configs():
    configs = list_configs()
    return render_template('available_configs.html', configs=configs)


@main.route('/initialize_config', methods=['GET', 'POST'])
def initialize_config():
    if request.method == 'POST':
        defaults_file = request.form.get('defaults_file')
        settings_file = request.form.get('settings_file')
        if defaults_file and settings_file:
            result_config = initialize_configuration(defaults_file, settings_file)
            result_filename = request.form.get('result_filename')
            save_path = os.path.join('downloads', 'settings', result_filename)
            with open(save_path, 'w') as file:
                yaml.dump(result_config, file)
            flash('Configuration initialized and saved successfully!', 'success')
            return redirect(url_for('main.index'))
    return render_template('initialize_config.html')


@main.route('/delete/config/<int:config_id>', methods=['POST'])
def delete_config(config_id):
    # Logic to delete the configuration
    flash('Configuration deleted successfully!', 'success')
    return ('', 204)
