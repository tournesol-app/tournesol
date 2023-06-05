import React from 'react';

import { KeyboardArrowDown, KeyboardArrowUp } from '@mui/icons-material';
import {
  Alert,
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
  criteria,
  criterion,
  checkedCriteria,
  index,
  handleUp,
  handleDown,
  setCheckedCriteria,
}: {
  criteria: PollCriteria[];
  criterion: string | PollCriteria;
  checkedCriteria: string[];
  index: number;
  handleUp: (index: number) => void;
  handleDown: (index: number) => void;
  setCheckedCriteria: (target: string[]) => void;
}) => {
  const criterionIsString = typeof criterion === 'string';

  const handleCheck = () => {
    const tempCheckedCriteria = [...checkedCriteria];
    if (criterionIsString) {
      const index = tempCheckedCriteria.indexOf(criterion);
      tempCheckedCriteria.splice(index, 1);
      setCheckedCriteria(tempCheckedCriteria);
    } else {
      tempCheckedCriteria.push(criterion.name);
      setCheckedCriteria(tempCheckedCriteria);
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
          id={`id_checkbox_skip_${criterion}`}
          size="small"
          checked={criterionIsString}
          onChange={handleCheck}
          color="secondary"
          sx={{
            pr: 2,
          }}
        />
        <CriteriaIcon
          criteriaName={criterionIsString ? criterion : criterion.name}
          sx={{
            marginRight: '8px',
          }}
        />
        <Typography>
          <CriteriaLabel
            criteria={criterionIsString ? criterion : criterion.name}
            criteriaLabel={
              criterionIsString
                ? criteria.find((c) => c.name == criterion)?.label ?? criterion
                : criterion.label
            }
            tooltip={false}
          />
        </Typography>
      </Grid>
      {criterionIsString && (
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
  checkedCriteria,
  setCheckedCriteria,
}: {
  checkedCriteria: string[];
  setCheckedCriteria: (target: string[]) => void;
}) => {
  const { t } = useTranslation();
  const { criterias } = useCurrentPoll();

  const handleUp = (index: number) => {
    if (index === 0) return;
    const tempCheckedCriteria = [...checkedCriteria];
    const tempCriterion = tempCheckedCriteria[index];
    tempCheckedCriteria[index] = tempCheckedCriteria[index - 1];
    tempCheckedCriteria[index - 1] = tempCriterion;
    setCheckedCriteria(tempCheckedCriteria);
  };
  const handleDown = (index: number) => {
    if (index === checkedCriteria.length - 1) return;
    const tempCheckedCriteria = [...checkedCriteria];
    const tempCriterion = tempCheckedCriteria[index];
    tempCheckedCriteria[index] = tempCheckedCriteria[index + 1];
    tempCheckedCriteria[index + 1] = tempCriterion;
    setCheckedCriteria(tempCheckedCriteria);
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
        {checkedCriteria.map((criterion, index) => (
          <OrderableCriterionRow
            key={criterion}
            criterion={criterion}
            criteria={criterias}
            checkedCriteria={checkedCriteria}
            index={index}
            handleDown={handleDown}
            handleUp={handleUp}
            setCheckedCriteria={setCheckedCriteria}
          />
        ))}
        {checkedCriteria.length === 0 && (
          <Alert severity="info">
            <Typography>
              {t('pollUserSettingsForm.displayedCriteriaEmpty')}
            </Typography>
          </Alert>
        )}
      </Grid>
      <Grid item xs={6}>
        <Box mt={2} mb={1}>
          <Typography>{t('pollUserSettingsForm.optionalCriteria')}</Typography>
          <Divider />
        </Box>
        {criterias
          .filter((c) => !checkedCriteria.includes(c.name) && c.optional)
          .map((criterion, index) => (
            <OrderableCriterionRow
              key={criterion.name}
              criterion={criterion}
              criteria={criterias}
              checkedCriteria={checkedCriteria}
              index={index}
              handleDown={handleDown}
              handleUp={handleUp}
              setCheckedCriteria={setCheckedCriteria}
            />
          ))}
        {checkedCriteria.length === criterias.length - 1 && (
          <Alert severity="info">
            <Typography>
              {t('pollUserSettingsForm.optionalCriteriaEmpty')}
            </Typography>
          </Alert>
        )}
      </Grid>
    </Grid>
  );
};

export default ComparisonCriteriaOrderField;
