import { UsersService } from 'src/services/openapi';

/**
 * A generic pool of UIDs, supporting multiple polls.
 *
 * A pool can be used to suggest UIDs to compare, or anything else that
 * involves randomly selecting a UID from a pre-defined list.
 *
 * A pool should always be cleared at logout.
 */
export class BasePool {
  _suggestions: { [key: string]: string[] };

  constructor() {
    this._suggestions = {};
  }

  isEmpty(poll: string) {
    return (
      this._suggestions[poll] == null || this._suggestions[poll].length === 0
    );
  }

  fill(poll: string, uids: string[], exclude?: string[] | null) {
    const excludeSet = new Set(exclude);
    this._suggestions[poll] = uids.filter((uid) => !excludeSet?.has(uid));
  }

  random(poll: string, exclude?: string[] | null): string | null {
    if (this.isEmpty(poll)) {
      return null;
    }

    const excludeSet = new Set(exclude);
    const uids = [
      ...this._suggestions[poll].filter((uid) => !excludeSet?.has(uid)),
    ];

    if (uids.length === 0) {
      return null;
    }

    const selected = uids[Math.floor(Math.random() * uids.length)];
    this._suggestions[poll].splice(
      this._suggestions[poll].indexOf(selected),
      1
    );

    return selected;
  }

  clear() {
    this._suggestions = {};
  }
}

/**
 * A pool that can suggest UIDs to compare.
 */
export class SuggestionPool extends BasePool {
  async getSuggestion(
    poll: string,
    exclude?: Array<string | null>
  ): Promise<string | null> {
    const excluded =
      (exclude?.filter((elem) => elem != null) as string[]) ?? [];

    if (this.isEmpty(poll)) {
      const suggestions = await UsersService.usersMeSuggestionsTocompareList({
        pollName: poll,
      });

      if (suggestions && suggestions.length > 0) {
        this.fill(
          poll,
          suggestions.map((item) => item.entity.uid),
          excluded
        );
      }
    }

    if (this.isEmpty(poll)) {
      return null;
    }

    return this.random(poll, excluded);
  }
}

export const autoSuggestionPool = new SuggestionPool();
