import { EntityResult } from './types';

/**
 * Return a random entity with uid not included in the `exclude` array.
 */
export const selectRandomEntity = (
  entities: Array<EntityResult>,
  exclude: string[]
): EntityResult => {
  const filtered = entities.filter(
    (reco) => !exclude.includes(reco.entity.uid)
  );

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
