def find_highest_similarity(tuples_list):
    highest_value = None
    for tuple_item in tuples_list:
        last_element = tuple_item[-1]
        if highest_value is None or last_element > highest_value:
            highest_value = last_element
    return highest_value
