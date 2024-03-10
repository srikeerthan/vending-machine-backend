from sqlalchemy.orm import class_mapper


def model_to_dict(obj):
    """
    Convert SQLAlchemy model object to dictionary
    """
    # Get the mapper for the SQLAlchemy model object
    mapper = class_mapper(obj.__class__)

    # Create an empty dictionary to store the attributes
    result = {}

    # Loop through each column in the mapper
    for column in mapper.columns:
        # Get the attribute value from the SQLAlchemy model object
        value = getattr(obj, column.key)

        # Add the attribute key-value pair to the result dictionary
        result[column.key] = value

    return result
