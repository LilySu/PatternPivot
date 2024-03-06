class SearchOptionsCycler:
    def __init__(self, file_path: str):
        """
        Initializes the SearchOptionsCycler with search queries from a file and predefined order and video duration lists.
        Also initializes the index tracking for each attribute and sets the default cycling attribute.
        """
        self.search_queries = self.import_search_queries(file_path)
        self.orders = ['date', 'rating', 'relevance', 'title', 'videoCount', 'viewCount']
        self.video_durations = ['any', 'long', 'medium', 'short']
        # Cycling through attributes: SEARCH_QUERY, ORDER, VIDEO_DURATION
        self.attributes_cycle = ['search_queries', 'orders', 'video_durations']
        self.current_attribute_index = 0  # Index to track which attribute is currently being cycled through
        # Tracking the current index for each attribute list
        self.indexes = {attr: 0 for attr in self.attributes_cycle}

    def import_search_queries(self, file_path: str) -> list:
        """
        Imports search queries from a text file into a list.
        """
        try:
            with open(file_path, 'r') as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
            return []

    def set_cycling_attribute(self, attribute: str) -> None:
        """
        Sets the attribute that will be cycled through when getting the next set of options.
        """
        # Map user-friendly attribute names to internal list names
        attr_map = {'SEARCH_QUERY': 'search_queries', 'ORDER': 'orders', 'VIDEO_DURATION': 'video_durations'}
        if attribute in attr_map:
            self.current_attribute_index = self.attributes_cycle.index(attr_map[attribute])
        else:
            print("Invalid attribute. Valid options are: SEARCH_QUERY, ORDER, VIDEO_DURATION.")

    def rotate_to_next_attribute(self) -> None:
        """
        Moves to the next attribute in the cycle, resetting the index for the new attribute.
        """
        self.current_attribute_index = (self.current_attribute_index + 1) % len(self.attributes_cycle)
        current_attr_key = self.attributes_cycle[self.current_attribute_index]
        self.indexes[current_attr_key] = 0  # Reset index for the new attribute

    def get_next_options(self):
        # Get the current attribute list based on the current_attribute_index
        current_attr_list_name = self.attributes_cycle[self.current_attribute_index]
        current_attr_list = getattr(self, current_attr_list_name)

        # Increment the index for the current attribute list and wrap it if needed
        self.indexes[current_attr_list_name] = (self.indexes[current_attr_list_name] + 1) % len(current_attr_list)

        # After incrementing, if the index wraps back to 0, it means we've cycled through all elements
        # Move to the next attribute in the cycle
        if self.indexes[current_attr_list_name] == 0:
            self.current_attribute_index = (self.current_attribute_index + 1) % len(self.attributes_cycle)
            # Optionally, reset the index for the next attribute to start from the beginning
            next_attr_list_name = self.attributes_cycle[self.current_attribute_index]
            self.indexes[next_attr_list_name] = 0

        # Build and return the options dictionary with the current values
        options = {
            'SEARCH_QUERY': self.search_queries[self.indexes['search_queries']],
            'ORDER': self.orders[self.indexes['orders']],
            'VIDEO_DURATION': self.video_durations[self.indexes['video_durations']],
        }
        return options


def merge_dicts_based_on_larger(dict1, dict2):
    # Determine which dictionary is larger
    larger_dict = dict1 if len(dict1) > len(dict2) else dict2
    smaller_dict = dict2 if larger_dict is dict1 else dict1

    # Update the values of the larger dictionary with values from the smaller dictionary
    # Gets any unique keys from the smaller dictionary.
    for key in smaller_dict.keys():
        if key in larger_dict:
            # Update the larger dictionary with values from the smaller one
            larger_dict[key] = smaller_dict[key]

    # Output the larger dictionary with updated values
    return larger_dict