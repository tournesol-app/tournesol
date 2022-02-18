import { availableRecommendationsLanguages } from 'src/utils/constants';
import { uniq } from 'src/utils/array';

export const saveRecommendationsLanguages = (value: string) => {
  localStorage.setItem('recommendationsLanguages', value);
};

export const loadRecommendationsLanguages = (): string | null =>
  localStorage.getItem('recommendationsLanguages');

export const recommendationsLanguagesFromNavigator = (): string =>
  uniq(
    navigator.languages
      .map((languageTag) => languageTag.split('-', 1)[0])
      .filter((language) =>
        availableRecommendationsLanguages.includes(language)
      )
  ).join(',');
