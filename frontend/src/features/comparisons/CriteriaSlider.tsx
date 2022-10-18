import React from 'react';
import { useTranslation } from 'react-i18next';

import makeStyles from '@mui/styles/makeStyles';
import Typography from '@mui/material/Typography';
import { Box, Slider, Grid, Checkbox, Chip, Tooltip } from '@mui/material';

import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { Link } from '@mui/material';
import { CriteriaIcon } from 'src/components';
import { criteriaLinks, getCriteriaTooltips } from 'src/utils/constants';
import { HelpOutline } from '@mui/icons-material';

const SLIDER_MIN_STEP = -10;
const SLIDER_MAX_STEP = 10;
const SLIDER_STEP = 1;

const useStyles = makeStyles(() => ({
  criteriaContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    marginBottom: '16px',
  },
  sliderContainer: {
    display: 'flex',
    flexDirection: 'row',
    width: '100%',
    alignItems: 'center',
  },
  slider: {
    flex: '1 1 0px',
  },
  criteriaNameDisplay: {
    display: 'flex',
    flexDirection: 'row',
    alignSelf: 'flex-start',
    width: '100%',
  },
}));

type Props = {
  children: React.ReactNode;
  criteria: string;
};

const CriteriaLabelWithTooltip = ({ children, criteria }: Props) => {
  const { t } = useTranslation();
  const tooltip = getCriteriaTooltips(t, criteria) || '';
  const helpIcon = <HelpOutline fontSize="inherit" sx={{}} />;
  return tooltip ? (
    <Tooltip title={tooltip} placement="top">
      <Box component="span" sx={{ cursor: 'help' }}>
        {children} {helpIcon}
      </Box>
    </Tooltip>
  ) : (
    <>{children}</>
  );
};

const CriteriaLabelWithLink = ({ children, criteria }: Props) => {
  return criteriaLinks[criteria] ? (
    <Link
      color="text.secondary"
      href={criteriaLinks[criteria]}
      id={`id_explanation_${criteria}`}
      target="_blank"
      rel="noreferrer"
      underline="hover"
      sx={{ cursor: 'help' }}
    >
      {children}
    </Link>
  ) : (
    <>{children}</>
  );
};

const CriteriaLabel = ({
  criteria,
  criteriaLabel,
}: {
  criteria: string;
  criteriaLabel: string;
}) => {
  return (
    <CriteriaLabelWithTooltip criteria={criteria}>
      <CriteriaLabelWithLink criteria={criteria}>
        {criteriaLabel}
      </CriteriaLabelWithLink>
    </CriteriaLabelWithTooltip>
  );
};

const CriteriaSlider = ({
  criteria,
  criteriaLabel,
  criteriaValue,
  disabled,
  handleSliderChange,
}: {
  criteria: string;
  criteriaLabel: string;
  criteriaValue: number | undefined;
  disabled?: boolean;
  handleSliderChange: (criteria: string, value: number | undefined) => void;
}) => {
  const { t } = useTranslation();
  const classes = useStyles();
  const { criteriaByName } = useCurrentPoll();

  const computeMedian = function (
    min: number,
    max: number,
    step: number
  ): number {
    return (max - min) / (2 * step);
  };

  const neutralPos = computeMedian(
    SLIDER_MIN_STEP,
    SLIDER_MAX_STEP,
    SLIDER_STEP
  );

  return (
    <div
      id={`id_container_criteria_${criteria}`}
      className={classes.criteriaContainer}
      style={{ width: '100%' }}
    >
      <div className={classes.criteriaNameDisplay}>
        <Grid
          item
          xs={12}
          direction="row"
          justifyContent="center"
          alignItems="center"
          flexWrap="nowrap"
          container
        >
          <CriteriaIcon
            criteriaName={criteria}
            sx={{
              marginRight: '8px',
            }}
          />
          <Typography fontSize={{ xs: '90%', sm: '100%' }}>
            <CriteriaLabel criteria={criteria} criteriaLabel={criteriaLabel} />
            {criteriaValue === undefined && (
              <Chip
                component="span"
                size="small"
                label={t('comparison.criteriaSkipped')}
                sx={{ height: '100%', ml: 1 }}
              />
            )}
          </Typography>
          <Box component="span" flexGrow={1} />
          {(criteriaByName[criteria]?.optional ||
            criteriaValue == undefined) && (
            <Checkbox
              id={`id_checkbox_skip_${criteria}`}
              size="small"
              disabled={disabled}
              checked={criteriaValue !== undefined}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                handleSliderChange(criteria, e.target.checked ? 0 : undefined)
              }
              color="secondary"
              sx={{
                padding: 0,
                marginLeft: '8px',
              }}
            />
          )}
        </Grid>
      </div>
      <div className={classes.sliderContainer}>
        <Slider
          sx={{
            [`& span[data-index="${neutralPos}"].MuiSlider-mark`]: {
              height: '16px',
            },
            '& .MuiSlider-thumb:before': {
              fontSize: '11px',
              content: '"❰❱"',
              color: 'white',
              textAlign: 'center',
              lineHeight: 1.6,
            },
          }}
          id={`slider_expert_${criteria}`}
          aria-label="custom thumb label"
          color="secondary"
          min={SLIDER_MIN_STEP}
          max={SLIDER_MAX_STEP}
          step={SLIDER_STEP}
          marks
          value={criteriaValue || 0}
          className={classes.slider}
          track={false}
          disabled={disabled || criteriaValue === undefined}
          onChange={(_: Event, score: number | number[]) =>
            handleSliderChange(criteria, score as number)
          }
        />
      </div>
    </div>
  );
};

export default CriteriaSlider;
