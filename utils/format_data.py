def exchange_rate_format(data):
    """Return a dict with the exchange rate data formatted for serialization"""
    return {
        'provider_1': {
            'name': 'dof',
            'rate': data.dof_rate,
            'date': data.dof_date,
            'last_updated': data.dof_last_updated,
        },
        'provider_2': {
            'name': 'fixer',
            'rate': data.fixer_rate,
            'date': data.fixer_date,
            'last_updated': data.fixer_last_updated,
        },
        'provider_3': {
            'name': 'banxico',
            'rate': data.banxico_rate,
            'date': data.banxico_date,
            'last_updated': data.banxico_last_updated,
        },
        'created': data.created,
    }
