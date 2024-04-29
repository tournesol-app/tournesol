import { SuggestionPool } from './suggestionPool';

/**
 * A generic history of UIDs, supporting appends to both ends and multiple
 * polls.
 *
 * A history can be used, for instance, to keep track of all UIDs that have
 * been displayed by an entity selector.
 *
 * A history should always be cleared at logout.
 */
export class BaseHistory {
  // The current position in the history.
  _cursor: { [key: string]: number };
  _history: { [key: string]: string[] };

  constructor() {
    this._cursor = {};
    this._history = {};
  }

  isCursorInitialized(poll: string) {
    return this._cursor[poll] != undefined;
  }

  isEmpty(poll: string) {
    return this._history[poll] == undefined || this._history[poll].length === 0;
  }

  /**
   * Insert an UID in the history at the left or the right of the current
   * cursor position, and move the cursor to this new position.
   */
  insert(poll: string, uid: string, position: 'left' | 'right') {
    if (this._history[poll] == undefined) {
      this._history[poll] = [];
    }

    if (this._history[poll][this._cursor[poll]] === uid) {
      return;
    }

    if (position === 'right') {
      this._cursor[poll] += 1;
    }

    this._history[poll].splice(this._cursor[poll], 0, uid);
  }

  /**
   * Append a new UID to the left of the history and move the cursor to this
   * new position.
   */
  appendLeft(poll: string, uid: string) {
    if (this._history[poll] == undefined) {
      this._history[poll] = [];
    }

    this._history[poll].unshift(uid);
    this._cursor[poll] = 0;
  }

  /**
   * Append a new UID to the right of the history and move the cursor to this
   * new position.
   */
  appendRight(poll: string, uid: string) {
    if (this._history[poll] == undefined) {
      this._history[poll] = [];
    }

    this._history[poll].push(uid);
    this._cursor[poll] = this._history[poll].length - 1;
  }

  /**
   * Move the cursor one step to the left and return the UID found if any.
   */
  nextLeft(poll: string): string | null {
    if (this.isEmpty(poll)) {
      return null;
    }

    if (!this.isCursorInitialized(poll)) {
      this._cursor[poll] = this._history[poll].length;
    }

    if (this._cursor[poll] <= 0) {
      return null;
    }

    this._cursor[poll] -= 1;
    return this._history[poll].at(this._cursor[poll]) ?? null;
  }

  /**
   * Move the cursor one step to the right and return the UID found if any.
   */
  nextRight(poll: string): string | null {
    if (this.isEmpty(poll)) {
      return null;
    }

    if (!this.isCursorInitialized(poll)) {
      this._cursor[poll] = this._history[poll].length - 1;
    }

    if (this._cursor[poll] >= this._history[poll].length - 1) {
      return null;
    }

    this._cursor[poll] += 1;
    return this._history[poll].at(this._cursor[poll]) ?? null;
  }

  hasNextLeft(poll: string): boolean {
    if (this.isEmpty(poll)) {
      return false;
    }

    if (!this.isCursorInitialized(poll)) {
      this._cursor[poll] = this._history[poll].length - 1;
    }

    return this._history[poll][this._cursor[poll] - 1] !== undefined;
  }

  hasNextRight(poll: string): boolean {
    if (this.isEmpty(poll)) {
      return false;
    }

    if (!this.isCursorInitialized(poll)) {
      this._cursor[poll] = this._history[poll].length - 1;
    }

    return this._history[poll][this._cursor[poll] + 1] !== undefined;
  }

  clear() {
    this._cursor = {};
    this._history = {};
  }
}

/**
 * A SuggestionHistory can automatically get UIDs from a suggestion pool.
 */
export class SuggestionHistory extends BaseHistory {
  _suggestionPool: SuggestionPool;

  constructor(pool: SuggestionPool) {
    super();
    this._suggestionPool = pool;
  }

  /**
   * Same as `nextLeft`, except if null should be returned, return a new UID
   * from the suggestion pool instead.
   */
  async nextLeftOrSuggestion(
    poll: string,
    exclude?: Array<string | null>
  ): Promise<string | null> {
    if (this.hasNextLeft(poll)) {
      return this.nextLeft(poll);
    }

    const suggestion = await this._suggestionPool.getSuggestion(poll, exclude);

    if (suggestion) {
      this.appendLeft(poll, suggestion);
    }

    return suggestion;
  }

  /**
   * Same as `nextRight`, except if null should be returned, return a new UID
   * from the suggestion pool instead.
   */
  async nextRightOrSuggestion(
    poll: string,
    exclude?: Array<string | null>
  ): Promise<string | null> {
    if (this.hasNextRight(poll)) {
      return this.nextRight(poll);
    }

    const suggestion = await this._suggestionPool.getSuggestion(poll, exclude);

    if (suggestion) {
      this.appendRight(poll, suggestion);
    }

    return suggestion;
  }
}
