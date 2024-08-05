import os

# Define the expected structure for Settings and Defaults YAML
SETTINGS_SCHEMA = {
    'process': {
        'type': dict,
        'mandatory': True,
        'contents': {
            'process_name': {'type': str, 'mandatory': True},
            'process_description': {'type': str, 'mandatory': False},
            'start_date': {'type': str, 'mandatory': False},
            'end_date': {'type': str, 'mandatory': False},
            'num_cases': {'type': int, 'mandatory': False},
            'traces': {'type': list, 'mandatory': False},
            'traces_counts': {'type': list, 'mandatory': False},
            'case_attributes': {
                'type': list,
                'mandatory': False,
                'contents': {
                    'attribute_id': {'type': int, 'mandatory': False},
                    'name': {'type': str, 'mandatory': True},
                    'type': {'type': str, 'mandatory': True},
                    'distribution': {'type': str, 'mandatory': False},
                    'categories': {'type': list, 'mandatory': False},
                    'as_attribute': {'type': str, 'mandatory': False},
                    'range': {'type': list, 'mandatory': False},
                    'resource_type': {'type': str, 'mandatory': False},
                    'resource_count': {'type': int, 'mandatory': False},
                    'generation_level': {'type': str, 'mandatory': False},
                    'adjustment_type': {'type': str, 'mandatory': False},
                },
            },
            'activities': {
                'type': list,
                'mandatory': True,
                'contents': {
                    'name': {'type': str, 'mandatory': True},
                    'trace': {'type': str, 'mandatory': False},
                    'order': {'type': int, 'mandatory': False},
                    'min_weight': {'type': int, 'mandatory': False},
                    'max_weight': {'type': int, 'mandatory': False},
                    'distribution': {'type': str, 'mandatory': False},
                    'duration_range': {'type': list, 'mandatory': False},
                    'duration_uom': {'type': str, 'mandatory': False},
                    'working_hours': {'type': list, 'mandatory': False},
                    'working_days': {'type': list, 'mandatory': False},
                    'transaction_types': {
                        'type': list,
                        'mandatory': False,
                        'contents': {
                            'name': {'type': str, 'mandatory': True},
                            'order': {'type': int, 'mandatory': False},
                            'duration_range': {'type': list, 'mandatory': False},
                            'duration_uom': {'type': str, 'mandatory': False},
                            'working_hours': {'type': list, 'mandatory': False},
                            'working_days': {'type': list, 'mandatory': False},
                        },
                    },
                    'activity_attributes': {
                        'type': list,
                        'mandatory': False,
                        'contents': {
                            'attribute_id': {'type': int, 'mandatory': False},
                            'name': {'type': str, 'mandatory': True},
                            'type': {'type': str, 'mandatory': True},
                            'distribution': {'type': str, 'mandatory': False},
                            'categories': {'type': list, 'mandatory': False},
                            'as_attribute': {'type': str, 'mandatory': False},
                            'resource_type': {'type': str, 'mandatory': False},
                            'resource_count': {'type': int, 'mandatory': False},
                            'generation_level': {'type': str, 'mandatory': False},
                            'range': {'type': list, 'mandatory': False},
                        },
                    },
                },
            },
            'event_attributes': {
                'type': list,
                'mandatory': False,
                'contents': {
                    'attribute_id': {'type': int, 'mandatory': False},
                    'name': {'type': str, 'mandatory': True},
                    'type': {'type': str, 'mandatory': True},
                    'distribution': {'type': str, 'mandatory': False},
                    'categories': {'type': list, 'mandatory': False},
                    'as_attribute': {'type': str, 'mandatory': False},
                    'range': {'type': list, 'mandatory': False},
                    'resource_type': {'type': str, 'mandatory': False},
                    'resource_count': {'type': int, 'mandatory': False},
                    'generation_level': {'type': str, 'mandatory': False},
                    'adjustment_type': {'type': str, 'mandatory': False},
                },
            },
            'object_types': {
                'type': list,
                'mandatory': False,
                'contents': {
                    'name': {'type': str, 'mandatory': True},
                    'range': {'type': list, 'mandatory': False},
                    'resource_type': {'type': str, 'mandatory': False},
                    'object_attributes': {
                                            'type': list,
                                            'mandatory': False,
                                            'contents': {
                                                'attribute_id': {'type': int, 'mandatory': False},
                                                'name': {'type': str, 'mandatory': True},
                                                'type': {'type': str, 'mandatory': True},
                                                'distribution': {'type': str, 'mandatory': False},
                                                'categories': {'type': list, 'mandatory': False},
                                                'as_attribute': {'type': str, 'mandatory': False},
                                                'range': {'type': list, 'mandatory': False},
                                                'resource_type': {'type': str, 'mandatory': False},
                                                'resource_count': {'type': int, 'mandatory': False},
                                                'generation_level': {'type': str, 'mandatory': False},
                                                'adjustment_type': {'type': str, 'mandatory': False},
                                            },
                                        },
                    'activity_qualifiers': {
                        'type': list,
                        'mandatory': False,
                        'contents': {
                            'name': {'type': str, 'mandatory': True},
                            'to_activity': {'type': str, 'mandatory': True},
                        },
                    },
                    'object_qualifiers': {
                        'type': list,
                        'mandatory': False,
                        'contents': {
                            'name': {'type': str, 'mandatory': True},
                            'to_object': {'type': str, 'mandatory': True},
                        },
                    },
                },
            },
        },
    },
}

