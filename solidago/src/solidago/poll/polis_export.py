from io import StringIO

import requests
import pandas as pd

from .poll import *


class PolisExport(Poll):
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
        
        ratings = PolisExport.load(poll_identifier, "votes").rename(columns={
            "voter-id": "username",
            "comment-id": "entity_name",
            "vote": "value"
        })
        ratings[["criterion", "min", "max"]] = ["default", -1, 1]
        
        return summary, users, entities, ratings
    
    def __init__(self, poll_identifier: str):
        summary, users, entities, ratings = PolisExport.load_dfs(poll_identifier)
        from solidago.poll import Users, Entities, AllPublic, Ratings
        super().__init__(
            users=Users(users),
            entities=Entities(entities),
            made_public=AllPublic(),
            ratings=Ratings(init_data=ratings),
        )
        self.summary = summary
