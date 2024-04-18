import { UidHistory } from 'src/features/suggestions/uidHistory';

describe('class: UidHistory', () => {
  const pollA = 'foo';
  const pollB = 'bar';

  it('constructor', () => {
    const history = new UidHistory();
    expect(history.isEmpty(pollA)).toEqual(true);
    expect(history.isEmpty(pollB)).toEqual(true);
    expect(history.moveLeft(pollA)).toBeNull();
    expect(history.moveLeft(pollB)).toBeNull();
    expect(history.moveRight(pollA)).toBeNull();
    expect(history.moveRight(pollB)).toBeNull();
    expect(history.hasNextLeft(pollA)).toEqual(false);
    expect(history.hasNextLeft(pollB)).toEqual(false);
    expect(history.hasNextRight(pollA)).toEqual(false);
    expect(history.hasNextRight(pollB)).toEqual(false);
  });

  it('method: isEmpty - is poll specific', () => {
    const history = new UidHistory();
    history.appendRight(pollA, 'uid1');

    expect(history.isEmpty(pollA)).toEqual(false);
    expect(history.isEmpty(pollB)).toEqual(true);
  });

  it('method: appendLeft - is poll specific', () => {
    const history = new UidHistory();
    ['uid1', 'uid2'].forEach((uid) => history.appendLeft(pollA, uid));
    ['uidA', 'uidB'].forEach((uid) => history.appendLeft(pollB, uid));

    expect(history.moveRight(pollA)).toEqual('uid1');
    expect(history.moveRight(pollB)).toEqual('uidA');
  });

  it('method: appendLeft - reset the history cursor', () => {
    const history = new UidHistory();

    history.appendLeft(pollA, 'uid1');
    expect(history.moveRight(pollA)).toBeNull();

    history.appendLeft(pollA, 'uid2');
    expect(history.moveRight(pollA)).toEqual('uid1');

    history.appendLeft(pollA, 'uid3');
    history.appendLeft(pollA, 'uid4');
    expect(history.moveRight(pollA)).toEqual('uid3');

    history.moveRight(pollA);
    history.moveRight(pollA);
    history.appendLeft(pollA, 'uid5');
    expect(history.moveRight(pollA)).toEqual('uid4');
  });

  it('method: appendRight - is poll specific', () => {
    const history = new UidHistory();
    ['uid1', 'uid2'].forEach((uid) => history.appendRight(pollA, uid));
    ['uidA', 'uidB'].forEach((uid) => history.appendRight(pollB, uid));

    expect(history.moveLeft(pollA)).toEqual('uid1');
    expect(history.moveLeft(pollB)).toEqual('uidA');
  });

  it('method: appendRight - reset the history cursor', () => {
    const history = new UidHistory();

    history.appendRight(pollA, 'uid1');
    expect(history.moveLeft(pollA)).toBeNull();

    history.appendRight(pollA, 'uid2');
    expect(history.moveLeft(pollA)).toEqual('uid1');

    history.appendRight(pollA, 'uid3');
    history.appendRight(pollA, 'uid4');
    expect(history.moveLeft(pollA)).toEqual('uid3');

    history.moveLeft(pollA);
    history.moveLeft(pollA);
    history.appendRight(pollA, 'uid5');
    expect(history.moveLeft(pollA)).toEqual('uid4');
  });

  it('method: moveLeft - is poll specific', () => {
    const history = new UidHistory();
    ['uid1', 'uid2', 'uid3', 'uid4'].forEach((uid) =>
      history.appendRight(pollA, uid)
    );
    ['uidA', 'uidB', 'uidC', 'uidD'].forEach((uid) =>
      history.appendRight(pollB, uid)
    );

    expect(history.moveLeft(pollA)).toEqual('uid3');
    expect(history.moveLeft(pollA)).toEqual('uid2');
    expect(history.moveLeft(pollA)).toEqual('uid1');
    expect(history.moveLeft(pollA)).toBeNull();

    expect(history.moveLeft(pollB)).toEqual('uidC');
    expect(history.moveLeft(pollB)).toEqual('uidB');
    expect(history.moveLeft(pollB)).toEqual('uidA');
    expect(history.moveLeft(pollB)).toBeNull();
  });

  it('method: moveRight - is poll specific', () => {
    const history = new UidHistory();
    ['uid1', 'uid2', 'uid3', 'uid4'].forEach((uid) =>
      history.appendRight(pollA, uid)
    );
    ['uidA', 'uidB', 'uidC', 'uidD'].forEach((uid) =>
      history.appendRight(pollB, uid)
    );

    expect(history.moveRight(pollA)).toBeNull();
    expect(history.moveRight(pollB)).toBeNull();

    history.moveLeft(pollA);
    expect(history.moveRight(pollA)).toEqual('uid4');

    history.moveLeft(pollA);
    history.moveLeft(pollA);
    expect(history.moveRight(pollA)).toEqual('uid3');
    expect(history.moveRight(pollA)).toEqual('uid4');
    expect(history.moveRight(pollA)).toBeNull();

    for (let i = 0; i < 10; i++) {
      history.moveLeft(pollA);
    }
    expect(history.moveRight(pollA)).toEqual('uid2');

    history.moveLeft(pollB);
    expect(history.moveRight(pollB)).toEqual('uidD');
    expect(history.moveRight(pollB)).toBeNull();
  });

  it('method: hasNextLeft - is poll specific', () => {
    const history = new UidHistory();
    ['uid1', 'uid2', 'uid3', 'uid4'].forEach((uid) =>
      history.appendLeft(pollA, uid)
    );
    ['uidA', 'uidB', 'uidC', 'uidD'].forEach((uid) =>
      history.appendLeft(pollB, uid)
    );

    expect(history.hasNextLeft(pollA)).toEqual(false);
    expect(history.hasNextLeft(pollB)).toEqual(false);

    history.moveRight(pollA);
    expect(history.hasNextLeft(pollA)).toEqual(true);
    expect(history.moveLeft(pollA)).toEqual('uid4');
    expect(history.hasNextLeft(pollA)).toEqual(false);

    for (let i = 0; i < 10; i++) {
      history.moveRight(pollA);
    }
    expect(history.hasNextLeft(pollA)).toEqual(true);
    expect(history.moveLeft(pollA)).toEqual('uid2');
    expect(history.hasNextLeft(pollA)).toEqual(true);

    history.moveRight(pollB);
    expect(history.hasNextLeft(pollB)).toEqual(true);
    expect(history.moveLeft(pollB)).toEqual('uidD');
    expect(history.hasNextLeft(pollB)).toEqual(false);
  });

  it('method: hasNextRight - is poll specific', () => {
    const history = new UidHistory();
    ['uid1', 'uid2', 'uid3', 'uid4'].forEach((uid) =>
      history.appendRight(pollA, uid)
    );
    ['uidA', 'uidB', 'uidC', 'uidD'].forEach((uid) =>
      history.appendRight(pollB, uid)
    );

    expect(history.hasNextRight(pollA)).toEqual(false);
    expect(history.hasNextRight(pollB)).toEqual(false);

    history.moveLeft(pollA);
    expect(history.hasNextRight(pollA)).toEqual(true);
    expect(history.moveRight(pollA)).toEqual('uid4');
    expect(history.hasNextRight(pollA)).toEqual(false);

    for (let i = 0; i < 10; i++) {
      history.moveLeft(pollA);
    }
    expect(history.hasNextRight(pollA)).toEqual(true);
    expect(history.moveRight(pollA)).toEqual('uid2');
    expect(history.hasNextRight(pollA)).toEqual(true);

    history.moveLeft(pollB);
    expect(history.hasNextRight(pollB)).toEqual(true);
    expect(history.moveRight(pollB)).toEqual('uidD');
    expect(history.hasNextRight(pollB)).toEqual(false);
  });

  it('method: clear - clears everything', () => {
    const history = new UidHistory();
    const pollC = 'foobar';

    ['uid1', 'uid2', 'uid3'].forEach((uid) => history.appendRight(pollA, uid));
    ['uidA', 'uidB', 'uidC'].forEach((uid) => history.appendRight(pollB, uid));
    ['uidX', 'uidY', 'uidZ'].forEach((uid) => history.appendRight(pollC, uid));

    // Move at the beginning of the history A.
    history.moveLeft(pollA);
    history.moveLeft(pollA);
    // Move in the middle of the history B.
    history.moveLeft(pollB);

    expect(history.isEmpty(pollA)).toEqual(false);
    expect(history.isEmpty(pollB)).toEqual(false);
    expect(history.isEmpty(pollC)).toEqual(false);

    history.clear();

    expect(history.isEmpty(pollA)).toEqual(true);
    expect(history.isEmpty(pollB)).toEqual(true);
    expect(history.isEmpty(pollC)).toEqual(true);

    expect(history.moveLeft(pollA)).toBeNull();
    expect(history.moveLeft(pollB)).toBeNull();
    expect(history.moveLeft(pollC)).toBeNull();

    expect(history.moveRight(pollA)).toBeNull();
    expect(history.moveRight(pollB)).toBeNull();
    expect(history.moveRight(pollC)).toBeNull();

    expect(history.hasNextRight(pollA)).toEqual(false);
    expect(history.hasNextRight(pollB)).toEqual(false);
    expect(history.hasNextRight(pollC)).toEqual(false);
  });
});
