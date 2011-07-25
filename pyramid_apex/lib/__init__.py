from pyramid.threadlocal import get_current_registry

def apex_settings(key=None):
    settings = get_current_registry().settings
        
    if key:
        return settings.get('apex.%s' % key)
    else:
        apex_settings = []
        for k, v in settings.items():
            if k.startswith('apex.'):
                apex_settings.append({k.split('.')[1]: v})

        return apex_settings