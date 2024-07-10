import re


def clean_string(string):
    """
    Removes tabs and leading/trailing whitespace from a string.
    """
    return string.strip().replace("\t", "")


def process_string(string):
    """
    Processes the input string by removing lines that contain specific patterns.
    """
    lines = string.split("\n")
    # Filter out lines containing '-----' or 'Filename'
    filtered_lines = [
        line for line in lines if "-----" not in line and "Filename" not in line
    ]
    return "\n".join(filtered_lines)


def get_root_error(messages):
    """
    Extracts and formats the root cause error from a list of messages.
    """
    pattern = "ROOT CAUSE"
    flag = True
    # Find the first message containing 'ROOT CAUSE'
    root_error = [m for m in messages if pattern in m][0]
    if root_error:
        if "This error is from your code" in root_error:
            flag = False
        root_error = re.sub(r"\nNote: .*", "", root_error)
        root_error = root_error.split("\n")
        # Reformat the root cause error message
        root_error = [
            root_error[-1].replace(f" -->{pattern}:", "").strip()
        ] + root_error[:-1]
    return root_error, flag


def get_my_code_error(messages):
    """
    Extracts and formats errors that are identified as coming from the user's code.
    """
    pattern = "This error is from your code"
    # Filter and format messages indicating user's code errors
    my_code_error = [
        m.replace("Note: " + pattern, "").strip()
        for m in messages
        if pattern in m and "ROOT CAUSE" not in m
    ]

    return my_code_error


def get_error(string):
    """
    Splits the input string into segments, processes each segment to extract
    the root cause error and any errors from the user's code, and returns them.
    """
    # Split the input string into segments based on a delimiter
    messages = [
        process_string(clean_string(segment))
        for segment in string.split(
            "==================================================="
        )
    ]
    root_error, continue_get_messages = get_root_error(messages)

    mess = messages if continue_get_messages else ""

    my_code_error = get_my_code_error(mess)

    # Format the return value based on whether there are errors from the user's code
    if my_code_error:
        my_code_error = (
            my_code_error[-1].split("\n")
            if "self.cerebro.run()" not in my_code_error
            else ""
        )
        return [root_error, my_code_error]

    return [root_error, ""]
