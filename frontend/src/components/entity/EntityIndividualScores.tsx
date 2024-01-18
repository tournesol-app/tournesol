import React from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Box, Chip } from '@mui/material';

import { useCurrentPoll } from 'src/hooks';
import { ContributorCriteriaScore } from 'src/services/openapi';
import TournesolScore from './TournesolScore';

/**
 * Display a list of MUI Chip representing individual scores.
 *
 * Only the main criterion is supported for now.
 */
export const EntityIndividualScores = ({
  scores,
}: {
  scores?: ContributorCriteriaScore[];
}) => {
  const { t } = useTranslation();

  const { getCriteriaLabel, options } = useCurrentPoll();
  const mainCriterionName = options?.mainCriterionName ?? '';

  let mainCriterionScore: number | undefined;
  if (scores) {
    mainCriterionScore = scores.find(
      (score) => score.criteria === mainCriterionName
    )?.score;
  }

  if (mainCriterionScore == undefined) {
    return <></>;
  }

  return (
    <Chip
      size="small"
      variant="outlined"
      sx={{
        fontSize: '0.8125em',
      }}
      label={
        <Box display="flex" columnGap="2px">
          <Trans t={t} i18nKey="entityIndividualScores.inYourOpinion">
            in your opinion
            <TournesolScore
              score={mainCriterionScore}
              tooltip={getCriteriaLabel(mainCriterionName)}
            />
          </Trans>
        </Box>
      }
    />
  );
};

export default EntityIndividualScores;
