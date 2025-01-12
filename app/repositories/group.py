from . import BaseRepository
from database import supabase
from schemas import CreateGroup, UpdateGroup

class GroupRepository(BaseRepository[dict, CreateGroup, UpdateGroup]):
     def __init__(self):
        super().__init__(supabase, "groups", pk="group_id")
