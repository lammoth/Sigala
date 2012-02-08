import os
import glob

ruta = os.path.join(os.path.abspath(os.curdir), __file__)
ruta = os.path.dirname(ruta)
lista = [t for t in glob.glob1(ruta, "rpc_*.py")]
lista = map(lambda k:k.split(".")[0], lista)
__all__=list(lista)
