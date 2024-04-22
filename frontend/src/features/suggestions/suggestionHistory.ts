import { randomUidToCompare } from 'src/features/suggestions/suggestionPool';

/**
 * A history of UIDs, supporting appends to both ends and multiple polls.
 *
 * A history can be used, for instance, to keep track of all UIDs that have
 * been displayed by an entity selector.
 *
 * A history should always be cleared at logout.
 */
export class SuggestionHistory {
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

  isEmpty(poll: string) {
    if (this.#history[poll] == undefined || this.#history[poll].length === 0) {
      return true;
    }

    return false;
  }

  /**
   * Insert an UID in the history at the left or the right of the current
   * cursor position, and move the cursor to this new position.
   */
  insert(poll: string, uid: string, position: 'left' | 'right') {
    if (this.#history[poll] == undefined) {
      this.#history[poll] = [];
    }

    if (this.#history[poll][this.#cursor[poll]] === uid) {
      return;
    }

    if (position === 'right') {
      this.#cursor[poll] += 1;
    }

    this.#history[poll].splice(this.#cursor[poll], 0, uid);
  }

  /**
   * Append a new UID to the left of the history and move the cursor to this
   * new position.
   */
  appendLeft(poll: string, uid: string) {
    if (this.#history[poll] == undefined) {
      this.#history[poll] = [];
    }

    this.#history[poll].unshift(uid);
    this.#cursor[poll] = 0;
  }

  /**
   * Append a new UID to the right of the history and move the cursor to this
   * new position.
   */
  appendRight(poll: string, uid: string) {
    if (this.#history[poll] == undefined) {
      this.#history[poll] = [];
    }

    this.#history[poll].push(uid);
    this.#cursor[poll] = this.#history[poll].length - 1;
  }

  /**
   * Move the cursor one step to the left and return the found UID if any.
   */
  nextLeft(poll: string): string | null {
    if (this.isEmpty(poll)) {
      return null;
    }

    if (!this.isCursorInitialized(poll)) {
      this.#cursor[poll] = this.#history[poll].length;
    }

    if (this.#cursor[poll] <= 0) {
      return null;
    }

    this.#cursor[poll] -= 1;
    return this.#history[poll].at(this.#cursor[poll]) ?? null;
  }

  /**
   * Move the cursor one step to the right and return the found UID if any.
   */
  nextRight(poll: string): string | null {
    if (this.isEmpty(poll)) {
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

  hasNextLeft(poll: string): boolean {
    if (this.isEmpty(poll)) {
      return false;
    }

    if (!this.isCursorInitialized(poll)) {
      this.#cursor[poll] = this.#history[poll].length - 1;
    }

    return this.#history[poll][this.#cursor[poll] - 1] !== undefined;
  }

  hasNextRight(poll: string): boolean {
    if (this.isEmpty(poll)) {
      return false;
    }

    if (!this.isCursorInitialized(poll)) {
      this.#cursor[poll] = this.#history[poll].length - 1;
    }

    return this.#history[poll][this.#cursor[poll] + 1] !== undefined;
  }

  /**
   * Same as `nextLeft`, except if null should be returned, return a new UID
   * from the pool auto suggestion instead.
   */
  async nextLeftOrSuggestion(
    poll: string,
    exclude: Array<string | null>
  ): Promise<string | null> {
    if (this.hasNextLeft(poll)) {
      return this.nextLeft(poll);
    }

    const suggestion = await randomUidToCompare(poll, exclude);

    if (suggestion) {
      this.appendLeft(poll, suggestion);
    }

    return suggestion;
  }

  /**
   * Same as `nextRight`, except if null should be returned, return a new UID
   * from the pool auto suggestion instead.
   */
  async nextRightOrSuggestion(
    poll: string,
    exclude: Array<string | null>
  ): Promise<string | null> {
    if (this.hasNextRight(poll)) {
      return this.nextRight(poll);
    }

    const suggestion = await randomUidToCompare(poll, exclude);

    if (suggestion) {
      this.appendRight(poll, suggestion);
    }

    return suggestion;
  }

  clear() {
    this.#cursor = {};
    this.#history = {};
  }
}
