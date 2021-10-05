export const mainCriteriaNames: string[][] = [
  ['reliability', 'Reliable & not misleading'],
  ['pedagogy', 'Clear & pedagogical'],
  ['importance', 'Important and actionable'],
  ['layman_friendly', 'Layman-friendly'],
  ['entertaining_relaxing', 'Entertaining and relaxing'],
  ['engaging', 'Engaging & thought-provoking'],
  ['diversity_inclusion', 'Diversity & inclusion'],
  ['better_habits', 'Encourages better habits'],
  ['backfire_risk', 'Resilience to backfiring risks'],
];

export const mainCriteriaNamesObj: { [c: string]: string } =
  Object.fromEntries(mainCriteriaNames);

export const allCriteriaNames: string[][] = [
  ['largely_recommended', 'Should be largely recommended'],
  ...mainCriteriaNames,
];

export const allCriteriaNamesObj: { [c: string]: string } =
  Object.fromEntries(allCriteriaNames);
