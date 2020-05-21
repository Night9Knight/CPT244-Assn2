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
        self.day = None
        self.time = None


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
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    time_of_day = ["0900-0930", "0930-1000", "1000-1030", "1030-1100", "1100-1130", "1130-1200", "1200-1230",
                   "1230-1300", "1400-1430", "1430-1500", "1500-1530", "1530-1600", "1600-1630", "1630-1700",
                   "1700-1730"]
    w = 0
    z = 0

    for i in range(1, 301):
        new_venue = Venue()
        new_venue.venue_id = i

        if 1 <= i - w * 60 <= 15:
            new_venue.venue_type = "VR"
            new_venue.day = days_of_week[w]
            new_venue.time = time_of_day[z]
            z += 1
        elif 16 <= i - w * 60 <= 30:
            new_venue.venue_type = "MR"
            new_venue.day = days_of_week[w]
            new_venue.time = time_of_day[z]
            z += 1
        elif 31 <= i - w * 60 <= 45:
            new_venue.venue_type = "IR"
            new_venue.day = days_of_week[w]
            new_venue.time = time_of_day[z]
            z += 1
        else:
            new_venue.venue_type = "BJIM"
            new_venue.day = days_of_week[w]
            new_venue.time = time_of_day[z]
            z += 1
            if i - w * 60 == 60:
                w += 1

        if z == 15:
            z = 0

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
        self.SIZE = 118
        self.random_venue_list = [None] * self.SIZE
        self.staff_list = staff_record_handler()
        self.venue_presentation = {}

        with open("SupExaAssign.csv") as SupExaAssign:
            sea_reader = csv.reader(SupExaAssign, delimiter=",")
            line_count = 0

            for row in sea_reader:
                if line_count > 0:
                    new_presentation = Presentation()
                    new_presentation.presentation_id = row[0]
                    for data in range(1, 4):
                        new_presentation.staff_list.append(self.staff_list[row[data]])
                    self.presentation_list.append(new_presentation)
                line_count += 1

    def randomize_venue(self, venue_list):
        self.random_venue_list = random.sample(range(300), 118)
        for i in range(self.SIZE):
            self.presentation_list[i].assigned_venue = venue_list[self.random_venue_list[i]]
            self.venue_presentation[self.random_venue_list[i]] = self.presentation_list[i]

        self.presentation_list.sort(key=lambda presentation: presentation.assigned_venue.venue_id)

    def fitness(self):
        total_fitness = 0
        for presentation in self.presentation_list:

            # one day has 60 presentations
            day_category = presentation.assigned_venue.venue_id / 60
            # each day, all venues have 15 presentation
            same_time_category = presentation.assigned_venue.venue_id % 15
            # HC02
            if presentation.assigned_venue.availability == False:
                total_fitness += 1000

            for staff in presentation.staff_list:
                # HC03
                if presentation.assigned_venue.venue_id in staff.unavailable_slot:
                    total_fitness += 1000

                # HC04 : checking whether the staff exists in other presentations' staff list
                # that has the same time and day
                # using the venue_presentation dictionary, we can identify the presentations having the same time and
                # day
                for i in range(4):
                    current_venue_id = day_category * 60 + i * 15 + same_time_category
                    other_presentation = self.venue_presentation.get(current_venue_id)
                    if other_presentation and other_presentation.presentation_id != presentation.presentation_id:
                        if staff in other_presentation.staff_list:
                            total_fitness += 1000

                # for other_presentation in self.presentation_list:
                #     if other_presentation.presentation_id != presentation.presentation_id:
                #         # checking if the same staff in this presentation exists in other presentations
                #         if staff in other_presentation.staff_list:
                #
                #             if other_presentation.assigned_venue.time == presentation.assigned_venue.time and other_presentation.assigned_venue.day == presentation.assigned_venue.day:
                #                 total_fitness += 1000

                # if before_presentation:
                #     if staff in before_presentation.staff_list:
                #         if before_presentation.assigned_venue.venue_id == presentation.assigned_venue.venue_id - 1:
                #             staff.consecutive_presentation_pref = int(staff.consecutive_presentation_pref) - 1
                #             if staff.consecutive_presentation_pref <= 0:
                #                 total_fitness += 10
                #
                #             if staff.same_venue_pref == "yes":
                #                 if before_presentation.assigned_venue.venue_type != presentation.assigned_venue.venue_type:
                #                     total_fitness += 10

        attended_days = []
        for key in self.staff_list:
            staff = self.staff_list.get(key)
            attended_days.clear()
            line_num = 0
            before_presentation = None
            consecutive_presentation = staff.consecutive_presentation_pref

            for presentation in self.presentation_list:
                if line_num:
                    before_presentation = self.presentation_list[line_num - 1]

                # SC01 and SC03
                # the following code runs when before_presentation points towards the presentation
                # occupying the time slot right before the current presentation
                if before_presentation:
                    if staff in before_presentation.staff_list and staff in presentation.staff_list:
                        consecutive_presentation = int(consecutive_presentation) - 1

                        if consecutive_presentation < 0:
                            total_fitness += 10

                        if staff.same_venue_pref == "yes":
                            if before_presentation.assigned_venue.venue_type != presentation.assigned_venue.venue_type:
                                total_fitness += 10

                    else:
                        consecutive_presentation = staff.consecutive_presentation_pref

                # SC02
                if staff in presentation.staff_list:
                    if presentation.assigned_venue.day not in attended_days:
                        attended_days.append(presentation.assigned_venue.day)
                        if len(attended_days) > int(staff.attend_day):
                            total_fitness += 10

                line_num += 1
        print("Fitness : " + str(total_fitness))
        return total_fitness

    def print(self):
        for presetation in self.presentation_list:
            print("/////////////////////")
            print("Presentation ID : " + str(presetation.presentation_id))
            print("Venue ID : " + str(presetation.assigned_venue.venue_id))
            staffs = ""
            for staff in presetation.staff_list:
                staffs += str(staff.staff_id)
                staffs += " "
            print("Staffs : " + staffs)
        print("/////////////////////")


