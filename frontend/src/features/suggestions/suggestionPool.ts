/**
 * A generic pool of UIDs, supporting multiple polls.
 *
 * A pool can be used to suggest UIDs to compare, or anything else that
 * involves randomly selecting a UID from a pre-defined list.
 *
 * A pool should always be cleared at logout.
 */
class SuggestionPool {
  #suggestions: { [key: string]: string[] };

  constructor() {
    this.#suggestions = {};
  }

  isEmpty(poll: string) {
    return (
      this.#suggestions[poll] == null || this.#suggestions[poll].length === 0
    );
  }

  fill(poll: string, uids: string[], exclude?: string[] | null) {
    const excludeSet = new Set(exclude);
    this.#suggestions[poll] = uids.filter((uid) => !excludeSet?.has(uid));
  }

  random(poll: string, exclude?: string[] | null): string | null {
    if (this.isEmpty(poll)) {
      return null;
    }

    const excludeSet = new Set(exclude);
    const uids = [
      ...this.#suggestions[poll].filter((uid) => !excludeSet?.has(uid)),
    ];

    const selected = uids[Math.floor(Math.random() * uids.length)];
    this.#suggestions[poll].splice(
      this.#suggestions[poll].indexOf(selected),
      1
    );
    return selected;
  }

  clear() {
    this.#suggestions = {};
  }
}

export const autoSuggestionPool = new SuggestionPool();
