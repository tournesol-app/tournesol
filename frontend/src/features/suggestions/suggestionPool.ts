import { UsersService } from 'src/services/openapi';

/**
 * A generic pool of UIDs, supporting multiple polls.
 *
 * A pool can be used to suggest UIDs to compare, or anything else that
 * involves randomly selecting a UID from a pre-defined list.
 *
 * A pool should always be cleared at logout.
 */
export class SuggestionPool {
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

    if (uids.length === 0) {
      return null;
    }

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

export const randomUidToCompare = async (
  poll: string,
  exclude: Array<string | null>
): Promise<string | null> => {
  const excluded = exclude.filter((elem) => elem != null) as string[];

  if (autoSuggestionPool.isEmpty(poll)) {
    const suggestions = await UsersService.usersMeSuggestionsTocompareList({
      pollName: poll,
    });

    if (suggestions && suggestions.length > 0) {
      autoSuggestionPool.fill(
        poll,
        suggestions.map((item) => item.entity.uid),
        excluded
      );
    }
  }

  if (autoSuggestionPool.isEmpty(poll)) {
    return null;
  }

  return autoSuggestionPool.random(poll, excluded);
};
