# -*- coding: utf-8 -*-

from odoo import models, fields, api
from random import randint

class PokemonExperienceCron(models.Model):
    _name = 'pokedex.experience.cron'
    _description = 'Pokemon Experience Cron'
    
    @api.model
    def _award_experience(self):
        """Cron job to award experience to all trainer pokemon"""
        trainer_pokemons = self.env['pokedex.trainer.pokemon'].search([])
        for pokemon in trainer_pokemons:
            # Award between 1-10 XP randomly
            xp_gain = randint(1, 10)
            old_level = pokemon.level
            
            # Update experience
            pokemon.experience += xp_gain
            
            # Level up when experience reaches threshold
            # Simple formula: 100 * current level = XP needed for next level
            if pokemon.experience >= (100 * pokemon.level):
                pokemon.experience = 0  # Reset experience
                pokemon.level_up()  # This will trigger the automated action