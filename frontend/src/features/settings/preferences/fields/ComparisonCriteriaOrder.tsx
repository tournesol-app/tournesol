import React from 'react';

import { KeyboardArrowDown, KeyboardArrowUp } from '@mui/icons-material';
import {
  Box,
  Checkbox,
  Divider,
  Grid,
  IconButton,
  Typography,
} from '@mui/material';

import { useTranslation } from 'react-i18next';
import { CriteriaIcon } from 'src/components';
import { CriteriaLabel } from 'src/features/comparisons/CriteriaSlider';
import { useCurrentPoll } from 'src/hooks';
import { PollCriteria } from 'src/services/openapi';

const OrderableCriterionRow = ({
  criterias,
  criteria,
  checkedCriterias,
  index,
  handleUp,
  handleDown,
  setCheckedCriterias,
}: {
  criterias: PollCriteria[];
  criteria: string | PollCriteria;
  checkedCriterias: string[];
  index: number;
  handleUp: (index: number) => void;
  handleDown: (index: number) => void;
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
          <IconButton onClick={() => handleUp(index)}>
            <KeyboardArrowUp />
          </IconButton>
          <IconButton onClick={() => handleDown(index)}>
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

  const handleUp = (index: number) => {
    if (index === 0) return;
    const tempCriteria = checkedCriterias[index];
    checkedCriterias[index] = checkedCriterias[index - 1];
    checkedCriterias[index - 1] = tempCriteria;
    setCheckedCriterias([...checkedCriterias]);
  };
  const handleDown = (index: number) => {
    if (index === checkedCriterias.length - 1) return;
    const tempCriteria = checkedCriterias[index];
    checkedCriterias[index] = checkedCriterias[index + 1];
    checkedCriterias[index + 1] = tempCriteria;
    setCheckedCriterias([...checkedCriterias]);
  };

  return (
    <Grid flexDirection="row-reverse" container columnSpacing={5}>
      <Grid item xs={12}>
        <Typography paragraph>
          <strong>{t('pollUserSettingsForm.criteriaPersonalization')}</strong>
        </Typography>
      </Grid>
      <Grid item xs={6}>
        <Box mt={2} mb={1}>
          <Typography>{t('pollUserSettingsForm.displayedCriteria')}</Typography>
          <Divider />
        </Box>
        {checkedCriterias.map((criteria, index) => (
          <OrderableCriterionRow
            key={criteria}
            criteria={criteria}
            criterias={criterias}
            checkedCriterias={checkedCriterias}
            index={index}
            handleDown={handleDown}
            handleUp={handleUp}
            setCheckedCriterias={setCheckedCriterias}
          />
        ))}
      </Grid>
      <Grid item xs={6}>
        <Box mt={2} mb={1}>
          <Typography>{t('pollUserSettingsForm.optionalCriteria')}</Typography>
          <Divider />
        </Box>
        {criterias
          .filter((c) => !checkedCriterias.includes(c.name) && c.optional)
          .map((criteria, index) => (
            <OrderableCriterionRow
              key={criteria.name}
              criteria={criteria}
              criterias={criterias}
              checkedCriterias={checkedCriterias}
              index={index}
              handleDown={handleDown}
              handleUp={handleUp}
              setCheckedCriterias={setCheckedCriterias}
            />
          ))}
      </Grid>
    </Grid>
  );
};

export default ComparisonCriteriaOrderField;
