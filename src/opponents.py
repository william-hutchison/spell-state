class Opponent:

    def __init__(self, subject_wizard):

        self.subject_wizard = subject_wizard
        self.ruler_state = subject_wizard.ruler_state

    def update(self, map_topology, map_resource, map_item, map_entities):

        cast_attempt = None
        move_character_attempt = None
        move_spell_attempt = None

        self.subject_wizard.update(map_entities, map_topology, map_resource, map_item, cast_attempt, move_character_attempt, move_spell_attempt)
