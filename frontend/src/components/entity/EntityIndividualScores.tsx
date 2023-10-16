import React from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Box, Chip, Avatar, Tooltip } from '@mui/material';

import { useCurrentPoll } from 'src/hooks';
import { ContributorCriteriaScore } from 'src/services/openapi';

export const EntityIndividualScores = ({
  scores,
}: {
  scores?: ContributorCriteriaScore[];
}) => {
  const { t } = useTranslation();

  const { getCriteriaLabel, options } = useCurrentPoll();
  const mainCriterionName = options?.mainCriterionName ?? '';

  let mainCriterionScore: string | undefined;
  if (scores) {
    mainCriterionScore = scores
      .find((score) => score.criteria === mainCriterionName)
      ?.score?.toFixed(0);
  }

  return (
    <Box display="flex" justifyContent="flex-end" pr={1}>
      <Tooltip
        title={getCriteriaLabel(mainCriterionName)}
        placement="top-start"
      >
        <Chip
          size="small"
          variant="outlined"
          avatar={<Avatar alt="sunflower icon" src="/svg/tournesol.svg" />}
          label={
            <Trans t={t} i18nKey="entityIndividualScores.inYourOpinion">
              your view <strong>{{ mainCriterionScore }}</strong>
            </Trans>
          }
        />
      </Tooltip>
    </Box>
  );
};

export default EntityIndividualScores;
