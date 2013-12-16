#------------------------------------------------------------------------------
# misc utility functions
#------------------------------------------------------------------------------

def remove_dots_from_dict(d):
    '''
    Remove dots from keys in dict d
    '''
    for k,v in d.iteritems():
        if isinstance(v, dict):
            d[k] = remove_dots_from_dict(v)
        else:
            if k.find('.') >= 0:
                del d[k]
                new_key = k.replace('.', '')
                d[new_key] = v
