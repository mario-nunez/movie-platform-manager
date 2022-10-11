import json
import re


class SeriesManagementPlatform:

    def __init__(self):
        self.series = []
        self.menu_end = False
        self.search_end = False
        self.MENU_OPTIONS = {
            "1": self.add_series,
            "2": self.edit_series,
            "3": self.delete_series,
            "4": self.search_info,
            "5": self.show_all_series,
            "6": self.delete_all_series,
            "7": self.exit_program
        }
        self.SEARCH_OPTIONS = {
            "1": self.search_above_rating,
            "2": self.search_below_rating,
            "3": self.search_seen,
            "4": self.search_not_seen,
            "5": self.back_to_menu
        }

    # ---------- Request user general info ---------

    def read_menu_option(self):
        print("""\n--------------- HOME MENU ---------------\n"""
            f"""What do you want to do? (1-{len(self.MENU_OPTIONS)}):\n""")
        self.print_functions_dict(self.MENU_OPTIONS)
        return input("Select option: ")

    def read_search_option(self):
        print("""\n--------------- SEARCH MENU ---------------\n"""
            f"""What do you want to do? (1-{len(self.SEARCH_OPTIONS)}):\n""")
        self.print_functions_dict(self.SEARCH_OPTIONS)
        return input("Select option: ")

    def read_series_info(self):
        correct = False
        while correct is False:
            title = input("Insert series title: ")
            episodes = input("Insert the number of episodes: ")
            seen = input("Have you seen it? (yes/no): ")
            rating = input("Insert your rating (0-10): ")
            print("\n")

            validation_results = [
               self.validate_existing_title(title),
               self.validate_episodes(episodes),
               self.validate_rating(rating),
               self.validate_seen(seen)
            ]
            if all(validation_results):
                correct = True
            else:
                print("\nPlease enter valid values.\n")

        return title, int(episodes), seen, float(rating)

    # ---------- Validation methods (True -> OK ; False -> Failed) ---------

    def validate_menu_option_selected(self, option):
        if option.isdigit() and (1 <= int(option) < len(self.MENU_OPTIONS)):
            return True
        return False

    def validate_search_option_selected(self, option):
        if option.isdigit() and (1 <= int(option) < len(self.SEARCH_OPTIONS)):
            return True
        return False

    def validate_seen(self, seen):
        seen_values = ["yes", "no"]
        if seen.lower() not in seen_values:
            print(f"Incorrect value \"{seen}\" in \"Have you seen it?\" field.")
            return False
        return True

    def validate_episodes(self, num):
        if re.match(r'^\d*$', num) is None:
            print(f"Nº of episodes \"{num}\" has incorrect format.")
            return False
        return True

    def validate_rating(self, num):
        if re.match(r'^10|[0-9](\.[0-9]+)?$', num) is None:
            print(f"Rating \"{num}\" has incorrect format.")
            return False
        return True if float(num) <= 10 else False

    def validate_existing_id(self, id_):
        if not any(item["id"] == id_ for item in self.series):
            print(f"Id \"{id_}\" was not found.")
            return False
        return True

    def validate_existing_title(self, title):
        if any(item["title"] == title for item in self.series):
            print(f"Title \"{title}\" already exists.")
            return False
        return True

    # ---------- Creation methods ---------

    def create_dict(self, id_, title, episodes, seen, rating):
        series_dict = {
            "id": id_,
            "title": title,
            "episodes": int(episodes),
            "seen": seen,
            "rating": round(float(rating), 2)
        }

        return series_dict

    def create_id(self):
        return 0 if not self.series else self.series[-1]["id"] + 1

    # ---------- General menu methods ---------

    def add_series(self):
        print("Adding a new series...")
        id_ = self.create_id()
        title, episodes, seen, rating = self.read_series_info()
        series_dict = self.create_dict(id_, title, episodes, seen, rating)
        self.series.append(series_dict)
        print(f'Series information stored: {self.series[-1]}')

    def edit_series(self):
        if self.check_if_series() is False:
            return None
        print("Editing series...")
        self.show_all_series()
        correct = False
        while correct is False:
            try:
                id_edit = int(input("Select the id series to edit: "))
            except ValueError:
                print("Id must be an integer number.")
            if self.validate_existing_id(id_edit):
                correct = True
        series_index = self.locate_series(id_edit)
        print("Please introduce the new series information:")
        title, episodes, seen, rating = self.read_series_info()
        self.series[series_index] = self.create_dict(id_edit, title, episodes, seen, rating)
        print(f"Series updated with the following data: {self.series[series_index]}")

    def delete_series(self):
        if self.check_if_series() is False:
            return None
        print("Deleting series...")
        self.show_all_series()
        correct = False
        while correct is False:
            try:
                id_delete = int(input("Select the id series to delete: "))
            except ValueError:
                print("Id must be an integer number.")
            if self.validate_existing_id(id_delete):
                correct = True
        series_index = self.locate_series(id_delete)
        del self.series[series_index]
        print(f"Series with id \"{id_delete}\" has been deleted.")

    def search_info(self):
        if self.check_if_series() is False:
            return None
        print("Searching series...")
        while self.search_end is False:
            option_selected = self.read_search_option()
            # Redirect to the correspondent function
            self.SEARCH_OPTIONS.get(option_selected, self.option_not_found)()
        print("Exiting search menu...")
        self.search_end = False

    def show_all_series(self):
        if self.check_if_series() is False:
            return None
        print("Showing all series...")
        self.pretty_print_json(self.series)

    def delete_all_series(self):
        if self.check_if_series() is False:
            return None
        print("Deleting all series records...")
        self.series.clear()
        print("All series have been deleted.")

    def exit_program(self):
        self.menu_end = True
        print("Exiting program...")

    # ---------- Search menu methods ---------

    def search_above_rating(self):
        print("Searching above rating...")
        correct = False
        while correct is False:
            rating = input("Insert rating lower limit: ")
            if self.validate_rating(rating):
                correct = True
        series_above_rating = list(filter(lambda x:
            x.get("rating") >= float(rating), self.series))
        if series_above_rating:
            self.pretty_print_json(series_above_rating)
        else:
            self.no_series_match()

    def search_below_rating(self):
        print("Searching below rating...")
        correct = False
        while correct is False:
            rating = input("Insert rating upper limit: ")
            if self.validate_rating(rating):
                correct = True
        series_below_rating = list(filter(lambda x:
            x.get("rating") <= float(rating), self.series))
        if series_below_rating:
            self.pretty_print_json(series_below_rating)
        else:
            self.no_series_match()

    def search_seen(self):
        print("Searching series seen...")
        series_seen =  list(filter(lambda x:
            x.get("seen") == "yes", self.series))
        if series_seen:
            self.pretty_print_json(series_seen)
        else:
            self.no_series_match()

    def search_not_seen(self):
        print("Searching series not seen...")
        series_not_seen =  list(filter(lambda x:
            x.get("seen") == "no", self.series))
        if series_not_seen:
            self.pretty_print_json(series_not_seen)
        else:
            self.no_series_match()

    def back_to_menu(self):
        print("Back to home menu...")
        self.search_end = True

    # ---------- Auxiliar methods ---------

    def locate_series(self, id_):
        """
        Returns the index of the list of series in which a certain series is 
        located.
        """
        # Use next instead of list to obtain the index value in a variable
        element_found = next(filter(lambda x: x.get("id") == id_, self.series))
        series_index = self.series.index(element_found)
        return series_index

    def print_functions_dict(self, func_dict):
        for item in func_dict.items():
            name_show = item[1].__name__
            print(f'\t{item[0]}. {name_show.replace("_", " ").capitalize()}')

    def pretty_print_json(self, element):
        print(json.dumps(element, sort_keys=False, indent=4))

    def check_if_series(self):
        if not self.series:
            print("There are no series stored yet.")
            return False
        return True

    def no_series_match(self):
        print("No results found.")

    def option_not_found(self):
        print("Please enter a valid option.")

    # ---------- Main method ---------

    def main(self):
        while self.menu_end is False:
            # Show options to the user
            option_selected = self.read_menu_option()
            # Redirect to the correspondent function
            self.MENU_OPTIONS.get(option_selected, self.option_not_found)()
        print("\nProgram finished.")


if __name__ == "__main__":
    program = SeriesManagementPlatform()
    program.main()
