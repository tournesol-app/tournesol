import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid2 } from '@mui/material';

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
      sx={{
        display: 'flex',

        flexDirection: uid
          ? alignment === 'left'
            ? 'row'
            : 'row-reverse'
          : alignment !== 'left'
          ? 'row'
          : 'row-reverse',

        alignItems: 'center',
        justifyContent: 'space-between',
      }}
    >
      <Grid2
        container
        spacing={{ xs: 2, sm: 1 }}
        direction={alignment === 'left' ? 'row' : 'row-reverse'}
        sx={{
          display: uid ? 'flex' : 'none',
          justifyContent: 'flex-start',
        }}
      >
        <Grid2>
          <EntitySelectButton
            value={inputValue || uid || ''}
            onChange={onEntitySelect}
            otherUid={otherUid}
            history={history}
          />
        </Grid2>
        <Grid2>
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
        </Grid2>
      </Grid2>
    </Box>
  );
};

export default EntitySelectorControls;
