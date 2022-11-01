import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
} from '@mui/material';

import { TitledSection } from 'src/components';
import { useCurrentPoll } from 'src/hooks';
import { getMetadataName } from 'src/utils/constants';

interface FilterProps {
  value: string;
  onChange: (value: string) => void;
}

function RatingOrderByInput(props: FilterProps) {
  const { t } = useTranslation();
  const { name: pollName, options } = useCurrentPoll();

  const extraMetadataOrderBy = options?.extraMetadataOrderBy ?? [];

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
          inputProps={{ 'data-testid': 'order-by-metadata-input' }}
        >
          <MenuItem value="last_compared_at">
            {t('ratingOrderByInput.lastComparisonDate')}&nbsp;
            {t('ratingOrderByInput.(asc)')}
          </MenuItem>
          <MenuItem value="-last_compared_at">
            {t('ratingOrderByInput.lastComparisonDate')}&nbsp;
            {t('ratingOrderByInput.(desc)')}
          </MenuItem>
          <MenuItem value="n_comparisons">
            {t('ratingOrderByInput.numberOfComparisons')}&nbsp;
            {t('ratingOrderByInput.(asc)')}
          </MenuItem>
          <MenuItem value="-n_comparisons">
            {t('ratingOrderByInput.numberOfComparisons')}&nbsp;
            {t('ratingOrderByInput.(desc)')}
          </MenuItem>
          {extraMetadataOrderBy.map((metadata) => [
            <MenuItem key={`${metadata}`} value={`${metadata}`}>
              {getMetadataName(t, pollName, metadata)}&nbsp;
              {t('ratingOrderByInput.(asc)')}
            </MenuItem>,
            <MenuItem key={`-${metadata}`} value={`-${metadata}`}>
              {getMetadataName(t, pollName, metadata)}&nbsp;
              {t('ratingOrderByInput.(desc)')}
            </MenuItem>,
          ])}
        </Select>
      </FormControl>
    </TitledSection>
  );
}

export default RatingOrderByInput;
