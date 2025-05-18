# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import json

class PokedexAPI(http.Controller):
    @http.route('/api/pokemon', type='http', auth='public', methods=['GET'], csrf=False)
    def get_all_pokemon(self, **kw):
        pokemon = request.env['pokedex.pokemon'].sudo().search([])
        result = []
        for p in pokemon:
            result.append({
                'id': p.id,
                'name': p.name,
                'pokedex_number': p.pokedex_number,
                'type': p.type_id.name,
                'image_url': p.image_url,
            })
        return request.make_response(
            json.dumps(result),
            headers=[('Content-Type', 'application/json')]
        )
    
    @http.route('/api/pokemon/<int:pokemon_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_pokemon(self, pokemon_id, **kw):
        pokemon = request.env['pokedex.pokemon'].sudo().browse(pokemon_id)
        if not pokemon.exists():
            return request.not_found()
            
        skills = []
        for skill in pokemon.skill_ids:
            skills.append({
                'id': skill.id,
                'name': skill.name,
                'power': skill.power,
                'type': skill.type_id.name if skill.type_id else None
            })
            
        result = {
            'id': pokemon.id,
            'name': pokemon.name,
            'pokedex_number': pokemon.pokedex_number,
            'type': pokemon.type_id.name,
            'secondary_type': pokemon.secondary_type_id.name if pokemon.secondary_type_id else None,
            'stats': {
                'hp': pokemon.base_hp,
                'attack': pokemon.base_attack,
                'defense': pokemon.base_defense,
                'speed': pokemon.base_speed,
            },
            'height': pokemon.height,
            'weight': pokemon.weight,
            'skills': skills,
            'image_url': pokemon.image_url,
            'description': pokemon.description,
        }
        
        return request.make_response(
            json.dumps(result),
            headers=[('Content-Type', 'application/json')]
        )
    
    @http.route('/api/pokemon/search/<string:name>', type='http', auth='public', methods=['GET'], csrf=False)
    def search_pokemon(self, name, **kw):
        """Search for Pokemon by name or ID using the PokeAPI integration"""
        try:
            # First try local database
            pokemon = request.env['pokedex.pokemon'].sudo().search([
                '|',
                ('name', 'ilike', name),
                ('pokedex_number', '=', name if name.isdigit() else 0)
            ], limit=1)
            
            # If not found locally, try to import
            if not pokemon:
                api_sync = request.env['pokedex.api.sync'].sudo()
                pokemon = api_sync.import_pokemon(name)
                
            if not pokemon:
                return request.not_found()
                
            # Return Pokemon data
            skills = []
            for skill in pokemon.skill_ids:
                skills.append({
                    'id': skill.id,
                    'name': skill.name,
                    'power': skill.power,
                    'type': skill.type_id.name if skill.type_id else None
                })
                
            result = {
                'id': pokemon.id,
                'name': pokemon.name,
                'pokedex_number': pokemon.pokedex_number,
                'type': pokemon.type_id.name,
                'secondary_type': pokemon.secondary_type_id.name if pokemon.secondary_type_id else None,
                'stats': {
                    'hp': pokemon.base_hp,
                    'attack': pokemon.base_attack,
                    'defense': pokemon.base_defense,
                    'speed': pokemon.base_speed,
                },
                'height': pokemon.height,
                'weight': pokemon.weight,
                'skills': skills,
                'image_url': pokemon.image_url,
                'description': pokemon.description,
            }
            
            return request.make_response(
                json.dumps(result),
                headers=[('Content-Type', 'application/json')]
            )
            
        except Exception as e:
            error = {'error': str(e)}
            return request.make_response(
                json.dumps(error),
                headers=[('Content-Type', 'application/json')],
                status=500
            )
        
    @http.route('/api/trainers', type='http', auth='public', methods=['GET'], csrf=False)
    def get_trainers(self, **kw):
        trainers = request.env['res.partner'].sudo().search([('is_trainer', '=', True)])
        result = []
        for trainer in trainers:
            result.append({
                'id': trainer.id,
                'name': trainer.name,
                'pokemon_count': trainer.pokemon_count,
                'trainer_level': trainer.trainer_level,
            })
        return request.make_response(
            json.dumps(result),
            headers=[('Content-Type', 'application/json')]
        )
    
    @http.route('/api/trainers/<int:trainer_id>/pokemon', type='http', auth='public', methods=['GET'], csrf=False)
    def get_trainer_pokemon(self, trainer_id, **kw):
        trainer = request.env['res.partner'].sudo().browse(trainer_id)
        if not trainer.exists() or not trainer.is_trainer:
            return request.not_found()
            
        result = []
        for pokemon in trainer.trainer_pokemon_ids:
            result.append({
                'id': pokemon.id,
                'pokemon_name': pokemon.pokemon_id.name,
                'nickname': pokemon.nickname or pokemon.pokemon_id.name,
                'level': pokemon.level,
                'experience': pokemon.experience,
                'stats': {
                    'hp': pokemon.hp,
                    'attack': pokemon.attack,
                    'defense': pokemon.defense,
                    'speed': pokemon.speed,
                },
                'image_url': pokemon.image_url,
            })
            
        return request.make_response(
            json.dumps(result),
            headers=[('Content-Type', 'application/json')]
        )
    
    # Add POST, PUT, DELETE methods for CRUD operations
    @http.route('/api/pokemon', type='json', auth='user', methods=['POST'], csrf=False)
    def create_pokemon(self, **kw):
        # Create a new pokemon (requires authentication)
        data = request.jsonrequest
        
        required_fields = ['name', 'pokedex_number', 'type_id']
        for field in required_fields:
            if field not in data:
                return {'error': f"Missing required field: {field}"}
        
        try:
            pokemon = request.env['pokedex.pokemon'].create({
                'name': data.get('name'),
                'pokedex_number': data.get('pokedex_number'),
                'type_id': data.get('type_id'),
                'secondary_type_id': data.get('secondary_type_id'),
                'base_hp': data.get('base_hp', 100),
                'base_attack': data.get('base_attack', 50),
                'base_defense': data.get('base_defense', 50),
                'base_speed': data.get('base_speed', 50),
                'height': data.get('height', 0.0),
                'weight': data.get('weight', 0.0),
                'image_url': data.get('image_url'),
                'description': data.get('description'),
            })
            return {'success': True, 'id': pokemon.id}
        except Exception as e:
            return {'error': str(e)}