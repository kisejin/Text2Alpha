def extract_error_message(error):
    print(f"Error: \n{str(error)}\n")
    error_lines = str(error).split('\n')
    for line in error_lines:
        if 'Error' in line or 'Exception' in line:
            return line.strip()
    return error_lines[-1].strip()