DEFAULTS_SCHEMA = {
    "general_defaults": {
        "type": "dict",
        'mandatory': True,
        "schema": {
            "process_id_start": {"type": "integer", "required": True},
            "case_id_start": {"type": "integer", "required": True},
            "attribute_definition_id_start": {"type": "integer", "required": True},
            "case_attribute_id_start": {"type": "integer", "required": True},
            "activity_id_start": {"type": "integer", "required": True},
            "activity_instance_id_start": {"type": "integer", "required": True},
            "event_id_start": {"type": "integer", "required": True},
            "event_attribute_id_start": {"type": "integer", "required": True},
            "object_id": {"type": "integer", "required": True},
            "object_type_id": {"type": "integer", "required": True},
            "object_attribute_id": {"type": "integer", "required": True},
        },
        "required": True,
    },
    "trace_generation_defaults": {
        "type": "dict",
        'mandatory': True,
        "schema": {
            "additional_trace_patterns_range": {"type": "list", "schema": {"type": "integer"}, "required": True},
            "replays_range": {"type": "list", "schema": {"type": "integer"}, "required": True},
            "traces_in_pattern_range": {"type": "list", "schema": {"type": "integer"}, "required": True},
        },
        "required": True,
    },
    "process_defaults": {
        "type": "dict",
        'mandatory': True,
        "schema": {
            "num_cases": {"type": "integer", "required": True},
            "case_attributes": {"type": "list", "schema": {"type": "dict"}, "required": True},
            "event_attributes": {"type": "list", "schema": {"type": "dict"}, "required": True},
            "object_types": {"type": "list", "schema": {"type": "dict"}, "required": True},
            "description": {"type": "string", "required": True},
            "working_days": {"type": "list", "schema": {"type": "string"}, "required": True},
            "working_hours": {"type": "list", "schema": {"type": "integer"}, "required": True},
        },
        "required": True,
    },
    "activity_defaults": {
        "type": "dict",
        'mandatory': True,
        "schema": {
            "min_weight": {"type": "integer", "required": True},
            "max_weight": {"type": "integer", "required": True},
            "duration_range": {"type": "list", "schema": {"type": "integer"}, "required": True},
            "duration_uom": {"type": "string", "allowed": ["seconds", "minutes", "hours", "days"], "required": True},
            "transaction_types": {"type": "list", "schema": {"type": "dict"}, "required": True},
            "transaction_duration_range": {"type": "list", "schema": {"type": "integer"}, "required": True},
            "transaction_duration_uom": {"type": "string", "allowed": ["seconds", "minutes", "hours", "days"], "required": True},
            "activity_attributes": {"type": "list", "schema": {"type": "dict"}, "required": True},
            "working_days": {"type": "list", "schema": {"type": "string"}, "required": True},
            "working_hours": {"type": "list", "schema": {"type": "integer"}, "required": True},
        },
        "required": True,
    },
    "attribute_defaults": {
        "type": "dict",
        'mandatory': True,
        "schema": {
            "range": {"type": "list", "schema": {"type": "integer"}, "required": True},
            "distribution": {"type": "string", "required": True},
            "type": {"type": "string", "required": True},
            "as_attribute": {"type": "string", "required": True},
            "adjustment_type": {
                "type": "string",
                "allowed": ["no change", "slight change", "moderate change", "significant change"],
                "required": True,
            },
            "generation_level": {"type": "string", "required": True},
            "resource_type": {"type": "string", "required": True},
            "resource_count": {
                "type": "integer",
                "required": True,
            },
        },
        "required": True,
    },
    "object_type_defaults": {
        "type": "dict",
        'mandatory': True,
        "schema": {
            "range": {"type": "list", "schema": {"type": "integer"}, "required": True},
            "object_attributes": {"type": "list", "schema": {"type": "dict"}, "required": True},
            "activity_qualifiers": {"type": "list", "schema": {"type": "dict"}, "required": True},
        },
        "required": True,
    },
}


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    DEFAULTS_UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads\\defaults')
    SETTINGS_UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads\\settings')
    DEFAULTS_DOWNLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'downloads\\defaults')
    SETTINGS_DOWNLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'downloads\\settings')
    CONFIG_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config')
    DEFAULTS_SCHEMA = DEFAULTS_SCHEMA
    SETTINGS_SCHEMA = SETTINGS_SCHEMA
    ALLOWED_EXTENSIONS = {'yaml'}
