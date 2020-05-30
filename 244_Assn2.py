import csv
import random
from tqdm import trange
from colorama import Fore
from tabulate import tabulate
import os


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
    w = 0

    for i in range(1, 301):
        new_venue = Venue()
        new_venue.venue_id = i

        if 1 <= i - w * 60 <= 15:
            new_venue.venue_type = "VR"
        elif 16 <= i - w * 60 <= 30:
            new_venue.venue_type = "MR"
        elif 31 <= i - w * 60 <= 45:
            new_venue.venue_type = "IR"
        else:
            new_venue.venue_type = "BJIM"
            if i - w * 60 == 60:
                w += 1

        new_venue.day = (i - 1) / 60  # stores the day as int (Mon - Fri : 0 - 4)
        new_venue.time = (i - 1) % 15  # stores the time as int (0900-0930.....1700-1730: 0.....14)

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
    def __init__(self, s_list):
        self.presentation_list = []
        self.SIZE = 118
        self.random_venue_list = [None] * self.SIZE
        self.staff_list = s_list

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

    def fitness(self):
        total_fitness = 0
        venue_presentation = {}
        list_of_presentation_id = []

        for i in range(self.SIZE):
            venue_presentation[self.random_venue_list[i]] = self.presentation_list[i]

        # self.presentation_list.sort(key=lambda p: p.assigned_venue.venue_id)
        for presentation in self.presentation_list:
            list_of_presentation_id.append(presentation.presentation_id)

            # HC03 : check whether the venue is available or not
            if not presentation.assigned_venue.availability:
                total_fitness += 1000

            for staff in presentation.staff_list:
                # HC04 : check whether the staff is unavailable for the assigned slot
                if presentation.assigned_venue.venue_id in staff.unavailable_slot:
                    total_fitness += 1000

                # HC02 : checking whether the staff exists in other presentations' staff list
                # that is in a slot that has the same time and day
                for i in range(4):
                    # gets venue_id of presentations with same time and day
                    same_time_venue_id = presentation.assigned_venue.day * 60 + i * 15 + presentation.assigned_venue.time
                    # refers venue_presentation dictionary to obtain the respective presentation
                    other_presentation = venue_presentation.get(same_time_venue_id)
                    if other_presentation and other_presentation.presentation_id != presentation.presentation_id:
                        if staff in other_presentation.staff_list:
                            total_fitness += 1000

        attended_days = []
        for key in self.staff_list:
            staff = self.staff_list.get(key)
            attended_days.clear()
            consecutive_presentation = staff.consecutive_presentation_pref
            other_presentation = None

            for presentation in self.presentation_list:

                if staff in presentation.staff_list:
                    # SC01 and SC03
                    if presentation.assigned_venue.time != 0:  # presentation is not the first one for the day
                        # stores the modulus 15 value of timeslot of the previous venue id
                        previous_time_slot = presentation.assigned_venue.time - 1
                        for i in range(4):
                            # get all presentations that uses the time slot before the current presentation
                            previous_venue_id = presentation.assigned_venue.day * 60 + i * 15 + previous_time_slot
                            other_presentation = venue_presentation.get(previous_venue_id)

                            # runs when other_presentation points towards a presentation occupying the previous time slot
                            if other_presentation:
                                if staff in other_presentation.staff_list:
                                    consecutive_presentation = int(consecutive_presentation) - 1

                                    if consecutive_presentation < 0:
                                        total_fitness += 10

                                    if staff.same_venue_pref == "yes":
                                        if other_presentation.assigned_venue.venue_type != presentation.assigned_venue.venue_type:
                                            total_fitness += 10
                                else:
                                    consecutive_presentation = staff.consecutive_presentation_pref
                            else:
                                consecutive_presentation = staff.consecutive_presentation_pref

                    # SC02 : check whether the number of presentation days exceed the number of prefered days of the staff
                    if presentation.assigned_venue.day not in attended_days:
                        if len(attended_days) < int(staff.attend_day):
                            attended_days.append(presentation.assigned_venue.day)
                        else:
                            total_fitness += 10

        # HC01 : A presentation is scheduled more than once
        if (len(list_of_presentation_id)) > len(set(list_of_presentation_id)):
            num_of_duplicates = len(list_of_presentation_id) - len(set(list_of_presentation_id))
            total_fitness += (num_of_duplicates * 1000)

        # print("Fitness : " + str(total_fitness))
        return total_fitness

    def print(self):
        for presentation in self.presentation_list:
            print("/////////////////////")
            print("Presentation ID : " + str(presentation.presentation_id))
            print("Venue ID : " + str(presentation.assigned_venue.venue_id))
            staffs = ""
            for staff in presentation.staff_list:
                staffs += str(staff.staff_id)
                staffs += " "
            print("Staffs : " + staffs)
        print("/////////////////////")


