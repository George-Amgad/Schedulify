from copy import deepcopy
import itertools

WEEK_DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Sat']
WEEK_DAYS_FULL = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Saturday']

class ScheduleError(Exception):
    pass

class DuplicateSubjectError(ValueError):
    pass

class Event:
    def __init__(self, name: str, day: str, *periods: int):
        # handle name
        if type(name) != str:
            raise TypeError("Event name must be a string")
        self.name = str(name)

        # handle invalid day input
        if type(day) != str:
            raise TypeError("Day must be a string")
        if day not in WEEK_DAYS:
            raise ValueError("Invalid day for an Event")

        # handle schedule
        if len(periods) == 0:
            raise ScheduleError("Event must have at least one period")

        for period in periods:
            if type(period) != int:
                raise TypeError("All periods must be int") # handle invalid period input

        # create list: days with the same size of periods
        days = []
        for i in range(len(periods)):
            days.append(day)

        # zip days with periods in a list: schedule
        self.schedule = list(zip(days, periods))

    def __repr__(self):
        day = self.schedule[0][0]
        periods = [self.schedule[i][1] for i in range(len(self.schedule))]
        text = f"Event('{self.name}', '{self.schedule[0][0]}'"
        for period in periods:
            text += f", {period}"
        text += ")"
        return text

    def __str__(self):
        day = self.schedule[0][0]
        periods = [self.schedule[i][1] for i in range(len(self.schedule))]
        return f"{self.name} on {WEEK_DAYS_FULL[WEEK_DAYS.index(day)]}, periods: {periods}"

class Group:
    def __init__(self, name: str, *events: Event):
        # handle name
        if type(name) != str:
            raise TypeError("Group name must be a string")
        self.name = str(name)

        # handle events
        self.events = []
        for event in events:
            if type(event) != Event:
                raise TypeError("All events must be of type Event")
            self.events.append(event)

    def __repr__(self):
        text = f"Group('{self.name}'"
        for event in self.events:
            text += f", {event.__repr__()}"
        text += ")"
        return text

    def __str__(self):
        return '\n'.join([event.__str__() for event in self.events])

class Subject:
    def __init__(self, name: str, cred_hours: int, *groups: Group):
        # handle name
        if type(name) != str:
            raise TypeError("Subject name must be a string")
        self.name = name

        # handle cred_hours
        if type(cred_hours) == int:
            self.cred_hours = cred_hours
        elif type(cred_hours) == float:
            self.cred_hours = int(cred_hours)
            print("Warning: cred_hours was converted from float to int")
        else:
            raise TypeError("Credit Hours must be an integer")

        # handle groups
        self.groups = []
        for group in groups:
            if type(group) != Group:
                raise TypeError("All groups must be of type Group")
            self.groups += [group]



    def __str__(self):
        text = f"""Subject:
\tName: {self.name}
\tCredit Hours: {self.cred_hours}\n"""

        for group in self.groups:
            text += f"\tSchedule ({group.name}):\n"
            group_lines = group.__str__().split('\n')
            for line in group_lines:
                if line:
                    text += f"\t\t{line}\n" # Adding 8 spaces for alignment
        return text

    def __repr__(self):
        text = f"Subject('{self.name}', {self.cred_hours}"
        for group in self.groups:
            text += f", {group.__repr__()}"
        text += ")"
        return text

class Table(dict):
    def __init__(self, size: int = 12):
        # initialize empty attributes
        self.subjects = []
        self.groups = []
        self.cred_hours = int() # total cerdit hours of all subjects in the table
        # handle dictionary properties
        day_schedules = [[None for i in range(size)] for i in range(len(WEEK_DAYS))] # a list of None values with a default size of 12
        super().__init__() # initialize dictionary behavior
        for i in range(len(WEEK_DAYS)):
            self[WEEK_DAYS[i]] = day_schedules[i]

    def get_cred_hours(self):
        self.cred_hours = 0
        for subject in self.subjects:
            self.cred_hours += subject.cred_hours
        return self.cred_hours

    # add the schedule of a group of a subject to the table, raise an error if an overlap exists
    def add_subject(self, subject: Subject, group_name: str):
        # handle invalid user input
        if type(subject) != Subject:
            raise TypeError("Subject must be of type Subject")
        if type(group_name) != str:
            raise TypeError("Group name must be a string")
        if group_name not in [group.name for group in subject.groups]:
            raise ValueError(f"No group named '{group_name}' was found")
        if subject in self.subjects:
            raise DuplicateSubjectError(f"Subject '{subject.name}' is already in the table")
        # accessing group schedule
        found_group = False
        for group in subject.groups:
            if group.name == group_name:
                found_group = True # Mark that the group was found
                for event in group.events:
                    for tup in event.schedule:
                        day = tup[0]
                        period = tup[1]
                        if self[day][period] != None:
                            raise ScheduleError("There is already a subject in this period")
                        # each cell in the table has a tuple containing the subject, the group name and the event name
                        self[day][period] = (subject, group.name, event.name)
        if not found_group:
            raise ValueError(f"There is no group with this name '{group_name}' for subject {subject.name}")
        # add the subject to self.subjects
        self.subjects.append(subject)
        self.cred_hours = self.get_cred_hours()

    def merge(self, other: 'Table'):
        if type(other) != Table:
            raise TypeError("You can only merge a Table to another Table")
        for key, value in other.items(): # where each key-value pair represents a day's schedule
            for item in value:
                if self[key][value.index(item)] != None:
                    raise ScheduleError("There is already a subject in this period")
                self[key][value.index(item)] = item

    def __iadd__(self, other: 'Table'):
        if type(other) == Subject:
            self.merge(other)
        return self

    def __repr__(self):
        return "Table()"

    def __str__(self):
        text = "Schedule Table:\n"
        for day_index, day in enumerate(WEEK_DAYS):
            day_full_name = WEEK_DAYS_FULL[day_index]
            text += f"  {day_full_name}:\n"
            day_has_events = False
            for period_index, item in enumerate(self[day]):
                if item:
                    subject_obj, group_name, event_name = item
                    text += f"    Period {period_index}: {subject_obj.name} ({group_name}) - {event_name}\n"
                    day_has_events = True
            if not day_has_events:
                text += "    No events scheduled\n"
        text += f"Total Credit Hours: {self.get_cred_hours()}\n"
        return text

