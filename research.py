class Research:

    def __init__(self, state):

        self.ruler_state = state
        self.under_research = 0

    def researching(self, research_amount):
        """Subtract build_amount from under_construction until 0 is reached, then return 0."""

        self.under_research -= research_amount
        if self.under_research <= 0:
            self.under_research = 0
            self.researched()

        return self.under_research

class ResearchSpellHeal(Research):

    def researched(self):
        pass
        #self.ruler_state.wizard.spell_dict["heal"][3] = True