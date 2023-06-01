import React from 'react';

import { KeyboardArrowDown, KeyboardArrowUp } from '@mui/icons-material';
import { Checkbox, Divider, Grid, IconButton, Typography } from '@mui/material';

import { useTranslation } from 'react-i18next';
import { CriteriaIcon } from 'src/components';
import { CriteriaLabel } from 'src/features/comparisons/CriteriaSlider';
import { useCurrentPoll } from 'src/hooks';
import { PollCriteria } from 'src/services/openapi';

const OrderableCriterionRow = ({
  criterias,
  criteria,
  checkedCriterias,
  handleUp,
  handleDown,
  setCheckedCriterias,
}: {
  criterias: PollCriteria[];
  criteria: string | PollCriteria;
  checkedCriterias: string[];
  handleUp: () => void;
  handleDown: () => void;
  setCheckedCriterias: (target: string[]) => void;
}) => {
  const criteriaIsString = typeof criteria === 'string';

  const handleCheck = () => {
    if (criteriaIsString) {
      const index = checkedCriterias.indexOf(criteria);
      checkedCriterias.splice(index, 1);
      setCheckedCriterias([...checkedCriterias]);
    } else {
      checkedCriterias.push(criteria.name);
      setCheckedCriterias([...checkedCriterias]);
    }
  };

  return (
    <Grid
      direction="row"
      justifyContent="space-between"
      alignItems="center"
      container
    >
      <Grid item display="flex" alignItems={'center'}>
        <Checkbox
          id={`id_checkbox_skip_${criteria}`}
          size="small"
          checked={criteriaIsString}
          onChange={handleCheck}
          color="secondary"
          sx={{
            pr: 2,
          }}
        />
        <CriteriaIcon
          criteriaName={criteriaIsString ? criteria : criteria.name}
          sx={{
            marginRight: '8px',
          }}
        />
        <Typography>
          <CriteriaLabel
            criteria={criteriaIsString ? criteria : criteria.name}
            criteriaLabel={
              criteriaIsString
                ? criterias.find((c) => c.name == criteria)?.label ?? criteria
                : criteria.label
            }
          />
        </Typography>
      </Grid>
      {criteriaIsString && (
        <Grid item display={'flex'}>
          <IconButton onClick={() => handleUp()}>
            <KeyboardArrowUp />
          </IconButton>
          <IconButton onClick={() => handleDown()}>
            <KeyboardArrowDown />
          </IconButton>
        </Grid>
      )}
    </Grid>
  );
};

const ComparisonCriteriaOrderField = ({
  checkedCriterias,
  setCheckedCriterias,
}: {
  checkedCriterias: string[];
  setCheckedCriterias: (target: string[]) => void;
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
      {checkedCriterias.map((criteria) => (
        <OrderableCriterionRow
          key={criteria}
          criteria={criteria}
          criterias={criterias}
          checkedCriterias={checkedCriterias}
          handleDown={handleDown}
          handleUp={handleUp}
          setCheckedCriterias={setCheckedCriterias}
        />
      ))}
      <Divider />
      {criterias
        .filter((c) => !checkedCriterias.includes(c.name) && c.optional)
        .map((criteria) => (
          <OrderableCriterionRow
            key={criteria.name}
            criteria={criteria}
            criterias={criterias}
            checkedCriterias={checkedCriterias}
            handleDown={handleDown}
            handleUp={handleUp}
            setCheckedCriterias={setCheckedCriterias}
          />
        ))}
    </>
  );
};

export default ComparisonCriteriaOrderField;
