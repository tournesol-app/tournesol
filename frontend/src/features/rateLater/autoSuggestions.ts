// A pool of UIDs that can be suggested.
export const AUTO_SUGGESTIONS: { [key: string]: string[] } = {};

export const clearAutoSuggestions = () => {
  Object.keys(AUTO_SUGGESTIONS).forEach((key) => (AUTO_SUGGESTIONS[key] = []));
};

export const isAutoSuggestionsEmpty = (poll: string) =>
  AUTO_SUGGESTIONS[poll] == null || AUTO_SUGGESTIONS[poll].length === 0;

export const fillAutoSuggestions = (
  poll: string,
  uids: string[],
  exclude?: string[] | null
) => {
  const excludeSet = new Set(exclude);
  AUTO_SUGGESTIONS[poll] = uids.filter((uid) => !excludeSet?.has(uid));
};

export const autoSuggestionsRandom = (
  poll: string,
  exclude?: string[] | null
): string | null => {
  if (isAutoSuggestionsEmpty(poll)) {
    return null;
  }

  const excludeSet = new Set(exclude);
  const uids = [
    ...AUTO_SUGGESTIONS[poll].filter((uid) => !excludeSet?.has(uid)),
  ];

  const selected = uids[Math.floor(Math.random() * uids.length)];
  AUTO_SUGGESTIONS[poll].splice(AUTO_SUGGESTIONS[poll].indexOf(selected), 1);
  return selected;
};
