
CONTEXT_PREFIX = 'unit_'

UNITS = {
    'weight':{
        'verbose_name': 'Weight',
        'default': 'kg',
        'precision': 2,
        'choices': (
            ('kg', 'Kilogramme'),
            ('lb', 'Pound')
        )
    },
    
    'hop':{
        'verbose_name': 'Hop',
        'default': 'g',
        'choices': (
            ('g', 'Gramme'),
            ('oz', 'Ounce')
        )
    },
    
    'volume':{
        'verbose_name': 'Volume',
        'default': 'l',
        'precision': 1,
        'choices': (
            ('l', 'Litre'),
            ('gal', 'Gallon')
        )
    },

    'temperature':{
        'verbose_name': 'Temperature',
        'default': 'c',
        'choices': (
            ('c', 'deg. C'),
            ('f', 'deg. F')
        )
    },

    'color':{
        'verbose_name': 'Color',
        'default': 'ebc',
        'choices': (
            ('ebc', 'EBC'),
            ('srm', 'SRM')
        )
    },
}
