import {
  ApiError,
  ContributorRating,
  ContributorRatingCreate,
  UsersService,
} from 'src/services/openapi';

export const getContributorRating = async (
  pollName: string,
  uid: string
): Promise<ContributorRating | null> => {
  try {
    return await UsersService.usersMeContributorRatingsRetrieve({
      pollName,
      uid,
    });
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.status === 404) {
        return null;
      }
    }

    throw error;
  }
};

/**
 * Update the value of the field `entity_seen` of a `ContributorRating`
 * belonging to the logged-in user.
 *
 * If the `ContributorRating` doesn't exist, it is created.
 *
 * @param pollName Name of the poll.
 * @param uid UID of the related entity.
 * @param entitySeen New value of the field `entity_seen`.
 * @param defaultIsPublic Set the field `is_public` to this value if the `ContributorRating` doesn't exist.
 */
export const updateContributorRatingEntitySeen = async (
  pollName: string,
  uid: string,
  entitySeen: boolean,
  defaultIsPublic: boolean
): Promise<ContributorRating | ContributorRatingCreate> => {
  try {
    return await UsersService.usersMeContributorRatingsPartialUpdate({
      pollName,
      uid,
      requestBody: {
        entity_seen: entitySeen,
      },
    });
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.status === 404) {
        return await UsersService.usersMeContributorRatingsCreate({
          pollName,
          requestBody: {
            uid: uid,
            entity_seen: entitySeen,
            is_public: defaultIsPublic,
          },
        });
      }
    }

    throw error;
  }
};
