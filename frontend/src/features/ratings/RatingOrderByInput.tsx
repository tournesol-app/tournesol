import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
} from '@mui/material';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { TitledSection } from 'src/components';

export const isPublicChoices = {
  true: 'Public',
  false: 'Private',
};

interface FilterProps {
  value: string;
  onChange: (value: string) => void;
}

function RatingOrderByInput(props: FilterProps) {
  const { t } = useTranslation();

  const handleChange = (event: SelectChangeEvent) => {
    props.onChange(event.target.value);
  };

  return (
    <TitledSection title={t('ratingOrderByInput.orderBy')}>
      <FormControl fullWidth size="small">
        <InputLabel id="order-by-metadata-label">
          {t('ratingOrderByInput.order')}
        </InputLabel>
        <Select
          id="order-by-metadata"
          labelId="order-by-metadata-label"
          label={t('ratingOrderByInput.order')}
          value={props.value}
          onChange={handleChange}
        >
          <MenuItem value="">--</MenuItem>
          <MenuItem value="last_compared_at">
            {t('ratingOrderByInput.lastComparisonDate(ASC)')}
          </MenuItem>
          <MenuItem value="-last_compared_at">
            {t('ratingOrderByInput.lastComparisonDate(DESC)')}
          </MenuItem>
          <MenuItem value="n_comparisons">
            {t('ratingOrderByInput.numberOfComparisons(ASC)')}
          </MenuItem>
          <MenuItem value="-n_comparisons">
            {t('ratingOrderByInput.numberOfComparisons(DESC)')}
          </MenuItem>
        </Select>
      </FormControl>
    </TitledSection>
  );
}

export default RatingOrderByInput;
