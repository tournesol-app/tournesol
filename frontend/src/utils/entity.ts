import { RelatedEntityObject } from './types';
import {
  Entity,
  Recommendation,
  Video,
  VideoSerializerWithCriteria,
} from 'src/services/openapi';

export const videoFromRelatedEntity = (entity: RelatedEntityObject): Video => {
  return {
    uid: entity.uid,
    name: entity.metadata.name,
    description: entity.metadata.description,
    publication_date: entity.metadata.publication_date,
    views: entity.metadata.views,
    uploader: entity.metadata.uploader,
    language: entity.metadata.language,
    rating_n_ratings: 0,
    rating_n_contributors: 0,
    duration: entity.metadata.duration,
    video_id: entity.metadata.video_id,
  };
};

export const videoWithScoresFromRecommendation = (
  entity: Recommendation
): VideoSerializerWithCriteria => {
  const video = videoFromRelatedEntity(entity);

  return {
    ...video,
    criteria_scores: entity.criteria_scores,
    tournesol_score: entity.tournesol_score ?? null,
    rating_n_ratings: entity.n_comparisons,
    rating_n_contributors: entity.n_contributors,
  };
};

/**
 * Return a random entity with uid not included in the `exclude` array.
 */
export const selectRandomEntity = (
  entities: Array<Entity | Recommendation>,
  exclude: string[]
): Entity | Recommendation => {
  const filtered = entities.filter((entity) => !exclude.includes(entity.uid));

  return filtered[Math.floor(Math.random() * filtered.length)];
};

/**
 * Return an array of uids already compared with `uid`.
 *
 * @param uid An entity uid.
 * @param comparisons An array of comparisons, represented in the form 'uidA/uidB'.
 */
export const alreadyComparedWith = (
  uid: string,
  comparisons: string[]
): string[] => {
  const alreadyCompared: Array<string> = [];

  comparisons.forEach((comparison) => {
    const split = comparison.split('/');
    const index = split.indexOf(uid);

    if (index !== -1) {
      if (index === 0) {
        alreadyCompared.push(split[1]);
      } else {
        alreadyCompared.push(split[0]);
      }
    }
  });

  return alreadyCompared;
};
