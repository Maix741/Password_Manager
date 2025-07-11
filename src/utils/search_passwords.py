import os

from .get_website_for_password import get_website_for_password


def search_passwords(data_path: str, search_query: str) -> list[str]:
    if not search_query: return []
    passwords_path: str = os.path.join(data_path, "passwords")
    passwords: list[str] = [os.path.splitext(password)[0] for password in os.listdir(passwords_path)]
    websites: list[str] = [get_website_for_password(passwords_path, password) for password in passwords]

    websites = [website.split(".")[1] if "." in website else website for website in websites]

    full_result: tuple[list[bool]] = search_in_multiple_lists(passwords, websites, search_query=search_query)
    combined_result: list[bool] = combine_lists(*full_result)

    result: list[str] = []
    for i in range(len(combined_result)):
        if combined_result[i]:
            result.append(passwords[i])
    return result


def combine_lists(list1, list2):
    """
    Combines two boolean lists into one, where a True in either list results in True in the combined list.

    Args:
        list1: The first boolean list.
        list2: The second boolean list.

    Returns:
        A new list containing the combined boolean values.
    """

    combined_list: list[bool] = []
    for i in range(max(len(list1), len(list2))):  # Iterate through the longer list
        val1 = list1[i] if i < len(list1) else False  # Get value from list1, default to False if out of bounds
        val2 = list2[i] if i < len(list2) else False  # Get value from list2, default to False if out of bounds
        combined_list.append(val1 or val2)

    return combined_list


def search_in_multiple_lists(*lists_to_search, search_query: str) -> tuple[list[bool]]:
    result: list[list[bool]] = []
    for list_to_search in lists_to_search:
        result.append(search_in_list(list_to_search, search_query))

    return tuple(result)


def search_in_list(data: list[str], search_query: str) -> list[bool]:
    """Searches for a search_query in a list-like object.

    Args:
        data: The list-like object to search.
        search_query: The value to search for.

    Returns:
        True if the search_query is found in the list, False otherwise.
    """
    results_list: list[str] = []
    for item in data:
        if search_query.lower() in item.lower(): results_list.append(True)
        else: results_list.append(False)

    return results_list
