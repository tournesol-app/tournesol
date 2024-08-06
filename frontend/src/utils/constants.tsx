import { TFunction } from 'react-i18next';
import { YouTube, HowToVote } from '@mui/icons-material';

import { AddToRateLaterList, CompareNowAction } from './action';
import {
  getAllCandidates,
  getTutorialDialogs as getPresidentielleTutorialDialogs,
} from './polls/presidentielle2022';
import {
  getTutorialVideos,
  getTutorialTips as getVideosTutorialTips,
  getTutorialDialogs as getVideosTutorialDialogs,
  getTutorialDialogActions as getVideosTutorialDialogActions,
} from './polls/videos';
import { SelectablePoll, RouteID } from './types';

export const YOUTUBE_POLL_NAME = 'videos';
export const PRESIDENTIELLE_2022_POLL_NAME = 'presidentielle2022';
const PRESIDENTIELLE_2022_ENABLED =
  import.meta.env.REACT_APP_POLL_PRESIDENTIELLE_2022_ENABLED === 'true';

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

/**
 * Return the translated name of a metadata.
 */
export function getMetadataName(
  t: TFunction,
  pollName: string,
  metadata: string
): string | undefined {
  let name;

  switch (pollName) {
    case YOUTUBE_POLL_NAME:
      switch (metadata) {
        case 'duration':
          name = t('videoMetadata.duration');
          break;
        case 'publication_date':
          name = t('videoMetadata.publication_date');
          break;
      }
      break;
  }

  return name;
}

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

/**
 * User settings.
 *
 * As the back end doesn't provide the default values of the user settings, we
 * define here the default values that should be used by the front end. In an
 * ideal world they always match the default values used by the back end.
 */

export const DEFAULT_RATE_LATER_AUTO_REMOVAL = 4;

export const YT_DEFAULT_AUTO_SELECT_ENTITIES = true;

export const YT_DEFAULT_UI_WEEKLY_COL_GOAL_MOBILE = false;

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
          disabledRouteIds: [
            RouteID.MyRateLaterList,
            RouteID.MyComparedItems,
            RouteID.Criteria,
          ],
          iconComponent: HowToVote,
          withSearchBar: false,
          topBarBackground:
            'linear-gradient(60deg, #8b8be8 0%, white 33%, #e16767 100%)',
          tutorialLength: 7,
          tutorialAlternatives: getAllCandidates,
          tutorialDialogs: getPresidentielleTutorialDialogs,
          tutorialRedirectTo: '/personal/feedback',
          tutorialKeepUIDsAfterRedirect: false,
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
    autoFillEmptySelectors: YT_DEFAULT_AUTO_SELECT_ENTITIES,
    extraMetadataOrderBy: ['duration', 'publication_date'],
    tutorialLength: 4,
    tutorialAlternatives: getTutorialVideos,
    tutorialDialogs: getVideosTutorialDialogs,
    tutorialDialogActions: getVideosTutorialDialogActions,
    tutorialTips: getVideosTutorialTips,
    tutorialRedirectTo: '/comparison',
    tutorialKeepUIDsAfterRedirect: true,
  },
];

export const LAST_POLL_NAME_STORAGE_KEY = 'last_poll_name';

export const PRESIDENTIELLE_2022_SURVEY_URL =
  'https://docs.google.com/forms/d/e/1FAIpQLScNUUKaapn0z6N64au-6YcFxAoViAyvbl53sZswYsWzDasHpw/viewform';
