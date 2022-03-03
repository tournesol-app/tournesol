import { RelatedEntityObject } from './types';
import { Video } from 'src/services/openapi';

export const videoFromRelatedEntity = (entity: RelatedEntityObject): Video => {
  return {
    uid: entity.uid,
    name: entity.metadata.name,
    description: entity.metadata.description,
    publication_date: entity.metadata.publication_date,
    views: entity.metadata.views,
    uploader: entity.metadata.uploader,
    language: entity.metadata.language,
    tournesol_score: null,
    rating_n_ratings: 0,
    rating_n_contributors: 0,
    duration: entity.metadata.duration,
    video_id: entity.metadata.video_id,
  };
};
