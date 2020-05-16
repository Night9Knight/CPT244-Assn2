import csv


class Staff:
    def __init__(self):
        self.staff_id = None
        self.unavailable_slot = []
        self.consecutive_presentation_pref = None
        self.attend_day = None
        self.same_venue_pref = None


class Venue:
    def __init__(self):
        self.venue_id = None
        self.venue_type = None
        self.availability = True


def staff_record_handler():  # Read all records related to staff
    staff_list = []  # List of staff
    for i in range(1, 48):
        newstaff = Staff()
        newstaff.staff_id = "S" + "{:0>3d}".format(i)
        staff_list.append(newstaff)

    with open('HC04.csv') as staff_unavailable_file:
        su_reader = csv.reader(staff_unavailable_file, delimiter=",")
        line_count = 0
        for row in su_reader:
            for data in range(len(row)):
                if data > 0:
                    staff_list[line_count].unavailable_slot.append(row[data])
            line_count += 1

    with open('SC01.csv') as consecutive_presentation_file:
        cp_reader = csv.reader(consecutive_presentation_file, delimiter=",")
        line_count = 0
        for row in cp_reader:
            staff_list[line_count].consecutive_presentation_pref = row[1]
            line_count += 1

    with open('SC02.csv') as num_day_file:
        nd_reader = csv.reader(num_day_file, delimiter=",")
        line_count = 0
        for row in nd_reader:
            staff_list[line_count].attend_day = row[1]
            line_count += 1

    with open('SC03.csv') as same_venue_file:
        sv_reader = csv.reader(same_venue_file, delimiter=",")
        line_count = 0
        for row in sv_reader:
            staff_list[line_count].same_venue_pref = row[1]
            line_count += 1

    return staff_list


def venue_record_handler():  # Read all records related to venue
    print("TBD")



class Presentation:
    staff_list = []
    presentation_id = None
    assigned_venue = None

    def __init__(self):
        print("TBD")


class Candidate:
    presentation_list = []

    def __init__(self):
        print("TBD")

    def randomize_venue(self):
        print("TBD")

    def fitness(self):
        print("TBD")

    def print(self):
        print("TBD")


class GeneticAlgorithm:
    def __init__(self):
        print("TBD")

    def generate_new_gen(self):
        print("TBD")

    def uniform_crossover(self):
        print("TBD")

    def run(self):
        print("TBD")


result = GeneticAlgorithm()
