import { PollCriteria } from 'src/services/openapi';
import { CriteriaValuesType } from 'src/utils/types';

// Name of the key used in the browser's local storage.
const PENDING_NS = 'pendingComparisons';

const initPending = () => '{}';

const pendingIsEmpty = (pending: string) => {
  return pending == null || pending === initPending();
};

const makePendingKey = (
  poll: string,
  uidA: string,
  uidB: string,
  criterion: string
) => {
  return `${poll}/${uidA}/${uidB}/${criterion}`;
};

const keyIsInvalid = (
  poll: string,
  uidA: string,
  uidB: string,
  criterion: string | null
) => {
  return [poll, uidA, uidB, criterion].includes('');
};

/**
 * Save a criterion rating for a pair of entities in a given poll.
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

  if (keyIsInvalid(poll, uidA, uidB, criterion)) {
    return null;
  }

  const pendingJSON = JSON.parse(pending);
  pendingJSON[makePendingKey(poll, uidA, uidB, criterion)] = rating;

  localStorage.setItem(PENDING_NS, JSON.stringify(pendingJSON));
};

/**
 * Retrieve a previously saved criterion rating for a pair of entities in a
 * given poll.
 *
 * If `pop` is true, the rating is deleted from the browser's local storage.
 *
 * See `getAllPendingRatings` to get all criterion ratings related to a pair
 * of entities.
 */
export const getPendingRating = (
  poll: string,
  uidA: string,
  uidB: string,
  criterion: string,
  pop?: boolean
): number | null => {
  const pending = localStorage.getItem(PENDING_NS) ?? initPending();

  if (pendingIsEmpty(pending)) {
    return null;
  }

  if (keyIsInvalid(poll, uidA, uidB, criterion)) {
    return null;
  }

  const pendingJSON = JSON.parse(pending);
  const pendingKey = makePendingKey(poll, uidA, uidB, criterion);

  const rating = pendingJSON[pendingKey];

  if (pop) {
    delete pendingJSON[pendingKey];
    localStorage.setItem(PENDING_NS, JSON.stringify(pendingJSON));
  }

  return rating ?? null;
};

/**
 * Delete a previously saved criterion rating for a pair of entities in a
 * given poll.
 *
 * See `clearAllPendingRatings` to clear all criterion ratings related to
 * a pair of entities.
 */
export const clearPendingRating = (
  poll: string,
  uidA: string,
  uidB: string,
  criterion: string
) => {
  const pending = localStorage.getItem(PENDING_NS) ?? initPending();

  if (pendingIsEmpty(pending)) {
    return;
  }

  if (keyIsInvalid(poll, uidA, uidB, criterion)) {
    return;
  }

  const pendingJSON = JSON.parse(pending);
  delete pendingJSON[makePendingKey(poll, uidA, uidB, criterion)];
  localStorage.setItem(PENDING_NS, JSON.stringify(pendingJSON));
};

/**
 * Retrieve all previously saved criterion ratings for a pair of entities in a
 * given poll.
 *
 * If `pop` is true, the ratings are deleted from the browser's local storage.
 *
 * To avoid parsing and writing a JSON content for each criterion, this
 * function doesn't call `getPendingRating`.
 */
export const getAllPendingRatings = (
  poll: string,
  uidA: string,
  uidB: string,
  criterias: PollCriteria[],
  pop?: boolean
): CriteriaValuesType => {
  const pendingCriteria: CriteriaValuesType = {};

  const pending = localStorage.getItem(PENDING_NS) ?? initPending();

  if (pendingIsEmpty(pending)) {
    return {};
  }

  if (keyIsInvalid(poll, uidA, uidB, null)) {
    return {};
  }

  if (criterias.length === 0) {
    return {};
  }

  const pendingJSON = JSON.parse(pending);

  criterias.map((criterion) => {
    const pendingKey = makePendingKey(poll, uidA, uidB, criterion.name);
    const rating = pendingJSON[pendingKey];

    if (rating) {
      pendingCriteria[criterion.name] = rating;

      if (pop) {
        delete pendingJSON[pendingKey];
      }
    }
  });

  localStorage.setItem(PENDING_NS, JSON.stringify(pendingJSON));
  return pendingCriteria;
};

/**
 * Delete all previously saved criterion ratings for a pair of entities in a
 * given poll.
 *
 * To avoid parsing and writing a JSON content for each criterion, this
 * function doesn't call `clearPendingRating`.
 */
export const clearAllPendingRatings = (
  poll: string,
  uidA: string,
  uidB: string,
  criterias: PollCriteria[]
) => {
  const pending = localStorage.getItem(PENDING_NS) ?? initPending();

  if (pendingIsEmpty(pending)) {
    return;
  }

  if (keyIsInvalid(poll, uidA, uidB, null)) {
    return;
  }

  if (criterias.length === 0) {
    return;
  }

  const pendingJSON = JSON.parse(pending);

  criterias.map((criterion) => {
    delete pendingJSON[makePendingKey(poll, uidA, uidB, criterion.name)];
  });

  localStorage.setItem(PENDING_NS, JSON.stringify(pendingJSON));
};

export const resetPendingRatings = () => {
  localStorage.setItem(PENDING_NS, initPending());
};
