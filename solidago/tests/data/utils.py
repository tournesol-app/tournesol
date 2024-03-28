from solidago.scoring_model import DirectScoringModel


def print_user_models(models, entities):
    print("{\n    " + ",\n    ".join([
        f"{user}: DirectScoringModel(" + "{\n        " + ",\n        ".join([
            f"{entity}: {str(models[user](entity, entities.loc[entity]))}"
            for entity in models[user].scored_entities(entities)
        ]) + "\n    })"
        for user in models
    ]) + "\n}")

def print_global_model(model, entities):
    print("DirectScoringModel({\n    " + "\n    ".join([
            f"{entity}: {str(model(entity, entities.loc[entity]))},"
            for entity in model.scored_entities(entities)
        ]) + "\n})")

def print_scaled_model(scaled_model, user, base_model, indent):
    args = ["multiplicator", "translation", 
        "multiplicator_left_uncertainty", "multiplicator_right_uncertainty", 
        "translation_left_uncertainty", "translation_right_uncertainty"]
    if isinstance(scaled_model, DirectScoringModel):
        return base_model
    results = f"ScaledScoringModel(\n"
    results += f"{indent}    base_model=learned_models[{user}],\n"
    for arg in args:
        results += f"{indent}    {arg}={getattr(scaled_model, arg)},\n"
    results += f"{indent})"
    return results

def print_scaled_models(scaled_models):
    results = "{\n"
    for user in scaled_models:
        results += f"    {user}: "
        results += print_scaled_model(scaled_models[user], 
            user, f"learned_models[{user}]", "    ")
        results += ",\n"
    results += "}"
    print(results)


