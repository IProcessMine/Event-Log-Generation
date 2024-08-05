-- Process table
drop table if exists Process CASCADE ;
CREATE TABLE Process (
    process_id INT PRIMARY KEY,
    process_name VARCHAR(255) NOT NULL,
    description VARCHAR(1000) NOT NULL
);

-- Case table
drop table if exists Cases CASCADE;
CREATE TABLE Cases (
    case_id INT PRIMARY KEY,
    process_id INT NOT NULL,
    start_time timestamp,
    end_time timestamp,
    FOREIGN KEY (process_id) REFERENCES Process(process_id) ON DELETE CASCADE
);

-- Activity table
drop table if exists Activity CASCADE ;
CREATE TABLE Activity (
    activity_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    process_id INT NOT NULL,
    FOREIGN KEY (process_id) REFERENCES Process(process_id) ON DELETE CASCADE
);

-- Activity Instance table
drop table if exists ActivityInstance CASCADE ;
CREATE TABLE ActivityInstance (
    activity_instance_id INT PRIMARY KEY,
    activity_id INT NOT NULL,
    case_id INT NOT NULL,
    FOREIGN KEY (activity_id) REFERENCES Activity(activity_id) ON DELETE CASCADE,
    FOREIGN KEY (case_id) REFERENCES Cases(case_id) ON DELETE CASCADE
);

-- Event table
drop table if exists Event CASCADE ;
CREATE TABLE Event (
    event_id INT PRIMARY KEY,
    case_id INT NOT NULL,
    activity_instance_id INT NOT NULL,
    start_time timestamp NOT NULL,
    end_time timestamp NOT NULL,
    position_in_trace INT,
    transaction_type VARCHAR(255),
    resource VARCHAR(255),
    FOREIGN KEY (case_id) REFERENCES Cases(case_id) ON DELETE CASCADE,
    FOREIGN KEY (activity_instance_id) REFERENCES ActivityInstance(activity_instance_id) ON DELETE CASCADE
);

drop table if exists AttributeDefinition CASCADE;
CREATE TABLE AttributeDefinition (
    attribute_id INT PRIMARY KEY,
    attribute_name VARCHAR(255) NOT NULL,
    attribute_type VARCHAR(255) NOT NULL,
    attribute_value_type VARCHAR(255) NOT NULL
);

drop table if exists CaseAttribute CASCADE;
CREATE TABLE CaseAttribute (
    case_attribute_id INT PRIMARY KEY,
    case_id INT NOT NULL,
    attribute_id INT NOT NULL,
    attribute_value VARCHAR(255),
    FOREIGN KEY (case_id) REFERENCES Cases(case_id) ON DELETE CASCADE,
    FOREIGN KEY (attribute_id) REFERENCES AttributeDefinition(attribute_id)
);
-- Event Attribute table
drop table if exists EventAttribute CASCADE;
CREATE TABLE EventAttribute (
    event_attribute_id INT PRIMARY KEY,
    event_id INT NOT NULL,
    attribute_id INT NOT NULL,
    attribute_value VARCHAR(255),
    FOREIGN KEY (event_id) REFERENCES Event(event_id) ON DELETE CASCADE,
    FOREIGN KEY (attribute_id) REFERENCES AttributeDefinition(attribute_id)
);