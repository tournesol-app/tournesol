import React from 'react';

import { KeyboardArrowDown, KeyboardArrowUp } from '@mui/icons-material';
import { Checkbox, Grid, IconButton, Typography } from '@mui/material';

import { useTranslation } from 'react-i18next';
import { CriteriaIcon } from 'src/components';
import { CriteriaLabel } from 'src/features/comparisons/CriteriaSlider';
import { useCurrentPoll } from 'src/hooks';

const ComparisonCriteriaOrderField = ({
  checkedCriterias,
}: {
  checkedCriterias: string[];
}) => {
  const { t } = useTranslation();
  const { criterias } = useCurrentPoll();

  const handleUp = () => {
    return;
  };
  const handleDown = () => {
    return;
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
            <Grid item display="flex" alignItems={'center'}>
              <Checkbox
                id={`id_checkbox_skip_${criteria}`}
                size="small"
                checked={checkedCriterias.includes(criteria.name)}
                color="secondary"
                sx={{
                  pr: 2,
                }}
              />
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
