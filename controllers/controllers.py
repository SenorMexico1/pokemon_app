# -*- coding: utf-8 -*-
# from odoo import http


# class PokedexApp(http.Controller):
#     @http.route('/pokedex_app/pokedex_app/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pokedex_app/pokedex_app/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pokedex_app.listing', {
#             'root': '/pokedex_app/pokedex_app',
#             'objects': http.request.env['pokedex_app.pokedex_app'].search([]),
#         })

#     @http.route('/pokedex_app/pokedex_app/objects/<model("pokedex_app.pokedex_app"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pokedex_app.object', {
#             'object': obj
#         })
