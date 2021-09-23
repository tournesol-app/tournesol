const mainCriteriaNames: { [s: string]: string } = {
  reliability: 'Reliable & not misleading',
  pedagogy: 'Clear & pedagogical',
  importance: 'Important and actionable',
  layman_friendly: 'Layman-friendly',
  entertaining_relaxing: 'Entertaining and relaxing',
  engaging: 'Engaging & thought-provoking',
  diversity_inclusion: 'Diversity & inclusion',
  better_habits: 'Encourages better habits',
  backfire_risk: 'Resilience to backfiring risks',
};

const allCriteriaNames = { ...mainCriteriaNames };
allCriteriaNames['largely_recommended'] = 'Should be largely recommended';

export { mainCriteriaNames, allCriteriaNames };
