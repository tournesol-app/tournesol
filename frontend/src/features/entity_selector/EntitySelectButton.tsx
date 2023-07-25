import React, { useEffect, useState, useMemo } from 'react';
import {
  Autocomplete,
  Box,
  TextField,
  ClickAwayListener,
  useMediaQuery,
  Theme,
  Button,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import {
  PRESIDENTIELLE_2022_POLL_NAME,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';
import { Entity, UsersService } from 'src/services/openapi';
import { getRecommendations } from 'src/utils/api/recommendations';
import { getAllCandidates } from 'src/utils/polls/presidentielle2022';
import SelectorListBox, { EntitiesTab } from './EntityTabsBox';
import SelectorPopper from './SelectorPopper';
import { useLoginState } from 'src/hooks';

// in milliseconds
const TYPING_DELAY = 300;

interface Props {
  value: string;
  onChange: (value: string) => void;
  otherUid: string | null;
}

const VideoInput = ({ value, onChange, otherUid }: Props) => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const [menuAnchor, setMenuAnchor] = React.useState<null | HTMLElement>(null);
  const [suggestionsOpen, setSuggestionsOpen] = useState(false);
  const [fieldValue, setFieldValue] = useState(value);

  const { isLoggedIn } = useLoginState();
  const fullScreenModal = useMediaQuery(
    (theme: Theme) => `${theme.breakpoints.down('sm')}, (pointer: coarse)`,
    { noSsr: true }
  );

  const handleOptionClick = (uid: string) => {
    onChange(uid);
    setSuggestionsOpen(false);
  };

  const toggleSuggestions = (event: React.MouseEvent<HTMLButtonElement>) => {
    setSuggestionsOpen((open) => !open);
    if (menuAnchor === null) {
      setMenuAnchor(event.currentTarget);
    }
  };

  useEffect(() => {
    const timeOutId = setTimeout(() => {
      setSuggestionsOpen(false);
    }, TYPING_DELAY);

    return () => clearTimeout(timeOutId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fieldValue]);

  const tabs: EntitiesTab[] = useMemo(
    () => [
      /*
      The suggestions tab is commented for now. We are investigating
      performance issue.
      {
        name: 'suggestions',
        label: t('entitySelector.suggestions'),
        fetch: async () => {
          const response = await UsersService.usersMeEntitiesToCompareList({
            pollName: YOUTUBE_POLL_NAME,
            limit: 20,
            firstEntityUid: otherUid || undefined,
          });
          return response.results ?? [];
        },
        disabled: !isLoggedIn,
      },
      */
      {
        name: 'rate-later',
        label: t('entitySelector.rateLater'),
        fetch: async () => {
          const response = await UsersService.usersMeRateLaterList({
            pollName,
            limit: 20,
          });
          return (response.results ?? []).map((rl) => rl.entity);
        },
        disabled: !isLoggedIn,
      },
      {
        name: 'recently-compared',
        label: t('entitySelector.recentlyCompared'),
        fetch: async () => {
          const response = await UsersService.usersMeContributorRatingsList({
            pollName: YOUTUBE_POLL_NAME,
            limit: 20,
          });
          return (response.results ?? []).map((rating) => rating.entity);
        },
        disabled: !isLoggedIn,
      },
      {
        name: 'recommendations',
        label: t('entitySelector.recommendations'),
        fetch: async () => {
          const response = await getRecommendations(
            'videos',
            20,
            '?date=Month',
            []
          );
          return response.results ?? [];
        },
      },
      {
        name: 'unconnected',
        label: t('entitySelector.unconnected'),
        fetch: async () => {
          const response = await UsersService.usersMeUnconnectedEntitiesList({
            pollName: YOUTUBE_POLL_NAME,
            uid: otherUid || '',
            limit: 20,
            strict: false,
          });
          return response.results ?? [];
        },
        disabled: !isLoggedIn || !otherUid,
      },
    ],
    [t, isLoggedIn, otherUid, pollName]
  );

  return (
    <ClickAwayListener onClickAway={() => setSuggestionsOpen(false)}>
      <Box>
        <Button
          onClick={toggleSuggestions}
          size="small"
          variant="contained"
          color="secondary"
          sx={{ minWidth: '110px', fontSize: { xs: '0.7rem', sm: '0.8rem' } }}
          disableElevation
          data-testid="entity-select-button"
        >
          {t('entitySelector.select')}
        </Button>
        <SelectorPopper
          modal={fullScreenModal}
          open={suggestionsOpen}
          anchorEl={menuAnchor}
          onClose={() => setSuggestionsOpen(false)}
        >
          <SelectorListBox
            value={value}
            onChange={(e) => {
              onChange(e);
              setFieldValue(e);
            }}
            tabs={tabs}
            onSelectEntity={handleOptionClick}
            elevation={10}
          />
        </SelectorPopper>
      </Box>
    </ClickAwayListener>
  );
};

const CandidateInput = ({ onChange, value }: Props) => {
  const [options, setOptions] = useState<Entity[]>([]);

  useEffect(() => {
    getAllCandidates().then((candidates) => {
      const sortedCandidates = [...candidates].sort((a, b) => {
        // Sort by last name
        const aName: string = a?.metadata?.name.split(' ').slice(1).join(' ');
        const bName: string = b?.metadata?.name.split(' ').slice(1).join(' ');
        return aName.localeCompare(bName);
      });
      setOptions(sortedCandidates);
    });
  }, []);

  return (
    <Autocomplete
      value={options.find((opt) => opt.uid == value) || null}
      selectOnFocus
      blurOnSelect
      onChange={(event, newValue) => {
        onChange(newValue?.uid ?? '');
      }}
      options={options}
      getOptionLabel={(option) => option.metadata?.name}
      renderInput={(params) => (
        <TextField color="secondary" variant="standard" {...params} />
      )}
    />
  );
};

const EntitySelectButton = (props: Props) => {
  const { name: pollName } = useCurrentPoll();
  if (pollName === YOUTUBE_POLL_NAME) {
    return <VideoInput {...props} />;
  }
  if (pollName === PRESIDENTIELLE_2022_POLL_NAME) {
    return <CandidateInput {...props} />;
  }
  return null;
};

export default EntitySelectButton;
