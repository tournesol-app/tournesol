/**
 * A class representing the history of UIDs suggested for comparison.
 *
 * The public methods `previous` and `next` allows to navigate in the history
 * of suggestions.
 */
class AutoHistory {
  // The current position in the history.
  #cursor: { [key: string]: number };
  #history: { [key: string]: string[] };

  constructor() {
    this.#cursor = {};
    this.#history = {};
  }

  isCursorInitialized(poll: string) {
    if (this.#cursor[poll] == undefined) {
      return false;
    }

    return true;
  }

  isHistoryEmpty(poll: string) {
    if (this.#history[poll] == undefined || this.#history[poll].length === 0) {
      return true;
    }

    return false;
  }

  push(poll: string, uid: string) {
    if (this.#history[poll] == undefined) {
      this.#history[poll] = [];
    }

    this.#history[poll].push(uid);
    this.#cursor[poll] = this.#history[poll].length - 1;
  }

  previous(poll: string): string | null {
    if (this.isHistoryEmpty(poll)) {
      return null;
    }

    if (!this.isCursorInitialized(poll)) {
      this.#cursor[poll] = this.#history[poll].length;
    }

    // End of the history. We could also restart at length - 1 instead.
    if (this.#cursor[poll] <= 0) {
      return null;
    }

    this.#cursor[poll] -= 1;
    return this.#history[poll].at(this.#cursor[poll]) ?? null;
  }

  next(poll: string): string | null {
    if (this.isHistoryEmpty(poll)) {
      return null;
    }

    if (!this.isCursorInitialized(poll)) {
      this.#cursor[poll] = this.#history[poll].length - 1;
    }

    if (this.#cursor[poll] >= this.#history[poll].length - 1) {
      return null;
    }

    this.#cursor[poll] += 1;
    return this.#history[poll].at(this.#cursor[poll]) ?? null;
  }

  hasNext(poll: string): boolean {
    if (this.isHistoryEmpty(poll)) {
      return false;
    }

    if (!this.isCursorInitialized(poll)) {
      this.#cursor[poll] = this.#history[poll].length - 1;
    }

    return this.#history[poll].at(this.#cursor[poll] + 1) !== undefined;
  }
}

export const autoHistory = new AutoHistory();

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

  if (selected) {
    autoHistory.push(poll, selected);
  }

  return selected;
};
