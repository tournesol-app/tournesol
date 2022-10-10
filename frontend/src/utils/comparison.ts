import { PollCriteria } from 'src/services/openapi';
import { CriteriaValuesType } from 'src/utils/types';

const PENDING_NS = 'pending';

export const setPendingRating = (
  uidA: string,
  uidB: string,
  criterion: string,
  rating: number
) => {
  localStorage.setItem(
    `${PENDING_NS}/${uidA}/${uidB}/${criterion}`,
    rating.toString()
  );
};

export const getPendingRating = (
  uidA: string,
  uidB: string,
  criterion: string,
  pop?: boolean
) => {
  const rating = localStorage.getItem(
    `${PENDING_NS}/${uidA}/${uidB}/${criterion}`
  );

  if (pop) {
    localStorage.removeItem(`${PENDING_NS}/${uidA}/${uidB}/${criterion}`);
  }

  return rating;
};

export const getAllPendingRatings = (
  uidA: string,
  uidB: string,
  criterias: PollCriteria[],
  pop?: boolean
) => {
  const pendings: CriteriaValuesType = {};

  criterias.map((criterion) => {
    const pendingRating = getPendingRating(uidA, uidB, criterion.name, pop);
    if (pendingRating) {
      pendings[criterion.name] = Number.parseInt(pendingRating);
    }
  });

  return pendings;
};
