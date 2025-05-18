{
    'name': "pokedex_app",

    'description': "Pokedex App with PokéAPI Integration",

    'author': "Andre Romero",

    # Categories can be used to filter modules in modules listing
    'category': 'Customizations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/ir_cron.xml',
        'data/ir_actions_server.xml',
        'wizards/pokemon_catch_views.xml',
        'wizards/pokemon_search_views.xml',
    ],
    # assets
    'qweb': [
        'static/src/xml/pokemon_templates.xml',
    ],
    # other data
    'installable': True,
    'application': True,
    'auto_install': False,
}