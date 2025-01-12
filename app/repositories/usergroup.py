from . import BaseRepository
from database import supabase
from schemas import CreateUG, UpdateUG

class UGRepository(BaseRepository[dict, CreateUG, UpdateUG]):
     def __init__(self):
        super().__init__(supabase, "users_groups", pk="")
