import React, { useEffect, useState, useRef, useMemo } from 'react';
import {
  Autocomplete,
  Box,
  TextField,
  ClickAwayListener,
  InputAdornment,
  IconButton,
  useMediaQuery,
  Theme,
} from '@mui/material';
import { ArrowDropDown } from '@mui/icons-material';
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

interface Props {
  value: string;
  onChange: (value: string) => void;
  otherUid: string | null;
}

const VideoInput = ({ value, onChange, otherUid }: Props) => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const [suggestionsOpen, setSuggestionsOpen] = useState(false);
  const inputRef = useRef<HTMLDivElement>(null);
  const { isLoggedIn } = useLoginState();
  const fullScreenModal = useMediaQuery(
    (theme: Theme) => `${theme.breakpoints.down('sm')}, (pointer: coarse)`,
    { noSsr: true }
  );

  const handleOptionClick = (uid: string) => {
    onChange(uid);
    setSuggestionsOpen(false);
  };

  const toggleSuggestions = () => setSuggestionsOpen((open) => !open);

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
        <TextField
          color="secondary"
          fullWidth
          ref={inputRef}
          value={value}
          placeholder={t('entitySelector.pasteUrlOrVideoId')}
          onChange={(e) => {
            setSuggestionsOpen(false);
            onChange(e.target.value);
          }}
          variant="standard"
          onFocus={(e) => {
            e.target.select();
          }}
          onClick={() => {
            if (!fullScreenModal && !suggestionsOpen) {
              setSuggestionsOpen(true);
            }
          }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={toggleSuggestions}
                  size="small"
                  sx={{
                    ...(suggestionsOpen && {
                      transform: 'rotate(180deg)',
                    }),
                  }}
                >
                  <ArrowDropDown />
                </IconButton>
              </InputAdornment>
            ),
            sx: (theme) => ({
              [theme.breakpoints.down('sm')]: {
                fontSize: '0.7rem',
              },
            }),
          }}
        />
        <SelectorPopper
          modal={fullScreenModal}
          open={suggestionsOpen}
          anchorEl={inputRef.current}
          onClose={() => setSuggestionsOpen(false)}
        >
          <SelectorListBox
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

const EntityInput = (props: Props) => {
  const { name: pollName } = useCurrentPoll();
  if (pollName === YOUTUBE_POLL_NAME) {
    return <VideoInput {...props} />;
  }
  if (pollName === PRESIDENTIELLE_2022_POLL_NAME) {
    return <CandidateInput {...props} />;
  }
  return null;
};

export default EntityInput;
