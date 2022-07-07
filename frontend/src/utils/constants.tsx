import { TFunction } from 'react-i18next';
import { YouTube, HowToVote } from '@mui/icons-material';

import { AddToRateLaterList, CompareNowAction } from './action';
import {
  getAllCandidates,
  getTutorialDialogs as getPresidentielleTutorialDialogs,
} from './polls/presidentielle2022';
import {
  getTutorialVideos,
  getTutorialDialogs as getVideosTutorialDialogs,
} from './polls/videos';
import { SelectablePoll, RouteID } from './types';

export const YOUTUBE_POLL_NAME = 'videos';
export const PRESIDENTIELLE_2022_POLL_NAME = 'presidentielle2022';
const PRESIDENTIELLE_2022_ENABLED =
  process.env.REACT_APP_POLL_PRESIDENTIELLE_2022_ENABLED === 'true';

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

export const criteriaToEmoji: Record<string, string> = {
  be_president: '🇫🇷',
  energy_environment: '🌳',
  international: '🌍',
  education_culture: '🎓',
  health: '🏥',
  institutions_democracy: '🗳️',
  labour_economy: '🏦',
  solidarity: '🤝',
};

export const getCriteriaTooltips = (t: TFunction, criteria: string) => {
  return {
    // presidentielle2022
    energy_environment: t('criteriaTooltips.energy_environment'),
    international: t('criteriaTooltips.international'),
    education_culture: t('criteriaTooltips.education_culture'),
    health: t('criteriaTooltips.health'),
    institutions_democracy: t('criteriaTooltips.institutions_democracy'),
    labour_economy: t('criteriaTooltips.labour_economy'),
    solidarity: t('criteriaTooltips.solidarity'),
    // videos
    pedagogy: t('criteriaTooltips.pedagogy'),
    importance: t('criteriaTooltips.importance'),
    layman_friendly: t('criteriaTooltips.layman_friendly'),
    entertaining_relaxing: t('criteriaTooltips.entertaining_relaxing'),
    engaging: t('criteriaTooltips.engaging'),
    diversity_inclusion: t('criteriaTooltips.diversity_inclusion'),
    better_habits: t('criteriaTooltips.better_habits'),
    backfire_risk: t('criteriaTooltips.backfire_risk'),
    reliability: t('criteriaTooltips.reliability'),
  }[criteria];
};

export const criteriaLinks: Record<string, string> = {
  reliability: 'https://wiki.tournesol.app/wiki/Reliable_and_not_misleading',
  pedagogy: 'https://wiki.tournesol.app/wiki/Clear_and_pedagogical',
  importance: 'https://wiki.tournesol.app/wiki/Important_and_actionable',
  layman_friendly: 'https://wiki.tournesol.app/wiki/Layman-friendly',
  entertaining_relaxing:
    'https://wiki.tournesol.app/wiki/Entertaining_and_relaxing',
  engaging: 'https://wiki.tournesol.app/wiki/Engaging_and_thought-provoking',
  diversity_inclusion:
    'https://wiki.tournesol.app/wiki/Diversity_and_inclusion',
  better_habits: 'https://wiki.tournesol.app/wiki/Encourages_better_habits',
  backfire_risk:
    'https://wiki.tournesol.app/wiki/Resilience_to_backfiring_risks',
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

export const getRecommendationPageName = (
  t: TFunction,
  pollName: string,
  personal?: boolean
) => {
  switch (pollName) {
    case PRESIDENTIELLE_2022_POLL_NAME:
      return t('recommendationsPage.title.results');
    default:
      if (personal) {
        return t('recommendationsPage.title.personalRecommendations');
      }
      return t('recommendationsPage.title.recommendations');
  }
};

/*
  The most specific paths should be listed first,
  to be routed correctly.
*/
export const polls: Array<SelectablePoll> = [
  ...(PRESIDENTIELLE_2022_ENABLED
    ? [
        {
          name: PRESIDENTIELLE_2022_POLL_NAME,
          defaultAuthEntityActions: [CompareNowAction],
          defaultAnonEntityActions: [],
          displayOrder: 20,
          mainCriterionName: 'be_president',
          path: '/presidentielle2022/',
          disabledRouteIds: [RouteID.MyRateLaterList, RouteID.MyComparedItems],
          iconComponent: HowToVote,
          withSearchBar: false,
          topBarBackground:
            'linear-gradient(60deg, #8b8be8 0%, white 33%, #e16767 100%)',
          tutorialLength: 7,
          tutorialAlternatives: getAllCandidates,
          tutorialDialogs: getPresidentielleTutorialDialogs,
          tutorialRedirectTo: '/personal/feedback',
          unsafeDefault: true,
        },
      ]
    : []),
  {
    name: YOUTUBE_POLL_NAME,
    defaultAuthEntityActions: [CompareNowAction, AddToRateLaterList],
    defaultAnonEntityActions: [],
    defaultRecoLanguageDiscovery: true,
    defaultRecoSearchParams: 'date=Month',
    allowPublicPersonalRecommendations: true,
    mainCriterionName: 'largely_recommended',
    displayOrder: 10,
    path: '/',
    disabledRouteIds: [RouteID.MyFeedback],
    iconComponent: YouTube,
    withSearchBar: true,
    topBarBackground: null,
    comparisonsCanBePublic: true,
    tutorialLength: 4,
    tutorialAlternatives: getTutorialVideos,
    tutorialDialogs: getVideosTutorialDialogs,
    tutorialRedirectTo: '/comparisons',
  },
];

export const LAST_POLL_NAME_STORAGE_KEY = 'last_poll_name';

export const PRESIDENTIELLE_2022_SURVEY_URL =
  'https://docs.google.com/forms/d/e/1FAIpQLScNUUKaapn0z6N64au-6YcFxAoViAyvbl53sZswYsWzDasHpw/viewform';
