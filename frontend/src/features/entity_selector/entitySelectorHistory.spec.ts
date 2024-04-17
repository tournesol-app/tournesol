import { UidHistory } from 'src/features/entity_selector/entitySelectorHistory';

describe('class: UidHistory', () => {
  const pollA = 'foo';
  const pollB = 'bar';

  it('constructor', () => {
    const history = new UidHistory();
    expect(history.isHistoryEmpty(pollA)).toEqual(true);
    expect(history.isHistoryEmpty(pollB)).toEqual(true);
    expect(history.previous(pollA)).toBeNull();
    expect(history.previous(pollB)).toBeNull();
    expect(history.next(pollA)).toBeNull();
    expect(history.next(pollB)).toBeNull();
    expect(history.hasNext(pollA)).toEqual(false);
    expect(history.hasNext(pollB)).toEqual(false);
  });

  it('method: isHistoryEmpty - is poll specific', () => {
    const history = new UidHistory();
    history.push(pollA, 'uid1');

    expect(history.isHistoryEmpty(pollA)).toEqual(false);
    expect(history.isHistoryEmpty(pollB)).toEqual(true);
  });

  it('method: push - is poll specific', () => {
    const history = new UidHistory();
    ['uid1', 'uid2'].forEach((uid) => history.push(pollA, uid));
    ['uidA', 'uidB'].forEach((uid) => history.push(pollB, uid));

    expect(history.previous(pollA)).toEqual('uid1');
    expect(history.previous(pollB)).toEqual('uidA');
  });

  it('method: push - reset the history cursor', () => {
    const history = new UidHistory();

    history.push(pollA, 'uid1');
    expect(history.previous(pollA)).toBeNull();

    history.push(pollA, 'uid2');
    expect(history.previous(pollA)).toEqual('uid1');

    history.push(pollA, 'uid3');
    history.push(pollA, 'uid4');
    expect(history.previous(pollA)).toEqual('uid3');

    history.previous(pollA);
    history.previous(pollA);
    history.push(pollA, 'uid5');
    expect(history.previous(pollA)).toEqual('uid4');
  });

  it('method: previous - is poll specific', () => {
    const history = new UidHistory();
    ['uid1', 'uid2', 'uid3', 'uid4'].forEach((uid) => history.push(pollA, uid));
    ['uidA', 'uidB', 'uidC', 'uidD'].forEach((uid) => history.push(pollB, uid));

    expect(history.previous(pollA)).toEqual('uid3');
    expect(history.previous(pollA)).toEqual('uid2');
    expect(history.previous(pollA)).toEqual('uid1');
    expect(history.previous(pollA)).toBeNull();

    expect(history.previous(pollB)).toEqual('uidC');
    expect(history.previous(pollB)).toEqual('uidB');
    expect(history.previous(pollB)).toEqual('uidA');
    expect(history.previous(pollB)).toBeNull();
  });

  it('method: next - is poll specific', () => {
    const history = new UidHistory();
    ['uid1', 'uid2', 'uid3', 'uid4'].forEach((uid) => history.push(pollA, uid));
    ['uidA', 'uidB', 'uidC', 'uidD'].forEach((uid) => history.push(pollB, uid));

    expect(history.next(pollA)).toBeNull();
    expect(history.next(pollB)).toBeNull();

    history.previous(pollA);
    expect(history.next(pollA)).toEqual('uid4');

    history.previous(pollA);
    history.previous(pollA);
    expect(history.next(pollA)).toEqual('uid3');
    expect(history.next(pollA)).toEqual('uid4');
    expect(history.next(pollA)).toBeNull();

    for (let i = 0; i < 10; i++) {
      history.previous(pollA);
    }
    expect(history.next(pollA)).toEqual('uid2');

    history.previous(pollB);
    expect(history.next(pollB)).toEqual('uidD');
    expect(history.next(pollB)).toBeNull();
  });

  it('method: hasNext - is poll specific', () => {
    const history = new UidHistory();
    ['uid1', 'uid2', 'uid3', 'uid4'].forEach((uid) => history.push(pollA, uid));
    ['uidA', 'uidB', 'uidC', 'uidD'].forEach((uid) => history.push(pollB, uid));

    expect(history.hasNext(pollA)).toEqual(false);
    expect(history.hasNext(pollB)).toEqual(false);

    history.previous(pollA);
    expect(history.hasNext(pollA)).toEqual(true);
    expect(history.next(pollA)).toEqual('uid4');
    expect(history.hasNext(pollA)).toEqual(false);

    for (let i = 0; i < 10; i++) {
      history.previous(pollA);
    }
    expect(history.hasNext(pollA)).toEqual(true);
    expect(history.next(pollA)).toEqual('uid2');
    expect(history.hasNext(pollA)).toEqual(true);

    history.previous(pollB);
    expect(history.hasNext(pollB)).toEqual(true);
    expect(history.next(pollB)).toEqual('uidD');
    expect(history.hasNext(pollB)).toEqual(false);
  });

  it('method: clear - clears everything', () => {
    const history = new UidHistory();
    const pollC = 'foobar';

    ['uid1', 'uid2', 'uid3'].forEach((uid) => history.push(pollA, uid));
    ['uidA', 'uidB', 'uidC'].forEach((uid) => history.push(pollB, uid));
    ['uidX', 'uidY', 'uidZ'].forEach((uid) => history.push(pollC, uid));

    // Move at the beginning of the history A.
    history.previous(pollA);
    history.previous(pollA);
    // Move in the middle of the history B.
    history.previous(pollB);

    expect(history.isHistoryEmpty(pollA)).toEqual(false);
    expect(history.isHistoryEmpty(pollB)).toEqual(false);
    expect(history.isHistoryEmpty(pollC)).toEqual(false);

    history.clear();

    expect(history.isHistoryEmpty(pollA)).toEqual(true);
    expect(history.isHistoryEmpty(pollB)).toEqual(true);
    expect(history.isHistoryEmpty(pollC)).toEqual(true);

    expect(history.previous(pollA)).toBeNull();
    expect(history.previous(pollB)).toBeNull();
    expect(history.previous(pollC)).toBeNull();

    expect(history.next(pollA)).toBeNull();
    expect(history.next(pollB)).toBeNull();
    expect(history.next(pollC)).toBeNull();

    expect(history.hasNext(pollA)).toEqual(false);
    expect(history.hasNext(pollB)).toEqual(false);
    expect(history.hasNext(pollC)).toEqual(false);
  });
});
