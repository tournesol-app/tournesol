import {
  BasePool,
  SuggestionPool,
} from 'src/features/suggestions/suggestionPool';

describe('class: BasePool', () => {
  const pollA = 'foo';
  const pollB = 'bar';

  const setup = () => {
    return new BasePool();
  };

  it('constructor', () => {
    const pool = setup();
    expect(pool.isEmpty(pollA)).toEqual(true);
    expect(pool.random(pollA)).toBeNull();
  });

  it('method: isEmpty - is poll specific', () => {
    const pool = setup();
    pool.fill(pollA, ['uid1', 'uid2']);

    expect(pool.isEmpty(pollA)).toEqual(false);
    expect(pool.isEmpty(pollB)).toEqual(true);
  });

  it('method: fill - is poll specific', () => {
    const pool = setup();
    pool.fill(pollA, ['uid1']);
    pool.fill(pollB, ['uid2']);

    expect(pool._suggestions[pollA]).toEqual(['uid1']);
    expect(pool._suggestions[pollB]).toEqual(['uid2']);
  });

  it('method: fill - replaces the suggestions', () => {
    const pool = setup();
    pool.fill(pollA, ['uid1', 'uid2']);
    pool.fill(pollA, ['uid3', 'uid4']);

    expect(new Set(pool._suggestions[pollA])).toEqual(
      new Set(['uid3', 'uid4'])
    );
  });

  it('method: fill - can exclude UIDs', () => {
    const pool = setup();
    const uids = ['uid1', 'uid2', 'uid3', 'uid4'];
    pool.fill(pollA, uids, ['uid1', 'uid3', 'uid4']);

    expect(pool._suggestions[pollA]).toEqual(['uid2']);
  });

  it('method: random - is poll specific', () => {
    const pool = setup();
    pool.fill(pollA, ['uid1', 'uid2']);

    const results = [];
    results.push(pool.random(pollA));
    results.push(pool.random(pollA));

    expect(new Set(results)).toEqual(new Set(['uid1', 'uid2']));
    expect(pool.random(pollB)).toBeNull();
  });

  it('method: random - can exclude UIDs', () => {
    const pool = setup();
    const uids = ['uid1', 'uid2', 'uid3', 'uid4', 'uid5'];

    pool.fill(pollA, uids);

    expect(pool.random(pollA, uids)).toBeNull();
    expect(pool.random(pollA, uids.slice(0, 4))).toEqual('uid5');
  });

  it('method: clear - clears everything', () => {
    const pool = setup();
    const uids = ['uid1', 'uid2', 'uid3', 'uid4', 'uid5'];

    expect(pool.isEmpty(pollA)).toEqual(true);
    expect(pool.isEmpty(pollB)).toEqual(true);

    pool.fill(pollA, uids);
    pool.fill(pollB, uids);
    expect(pool.isEmpty(pollA)).toEqual(false);
    expect(pool.isEmpty(pollB)).toEqual(false);

    pool.clear();
    expect(pool.isEmpty(pollA)).toEqual(true);
    expect(pool.isEmpty(pollB)).toEqual(true);
  });
});

describe('class: SuggestionPool', () => {
  const pollA = 'foo';
  const pollB = 'bar';

  const setup = () => {
    return new SuggestionPool();
  };

  it('method: getSuggestion - is poll specific', async () => {
    fetchMock.mockIf(
      (req) =>
        req.method == 'GET' &&
        /users\/me\/suggestions\/foo\/tocompare/.test(req.url),
      () => ({
        init: {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
          },
        },
        body: JSON.stringify([
          { entity: { uid: 'uid1' } },
          { entity: { uid: 'uid2' } },
        ]),
      })
    );

    const pool = setup();
    expect(pool.isEmpty(pollA)).toEqual(true);

    const sugg1 = await pool.getSuggestion(pollA);

    expect(pool.isEmpty(pollA)).toEqual(false);
    expect(pool.isEmpty(pollB)).toEqual(true);

    const sugg2 = await pool.getSuggestion(pollA);

    expect(pool.isEmpty(pollA)).toEqual(true);
    expect(new Set([sugg1, sugg2])).toEqual(new Set(['uid1', 'uid2']));
  });

  it('method: getSuggestion - can exclude UIDs', async () => {
    fetchMock.mockIf(
      (req) =>
        req.method == 'GET' &&
        /users\/me\/suggestions\/foo\/tocompare/.test(req.url),
      () => ({
        init: {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
          },
        },
        body: JSON.stringify([
          { entity: { uid: 'uid1' } },
          { entity: { uid: 'uid2' } },
          { entity: { uid: 'uid3' } },
          { entity: { uid: 'uid4' } },
        ]),
      })
    );

    const pool = setup();

    expect(pool.isEmpty(pollA)).toEqual(true);
    await pool.getSuggestion(pollA, ['uid1', 'uid2']);
    expect(pool._suggestions[pollA].includes('uid1')).toBe(false);
    expect(pool._suggestions[pollA].includes('uid2')).toBe(false);
    expect(pool.isEmpty(pollA)).toEqual(false);
  });
});
