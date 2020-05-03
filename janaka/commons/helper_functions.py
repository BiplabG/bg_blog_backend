def is_valid_data_keys(data, required_keys):
    """
    This function validates the incoming data by checking if the json data has all the necessary keys that the requested
    task needs.
    Arguments:: data_keys: Dictionary: Incoming json data.
                required_keys: Array: Keys required for the requested task.
                returns True if all keys are there and raises AssertionError if not. 
    """
    for key in required_keys:
        assert key in data.keys(), f"Cannot find the key {key} is missing in the sent data."
        assert data[key].strip()!="" if type(data[key]) == str else data[key]!="", f"Empty string provided for the required key {key}."
    return True

def failure_message(operation, msg):
    """This function returns a formatted dictionary for the failure cases, or exceptions."""
    return {
        "operation":operation,
        "success":False,
        "message":f"Exception encountered buddy. Here is the exception message that can be helpful: {msg}",
    }
    