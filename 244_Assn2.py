class Staff:
    staff_id = None
    unavailable_slot = None
    consecutive_presentation_pref = None
    attend_day = 0
    venue_change_pref = None


class Venue:
    venue_id = None
    venue_type = None
    availability = False


class Presentation:
    staff_list = []
    presentation_id = None
    assigned_venue = None


class Candidate:
    presentation_list = []

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


result = GeneticAlgorithm
