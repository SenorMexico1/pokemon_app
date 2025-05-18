odoo.define('pokedex_app.pokemon_image_widget', function (require) {
    "use strict";
    
    var AbstractField = require('web.AbstractField');
    var registry = require('web.field_registry');
    
    var PokemonImageWidget = AbstractField.extend({
        className: 'o_pokemon_image',
        template: 'PokemonImageTemplate',
        
        _render: function () {
            var self = this;
            if (this.value) {
                this.$el.html('<img src="' + this.value + '" class="img-fluid pokemon-image"/>');
            } else {
                this.$el.html('<div class="o_pokemon_placeholder">No Image</div>');
            }
        },
    });
    
    registry.add('pokedex_image', PokemonImageWidget);
    
    return {
        PokemonImageWidget: PokemonImageWidget,
    };
});