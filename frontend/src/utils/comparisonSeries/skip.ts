/**
 * The day we will have different components using the skippedBy state, we
 * should consider using Redux instead of our custom localstorage accessors.
 */

const INITAL_SKIPPED_BY = '';

const skippedByIsEmpty = (skippedBy: string) => {
  return skippedBy === INITAL_SKIPPED_BY;
};

/**
 * Set the comparison series identified by `skipKey` as skipped by the user.
 *
 * @param skipKey The localstorage key identifying the comparison series.
 * @param username The username of the user.
 */
export const setSkippedBy = (skipKey: string, username: string) => {
  const skippedBy = localStorage.getItem(skipKey) ?? INITAL_SKIPPED_BY;
  let users: Array<string>;

  if (skippedByIsEmpty(skippedBy)) {
    users = [];
  } else {
    users = skippedBy.split(',');
  }

  if (!users.includes(username)) {
    users.push(username);
  }

  localStorage.setItem(skipKey, users.join(','));
};

/**
 * Return true if the comparison series identified by `skipKey` has been
 * skipped by the user.
 */
export const getSkippedBy = (skipKey: string, username: string): boolean => {
  const skippedBy = localStorage.getItem(skipKey) ?? INITAL_SKIPPED_BY;

  if (skippedByIsEmpty(skippedBy)) {
    return false;
  }

  const users = skippedBy.split(',');

  if (users.includes(username)) {
    return true;
  }

  return false;
};
