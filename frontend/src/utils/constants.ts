import { TFunction } from 'react-i18next';
import { YouTube } from '@mui/icons-material';
import { SelectablePoll } from './types';

export const YOUTUBE_POLL_NAME = 'videos';
export const PRESIDENTIELLE_2022_POLL_NAME = 'presidentielle2022';

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

export const getPollName = (t: TFunction, pollName: string) => {
  switch (pollName) {
    case PRESIDENTIELLE_2022_POLL_NAME:
      return t('poll.presidential2022');
    case YOUTUBE_POLL_NAME:
      return t('poll.videos');
    default:
      return pollName;
  }
};

export const getEntityName = (t: TFunction, pollName: string) => {
  switch (pollName) {
    case PRESIDENTIELLE_2022_POLL_NAME:
      return t('poll.entityCandidate');
    case YOUTUBE_POLL_NAME:
      return t('poll.entityVideo');
    default:
      return pollName;
  }
};

/*
  The most specific paths should be listed first,
  to be routed correctly.
*/
export const polls: Array<SelectablePoll> = [
  /* disable the poll presidentielle2022 for now
     as it doesn't exist in the back end
  {
    name: PRESIDENTIELLE_2022_POLL_NAME,
    displayOrder: 20,
    path: '/presidentielle2022/',
    disabledRouteIds: [RouteID.MyRateLaterList],
    iconComponent: HowToVote,
    withSearchBar: false,
    topBarBackground:
      'linear-gradient(60deg, #8b8be8 0%, white 33%, #e16767 100%)',
  },
  */
  {
    name: YOUTUBE_POLL_NAME,
    displayOrder: 10,
    path: '/',
    iconComponent: YouTube,
    withSearchBar: true,
    topBarBackground: null,
    tutorialLength: 7,
  },
];
