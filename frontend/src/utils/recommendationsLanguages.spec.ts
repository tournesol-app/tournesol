import { recommendationsLanguagesFromNavigator } from './recommendationsLanguages';

describe('recommendationsLanguagesFromNavigator', () => {
  const testCases = [
    [['en-US', 'en', 'fr-FR'], 'en,fr'],
    [['en', 'de-CH', 'de-DE', 'sq', 'fr-CH', 'fr-FR'], 'en,de,fr'],
    [['de-DE'], 'de'],
    [['es'], ''],
    [['zh-Hant', 'zh-cmn-Hans-CN', 'sl-rozaj-biske', 'de-CH-1901'], 'de'],
    [['de-CH-x-phonebk'], 'de'],
    [['enInvalidLanguageCode'], ''],
    [[], ''],
  ];

  testCases.forEach(([input, expected]) =>
    it(`converts ${JSON.stringify(input)}`, () => {
      const languagesGetter = jest.spyOn(window.navigator, 'languages', 'get');
      languagesGetter.mockReturnValue(input as string[]);
      expect(recommendationsLanguagesFromNavigator()).toEqual(expected);
    })
  );
});
