const MAX_LENGTH = 60;

export const ALREADY_SUGGESTED: { [key: string]: string[] } = {};

const initSuggested = (poll: string) => (ALREADY_SUGGESTED[poll] = []);

export const clearSuggested = (poll: string) =>
  (ALREADY_SUGGESTED[poll].length = 0);

export const dontSuggestAnymore = (poll: string, uid: string) => {
  if (ALREADY_SUGGESTED[poll] == null) {
    initSuggested(poll);
  }

  if (ALREADY_SUGGESTED[poll].length >= MAX_LENGTH) {
    clearSuggested(poll);
  }

  if (!ALREADY_SUGGESTED[poll].includes(uid)) {
    ALREADY_SUGGESTED[poll].push(uid);
  }
};
