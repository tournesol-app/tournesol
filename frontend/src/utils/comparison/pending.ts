import { PollCriteria } from 'src/services/openapi';
import { CriteriaValuesType } from 'src/utils/types';

const PENDING_NS = 'pendingComparisons';

const initPending = () => '{}';

/**
 * Save a criterion rating for a couple of entities in a given poll.
 *
 * The rating is saved in the browser's local storage, and can be retrieved
 * with `getPendingRating`.
 *
 * The ratings are saved with the following structure:
 *
 *  {
 *     `${pollName}/${uidA}/${uidB}`: ${rating},
 *  }
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
  let pending = localStorage.getItem(PENDING_NS);

  if (pending == null) {
    pending = initPending();
  }

  const pendingJSON = JSON.parse(pending);
  pendingJSON[`${poll}/${uidA}/${uidB}/${criterion}`] = rating;

  localStorage.setItem(PENDING_NS, JSON.stringify(pendingJSON));
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
): number | null => {
  const pending = localStorage.getItem(PENDING_NS);

  if (pending == null) {
    return null;
  }

  const pendingJSON = JSON.parse(pending);
  const rating = pendingJSON[`${poll}/${uidA}/${uidB}/${criterion}`];

  if (pop) {
    delete pendingJSON[`${poll}/${uidA}/${uidB}/${criterion}`];
    localStorage.setItem(PENDING_NS, JSON.stringify(pendingJSON));
  }

  return rating ? rating : null;
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
): CriteriaValuesType => {
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
