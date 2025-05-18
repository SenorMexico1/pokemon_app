# -*- coding: utf-8 -*-

from odoo import models, fields, api
from random import randint
from odoo.exceptions import UserError

class CatchPokemonWizard(models.TransientModel):
    _name = 'pokedex.catch.wizard'
    _description = 'Catch Pokemon Wizard'
    
    trainer_id = fields.Many2one('res.partner', string='Trainer', required=True, 
                                domain=[('is_trainer', '=', True)])
    pokemon_id = fields.Many2one('pokedex.pokemon', string='Pokemon to Catch', required=True)
    nickname = fields.Char(string='Nickname')
    catch_probability = fields.Float(string='Catch Probability', default=0.5)
    result_message = fields.Text(string='Result', readonly=True)
    
    def action_search_pokemon(self):
        """Open the search Pokemon wizard"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pokedex.search.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_state': 'search',
                'catch_wizard_id': self.id
            }
        }
    
    def action_try_catch(self):
        self.ensure_one()
        
        # Calculate success based on probability
        success = randint(1, 100) <= (self.catch_probability * 100)
        
        if success:
            # Create the trainer's pokemon
            trainer_pokemon = self.env['pokedex.trainer.pokemon'].create({
                'pokemon_id': self.pokemon_id.id,
                'trainer_id': self.trainer_id.id,
                'nickname': self.nickname or self.pokemon_id.name,
                'level': 1,
                'experience': 0,
            })
            self.result_message = f"Congratulations! You caught {self.pokemon_id.name}!"
        else:
            self.result_message = f"Oh no! {self.pokemon_id.name} broke free and ran away!"
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pokedex.catch.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context,
        }