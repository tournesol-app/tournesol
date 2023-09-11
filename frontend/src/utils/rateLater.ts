const MAX_LENGTH = 60;

export const ALREADY_SUGGESTED: string[] = [];

export const clearSuggested = () => (ALREADY_SUGGESTED.length = 0);

export const dontSuggestAnymore = (uid: string) => {
  if (ALREADY_SUGGESTED.length >= MAX_LENGTH) {
    clearSuggested();
  }

  if (!ALREADY_SUGGESTED.includes(uid)) {
    ALREADY_SUGGESTED.push(uid);
  }
};
