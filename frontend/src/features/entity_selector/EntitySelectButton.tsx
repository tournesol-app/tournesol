import React, { useContext, useEffect, useMemo, useRef, useState } from 'react';
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
import { UsersService } from 'src/services/openapi';
import { getRecommendations } from 'src/utils/api/recommendations';
import { getGoodShortVideos } from 'src/utils/api/goodShortVideos';
import { getAllCandidates } from 'src/utils/polls/presidentielle2022';
import SelectorListBox, { EntitiesTab } from './EntityTabsBox';
import SelectorPopper from './SelectorPopper';
import { useLoginState, usePreferredLanguages } from 'src/hooks';
import { ComparisonsCountContext } from 'src/pages/comparisons/Comparison';
import { EntityObject } from 'src/utils/types';

// in milliseconds
const TYPING_DELAY = 50;

interface Props {
  value: string;
  onChange: (value: string) => void;
  otherUid: string | null;
  variant?: 'compact' | 'full';
  disabled?: boolean;
}

const VideoInput = ({
  value,
  onChange,
  otherUid,
  variant = 'compact',
  disabled = false,
}: Props) => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const selectorAnchor = useRef<HTMLDivElement>(null);
  const [suggestionsOpen, setSuggestionsOpen] = useState(false);

  const { isLoggedIn } = useLoginState();
  const fullScreenModal = useMediaQuery(
    (theme: Theme) => `${theme.breakpoints.down('sm')}, (pointer: coarse)`,
    { noSsr: true }
  );

  const comparisonsCount = useContext(ComparisonsCountContext).comparisonsCount;

  const preferredLanguages = usePreferredLanguages({ pollName });

  const handleOptionClick = (uid: string) => {
    onChange(uid);
    setSuggestionsOpen(false);
  };

  const toggleSuggestions = () => {
    setSuggestionsOpen((open) => !open);
  };

  useEffect(() => {
    const timeOutId = setTimeout(() => {
      setSuggestionsOpen(false);
    }, TYPING_DELAY);

    return () => clearTimeout(timeOutId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

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
          return response.results ?? [];
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
          return response.results ?? [];
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
        name: 'sub-sample',
        label: t('entitySelector.yourScores'),
        fetch: async () => {
          const response = await UsersService.usersMeSubsamplesList({
            pollName,
            limit: 20,
            ntile: 20,
          });
          return response.results ?? [];
        },
        disabled: !isLoggedIn,
        displayIndividualScores: true,
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
      {
        name: 'good-short-videos',
        label: t('entitySelector.goodShortVideos'),
        fetch: async () => {
          return await getGoodShortVideos({ preferredLanguages });
        },
        disabled: !isLoggedIn,
      },
    ],
    [t, isLoggedIn, otherUid, pollName, preferredLanguages]
  );

  return (
    <ClickAwayListener onClickAway={() => setSuggestionsOpen(false)}>
      <Box
        ref={selectorAnchor}
        sx={{
          width: variant === 'full' ? '100%' : 'auto',
        }}
      >
        <Button
          fullWidth={variant === 'full' ? true : false}
          onClick={toggleSuggestions}
          size="small"
          variant="contained"
          color="secondary"
          disabled={disabled}
          sx={
            variant === 'full'
              ? { minHeight: '100px', fontSize: '1rem' }
              : { minWidth: '80px', fontSize: { xs: '0.7rem', sm: '0.8rem' } }
          }
          disableElevation
          data-testid={`entity-select-button-${variant}`}
        >
          {variant === 'full'
            ? t('entitySelector.selectAVideo')
            : t('entitySelector.select')}
        </Button>
        {selectorAnchor.current &&
          selectorAnchor.current.offsetParent != null && (
            <SelectorPopper
              modal={fullScreenModal}
              open={suggestionsOpen}
              anchorEl={selectorAnchor.current}
              onClose={() => setSuggestionsOpen(false)}
            >
              <SelectorListBox
                tabs={tabs}
                onSelectEntity={handleOptionClick}
                elevation={10}
                entitySearchInput={true}
                displayDescription={comparisonsCount < 8}
              />
            </SelectorPopper>
          )}
      </Box>
    </ClickAwayListener>
  );
};

const CandidateInput = ({ onChange, value }: Props) => {
  const [options, setOptions] = useState<EntityObject[]>([]);

  useEffect(() => {
    getAllCandidates().then((results) => {
      const candidates = results.map((res) => res.entity);
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
