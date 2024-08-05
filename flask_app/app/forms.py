from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, IntegerField, SelectField, FieldList, FormField, DateField
from wtforms.fields.core import DecimalField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired, Optional, NumberRange
import logging

from flask_app.app.utils import list_configs, list_defaults

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AttributesForm(FlaskForm):
    attribute_id = IntegerField('Attribute ID', validators=[Optional(), NumberRange(min=1)])
    name = StringField('Name', validators=[DataRequired()])
    type = SelectField('Type', choices=[('Categorical', 'Categorical'), ('Numeric', 'Numeric'),
                                        ('Resource', 'Resource'), ('Character', 'Character'), ('Geo', 'Geo'),
                                        ('Company', 'Company'),
                                        ('PhoneNumber', 'PhoneNumber'), ('Email', 'Email'), ('Address', 'Address'),
                                        ('UUID', 'UUID'), ('DateTime', 'DateTime'), ('Money', 'Money')],
                       validators=[DataRequired()])
    distribution = SelectField('Distribution',
                               choices=[('normal', 'Normal'), ('uniform', 'Uniform'), ('exponential', 'Exponential'),
                                        ('pareto', 'Pareto')], validators=[Optional()])
    categories = StringField('Categories', validators=[Optional()])
    as_attribute = StringField('As Attribute', validators=[Optional()])
    range_min = IntegerField('Range Min', validators=[Optional(), NumberRange(min=0)])
    range_max = IntegerField('Range Max', validators=[Optional(), NumberRange(min=0)])
    resource_type = SelectField('Resource Type', choices=[('human', 'Human'), ('machine', 'Machine')],
                                validators=[Optional()])
    resource_count = IntegerField('Resource Count', validators=[Optional(), NumberRange(min=0)])
    generation_level = SelectField('Generation Level',
                                   choices=[('process', 'Process'), ('case', 'Case'), ('event', 'Event')],
                                   validators=[Optional()])
    adjustment_type = SelectField('Adjustment Type',
                                  choices=[('no_change', 'No Change'), ('slight_change', 'Slight Change'),
                                           ('full_change', 'Full Change')], validators=[Optional()])


class TransactionTypeForm(FlaskForm):
    name = SelectField('Transaction Types',
                       choices=[('schedule', 'Schedule'), ('start', 'Start'), ('assign', 'Assign'),
                                ('reassign', 'Reassign'), ('suspend', 'Suspend'),
                                ('resume', 'Resume'), ('complete', 'Complete'), ('custom', 'Custom')],
                       validators=[Optional()])
    custom_type = StringField('Custom Type Name', validators=[Optional()])
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)])

    transaction_duration_range_min = IntegerField('Transaction Duration Range Min',
                                                  validators=[Optional(), NumberRange(min=0)])
    transaction_duration_range_max = IntegerField('Transaction Duration Range Max',
                                                  validators=[Optional(), NumberRange(min=0)])
    transaction_duration_uom = SelectField('Transaction Duration Unit of Measure',
                                           choices=[('seconds', 'Seconds'), ('minutes', 'Minutes'), ('hours', 'Hours'),
                                                    ('days', "Days")], validators=[DataRequired()])


