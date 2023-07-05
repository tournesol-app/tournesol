/**
 * Given a language, return true if it matches the preferred language of the
 * user's browser.
 *
 * When the preferred language is 'fr-CA', the following calls return true:
 *
 *    isNavigatorLang('fr')
 *    isNavigatorLang('FR')
 *    isNavigatorLang('fr-CA')
 *    isNavigatorLang('FR-CA')
 *
 * The browser API is expected to return the language indentifier following
 * the RFC 5646.
 *
 * See: https://datatracker.ietf.org/doc/html/rfc5646#section-2.1
 */
export const isNavigatorLang = (lang: string) => {
  const expected = lang.toLowerCase();
  const found = window.navigator.language.toLocaleLowerCase();

  // `expected` can be the shortest ISO 639 code of a language.
  //  Example: 'fr'.
  if (found === expected) {
    return true;
  }

  // The shortest ISO 639 code can be followed by other "subtags" like the
  // region, or the variant. Example: 'fr-CA'.
  if (found.startsWith(expected + '-')) {
    return true;
  }

  return false;
};
