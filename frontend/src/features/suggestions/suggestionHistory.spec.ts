import { SuggestionHistory } from 'src/features/suggestions/suggestionHistory';

describe('class: SuggestionHistory', () => {
  const pollA = 'foo';
  const pollB = 'bar';

  it('constructor', () => {
    const history = new SuggestionHistory();
    expect(history.isEmpty(pollA)).toEqual(true);
    expect(history.isEmpty(pollB)).toEqual(true);
    expect(history.nextLeft(pollA)).toBeNull();
    expect(history.nextLeft(pollB)).toBeNull();
    expect(history.nextRight(pollA)).toBeNull();
    expect(history.nextRight(pollB)).toBeNull();
    expect(history.hasNextLeft(pollA)).toEqual(false);
    expect(history.hasNextLeft(pollB)).toEqual(false);
    expect(history.hasNextRight(pollA)).toEqual(false);
    expect(history.hasNextRight(pollB)).toEqual(false);
  });

  it('method: isEmpty - is poll specific', () => {
    const history = new SuggestionHistory();
    history.appendRight(pollA, 'uid1');

    expect(history.isEmpty(pollA)).toEqual(false);
    expect(history.isEmpty(pollB)).toEqual(true);
  });

  it('method: appendLeft - is poll specific', () => {
    const history = new SuggestionHistory();
    ['uid1', 'uid2'].forEach((uid) => history.appendLeft(pollA, uid));
    ['uidA', 'uidB'].forEach((uid) => history.appendLeft(pollB, uid));

    expect(history.nextRight(pollA)).toEqual('uid1');
    expect(history.nextRight(pollB)).toEqual('uidA');
  });

  it('method: appendLeft - reset the history cursor', () => {
    const history = new SuggestionHistory();

    history.appendLeft(pollA, 'uid1');
    expect(history.nextRight(pollA)).toBeNull();

    history.appendLeft(pollA, 'uid2');
    expect(history.nextRight(pollA)).toEqual('uid1');

    history.appendLeft(pollA, 'uid3');
    history.appendLeft(pollA, 'uid4');
    expect(history.nextRight(pollA)).toEqual('uid3');

    history.nextRight(pollA);
    history.nextRight(pollA);
    history.appendLeft(pollA, 'uid5');
    expect(history.nextRight(pollA)).toEqual('uid4');
  });

  it('method: appendRight - is poll specific', () => {
    const history = new SuggestionHistory();
    ['uid1', 'uid2'].forEach((uid) => history.appendRight(pollA, uid));
    ['uidA', 'uidB'].forEach((uid) => history.appendRight(pollB, uid));

    expect(history.nextLeft(pollA)).toEqual('uid1');
    expect(history.nextLeft(pollB)).toEqual('uidA');
  });

  it('method: appendRight - reset the history cursor', () => {
    const history = new SuggestionHistory();

    history.appendRight(pollA, 'uid1');
    expect(history.nextLeft(pollA)).toBeNull();

    history.appendRight(pollA, 'uid2');
    expect(history.nextLeft(pollA)).toEqual('uid1');

    history.appendRight(pollA, 'uid3');
    history.appendRight(pollA, 'uid4');
    expect(history.nextLeft(pollA)).toEqual('uid3');

    history.nextLeft(pollA);
    history.nextLeft(pollA);
    history.appendRight(pollA, 'uid5');
    expect(history.nextLeft(pollA)).toEqual('uid4');
  });

  it('method: nextLeft - is poll specific', () => {
    const history = new SuggestionHistory();
    ['uid1', 'uid2', 'uid3', 'uid4'].forEach((uid) =>
      history.appendRight(pollA, uid)
    );
    ['uidA', 'uidB', 'uidC', 'uidD'].forEach((uid) =>
      history.appendRight(pollB, uid)
    );

    expect(history.nextLeft(pollA)).toEqual('uid3');
    expect(history.nextLeft(pollA)).toEqual('uid2');
    expect(history.nextLeft(pollA)).toEqual('uid1');
    expect(history.nextLeft(pollA)).toBeNull();

    expect(history.nextLeft(pollB)).toEqual('uidC');
    expect(history.nextLeft(pollB)).toEqual('uidB');
    expect(history.nextLeft(pollB)).toEqual('uidA');
    expect(history.nextLeft(pollB)).toBeNull();
  });

  it('method: nextRight - is poll specific', () => {
    const history = new SuggestionHistory();
    ['uid1', 'uid2', 'uid3', 'uid4'].forEach((uid) =>
      history.appendRight(pollA, uid)
    );
    ['uidA', 'uidB', 'uidC', 'uidD'].forEach((uid) =>
      history.appendRight(pollB, uid)
    );

    expect(history.nextRight(pollA)).toBeNull();
    expect(history.nextRight(pollB)).toBeNull();

    history.nextLeft(pollA);
    expect(history.nextRight(pollA)).toEqual('uid4');

    history.nextLeft(pollA);
    history.nextLeft(pollA);
    expect(history.nextRight(pollA)).toEqual('uid3');
    expect(history.nextRight(pollA)).toEqual('uid4');
    expect(history.nextRight(pollA)).toBeNull();

    for (let i = 0; i < 10; i++) {
      history.nextLeft(pollA);
    }
    expect(history.nextRight(pollA)).toEqual('uid2');

    history.nextLeft(pollB);
    expect(history.nextRight(pollB)).toEqual('uidD');
    expect(history.nextRight(pollB)).toBeNull();
  });

  it('method: hasNextLeft - is poll specific', () => {
    const history = new SuggestionHistory();
    ['uid1', 'uid2', 'uid3', 'uid4'].forEach((uid) =>
      history.appendLeft(pollA, uid)
    );
    ['uidA', 'uidB', 'uidC', 'uidD'].forEach((uid) =>
      history.appendLeft(pollB, uid)
    );

    expect(history.hasNextLeft(pollA)).toEqual(false);
    expect(history.hasNextLeft(pollB)).toEqual(false);

    history.nextRight(pollA);
    expect(history.hasNextLeft(pollA)).toEqual(true);
    expect(history.nextLeft(pollA)).toEqual('uid4');
    expect(history.hasNextLeft(pollA)).toEqual(false);

    for (let i = 0; i < 10; i++) {
      history.nextRight(pollA);
    }
    expect(history.hasNextLeft(pollA)).toEqual(true);
    expect(history.nextLeft(pollA)).toEqual('uid2');
    expect(history.hasNextLeft(pollA)).toEqual(true);

    history.nextRight(pollB);
    expect(history.hasNextLeft(pollB)).toEqual(true);
    expect(history.nextLeft(pollB)).toEqual('uidD');
    expect(history.hasNextLeft(pollB)).toEqual(false);
  });

  it('method: hasNextRight - is poll specific', () => {
    const history = new SuggestionHistory();
    ['uid1', 'uid2', 'uid3', 'uid4'].forEach((uid) =>
      history.appendRight(pollA, uid)
    );
    ['uidA', 'uidB', 'uidC', 'uidD'].forEach((uid) =>
      history.appendRight(pollB, uid)
    );

    expect(history.hasNextRight(pollA)).toEqual(false);
    expect(history.hasNextRight(pollB)).toEqual(false);

    history.nextLeft(pollA);
    expect(history.hasNextRight(pollA)).toEqual(true);
    expect(history.nextRight(pollA)).toEqual('uid4');
    expect(history.hasNextRight(pollA)).toEqual(false);

    for (let i = 0; i < 10; i++) {
      history.nextLeft(pollA);
    }
    expect(history.hasNextRight(pollA)).toEqual(true);
    expect(history.nextRight(pollA)).toEqual('uid2');
    expect(history.hasNextRight(pollA)).toEqual(true);

    history.nextLeft(pollB);
    expect(history.hasNextRight(pollB)).toEqual(true);
    expect(history.nextRight(pollB)).toEqual('uidD');
    expect(history.hasNextRight(pollB)).toEqual(false);
  });

  it('method: clear - clears everything', () => {
    const history = new SuggestionHistory();
    const pollC = 'foobar';

    ['uid1', 'uid2', 'uid3'].forEach((uid) => history.appendRight(pollA, uid));
    ['uidA', 'uidB', 'uidC'].forEach((uid) => history.appendRight(pollB, uid));
    ['uidX', 'uidY', 'uidZ'].forEach((uid) => history.appendRight(pollC, uid));

    // Move at the beginning of the history A.
    history.nextLeft(pollA);
    history.nextLeft(pollA);
    // Move in the middle of the history B.
    history.nextLeft(pollB);

    expect(history.isEmpty(pollA)).toEqual(false);
    expect(history.isEmpty(pollB)).toEqual(false);
    expect(history.isEmpty(pollC)).toEqual(false);

    history.clear();

    expect(history.isEmpty(pollA)).toEqual(true);
    expect(history.isEmpty(pollB)).toEqual(true);
    expect(history.isEmpty(pollC)).toEqual(true);

    expect(history.nextLeft(pollA)).toBeNull();
    expect(history.nextLeft(pollB)).toBeNull();
    expect(history.nextLeft(pollC)).toBeNull();

    expect(history.nextRight(pollA)).toBeNull();
    expect(history.nextRight(pollB)).toBeNull();
    expect(history.nextRight(pollC)).toBeNull();

    expect(history.hasNextRight(pollA)).toEqual(false);
    expect(history.hasNextRight(pollB)).toEqual(false);
    expect(history.hasNextRight(pollC)).toEqual(false);
  });
});
