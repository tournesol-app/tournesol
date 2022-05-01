import { snakeToCamel } from './string';

describe('snake_case to camelCase conversion', () => {
  const testCases = [
    ['abc', 'abc'],
    ['long_key', 'longKey'],
    ['_abc', '_abc'],
    ['_long_key', '_longKey'],
    ['largely_recommended', 'largelyRecommended'],
  ];

  testCases.forEach(([input, expected]) =>
    it(input, () => {
      expect(snakeToCamel(input)).toEqual(expected);
    })
  );
});
