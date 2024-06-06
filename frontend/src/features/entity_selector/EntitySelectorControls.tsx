import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid } from '@mui/material';

import { SuggestionHistory } from 'src/features/suggestions/suggestionHistory';

import AutoEntityButton from './AutoEntityButton';
import EntitySelectButton from './EntitySelectButton';

interface EntitySelectorControlsProps {
  alignment?: 'left' | 'right';
  uid: string | null;
  otherUid: string | null;
  inputValue: string | null;
  history?: SuggestionHistory;
  disabled: boolean;
  orderedCriteriaRated?: boolean;
  onAutoClick: () => Promise<void>;
  onEntitySelect: (uid: string) => void;
}

const EntitySelectorControls = ({
  alignment = 'left',
  uid,
  otherUid,
  inputValue,
  history,
  disabled,
  orderedCriteriaRated = false,
  onAutoClick,
  onEntitySelect,
}: EntitySelectorControlsProps) => {
  const { t } = useTranslation();

  return (
    <Box
      display="flex"
      flexDirection={
        uid
          ? alignment === 'left'
            ? 'row'
            : 'row-reverse'
          : alignment !== 'left'
          ? 'row'
          : 'row-reverse'
      }
      alignItems="center"
      justifyContent="space-between"
    >
      <Grid
        container
        spacing={{ xs: 2, sm: 1 }}
        display={uid ? 'flex' : 'none'}
        direction={alignment === 'left' ? 'row' : 'row-reverse'}
        justifyContent="flex-start"
      >
        <Grid item>
          <EntitySelectButton
            value={inputValue || uid || ''}
            onChange={onEntitySelect}
            otherUid={otherUid}
            history={history}
          />
        </Grid>
        <Grid item>
          <AutoEntityButton
            disabled={disabled}
            onClick={onAutoClick}
            compactLabel={
              orderedCriteriaRated
                ? t('entitySelectorControls.next')
                : undefined
            }
            compactLabelLoc={alignment === 'left' ? 'right' : 'left'}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default EntitySelectorControls;