class ActivityForm(FlaskForm):
    activity_id = IntegerField('Activity ID', validators=[Optional(), NumberRange(min=1)])
    name = StringField('Name', validators=[DataRequired()])
    trace = StringField('Trace', validators=[Optional()])
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)])
    min_weight = DecimalField('Min Weight', validators=[Optional(), NumberRange(min=1)])
    max_weight = DecimalField('Max Weight', validators=[Optional(), NumberRange(min=1)])
    distribution = SelectField('Distribution',
                               choices=[('normal', 'Normal'), ('uniform', 'Uniform'), ('exponential', 'Exponential'),
                                        ('pareto', 'Pareto')], validators=[Optional()])
    duration_range_min = IntegerField('Duration Range Min', validators=[Optional(), NumberRange(min=0)])
    duration_range_max = IntegerField('Duration Range Max', validators=[Optional(), NumberRange(min=0)])
    duration_uom = SelectField('Distribution',
                               choices=[('seconds', 'Seconds'), ('minutes', 'Minutes'), ('hours', 'Hours'),
                                        ('days', 'Days')], validators=[Optional()])
    working_hours_min = IntegerField('Working Hours Range Min', validators=[Optional(), NumberRange(min=1, max=24)])
    working_hours_max = IntegerField('Working Hours Range Max', validators=[Optional(), NumberRange(min=1, max=24)])
    working_days = SelectMultipleField('Working Days',
                                       choices=[('weekdays', 'Weekdays'), ('weekend', 'Weekend'), (0, 'Monday'),
                                                (1, 'Tuesday'), (2, 'Wednesday'),
                                                (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')],
                                       validators=[Optional()])
    transaction_types = FieldList(FormField(TransactionTypeForm))
    activity_attributes = FieldList(FormField(AttributesForm))


class ProcessForm(FlaskForm):
    process_name = StringField('Process Name', validators=[DataRequired()])
    process_description = TextAreaField('Process Description', validators=[Optional()])
    process_id = IntegerField('Process ID', validators=[Optional(), NumberRange(min=1)])
    case_id = IntegerField('Case ID', validators=[Optional(), NumberRange(min=1)])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    num_cases = IntegerField('Number of Cases', validators=[Optional(), NumberRange(min=1)])
    traces = FieldList(StringField('Traces', validators=[Optional()]))
    case_attributes = FieldList(FormField(AttributesForm))
    activities = FieldList(FormField(ActivityForm))
    event_attributes = FieldList(FormField(AttributesForm))
    object_types = FieldList(StringField('Object Type', validators=[Optional()]))


class ObjectQualifiers(FlaskForm):
    name = StringField('Name', validators=[Optional()])
    to_object = StringField('To Object', validators=[Optional()])


class ActivityQualifiers(FlaskForm):
    name = StringField('Name', validators=[Optional()])
    to_activity = StringField('To Activity', validators=[Optional()])


class ObjectTypes(FlaskForm):
    object_id = IntegerField('Object ID', validators=[Optional(), NumberRange(min=1)])
    range_min = IntegerField('Range Min', validators=[Optional(), NumberRange(min=1)])
    range_max = IntegerField('Range Max', validators=[Optional(), NumberRange(min=1)])
    object_attributes = FieldList(FormField(ObjectQualifiers))
    activity_qualifiers = FieldList(FormField(ActivityQualifiers))
    object_qualifiers = FieldList(FormField(AttributesForm))


class ConfigSettingsForm(FlaskForm):
    get_from_defaults = BooleanField('Get from Defaults')
    default_options = SelectField('Default Options', choices=[list_defaults()])
    processes = FieldList(FormField(ProcessForm))


class ConfigDefaultForm(FlaskForm):
    process_id_start = IntegerField('Process ID Start', validators=[DataRequired(), NumberRange(min=1)])
    case_id_start = IntegerField('Case ID Start', validators=[DataRequired(), NumberRange(min=1)])
    attribute_definition_id_start = IntegerField('Attribute Definition ID Start',
                                                 validators=[DataRequired(), NumberRange(min=1)])
    case_attribute_id_start = IntegerField('Case Attribute ID Start', validators=[DataRequired(), NumberRange(min=1)])
    activity_id_start = IntegerField('Activity ID Start', validators=[DataRequired(), NumberRange(min=1)])
    activity_instance_id_start = IntegerField('Activity Instance ID Start',
                                              validators=[DataRequired(), NumberRange(min=1)])
    event_id_start = IntegerField('Event ID Start', validators=[DataRequired(), NumberRange(min=1)])
    event_attribute_id_start = IntegerField('Event Attribute ID Start', validators=[DataRequired(), NumberRange(min=1)])
    object_id = IntegerField('Object ID', validators=[DataRequired(), NumberRange(min=1)])
    object_type_id = IntegerField('Object Type ID', validators=[DataRequired(), NumberRange(min=1)])

    additional_trace_patterns_range_min = IntegerField('Additional Trace Patterns Range Min',
                                                       validators=[DataRequired(), NumberRange(min=1)])
    additional_trace_patterns_range_max = IntegerField('Additional Trace Patterns Range Max',
                                                       validators=[DataRequired(), NumberRange(min=1)])
    replays_range_min = IntegerField('Replays Range Min', validators=[DataRequired(), NumberRange(min=1)])
    replays_range_max = IntegerField('Replays Range Max', validators=[DataRequired(), NumberRange(min=1)])
    traces_in_pattern_range_min = IntegerField('Traces in Pattern Range Min',
                                               validators=[DataRequired(), NumberRange(min=1)])
    traces_in_pattern_range_max = IntegerField('Traces in Pattern Range Max',
                                               validators=[DataRequired(), NumberRange(min=1)])

    num_cases = IntegerField('Number of Cases', validators=[DataRequired(), NumberRange(min=1)])
    min_weight = DecimalField('Min Weight', validators=[DataRequired(), NumberRange(min=1.0)])
    max_weight = DecimalField('Max Weight', validators=[DataRequired(), NumberRange(min=1.0)])
    duration_range_min = IntegerField('Duration Range Min', validators=[DataRequired(), NumberRange(min=0)])
    duration_range_max = IntegerField('Duration Range Max', validators=[DataRequired(), NumberRange(min=0)])
    duration_uom = SelectField('Duration Unit of Measure',
                               choices=[('seconds', 'Seconds'), ('minutes', 'Minutes'), ('hours', 'Hours'),
                                        ('days', "Days")], validators=[DataRequired()])
    transaction_types = SelectMultipleField('Transaction Types',
                                            choices=[('schedule', 'Schedule'), ('start', 'Start'), ('assign', 'Assign'),
                                                     ('reassign', 'Reassign'), ('suspend', 'Suspend'),
                                                     ('resume', 'Resume'), ('complete', 'Complete')])
    transaction_duration_range_min = IntegerField('Transaction Duration Range Min',
                                                  validators=[DataRequired(), NumberRange(min=0)])
    transaction_duration_range_max = IntegerField('Transaction Duration Range Max',
                                                  validators=[DataRequired(), NumberRange(min=0)])
    transaction_duration_uom = SelectField('Transaction Duration Unit of Measure',
                                           choices=[('seconds', 'Seconds'), ('minutes', 'Minutes'), ('hours', 'Hours'),
                                                    ('days', "Days")], validators=[DataRequired()])
    attribute_range_min = IntegerField('Attribute Range Min', validators=[DataRequired(), NumberRange(min=0)])
    attribute_range_max = IntegerField('Attribute Range Max', validators=[DataRequired(), NumberRange(min=1)])
    distribution = SelectField('Distribution',
                               choices=[('normal', 'Normal'), ('uniform', 'Uniform'), ('exponential', 'Exponential'),
                                        ('pareto', 'Pareto')],
                               validators=[DataRequired()])
    adjustment_type = SelectField('Adjustment Type',
                                  choices=[('no change', 'No Change'), ('slight change', 'Slight Change'),
                                           ('moderate change', 'Moderate Change'),
                                           ('significant change', 'Significant Change')], validators=[DataRequired()])
    generation_level = SelectField('Generation Level',
                                   choices=[('event', 'Event'), ('case', 'Case'), ('process', 'Process')],
                                   validators=[DataRequired()])
    resource_type = SelectField('Generation Level', choices=[('human', 'Human'), ('machine', 'Machine')],
                                validators=[DataRequired()])
    resource_count = IntegerField('Resource Count', validators=[DataRequired(), NumberRange(min=1)])

    object_range_min = IntegerField('Object Range Min', validators=[DataRequired(), NumberRange(min=1)])
    object_range_max = IntegerField('Object Range Max', validators=[DataRequired(), NumberRange(min=1)])


class DeleteFileForm(FlaskForm):
    file = StringField('File name')
