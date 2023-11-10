export const AUTO_SUGGESTIONS: { [key: string]: string[] } = {};

export const clearAutoSuggestions = () => {
  Object.keys(AUTO_SUGGESTIONS).forEach((key) => (AUTO_SUGGESTIONS[key] = []));
};

export const isAutoSuggestionsEmpty = (poll: string) =>
  AUTO_SUGGESTIONS[poll] == null || AUTO_SUGGESTIONS[poll].length === 0;

export const fillAutoSuggestions = (
  poll: string,
  uids: string[],
  exclude?: string[]
) => {
  AUTO_SUGGESTIONS[poll] = uids.filter((uid) => !exclude?.includes(uid));
};

export const autoSuggestionsRandom = (
  poll: string,
  exclude?: string[]
): string | null => {
  if (isAutoSuggestionsEmpty(poll)) {
    return null;
  }

  const uids = [
    ...AUTO_SUGGESTIONS[poll].filter((uid) => !exclude?.includes(uid)),
  ];
  const selected = uids[Math.floor(Math.random() * uids.length)];

  AUTO_SUGGESTIONS[poll].splice(AUTO_SUGGESTIONS[poll].indexOf(selected), 1);
  return selected;
};
