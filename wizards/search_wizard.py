from odoo import models, fields, api
from odoo.exceptions import UserError

class PokemonSearchWizard(models.TransientModel):
    _name = 'pokedex.search.wizard'
    _description = 'Search and Import Pokemon from PokeAPI'
    
    # Search field
    search_term = fields.Char(string='Pokemon Name or ID', required=True,
                             help="Enter a Pokemon name (e.g., 'pikachu') or ID (e.g., '25')")
    
    # Result fields
    found_pokemon_id = fields.Many2one('pokedex.pokemon', string='Found Pokemon', readonly=True)
    search_message = fields.Char(string='Search Result', readonly=True)
    
    def search_pokemon(self):
        """Search for a Pokemon in the database or import from API"""
        self.ensure_one()
        
        if not self.search_term:
            raise UserError("Please enter a Pokemon name or ID to search!")
        
        # First, try to find the Pokemon in our database
        # Try by name (case insensitive)
        existing_pokemon = self.env['pokedex.pokemon'].search([
            ('name', 'ilike', self.search_term)
        ], limit=1)
        
        # If not found by name, try by pokedex number if search term is numeric
        if not existing_pokemon and self.search_term.isdigit():
            existing_pokemon = self.env['pokedex.pokemon'].search([
                ('pokedex_number', '=', int(self.search_term))
            ], limit=1)
        
        if existing_pokemon:
            # Pokemon already exists in database
            self.found_pokemon_id = existing_pokemon
            self.search_message = f"Found {existing_pokemon.name} in the Pokedex!"
            
            # Open the Pokemon form view
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'pokedex.pokemon',
                'res_id': existing_pokemon.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            # Pokemon not in database, try to import from PokeAPI
            try:
                api_sync = self.env['pokedex.api.sync']
                imported_pokemon = api_sync.import_pokemon(self.search_term.lower())
                
                self.found_pokemon_id = imported_pokemon
                self.search_message = f"Successfully imported {imported_pokemon.name} from PokeAPI!"
                
                # Show notification
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Pokemon Imported!',
                        'message': f'{imported_pokemon.name} has been added to your Pokedex!',
                        'type': 'success',
                        'sticky': False,
                        'next': {
                            'type': 'ir.actions.act_window',
                            'res_model': 'pokedex.pokemon',
                            'res_id': imported_pokemon.id,
                            'view_mode': 'form',
                            'target': 'current',
                        }
                    }
                }
                
            except Exception as e:
                raise UserError(f"Could not find Pokemon '{self.search_term}'. "
                              f"Please check the name/ID and try again.\n"
                              f"Error: {str(e)}")
    
    def import_batch(self):
        """Import the first 151 Pokemon (Generation 1)"""
        try:
            api_sync = self.env['pokedex.api.sync']
            
            # Show progress notification
            self.env['bus.bus'].sendone(
                (self._cr.dbname, 'res.partner', self.env.user.partner_id.id),
                {'type': 'simple_notification', 
                 'title': 'Import Started',
                 'message': 'Importing Generation 1 Pokemon... This may take a few minutes.'}
            )
            
            # Import Pokemon 1-151
            api_sync.sync_pokemon_batch(1, 151)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Import Complete!',
                    'message': 'Successfully imported 151 Pokemon!',
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(f"Error during batch import: {str(e)}")