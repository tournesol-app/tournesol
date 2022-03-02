import { TFunction } from 'react-i18next';

export const YOUTUBE_POLL_NAME = 'videos';

const UID_DELIMITER = ':';
export const UID_YT_NAMESPACE = 'yt' + UID_DELIMITER;

export const recommendationFilters = {
  date: 'date',
  language: 'language',
  uploader: 'uploader',
  unsafe: 'unsafe',
  reliability: 'reliability',
  pedagogy: 'pedagogy',
  importance: 'importance',
  layman_friendly: 'layman_friendly',
  entertaining_relaxing: 'entertaining_relaxing',
  engaging: 'engaging',
  diversity_inclusion: 'diversity_inclusion',
  better_habits: 'better_habits',
  backfire_risk: 'backfire_risk',
};

export const defaultRecommendationFilters = {
  date: null,
  language: null,
  uploader: null,
  unsafe: null,
  reliability: '50',
  pedagogy: '50',
  importance: '50',
  layman_friendly: '50',
  entertaining_relaxing: '50',
  engaging: '50',
  diversity_inclusion: '50',
  better_habits: '50',
  backfire_risk: '50',
};

// This constant is also defined in the browser extension so it should be updated there too if it changes.
export const availableRecommendationsLanguages = ['en', 'fr', 'de'];

export const getLanguageName = (t: TFunction, language: string) => {
  switch (language) {
    case 'en':
      return t('language.english');
    case 'fr':
      return t('language.french');
    case 'de':
      return t('language.german');
    default:
      return language.toUpperCase();
  }
};

export const polls = [
  /*
    The most specific paths should be listed first,
    to be routed correctly.
  */
  // {
  //   name: 'presidentielle',
  //   path: '/presidentielle',
  //   withSearchBar: false,
  //   topBarBackground:
  //     'linear-gradient(60deg, #8b8be8 0%, white 33%, #e16767 100%)',
  // },
  {
    name: YOUTUBE_POLL_NAME,
    path: '/',
    withSearchBar: true,
    topBarBackground: null,
  },
];
