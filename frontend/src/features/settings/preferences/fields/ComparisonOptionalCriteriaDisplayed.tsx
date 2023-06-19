import React from 'react';
import { useTranslation } from 'react-i18next';

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

import { CriteriaIcon } from 'src/components';
import { useCurrentPoll } from 'src/hooks';

const OrderableCriterionRow = ({
  index,
  checked,
  criterionName,
  criterionLabel,
  selectedCriteria,
  handleUp,
  handleDown,
  setCheckedCriteria,
}: {
  index: number;
  checked: boolean;
  criterionName: string;
  criterionLabel: string;
  selectedCriteria: string[];
  handleUp: (index: number) => void;
  handleDown: (index: number) => void;
  setCheckedCriteria: (target: string[]) => void;
}) => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const handleCheck = () => {
    const newSelection = [...selectedCriteria];

    if (checked) {
      const index = selectedCriteria.indexOf(criterionName);
      if (index === -1) return;

      newSelection.splice(index, 1);
      setCheckedCriteria(newSelection);
    } else {
      if (selectedCriteria.includes(criterionName)) return;

      newSelection.push(criterionName);
      setCheckedCriteria(newSelection);
    }
  };

  return (
    <Grid
      container
      direction="row"
      alignItems="center"
      justifyContent="space-between"
      wrap="nowrap"
    >
      <Grid item display="flex" alignItems="center">
        <Checkbox
          id={`id_selected_optional_${criterionName}`}
          checked={checked}
          onChange={handleCheck}
          size="small"
          color="secondary"
          sx={{ pl: 0, pr: 2 }}
        />
        <CriteriaIcon criteriaName={criterionName} sx={{ marginRight: 1 }} />
        <Typography>{criterionLabel}</Typography>
      </Grid>
      {checked && (
        <Grid item display="flex" flexWrap="nowrap">
          <IconButton
            aria-label={`${t(
              'pollUserSettingsForm.moveTheFollowingCriterionUp'
            )} ${criterionLabel}`}
            data-testid={`${pollName}_move_criterion_up_${criterionName}`}
            onClick={() => handleUp(index)}
            disabled={index <= 0}
          >
            <KeyboardArrowUp />
          </IconButton>
          <IconButton
            aria-label={`${t(
              'pollUserSettingsForm.moveTheFollowingCriterionDown'
            )} ${criterionLabel}`}
            data-testid={`${pollName}_move_criterion_down_${criterionName}`}
            onClick={() => handleDown(index)}
            disabled={index >= selectedCriteria.length - 1}
          >
            <KeyboardArrowDown />
          </IconButton>
        </Grid>
      )}
    </Grid>
  );
};

const ComparisonOptionalCriteriaDisplayed = ({
  displayedCriteria,
  onChange,
}: {
  displayedCriteria: string[];
  onChange: (target: string[]) => void;
}) => {
  const { t } = useTranslation();
  const { criterias } = useCurrentPoll();

  const moveUp = (index: number) => {
    if (index <= 0) return;
    const newSelection = [...displayedCriteria];

    const selectedCriterion = newSelection[index];
    const opponent = newSelection[index - 1];

    newSelection[index - 1] = selectedCriterion;
    newSelection[index] = opponent;
    onChange(newSelection);
  };

  const moveDown = (index: number) => {
    if (index >= displayedCriteria.length - 1) return;
    const newSelection = [...displayedCriteria];

    const selectedCriterion = newSelection[index];
    const opponent = newSelection[index + 1];

    newSelection[index] = opponent;
    newSelection[index + 1] = selectedCriterion;
    onChange(newSelection);
  };

  return (
    <Grid flexDirection="row" container spacing={2}>
      <Grid item xs={12}>
        <Typography paragraph mb={0}>
          <strong>
            {t('pollUserSettingsForm.selectTheCriteriaYouWantToDisplay')}
          </strong>
        </Typography>
      </Grid>
      <Grid
        item
        xs={12}
        sm={12}
        md={12}
        lg={6}
        minHeight={{ xs: 'initial', sm: 410 }}
      >
        <Box mb={1}>
          <Typography>{t('pollUserSettingsForm.optionalCriteria')}</Typography>
          <Divider />
        </Box>
        <Box display="flex" flexDirection="column" gap={{ xs: 2, sm: 0 }}>
          {criterias
            .filter((c) => !displayedCriteria.includes(c.name) && c.optional)
            .map((criterion, index) => (
              <OrderableCriterionRow
                key={criterion.name}
                index={index}
                checked={false}
                criterionName={criterion.name}
                criterionLabel={criterion.label}
                selectedCriteria={displayedCriteria}
                handleUp={moveUp}
                handleDown={moveDown}
                setCheckedCriteria={onChange}
              />
            ))}
        </Box>
        {displayedCriteria.length === criterias.length - 1 && (
          <Alert severity="info">
            <Typography>
              {t('pollUserSettingsForm.optionalCriteriaEmptyText')}
            </Typography>
          </Alert>
        )}
      </Grid>
      <Grid
        item
        xs={12}
        sm={12}
        md={12}
        lg={6}
        minHeight={{ xs: 'initial', sm: 410 }}
      >
        <Box mb={1}>
          <Typography>
            {t('pollUserSettingsForm.alwaysDisplayedCriteria')}
          </Typography>
          <Divider />
        </Box>
        <Box display="flex" flexDirection="column" gap={{ xs: 2, sm: 0 }}>
          {displayedCriteria.map((criterion, index) => (
            <OrderableCriterionRow
              key={criterion}
              index={index}
              checked={true}
              criterionName={criterion}
              criterionLabel={
                criterias.find((c) => c.name === criterion)?.label ?? criterion
              }
              selectedCriteria={displayedCriteria}
              handleDown={moveDown}
              handleUp={moveUp}
              setCheckedCriteria={onChange}
            />
          ))}
        </Box>
        {displayedCriteria.length === 0 && (
          <Alert severity="info">
            <Typography>
              {t('pollUserSettingsForm.alwaysDisplayedCriteriaEmptyText')}
            </Typography>
          </Alert>
        )}
      </Grid>
    </Grid>
  );
};

export default ComparisonOptionalCriteriaDisplayed;
