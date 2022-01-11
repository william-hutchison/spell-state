import glob

class Building:
    
    def __init__(self, ruler_state, location):

        self.ruler_state = ruler_state
        self.location = location
        self.time_last = glob.time.now()
        self.under_construction = 0

    def constructing(self, build_amount):
        """Subtract build_amount from under_construction until 0 is reached, then return 0."""

        self.under_construction -= build_amount
        if self.under_construction <= 0:
            self.under_construction = 0
            self.constructed()

        return self.under_construction


class Tower(Building):
    
    def __init__(self, ruler_state, location):

        super().__init__(ruler_state, location)
        self.constructing(0)

    def constructed(self):

        self.ruler_state.increase_pop_limit(self.ruler_state, 1)

    def update(self):

        pass


class House(Building):
    def __init__(self, ruler_state, location):

        super().__init__(ruler_state, location)
        self.under_construction = 6000

    def constructed(self):

        self.ruler_state.increase_pop_limit(self.ruler_state, 1)

    def update(self):

        pass