from datetime import datetime

from pycparser.c_ast import Struct
from pydantic import BaseModel

class Razvorot1(BaseModel):
    who: str
    quality: str
    what_was_he_doing: str
    reaction:str

class Razvorot2(BaseModel):
    scenery: str
    action: str


class Razvorot3(BaseModel):
    acceptance: str
    thank: str