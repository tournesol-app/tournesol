import React, { useMemo } from 'react';

import { TitledSection } from 'src/components';
import {
  Typography,
  FormControlLabel,
  Checkbox,
  Box,
  Tooltip,
} from '@mui/material';
import {
  CheckCircle,
  CheckCircleOutline,
  CheckBox,
  CheckBoxOutlineBlank,
  RadioButtonUnchecked,
  RadioButtonChecked,
} from '@mui/icons-material';

interface Props {
  title: string;
  value: string;
  choices: Record<string, React.ReactNode>;
  multipleChoice?: boolean;
  radio?: boolean;
  tooltips?: Record<string, React.ReactNode>;
  onChange: (value: string) => void;
}

const ChoicesFilterSection = ({
  title,
  value,
  choices,
  multipleChoice = false,
  radio = false,
  tooltips,
  onChange,
}: Props) => {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (multipleChoice) {
      // Multiple values allowed
      let all_values = value ? value.split(',') : [];

      if (event.target.checked) {
        // Add the checked value
        all_values.push(event.target.name);
      } else {
        // Remove the unchecked value
        all_values = all_values.filter((item) => item !== event.target.name);
      }
      onChange(all_values.join(','));
    } else {
      // Only one value allowed
      if (event.target.checked) {
        onChange(event.target.name);
      } else {
        // Radio buttons are not cleared when clicked and already checked
        if (radio) return;

        onChange('');
      }
    }
  };

  const valuesList = multipleChoice ? value.split(',') : [value];

  const { icon, checkedIcon } = useMemo(() => {
    if (multipleChoice) {
      return { icon: <CheckBoxOutlineBlank />, checkedIcon: <CheckBox /> };
    } else if (radio) {
      return {
        icon: <RadioButtonUnchecked />,
        checkedIcon: <RadioButtonChecked />,
      };
    } else {
      return { icon: <CheckCircleOutline />, checkedIcon: <CheckCircle /> };
    }
  }, [multipleChoice, radio]);

  return (
    <TitledSection title={title}>
      <Box display="flex" flexDirection="column">
        {Object.entries(choices).map(([choiceValue, choiceLabel]) => {
          const checked = valuesList.includes(choiceValue);

          return (
            <FormControlLabel
              control={
                <Checkbox
                  color="secondary"
                  icon={icon}
                  checkedIcon={checkedIcon}
                  checked={checked}
                  onChange={handleChange}
                  name={choiceValue}
                  size="small"
                  data-testid={`checkbox-choice-${choiceValue}`}
                />
              }
              label={
                <Typography
                  variant="body2"
                  color={checked ? 'secondary' : 'textPrimary'}
                  sx={{
                    flexGrow: 1,
                    '&::first-letter': {
                      textTransform: 'uppercase',
                    },
                  }}
                >
                  <Tooltip
                    title={tooltips?.[choiceValue] || ''}
                    placement="right"
                  >
                    <span>{choiceLabel}</span>
                  </Tooltip>
                </Typography>
              }
              key={choiceValue}
            />
          );
        })}
      </Box>
    </TitledSection>
  );
};

export default ChoicesFilterSection;
