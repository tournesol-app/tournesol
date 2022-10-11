import { PollCriteria } from 'src/services/openapi';
import { CriteriaValuesType } from 'src/utils/types';

// Name of the key used in the browser's local storage.
const PENDING_NS = 'pendingComparisons';

const initPending = () => '{}';

const makePendingKey = (
  poll: string,
  uidA: string,
  uidB: string,
  criterion: string
) => {
  return `${poll}/${uidA}/${uidB}/${criterion}`;
};

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
  pendingJSON[makePendingKey(poll, uidA, uidB, criterion)] = rating;

  localStorage.setItem(PENDING_NS, JSON.stringify(pendingJSON));
};

/**
 * Retrieve a previously saved criterion rating for a couple of entities in a
 * given poll.
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
  const pendingKey = makePendingKey(poll, uidA, uidB, criterion);

  const rating = pendingJSON[pendingKey];

  if (pop) {
    delete pendingJSON[pendingKey];
    localStorage.setItem(PENDING_NS, JSON.stringify(pendingJSON));
  }

  return rating ? rating : null;
};

/**
 * Delete a previously saved criterion rating for a couple of entities in a
 * given poll.
 */
export const clearPendingRating = (
  poll: string,
  uidA: string,
  uidB: string,
  criterion: string
) => {
  const pending = localStorage.getItem(PENDING_NS);

  if (pending == null) {
    return;
  }

  const pendingJSON = JSON.parse(pending);
  delete pendingJSON[makePendingKey(poll, uidA, uidB, criterion)];
  localStorage.setItem(PENDING_NS, JSON.stringify(pendingJSON));
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
