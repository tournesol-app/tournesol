import { TFunction } from 'react-i18next';

export const mainCriterias = [
  'reliability',
  'pedagogy',
  'importance',
  'layman_friendly',
  'entertaining_relaxing',
  'engaging',
  'diversity_inclusion',
  'better_habits',
  'backfire_risk',
];

export const allCriterias = ['largely_recommended', ...mainCriterias];

export const optionalCriterias: { [c: string]: boolean } = {
  largely_recommended: false,
  reliability: true,
  pedagogy: true,
  importance: true,
  layman_friendly: true,
  entertaining_relaxing: true,
  engaging: true,
  diversity_inclusion: true,
  better_habits: true,
  backfire_risk: true,
};

export const getCriteriaName = (t: TFunction, criteria: string) => {
  const names: Record<string, () => string> = {
    largely_recommended: () => t('criteria.shouldBeLargelyRecommended'),
    reliability: () => t('criteria.reliableAndNotMisleading'),
    pedagogy: () => t('criteria.clearAndPedagogical'),
    importance: () => t('criteria.importantAndActionable'),
    layman_friendly: () => t('criteria.laymanFriendly'),
    entertaining_relaxing: () => t('criteria.entertainingAndRelaxing'),
    engaging: () => t('criteria.engagingAndThoughtProvoking'),
    diversity_inclusion: () => t('criteria.diversityAndInclusion'),
    better_habits: () => t('criteria.encouragesBetterHabits'),
    backfire_risk: () => t('criteria.resilienceToBackfiringRisks'),
  };
  return names[criteria]?.() ?? '';
};

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
