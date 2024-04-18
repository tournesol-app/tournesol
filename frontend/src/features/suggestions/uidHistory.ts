/**
 * A generic history of UIDs, supporting appends to both ends and multiple
 * polls.
 *
 * A history can be used, for instance, to keep track of all UIDs that have
 * been displayed by an entity selector.
 *
 * A history should always be cleared at logout.
 */
export class UidHistory {
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

  appendLeft(poll: string, uid: string) {
    if (this.#history[poll] == undefined) {
      this.#history[poll] = [];
    }

    this.#history[poll].unshift(uid);
    this.#cursor[poll] = 0;
  }

  appendRight(poll: string, uid: string) {
    if (this.#history[poll] == undefined) {
      this.#history[poll] = [];
    }

    this.#history[poll].push(uid);
    this.#cursor[poll] = this.#history[poll].length - 1;
  }

  moveLeft(poll: string): string | null {
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

  moveRight(poll: string): string | null {
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

  clear() {
    this.#cursor = {};
    this.#history = {};
  }
}
