import { TFunction } from 'react-i18next';
import { recommendationsLanguages } from 'src/utils/constants';
import { uniq } from 'src/utils/array';

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
