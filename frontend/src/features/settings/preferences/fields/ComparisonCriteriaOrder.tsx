import React from 'react';

import { KeyboardArrowDown, KeyboardArrowUp } from '@mui/icons-material';
import { Grid, IconButton, Typography } from '@mui/material';

import { useTranslation } from 'react-i18next';
import { CriteriaIcon } from 'src/components';
import { CriteriaLabel } from 'src/features/comparisons/CriteriaSlider';
import { useCurrentPoll } from 'src/hooks';

const ComparisonCriteriaOrderField = () => {
  const { t } = useTranslation();
  const { criterias } = useCurrentPoll();

  // const tempCriterias = criterias;

  const handleUp = () => {
    // if (index == 0) return;
    // const temp = criterias[index - 1];
    // tempCriterias[index - 1] = criterias[index];
    // tempCriterias[index] = temp;
    // onChange([...tempCriterias]);
  };

  const handleDown = () => {
    // if (index == criterias.length - 1) return;
    // const temp = criterias[index + 1];
    // tempCriterias[index + 1] = criterias[index];
    // tempCriterias[index] = temp;
    // onChange([...tempCriterias]);
  };

  return (
    <>
      <Typography paragraph>
        {t('pollUserSettingsForm.criteriaPersonalization')}
      </Typography>
      {criterias
        .filter((c) => c.optional)
        .map((criteria, index) => (
          <Grid
            key={index}
            direction="row"
            justifyContent="space-between"
            alignItems="center"
            container
          >
            <Grid item display="flex">
              <CriteriaIcon
                criteriaName={criteria.name}
                sx={{
                  marginRight: '8px',
                }}
              />
              <Typography>
                <CriteriaLabel
                  criteria={criteria.name}
                  criteriaLabel={criteria.label}
                />
              </Typography>
            </Grid>
            <Grid item display={'flex'}>
              <IconButton onClick={() => handleUp()}>
                <KeyboardArrowUp />
              </IconButton>
              <IconButton onClick={() => handleDown()}>
                <KeyboardArrowDown />
              </IconButton>
            </Grid>
          </Grid>
        ))}
    </>
  );
};

export default ComparisonCriteriaOrderField;
