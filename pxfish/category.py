
def select_category(aq, category_path):
    """
    Finds all Libraries and Operation Types in a specific category

    Arguments:
        aq (Session Object): Aquarium session object
        category_path (String): the directory path for the category
    """
    category_entries = os.listdir(category_path)
    for directory_entry in category_entries:
        files = os.listdir(os.path.join(category_path, directory_entry))
        if directory_entry == 'libraries':
            for name in files:
                select_library(aq, category_path, name)
        elif directory_entry == 'operation_types':
            for name in files:
                select_operation_type(aq, category_path, name)
        else:
            logging.warning("Unexpected directory entry {} in {}".format(
                directory_entry,
                category_path
            ))

