import re

class AtomicSymbol:          
    greek_lower = [
        'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'vartheta',
        'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'rho', 'sigma', 'tau', 'upsilon',
        'phi', 'chi', 'psi', 'omega'
    ]

    greek_upper = [
        'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Upsilon', 'Phi', 'Psi', 'Omega'
    ]

    alpha_regex = None
    greek_alphabet = None
    alphabet_parser = None
    numeric_regex = re.compile('-?[0-9]+')
    
    @staticmethod
    def next_symbol(sym:str, rev=None) -> str:
        if rev is None:
            rev = False
        if rev:
            num_dir = -1
        else:
            num_dir = 1            
        cls = AtomicSymbol
        if sym.startswith('\\'):
            sym = sym[1:]
            if sym in cls.greek_alphabet:
                if sym[0].isupper():
                    i = cls.greek_upper.index(sym)
                    return cls.greek_upper[(i + 1) % len(cls.greek_upper)]
                else:
                    i = cls.greek_lower.index(sym)
                    return cls.greek_lower[(i + 1) % len(cls.greek_lower)]
        if sym.isnumeric() or (len(sym) > 0 and sym[1:].isnumeric()):
            sym = str(int(sym) + num_dir)
            return sym
        if sym.isalpha():
            next_ord = ord(sym[0]) + num_dir
            if sym[0].isupper():
                if next_ord >= ord('A') + 26:
                    next_ord = ord('A')
                elif next_ord < ord('A'):
                    next_ord = ord('Z')
            else:
                if next_ord >= ord('a') + 26:
                    next_ord = ord('a')
                elif next_ord < ord('a'):
                    next_ord = ord('z')
            return str(chr(next_ord))
        
        
AtomicSymbol.greek_alphabet = set(AtomicSymbol.greek_lower + AtomicSymbol.greek_upper)                
                
AtomicSymbol.alpha_regex = r'[a-zA-Z]|' + r'|'.join(
    [r'\\' + letter for letter in AtomicSymbol.greek_alphabet])

AtomicSymbol.alphabet_parser = re.compile(AtomicSymbol.alpha_regex)
    