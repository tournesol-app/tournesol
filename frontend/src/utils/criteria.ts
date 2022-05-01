import { criteriaToEmoji } from 'src/utils/constants';

export const displayScore = (score: number) => (10 * score).toFixed(1);

export const criteriaIcon = (criteriaName: string) => {
  const emoji =
    criteriaName in criteriaToEmoji ? criteriaToEmoji[criteriaName] : undefined;
  const imagePath =
    criteriaName === 'largely_recommended'
      ? '/svg/LogoSmall.svg'
      : `/svg/${criteriaName}.svg`;
  return { emoji, imagePath };
};
