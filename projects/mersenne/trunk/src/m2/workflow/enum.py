#--python--
#
#  Simple creation of an enum, where each value is the identifier string.
#    choices = Enum(['TRUE', 'FALSE')
#    assert choices.TRUE = 'TRUE'
#    assert choices.FALSE = 'FALSE'
#

class Enum(set):
    """Implement an enumerated set."""
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError


