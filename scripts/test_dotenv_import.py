import importlib.util
spec = importlib.util.find_spec('dotenv')
print('find_spec dotenv ->', spec)
try:
    import dotenv
    print('dotenv module file:', getattr(dotenv, '__file__', None))
    print('dotenv version:', getattr(dotenv, '__version__', None))
except Exception as e:
    print('import dotenv failed:', e)