class GeneticAlgorithm:
    def __init__(self, size):
        self.population = []  # List of candidates
        self.pop_size = size
        self.parent_use_percent = 10.0
        self.staff_list = staff_record_handler()
        self.venue_list = venue_record_handler()
        for i in range(self.pop_size):
            new_candidate = Candidate(self.staff_list)
            new_candidate.randomize_venue(self.venue_list)
            self.population.append(new_candidate)
        self.population = sorted(self.population, key=lambda candidate: candidate.fitness())  # Sort the population

    def generate_new_gen(self, mut):
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

            mutate_percent = mut
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
        obj = Candidate(self.staff_list)
        obj2 = Candidate(self.staff_list)
        obj_list = []  # To store conflict node (existing venue) of obj
        obj2_list = []  # To store conflict node (existing venue) of obj2

        # Perform crossover on same genes or other genes based on probability
        for i in range(obj.SIZE):
            b = random.random() >= 0.5

            if b:
                if c1.random_venue_list[i] not in obj.random_venue_list:
                    obj.presentation_list[i].assigned_venue = c1.presentation_list[i].assigned_venue
                    obj.random_venue_list[i] = c1.random_venue_list[i]
                else:
                    obj_list.append((i, c1.random_venue_list[i]))
                if c2.random_venue_list[i] not in obj2.random_venue_list:
                    obj2.presentation_list[i].assigned_venue = c2.presentation_list[i].assigned_venue
                    obj2.random_venue_list[i] = c2.random_venue_list[i]
                else:
                    obj2_list.append((i, c2.random_venue_list[i]))
            else:
                if c2.random_venue_list[i] not in obj.random_venue_list:
                    obj.presentation_list[i].assigned_venue = c2.presentation_list[i].assigned_venue
                    obj.random_venue_list[i] = c2.random_venue_list[i]
                else:
                    obj_list.append((i, c2.random_venue_list[i]))
                if c1.random_venue_list[i] not in obj2.random_venue_list:
                    obj2.presentation_list[i].assigned_venue = c1.presentation_list[i].assigned_venue
                    obj2.random_venue_list[i] = c1.random_venue_list[i]
                else:
                    obj2_list.append((i, c1.random_venue_list[i]))

        # Search if redundant venue in other list of genes is found in its list of genes. Assign to itself it is not.
        temp = obj_list
        temp2 = obj2_list
        for x in range(len(obj2_list)):
            for y in range(len(temp)):
                if obj2_list[x][1] not in obj.random_venue_list:
                    obj.presentation_list[temp[y][0]].assigned_venue = self.venue_list[obj2_list[x][1]]
                    obj.random_venue_list[temp[y][0]] = obj2_list[x][1]
                    temp.remove(temp[y])
                    break

        for x in range(len(obj_list)):
            for y in range(len(temp2)):
                if obj_list[x][1] not in obj2.random_venue_list:
                    obj2.presentation_list[temp2[y][0]].assigned_venue = self.venue_list[obj_list[x][1]]
                    obj2.random_venue_list[temp[y][0]] = obj_list[x][1]
                    temp2.remove(temp2[y])
                    break

        # Assign random unexisting venue if there are still presentation without any venue.
        for x in range(len(temp)):
            j = random.randint(0, 299)
            while j in obj.random_venue_list:
                j = random.randint(0, 299)
            obj.presentation_list[temp[x][0]].assigned_venue = self.venue_list[j]
            obj.random_venue_list[temp[x][0]] = j

        for x in range(len(temp2)):
            j = random.randint(0, 299)
            while j in obj2.random_venue_list:
                j = random.randint(0, 299)
            obj2.presentation_list[temp2[x][0]].assigned_venue = self.venue_list[j]
            obj2.random_venue_list[temp2[x][0]] = j

        return obj, obj2

    def mutate(self, obj):
        i = random.randint(0, obj.SIZE - 1)
        j = random.randint(0, 299)

        while j in obj.random_venue_list:
            j = random.randint(0, 299)

        obj.random_venue_list[i] = j  # Update the venue occupied by the chosen presentation
        obj.presentation_list[i].assigned_venue = self.venue_list[j]  # Update new venue for chosen presentation

    def run(self, steps, mut):
        max_steps = steps

        pbar = trange(1, max_steps + 1, bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.WHITE, Fore.RESET))
        for item in pbar:
            pass
            pbar.set_description("Processing Generation %d" % item)
            self.generate_new_gen(mut)

        self.print_result()

    def print_result(self):
        print("\nDone!!!")
        print("\nChoose an output format\n1. Table\n2. CSV")
        option = input("Choose an option : ")
        while option != "1" and option != "2":
            print("Invalid input, please try again. ")
            option = input("Choose an option : ")
            
        result_list = ["null"] * 300
        final_result_list = []
        filename = "GA_Result.csv"
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        venue = ["VR", "MR", "IR", "BJIM"]
        for presentation in self.population[0].presentation_list:
            result_list[presentation.assigned_venue.venue_id - 1] = presentation.presentation_id

        for i in range(0, len(result_list), 15):
            sub = [days[int(i / 60)], venue[int(i / 15) % 4]]
            for j in range(15):
                sub.append(result_list[i + j])
            final_result_list.append(sub)

        with open(filename, mode='w') as GAFile:
            file_writer = csv.writer(GAFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(result_list)

        print("\nBest arrangement are:")
        if option == "1":
            print(tabulate(final_result_list, headers=["Days of Week", "Venue", "\n\n0900-0930", "\n\n0930-1000",
                                                       "\n\n1000-1030", "\n\n1030-1100", "\n\n1100-1130",
                                                       "\n\n1130-1200",
                                                       "\n\n1200-1230", "Time Slots\n\n1230-1300", "\n\n1400-1430",
                                                       "\n\n1430-1500", "\n\n1500-1530", "\n\n1530-1600",
                                                       "\n\n1600-1630",
                                                       "\n\n1630-1700", "\n\n1700-1730"], tablefmt="pretty",
                           colalign=("center", "left")))
        elif option == "2":
            print(result_list[0], end="")
            for i in range(1, len(result_list)):
                print(", ", result_list[i], end="")
        print("\nFitness: ", self.population[0].fitness())
        print("\nThe result has been saved into ", filename)


# result = GeneticAlgorithm()
cmd_dict = {"1": "result.run", "2": "exit()"}  # store functionality


# define our clear function
def clear():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')

        # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')


while True:
    cmds = ["\nCommand list: ",
            "              1            :   Run the Genetic Algorithm.",
            "              2            :   Exit.\n"]
    print("\nHi user, this is our CPT 244 Assignment 2: Presentation Scheduling Using Genetic Algorithm".center(120, '_'))
    print("\n".join(cmds))
    cmdInput = input("Choose a command.\n")
    clear()

    if cmdInput in cmd_dict:
        if cmdInput == "1":
            pop_size = input("\nPlease enter your desire population size. (Recommended: 300)\n")
            try:
                val = int(pop_size)
            except ValueError:
                print("Invalid Input.")
                break
            result = eval("GeneticAlgorithm(val)")
            print("\nInitialization of Initial Population Done.")
            
            num_run = input("\nPlease enter your desire number of runs. (Recommended: >=300)\n")
            try:
                val = int(num_run)
            except ValueError:
                print("Invalid Input.")
                break
            mut_rate = input("\nPlease enter your desire mutation rate. (Recommended: <=0.05)\n")
            try:
                val2 = float(mut_rate)
                if val2 < 0 or val2 > 1.0:
                    print("Invalid range of input.")
                    break
            except ValueError:
                print("Invalid Input.")
                break
            clear()
            eval(cmd_dict[cmdInput] + "(val,val2)")

        else:
            eval(cmd_dict[cmdInput])
    else:
        print("\nInvalid input.")
