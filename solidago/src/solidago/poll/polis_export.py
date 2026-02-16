from io import StringIO

import requests
import pandas as pd

from .poll import *


class PolisExport(Poll):
    @staticmethod
    def _load_csv(poll_identifier: str, name: str) -> pd.DataFrame:
        try:
            return pd.read_csv(f"{poll_identifier}/{name}.csv")
        except FileNotFoundError:
            url = lambda name: f"https://pol.is/api/v3/reportExport/{poll_identifier}/{name}.csv"
            return pd.read_csv(StringIO(requests.get(url(name)).text))
    
    @staticmethod
    def _load_dfs(poll_identifier: str) -> tuple:
        summary = PolisExport._load_csv(poll_identifier, "summary")
        
        users = PolisExport._load_csv(poll_identifier, "participant-votes").set_index("participant")
        users.index.name = "username"
        
        entities = PolisExport._load_csv(poll_identifier, "comments").set_index("comment-id")
        entities = entities.join(PolisExport._load_csv(poll_identifier, "comment-groups"))
        entities.index.name = "entity_name"
        
        ratings = PolisExport._load_csv(poll_identifier, "votes").rename(columns={
            "voter-id": "username",
            "comment-id": "entity_name",
            "vote": "value"
        })
        ratings[["criterion", "min", "max"]] = ["default", -1, 1]
        
        return summary, users, entities, ratings
    
    def __init__(self, poll_identifier: str):
        summary, users, entities, ratings = PolisExport._load_dfs(poll_identifier)
        from solidago.poll import Users, Entities, PublicSettings, Ratings
        super().__init__(
            users=Users(users),
            entities=Entities(entities),
            public_settings=PublicSettings(),
            ratings=Ratings(init_data=ratings),
        )
        self.summary = summary
