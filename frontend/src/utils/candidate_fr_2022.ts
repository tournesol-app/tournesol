import { EntitiesService, Entity } from 'src/services/openapi';

export async function getAllCandidates(): Promise<Array<Entity>> {
  const candidates = await EntitiesService.entitiesList({
    type: 'candidate_fr_2022',
  });

  return candidates?.results ?? [];
}
