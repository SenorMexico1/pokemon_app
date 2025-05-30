from odoo import models, fields, api
from odoo.exceptions import UserError
from random import randint, choice

class PokemonCatchWizard(models.TransientModel):
    _name = 'pokedex.catch.wizard'
    _description = 'Catch Pokemon Wizard'
    
    # The trainer who is trying to catch a Pokemon
    trainer_id = fields.Many2one('res.partner', string='Trainer', 
                                required=True, default=lambda self: self.env.user.partner_id)
    
    # The Pokemon to try to catch
    pokemon_id = fields.Many2one('pokedex.pokemon', string='Pokemon to Catch', required=True)
    
    # Display info about the Pokemon
    pokemon_image = fields.Char(related='pokemon_id.image_url', string='Pokemon Image')
    pokemon_type = fields.Many2one(related='pokemon_id.type_id', string='Type')
    
    # Catch result fields
    catch_success = fields.Boolean(string='Catch Success', readonly=True)
    result_message = fields.Char(string='Result', readonly=True)
    
    @api.onchange('pokemon_id')
    def _onchange_pokemon_id(self):
        """Show Pokemon info when selected"""
        if self.pokemon_id:
            self.result_message = f"Try to catch {self.pokemon_id.name}?"
    
    def attempt_catch(self):
        """Attempt to catch the selected Pokemon"""
        self.ensure_one()  # Make sure we're working with a single record
        
        # Check if trainer already has this Pokemon
        existing_pokemon = self.env['pokedex.trainer.pokemon'].search([
            ('trainer_id', '=', self.trainer_id.id),
            ('pokemon_id', '=', self.pokemon_id.id)
        ])
        
        if existing_pokemon:
            raise UserError(f"You already have a {self.pokemon_id.name}!")
        
        # Randomize catch success (70% chance to catch)
        catch_roll = randint(1, 100)
        
        if catch_roll <= 70:
            # Success! Create the trainer's Pokemon
            new_pokemon = self.env['pokedex.trainer.pokemon'].create({
                'trainer_id': self.trainer_id.id,
                'pokemon_id': self.pokemon_id.id,
                'nickname': False,  # No nickname by default
                'level': 5,  # Start at level 5
                'experience': 0
            })
            
            self.catch_success = True
            self.result_message = f"Success! You caught {self.pokemon_id.name}!"
            
            # Return a notification action
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Pokemon Caught!',
                    'message': f'You successfully caught {self.pokemon_id.name}!',
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            # Failed to catch
            self.catch_success = False
            self.result_message = f"Oh no! {self.pokemon_id.name} escaped!"
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Pokemon Escaped!',
                    'message': f'{self.pokemon_id.name} broke free and ran away!',
                    'type': 'warning',
                    'sticky': False,
                }
            }