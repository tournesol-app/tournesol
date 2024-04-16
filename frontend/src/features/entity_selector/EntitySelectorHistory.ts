/**
 * A class representing a generic history of UIDs.
 *
 * One instance supports multiple polls. The public methods `previous` and
 * `next` allows to navigate in the history of UIDs.
 */
class UidHistory {
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

export const selectorAHistory = new UidHistory();
export const selectorBHistory = new UidHistory();
