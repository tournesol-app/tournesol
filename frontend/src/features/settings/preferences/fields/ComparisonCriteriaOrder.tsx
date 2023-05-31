import React from 'react';

import { KeyboardArrowDown, KeyboardArrowUp } from '@mui/icons-material';
import { Chip, Grid, IconButton, Typography } from '@mui/material';

import { useTranslation } from 'react-i18next';
import { CriteriaIcon } from 'src/components';
import { CriteriaLabel } from 'src/features/comparisons/CriteriaSlider';


interface ComparisonCriteriaOrderProps {
  criterias: any[];
  onChange: (target: any[]) => void;
}

const ComparisonCriteriaOrderField = ({
  criterias,
  onChange,
}: ComparisonCriteriaOrderProps) => {
  const { t } = useTranslation();

  const tempCriterias = criterias;

  const handleUp = (index: number) => {
    if(index==0)
      return;
    const temp = criterias[index-1];
    tempCriterias[index-1] = criterias[index];
    tempCriterias[index] = temp;
    onChange([...tempCriterias]);
  }

  const handleDown = (index: number) => {
    if(index==criterias.length-1)
      return;
    const temp = criterias[index+1];
    tempCriterias[index+1] = criterias[index];
    tempCriterias[index] = temp;
    onChange([...tempCriterias]);
  }

  return (
    <>
      <Typography paragraph>
        {t('pollUserSettingsForm.criteriaPersonalization')}
      </Typography>
      {criterias.filter((c) => c.optional).map((criteria, index) => (   
        <Grid
          key={index}
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          container
        >
          <Grid item display='flex'>
            <CriteriaIcon
              criteriaName={criteria.name}
              sx={{
                marginRight: '8px',
              }}
            />
            <Typography>
              <CriteriaLabel criteria={criteria.name} criteriaLabel={criteria.label} />
            </Typography>
          </Grid>
          <Grid item display={'flex'}> 
            <IconButton onClick={() => handleUp(index)}>
              <KeyboardArrowUp/>
            </IconButton>
            <IconButton onClick={() => handleDown(index)}>
              <KeyboardArrowDown/>
            </IconButton>
          </Grid>
        </Grid>
      ))}   
    </>
  );
};

export default ComparisonCriteriaOrderField;
