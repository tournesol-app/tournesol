import { PollCriteria } from 'src/services/openapi';
import { CriteriaValuesType } from 'src/utils/types';

const PENDING_NS = 'pending';

/**
 * Save a criterion rating for a couple of entity.
 *
 * The rating is saved in the browser's local storage, and can be retrieved
 * with `getPendingRating`.
 *
 * @param poll The name of the poll.
 * @param uidA UID of the entity A.
 * @param uidB UID of the entity B.
 * @param criterion Name of the criterion ralated to the rating.
 * @param rating A score given by a user.
 */
export const setPendingRating = (
  poll: string,
  uidA: string,
  uidB: string,
  criterion: string,
  rating: number
) => {
  localStorage.setItem(
    `${PENDING_NS}/${poll}/${uidA}/${uidB}/${criterion}`,
    rating.toString()
  );
};

/**
 * Retrieve a previously saved criterion rating for a couple of entity.
 *
 * If `pop` is true, the rating is deleted from the browser's local storage.
 */
export const getPendingRating = (
  poll: string,
  uidA: string,
  uidB: string,
  criterion: string,
  pop?: boolean
) => {
  const rating = localStorage.getItem(
    `${PENDING_NS}/${poll}/${uidA}/${uidB}/${criterion}`
  );

  if (pop) {
    localStorage.removeItem(
      `${PENDING_NS}/${poll}/${uidA}/${uidB}/${criterion}`
    );
  }

  return rating ? Number.parseInt(rating) : null;
};

/**
 * Retrieve all previously saved criterion ratings for a couple of entity.
 *
 * If `pop` is true, the ratings are deleted from the browser's local storage.
 */
export const getAllPendingRatings = (
  poll: string,
  uidA: string,
  uidB: string,
  criterias: PollCriteria[],
  pop?: boolean
) => {
  const pendings: CriteriaValuesType = {};

  criterias.map((criterion) => {
    const pendingRating = getPendingRating(
      poll,
      uidA,
      uidB,
      criterion.name,
      pop
    );
    if (pendingRating) {
      pendings[criterion.name] = pendingRating;
    }
  });

  return pendings;
};
