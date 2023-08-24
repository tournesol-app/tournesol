import { TFunction } from 'react-i18next';
import { uniq } from 'src/utils/array';

export const recommendationsLanguages: {
  [language: string]: (t: TFunction) => string;
} = {
  // This list should contain all the languages that may appear in the backend entities.
  // It currently contains all the languages detected by langdetect except Chinese because
  // it hasn't been decided how to handle the variants.
  //
  // Translation keys must be string literals without interpolation so that i18next-parser can extract them.
  //
  // The list of these language codes is also present in the browser extension (`availableRecommendationsLanguages`)
  // so it must be updated there too if it changes here.
  //
  af: (t: TFunction) => t('language.af'),
  ar: (t: TFunction) => t('language.ar'),
  bg: (t: TFunction) => t('language.bg'),
  bn: (t: TFunction) => t('language.bn'),
  ca: (t: TFunction) => t('language.ca'),
  cs: (t: TFunction) => t('language.cs'),
  cy: (t: TFunction) => t('language.cy'),
  da: (t: TFunction) => t('language.da'),
  de: (t: TFunction) => t('language.de'),
  el: (t: TFunction) => t('language.el'),
  en: (t: TFunction) => t('language.en'),
  es: (t: TFunction) => t('language.es'),
  et: (t: TFunction) => t('language.et'),
  fa: (t: TFunction) => t('language.fa'),
  fi: (t: TFunction) => t('language.fi'),
  fr: (t: TFunction) => t('language.fr'),
  gu: (t: TFunction) => t('language.gu'),
  he: (t: TFunction) => t('language.he'),
  hi: (t: TFunction) => t('language.hi'),
  hr: (t: TFunction) => t('language.hr'),
  hu: (t: TFunction) => t('language.hu'),
  id: (t: TFunction) => t('language.id'),
  it: (t: TFunction) => t('language.it'),
  ja: (t: TFunction) => t('language.ja'),
  kn: (t: TFunction) => t('language.kn'),
  ko: (t: TFunction) => t('language.ko'),
  lt: (t: TFunction) => t('language.lt'),
  lv: (t: TFunction) => t('language.lv'),
  mk: (t: TFunction) => t('language.mk'),
  ml: (t: TFunction) => t('language.ml'),
  mr: (t: TFunction) => t('language.mr'),
  ne: (t: TFunction) => t('language.ne'),
  nl: (t: TFunction) => t('language.nl'),
  no: (t: TFunction) => t('language.no'),
  pa: (t: TFunction) => t('language.pa'),
  pl: (t: TFunction) => t('language.pl'),
  pt: (t: TFunction) => t('language.pt'),
  ro: (t: TFunction) => t('language.ro'),
  ru: (t: TFunction) => t('language.ru'),
  sk: (t: TFunction) => t('language.sk'),
  sl: (t: TFunction) => t('language.sl'),
  so: (t: TFunction) => t('language.so'),
  sq: (t: TFunction) => t('language.sq'),
  sv: (t: TFunction) => t('language.sv'),
  sw: (t: TFunction) => t('language.sw'),
  ta: (t: TFunction) => t('language.ta'),
  te: (t: TFunction) => t('language.te'),
  th: (t: TFunction) => t('language.th'),
  tl: (t: TFunction) => t('language.tl'),
  tr: (t: TFunction) => t('language.tr'),
  uk: (t: TFunction) => t('language.uk'),
  ur: (t: TFunction) => t('language.ur'),
  vi: (t: TFunction) => t('language.vi'),
};

export const availableRecommendationsLanguages = Object.keys(
  recommendationsLanguages
);

export const getLanguageName = (t: TFunction, language: string) => {
  const labelFunction = recommendationsLanguages[language];
  if (labelFunction === undefined) return language.toUpperCase();
  return labelFunction(t);
};

export const saveRecommendationsLanguages = (value: string) => {
  localStorage.setItem('recommendationsLanguages', value);
  const event = new CustomEvent('tournesol:recommendationsLanguagesChange', {
    detail: { recommendationsLanguages: value },
  });
  document.dispatchEvent(event);
};

export const initRecommendationsLanguages = (): string => {
  const languages = loadRecommendationsLanguages();

  if (languages === null) {
    return recommendationsLanguagesFromNavigator();
  }

  return languages;
};

export const loadRecommendationsLanguages = (): string | null =>
  localStorage.getItem('recommendationsLanguages');

export const recommendationsLanguagesFromNavigator = (): string =>
  // This function also exists in the browser extension so it should be updated there too if it changes here.
  uniq(
    navigator.languages
      .map((languageTag) => languageTag.split('-', 1)[0])
      .filter((language) =>
        availableRecommendationsLanguages.includes(language)
      )
  ).join(',');
