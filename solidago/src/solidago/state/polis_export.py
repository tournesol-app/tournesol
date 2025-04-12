from typing import BinaryIO, Optional, Union
from urllib.request import urlretrieve
from pandas import DataFrame, Series
from io import StringIO

import requests
import pandas as pd

from .base import *


class PolisExport(State):
    @staticmethod
    def load(poll_identifier: str, name: str) -> tuple:
        try:
            return pd.read_csv(f"{poll_identifier}/{name}.csv")
        except FileNotFoundError:
            url = lambda name: f"https://pol.is/api/v3/reportExport/{poll_identifier}/{name}.csv"
            return pd.read_csv(StringIO(requests.get(url(name)).text))
    
    @staticmethod
    def load_dfs(poll_identifier: str) -> tuple:
        summary = PolisExport.load(poll_identifier, "summary")
        
        users = PolisExport.load(poll_identifier, "participant-votes").set_index("participant")
        users.index.name = "username"
        
        entities = PolisExport.load(poll_identifier, "comments").set_index("comment-id")
        entities = entities.join(PolisExport.load(poll_identifier, "comment-groups"))
        entities.index.name = "entity_name"
        
        assessments = PolisExport.load(poll_identifier, "votes").rename(columns={
            "voter-id": "username",
            "comment-id": "entity_name",
            "vote": "value"
        })
        assessments[["criterion", "min", "max"]] = ["default", -1, 1]
        
        return summary, users, entities, assessments
    
    def __init__(self, poll_identifier: str):
        summary, users, entities, assessments = PolisExport.load_dfs(poll_identifier)
        from solidago.state import Users, Entities, AllPublic, Assessments
        super().__init__(
            users=Users(users),
            entities=Entities(entities),
            made_public=AllPublic(),
            assessments=Assessments(init_data=assessments),
        )
        self.summary = summary