class GeneticAlgorithm:
    def __init__(self):
        self.population = []  # List of candidates
        self.pop_size = 400
        self.parent_use_percent = 10.0
        self.venue_list = venue_record_handler()
        for i in range(self.pop_size):
            new_candidate = Candidate()
            new_candidate.randomize_venue(self.venue_list)
            self.population.append(new_candidate)
        self.population = sorted(self.population, key=lambda candidate: candidate.fitness())  # Sort the population

    def generate_new_gen(self):
        new_pop = []

        while len(new_pop) < self.pop_size * (1.0 - (self.parent_use_percent / 100.0)):
            size = len(self.population)
            i = random.sample(range(size), 4)

            c1 = self.population[i[0]]
            c2 = self.population[i[1]]
            c3 = self.population[i[2]]
            c4 = self.population[i[3]]

            if c1.fitness() < c2.fitness():
                w1 = c1
            else:
                w1 = c2

            if c3.fitness() < c4.fitness():
                w2 = c3
            else:
                w2 = c4

            childs = self.uniform_crossover(w1, w2)
            child1 = childs[0]
            child2 = childs[1]

            mutate_percent = 0.01
            m1 = random.random() <= mutate_percent
            m2 = random.random() <= mutate_percent

            if m1:
                self.mutate(child1)
            if m2:
                self.mutate(child2)

            if child1.fitness() < w1.fitness():
                new_pop.append(child1)
            else:
                new_pop.append(w1)

            if child2.fitness() < w2.fitness():
                new_pop.append(child2)
            else:
                new_pop.append(w2)

        j = int(self.pop_size * (self.parent_use_percent / 100.0))
        for i in range(j):
            new_pop.append(self.population[i])

        self.population = sorted(new_pop, key=lambda candidate: candidate.fitness())

    def uniform_crossover(self, c1, c2):
        obj = Candidate()
        obj2 = Candidate()

        for i in range(obj.SIZE):
            b = random.random() >= 0.5

            if b:
                obj.presentation_list[i] = c1.presentation_list[i]
                obj2.presentation_list[i] = c2.presentation_list[i]
            else:
                obj.presentation_list[i] = c2.presentation_list[i]
                obj2.presentation_list[i] = c1.presentation_list[i]

        return obj, obj2

    def mutate(self, obj):
        i = random.randint(0, obj.SIZE)
        j = random.randint(1, 300)

        while j in obj.random_venue_list:
            j = random.randint(1, 300)

        obj.random_venue_list[i] = j  # Update the venue occupied by the chosen presentation
        obj.presentation_list[i].assigned_venue = self.venue_list[j - 1]  # Update new venue for chosen presentation

    def run(self):
        max_steps = 10000
        for i in range(max_steps):
            self.generate_new_gen()


# result = GeneticAlgorithm()
venue_run = venue_record_handler()
for item in venue_run:
    print(item.venue_id, item.venue_type, item.availability, item.day, item.time)

staff_run = staff_record_handler()
for record in staff_run:
    print(staff_run[record].staff_id, staff_run[record].attend_day, staff_run[record].unavailable_slot,
          staff_run[record].same_venue_pref, staff_run[record].consecutive_presentation_pref)

run = GeneticAlgorithm()
#run.population[0].print()
