import {
  recommendationsLanguagesFromNavigator,
  saveRecommendationsLanguages,
} from './recommendationsLanguages';

describe('recommendationsLanguagesFromNavigator', () => {
  const testCases = [
    [['en-US', 'en', 'fr-FR'], 'en,fr'],
    [['en', 'de-CH', 'de-DE', 'sq', 'fr-CH', 'fr-FR'], 'en,de,sq,fr'],
    [['de-DE'], 'de'],
    [['es'], 'es'],
    [['ho'], ''],
    [['zh-Hant', 'zh-cmn-Hans-CN', 'sl-rozaj-biske', 'de-CH-1901'], 'sl,de'],
    [['de-CH-x-phonebk'], 'de'],
    [['enInvalidLanguageCode'], ''],
    [[], ''],
  ];

  testCases.forEach(([input, expected]) =>
    it(`converts ${JSON.stringify(input)}`, () => {
      const languagesGetter = vi.spyOn(window.navigator, 'languages', 'get');
      languagesGetter.mockReturnValue(input as string[]);
      expect(recommendationsLanguagesFromNavigator()).toEqual(expected);
    })
  );
});

describe('saveRecommendationsLanguages', () => {
  it('dispatches an event for the extension', () => {
    const eventHandler = vi.fn((event) => {
      const { detail } = event;
      expect(detail).toEqual({ recommendationsLanguages: 'fr,de' });
    });
    document.addEventListener(
      'tournesol:recommendationsLanguagesChange',
      eventHandler
    );

    saveRecommendationsLanguages('fr,de');

    expect(eventHandler).toHaveBeenCalledTimes(1);
  });
});
