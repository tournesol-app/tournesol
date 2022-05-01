import { uniq } from './array';

describe('uniq', () => {
  const testCases = [
    [['a', 'a'], ['a']],
    [
      ['a', 'b'],
      ['a', 'b'],
    ],
    [['a'], ['a']],
    [
      ['1', 1],
      ['1', 1],
    ],
    [[], []],
  ];

  testCases.forEach(([input, expected]) =>
    it(JSON.stringify(input), () => {
      expect(uniq(input)).toEqual(expected);
    })
  );
});
