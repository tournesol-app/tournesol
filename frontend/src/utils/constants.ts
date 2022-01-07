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
