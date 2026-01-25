from solidago import *
from solidago.poll.scoring.user_models import CommonMultipliers, CommonTranslations, UserDirectScores, UserMultipliers, UserTranslations

def test_user_models():
    entities = Entities(["entity_1", "entity_2", "entity_3"])
    directs = UserModels(
        user_directs=UserDirectScores(["username", "entity_name", "criterion"], {
            ("aidjango", "entity_1", "default"): Score(2, 1, 1),
            ("aidjango", "entity_1", "importance"): Score(0, 1, 1),
            ("aidjango", "entity_2", "default"): Score(-1, 1, 1),
            ("aidjango", "entity_2", "importance"): Score(3, 1, 10),
            ("aidjango", "entity_3", "default"): Score(0, 0, 1),
            ("le_science4all", "entity_1", "default"): Score(0, 0, 0),
            ("le_science4all", "entity_1", "importance"): Score(-3, 1, 1),
            ("le_science4all", "entity_2", "default"): Score(-1, 0, 1),
        })
    )
    scaled = directs.user_scale(
        UserMultipliers(["username", "criterion"], {
            ("aidjango", "default"): Score(2, 0.1, 1),
            ("aidjango", "importance"): Score(1, 0, 0),
            ("le_science4all", "default"): Score(1, 0, 0),
            ("le_science4all", "importance"): Score(1, 0, 0),
        }), 
        UserTranslations(["username", "criterion"], {
            ("aidjango", "default"): Score(-1, 1, 1),
            ("aidjango", "importance"): Score(0, 0, 0),
            ("le_science4all", "default"): Score(1, 1, 1),
            ("le_science4all", "importance"): Score(0, 0, 0),
        }), 
        note="second"
    )
    rescaled = scaled.common_scale(
        CommonMultipliers(["criterion"], {
            ("default",): Score(2, 0, 0),
            ("importance",): Score(1, 0, 1),
        }), 
        CommonTranslations(["criterion"], {
            ("default",): Score(1, 0, 0),
            ("importance",): Score(3, 2, 2),
        }), 
        note="third"
    )
    squashed = rescaled.post_process("Squash", max=100.)
    
    assert squashed(entities)["le_science4all", "entity_1", "importance"].value == 0
    assert squashed(entities, "default")["le_science4all", "entity_2"].value > 70
    assert squashed["aidjango"]("entity_3")["importance"].isnan()
    assert squashed["aidjango"]("entity_2")["importance"] > 0
