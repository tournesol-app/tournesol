import { SuggestionPool } from 'src/features/suggestions/suggestionPool';

describe('class: SuggestionPool', () => {
  const pollA = 'foo';
  const pollB = 'bar';

  it('constructor', () => {
    const suggestionPool = new SuggestionPool();
    expect(suggestionPool.isEmpty(pollA)).toEqual(true);
    expect(suggestionPool.random(pollA)).toBeNull();
  });

  it('method: isEmpty - is poll specific', () => {
    const suggestionPool = new SuggestionPool();
    suggestionPool.fill(pollA, ['uid1', 'uid2']);

    expect(suggestionPool.isEmpty(pollA)).toEqual(false);
    expect(suggestionPool.isEmpty(pollB)).toEqual(true);
  });

  it('method: fill - is poll specific', () => {
    const suggestionPool = new SuggestionPool();
    suggestionPool.fill(pollA, ['uid1']);
    suggestionPool.fill(pollB, ['uid2']);

    expect(suggestionPool.random(pollA)).toEqual('uid1');
    expect(suggestionPool.random(pollB)).toEqual('uid2');
  });

  it('method: fill - replaces the suggestions', () => {
    const suggestionPool = new SuggestionPool();
    suggestionPool.fill(pollA, ['uid1', 'uid2']);
    suggestionPool.fill(pollA, ['uid3', 'uid4']);

    const results = [];
    results.push(suggestionPool.random(pollA));
    results.push(suggestionPool.random(pollA));

    expect(new Set(results)).toEqual(new Set(['uid3', 'uid4']));
  });

  it('method: fill - can exclude UIDs', () => {
    const suggestionPool = new SuggestionPool();
    const uids = ['uid1', 'uid2', 'uid3', 'uid4'];
    suggestionPool.fill(pollA, uids, ['uid1', 'uid3', 'uid4']);

    expect(suggestionPool.random(pollA)).toEqual('uid2');
  });

  it('method: random - is poll specific', () => {
    const suggestionPool = new SuggestionPool();
    suggestionPool.fill(pollA, ['uid1', 'uid2']);

    const results = [];
    results.push(suggestionPool.random(pollA));
    results.push(suggestionPool.random(pollA));

    expect(new Set(results)).toEqual(new Set(['uid1', 'uid2']));
    expect(suggestionPool.random(pollB)).toBeNull();
  });

  it('method: random - can exclude UIDs', () => {
    const suggestionPool = new SuggestionPool();
    const uids = ['uid1', 'uid2', 'uid3', 'uid4', 'uid5'];

    suggestionPool.fill(pollA, uids);

    expect(suggestionPool.random(pollA, uids)).toBeNull();
    expect(suggestionPool.random(pollA, uids.slice(0, 4))).toEqual('uid5');
  });

  it('method: clear - clears everything', () => {
    const suggestionPool = new SuggestionPool();
    const uids = ['uid1', 'uid2', 'uid3', 'uid4', 'uid5'];

    expect(suggestionPool.isEmpty(pollA)).toEqual(true);
    expect(suggestionPool.isEmpty(pollB)).toEqual(true);

    suggestionPool.fill(pollA, uids);
    suggestionPool.fill(pollB, uids);
    expect(suggestionPool.isEmpty(pollA)).toEqual(false);
    expect(suggestionPool.isEmpty(pollB)).toEqual(false);

    suggestionPool.clear();
    expect(suggestionPool.isEmpty(pollA)).toEqual(true);
    expect(suggestionPool.isEmpty(pollB)).toEqual(true);
  });
});
