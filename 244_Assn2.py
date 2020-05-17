import csv
import random


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
    staff_list = {}  # List of staff

    for i in range(1, 48):
        newstaff = Staff()
        new_sid = "S" + "{:0>3d}".format(i)
        newstaff.staff_id = new_sid
        staff_list[new_sid] = newstaff

    with open('HC04.csv') as staff_unavailable_file:
        su_reader = csv.reader(staff_unavailable_file, delimiter=",")
        line_count = 0
        for row in su_reader:
            sid = row[0]
            for data in range(len(row)):
                if data > 0:
                    staff_list[sid].unavailable_slot.append(int(row[data]))
            line_count += 1

    with open('SC01.csv') as consecutive_presentation_file:
        cp_reader = csv.reader(consecutive_presentation_file, delimiter=",")
        line_count = 0
        for row in cp_reader:
            staff_list[row[0]].consecutive_presentation_pref = row[1]
            line_count += 1

    with open('SC02.csv') as num_day_file:
        nd_reader = csv.reader(num_day_file, delimiter=",")
        line_count = 0
        for row in nd_reader:
            staff_list[row[0]].attend_day = row[1]
            line_count += 1

    with open('SC03.csv') as same_venue_file:
        sv_reader = csv.reader(same_venue_file, delimiter=",")
        line_count = 0
        for row in sv_reader:
            staff_list[row[0]].same_venue_pref = row[1]
            line_count += 1

    return staff_list


def venue_record_handler():  # Read all records related to venue
    venue_list = []  # List of venue
    w = 0

    for i in range(1, 301):
        new_venue = Venue()
        new_venue.venue_id = i

        if i - w * 60 <= 1 and i - w * 60 <= 15:
            new_venue.venue_type = "VR"
        elif i - w * 60 <= 16 and i - w * 60 <= 30:
            new_venue.venue_type = "MR"
        elif i - w * 60 <= 31 and i - w * 60 <= 45:
            new_venue.venue_type = "IR"
        else:
            new_venue.venue_type = "BJIM"
            if i - w * 60 == 60:
                w += 1
        venue_list.append(new_venue)

    with open("HC03.csv") as venue_unavailable_file:
        vu_reader = csv.reader(venue_unavailable_file, delimiter=",")

        for row in vu_reader:
            for data in range(1, len(row)):
                venue_list[int(row[data]) - 1].availability = False

    return venue_list


class Presentation:
    def __init__(self):
        self.staff_list = []
        self.presentation_id = None
        self.assigned_venue = Venue()


class Candidate:
    def __init__(self):
        self.presentation_list = []
        self.staff_list = staff_record_handler()
        with open("SupExaAssign.csv") as SupExaAssign:
            sea_reader = csv.reader(SupExaAssign, delimiter=",")
            line_count = 0

            for row in sea_reader:
                if line_count > 0:
                    new_presentation = Presentation()
                    new_presentation.presentation_id = row[0]
                    for data in range(1, 3):
                        new_presentation.staff_list.append(self.staff_list[row[data]])
                    self.presentation_list.append(new_presentation)
                line_count += 1

    def randomize_venue(self, venue_list):
        random_venue_list = []
        for presentation in self.presentation_list:
            r = random.randint(1, 300)
            if presentation.assigned_venue.venue_id != r and r not in random_venue_list:
                random_venue_list.append(r)
                presentation.assigned_venue = venue_list[r-1]

    def fitness(self):
        print("TBD")

    def print(self):
        print("TBD")


class GeneticAlgorithm:
    def __init__(self):
        self.population = []  # List of candidates
        self.pop_size = 400
        self.venue_list = venue_record_handler()
        new_candidate = Candidate()
        for i in range(self.pop_size):
            new_candidate.randomize_venue(self.venue_list)
            self.population.append(new_candidate)
        self.population = sorted(self.population, key=lambda candidate: candidate.fitness())  # Sort the population


    def generate_new_gen(self):
        print("TBD")

    def uniform_crossover(self):
        print("TBD")

    def mutate(self, obj):
        print("TBD")

    def run(self):
        print("TBD")


result = GeneticAlgorithm()
