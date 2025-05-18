# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class SearchPokemonWizard(models.TransientModel):
    _name = 'pokedex.search.wizard'
    _description = 'Search Pokemon Wizard'
    
    name = fields.Char(string='Pokemon Name or ID', help="Enter a Pokemon name (e.g., pikachu) or ID (e.g., 25)")
    result_ids = fields.Many2many('pokedex.pokemon', string='Search Results')
    state = fields.Selection([
        ('search', 'Search'),
        ('results', 'Results')
    ], default='search')
    
    def action_search(self):
        self.ensure_one()
        
        if not self.name:
            raise UserError("Please enter a Pokemon name or ID")
            
        # First search in local database
        local_results = self.env['pokedex.pokemon'].search([
            '|',
            ('name', 'ilike', self.name),
            ('pokedex_number', '=', self.name if self.name.isdigit() else 0)
        ])
        
        # If found locally, show results
        if local_results:
            self.write({
                'result_ids': [(6, 0, local_results.ids)],
                'state': 'results'
            })
        else:
            # If not found locally, try to import from API
            try:
                api_sync = self.env['pokedex.api.sync']
                new_pokemon = api_sync.import_pokemon(self.name)
                
                if new_pokemon:
                    self.write({
                        'result_ids': [(6, 0, [new_pokemon.id])],
                        'state': 'results'
                    })
            except Exception as e:
                raise UserError(f"Could not find Pokemon: {e}")
                
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pokedex.search.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context,
        }
        
    def action_select_pokemon(self):
        """Select a Pokemon and return to the catch wizard"""
        self.ensure_one()
        
        if not self.result_ids:
            raise UserError("No Pokemon selected")
            
        if len(self.result_ids) > 1:
            raise UserError("Please select only one Pokemon")
            
        # Get the catch wizard ID from context
        catch_wizard_id = self.env.context.get('catch_wizard_id')
        if not catch_wizard_id:
            return {'type': 'ir.actions.act_window_close'}
            
        # Update the catch wizard with the selected Pokemon
        catch_wizard = self.env['pokedex.catch.wizard'].browse(catch_wizard_id)
        catch_wizard.write({
            'pokemon_id': self.result_ids[0].id,
        })
        
        # Return to the catch wizard
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pokedex.catch.wizard',
            'view_mode': 'form',
            'res_id': catch_wizard_id,
            'target': 'new',
        }