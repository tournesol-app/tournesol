import React, { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Box,
  FormControl,
  InputLabel,
  ListItemText,
  MenuItem,
  Select,
  SelectChangeEvent,
} from '@mui/material';
import CallMadeIcon from '@mui/icons-material/CallMade';
import CallReceivedIcon from '@mui/icons-material/CallReceived';

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

  const genericItems = useMemo(
    () => [
      {
        label: t('ratingOrderByInput.lastComparisonDate'),
        value: 'last_compared_at',
        icon: CallMadeIcon,
      },
      {
        label: t('ratingOrderByInput.lastComparisonDate'),
        value: '-last_compared_at',
        icon: CallReceivedIcon,
      },
      {
        label: t('ratingOrderByInput.numberOfComparisons'),
        value: 'n_comparisons',
        icon: CallMadeIcon,
      },
      {
        label: t('ratingOrderByInput.numberOfComparisons'),
        value: '-n_comparisons',
        icon: CallReceivedIcon,
      },
      {
        label: t('ratingOrderByInput.collectiveTournesolScore'),
        value: 'collective_score',
        icon: CallMadeIcon,
      },
      {
        label: t('ratingOrderByInput.collectiveTournesolScore'),
        value: '-collective_score',
        icon: CallReceivedIcon,
      },
      {
        label: t('ratingOrderByInput.individualTournesolScore'),
        value: 'individual_score',
        icon: CallMadeIcon,
      },
      {
        label: t('ratingOrderByInput.individualTournesolScore'),
        value: '-individual_score',
        icon: CallReceivedIcon,
      },
    ],
    [t]
  );

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
          {/* Metadata available for any kind of entity type. */}
          {genericItems.map((item) => (
            <MenuItem key={item.value} value={item.value}>
              <Box display="flex" alignItems="center">
                <ListItemText>{item.label}</ListItemText>
                &nbsp;
                <item.icon fontSize="small" />
              </Box>
            </MenuItem>
          ))}

          {/* Metadata specific to the displayed entity type. */}
          {extraMetadataOrderBy.map((metadata) => [
            <MenuItem key={`${metadata}`} value={`${metadata}`}>
              <Box display="flex" alignItems="center">
                <ListItemText>
                  {getMetadataName(t, pollName, metadata)}
                </ListItemText>
                &nbsp;
                <CallMadeIcon fontSize="small" />
              </Box>
            </MenuItem>,
            <MenuItem key={`-${metadata}`} value={`-${metadata}`}>
              <Box display="flex" alignItems="center">
                <ListItemText>
                  {getMetadataName(t, pollName, metadata)}
                </ListItemText>
                &nbsp;
                <CallReceivedIcon fontSize="small" />
              </Box>
            </MenuItem>,
          ])}
        </Select>
      </FormControl>
    </TitledSection>
  );
}

export default RatingOrderByInput;