def build_tables(
    all_available_subjects: list, # List of Subject objects
    min_subjects: int,
    max_subjects: int,
    min_cred_hours: int,
    max_cred_hours: int,
    priority_subjects: list = None, # List of Subject objects
    num_tables_to_generate: int = 1,
) -> list: # Returns a list of Table objects
    """
    Generates a list of valid Table objects based on specified criteria,
    using a combinational approach for selecting subjects.
    Instead of random shuffling, it systematically explores combinations of subjects.

    Args:
        all_available_subjects: A list of all Subject objects that can be included.
        min_subjects: Minimum number of subjects required in a generated table.
        max_subjects: Maximum number of subjects allowed in a generated table.
        min_cred_hours: Minimum total credit hours required for a generated table.
        max_cred_hours: Maximum total credit hours allowed for a generated table.
        priority_subjects: An optional list of Subject objects to prioritize.
                           These subjects will always be included in the candidate set if possible.
        num_tables_to_generate: The desired number of valid tables to generate.

    Returns:
        A list of Table objects that satisfy all the given criteria.
    """
    valid_tables = []

    # 1. Separate priority and non-priority subjects that are actually available
    actual_priority_subjects = [s for s in (priority_subjects or []) if s in all_available_subjects]
    non_priority_available_subjects = [s for s in all_available_subjects if s not in actual_priority_subjects]

    # 2. Determine the range of how many non-priority subjects to add
    num_priority_actual = len(actual_priority_subjects)
    min_non_priority_to_add = max(0, min_subjects - num_priority_actual)
    max_non_priority_to_add = max_subjects - num_priority_actual

    # 3. Generate all candidate subject sets using combinations
    all_candidate_subject_sets = []
    for k in range(min_non_priority_to_add, max_non_priority_to_add + 1):
        if k < 0: # Ensure k is non-negative
            continue
        for non_priority_combo in itertools.combinations(non_priority_available_subjects, k):
            candidate_set = list(actual_priority_subjects) + list(non_priority_combo)
            # Add only if the total number of subjects is within bounds
            if min_subjects <= len(candidate_set) <= max_subjects:
                all_candidate_subject_sets.append(candidate_set)

    # 4. Iterate through each candidate set of subjects to try and build a table
    # Sort candidate sets for deterministic testing order (optional, but good for debugging)
    all_candidate_subject_sets.sort(key=lambda s_list: tuple(sorted(sub.name for sub in s_list)))


    for candidate_subjects_set in all_candidate_subject_sets:
        if len(valid_tables) >= num_tables_to_generate:
            break # Stop if enough tables are generated

        current_table = Table()
        subjects_successfully_added = []
        conflict_found_for_set = False # Flag to track if this specific set of subjects can be scheduled

        # Sort subjects within the set for a deterministic order of scheduling attempt
        subjects_to_schedule = sorted(candidate_subjects_set, key=lambda s: s.name)

        for subject in subjects_to_schedule:
            added_this_subject = False
            # Iterate through groups in a deterministic order (e.g., sorted by name)
            # No random shuffle here
            deterministic_groups = sorted(subject.groups, key=lambda g: g.name)

            for group in deterministic_groups:
                try:
                    # The add_subject method checks for conflicts before modifying the table.
                    # If ScheduleError is raised, the table's state remains unchanged, allowing
                    # us to try another group or declare the set unschedulable.
                    current_table.add_subject(subject, group.name)
                    subjects_successfully_added.append(subject)
                    added_this_subject = True
                    break # Subject successfully added with this group
                except ScheduleError:
                    continue # This group conflicted, try another for the same subject
                except DuplicateSubjectError:
                    # This should theoretically not happen if `candidate_subjects_set`
                    # contains unique subjects, which `itertools.combinations` ensures.
                    added_this_subject = True # Consider it added if already there
                    break
                except Exception as e:
                    print(f"Unexpected error adding subject {subject.name} group {group.name}: {e}")
                    conflict_found_for_set = True
                    break # An unexpected error occurred, give up on this subject set

            if not added_this_subject:
                # If the current subject could not be added with any of its groups,
                # then this entire `candidate_subjects_set` cannot form a valid table.
                conflict_found_for_set = True
                break

        if not conflict_found_for_set:
            # If all subjects in the candidate_subjects_set were successfully added,
            # now check if the total credit hours meet the criteria.
            current_cred_hours = current_table.get_cred_hours()

            if (min_cred_hours <= current_cred_hours <= max_cred_hours):
                valid_tables.append(current_table)

    if len(valid_tables) < num_tables_to_generate:
        print(f"Warning: Could only generate {len(valid_tables)} out of {num_tables_to_generate} requested tables after checking all viable combinations.")

    return valid_tables
