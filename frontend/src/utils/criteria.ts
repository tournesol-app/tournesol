import { criteriaToEmoji } from 'src/utils/constants';

export const criteriaIcon = (criteriaName: string) => {
  const emoji =
    criteriaName in criteriaToEmoji ? criteriaToEmoji[criteriaName] : undefined;
  const imagePath =
    criteriaName === 'largely_recommended'
      ? '/svg/LogoSmall.svg'
      : `/images/criteriaIcons/${criteriaName}.svg`;
  return { emoji, imagePath };
};

const criterionColors: { [criteria: string]: string } = {
  largely_recommended: '#ffc800',
  reliability: '#4F77DD',
  importance: '#DC8A5D',
  engaging: '#DFC642',
  pedagogy: '#C28BED',
  layman_friendly: '#4BB061',
  diversity_inclusion: '#76C6CB',
  backfire_risk: '#D37A80',
  better_habits: '#9DD654',
  entertaining_relaxing: '#D8B36D',
};

export const criterionColor = (criterion: string) =>
  criterionColors[criterion] || '#506ad4';
