import React, { useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';

import {
  Box,
  InputAdornment,
  IconButton,
  TextField,
  Typography,
  useTheme,
} from '@mui/material';
import { Close, Search } from '@mui/icons-material';

import { LoaderWrapper } from 'src/components';
import { RowEntityCard } from 'src/components/entity/EntityCard';
import { useCurrentPoll } from 'src/hooks';
import { PollsService } from 'src/services/openapi';
import { EntityResult } from 'src/utils/types';
import { extractVideoId } from 'src/utils/video';

interface EntitySearchInputProps {
  onClose?: () => void;
  onSearch?: () => void;
  onError?: () => void;
  onResults?: () => void;
  onResultSelect?: (uid: string) => void;
}

interface EntitySearchResultsProps {
  error?: boolean;
  loading: boolean;
  lastSearch: string;
  entities: EntityResult[];
  onSelect?: (uid: string) => void;
}

interface EntitySearchResultsListProps {
  entities: EntityResult[];
  onSelect?: (uid: string) => void;
}

const EntitySearchResultsList = ({
  entities,
  onSelect,
}: EntitySearchResultsListProps) => {
  return (
    <>
      {entities.length > 0 && (
        <Box
          bgcolor="white"
          sx={{
            overflowY: 'auto',
            ul: {
              li: {
                cursor: 'pointer',
                '&:hover': {
                  bgcolor: 'grey.100',
                },
              },
            },
          }}
        >
          <ul>
            {entities.map((res) => (
              <li
                key={res.entity.uid}
                onClick={onSelect && (() => onSelect(res.entity.uid))}
              >
                <RowEntityCard
                  key={res.entity.uid}
                  result={res}
                  metadataVariant="uploaderOnly"
                />
              </li>
            ))}
          </ul>
        </Box>
      )}
    </>
  );
};

const EntitySearchResults = ({
  error = false,
  loading,
  lastSearch,
  entities,
  onSelect,
}: EntitySearchResultsProps) => {
  const { t } = useTranslation();
  const nResults = entities.length;
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'stretch',
        overflow: 'hidden',
        width: '100%',
        backgroundColor: 'inherit',
      }}
    >
      <LoaderWrapper
        isLoading={loading}
        sx={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
      >
        <Box p={1} pb={2}>
          <Typography
            variant="subtitle1"
            textAlign="center"
            sx={{
              '& strong': {
                color: 'secondary.main',
                fontSize: '1.4rem',
              },
            }}
          >
            {error ? (
              t('entitySelector.errorOnLoading')
            ) : (
              <Trans
                t={t}
                i18nKey="entitySearchInput.searchResults"
                count={nResults}
              >
                <strong>{{ nResults }}</strong> results for {{ lastSearch }}
              </Trans>
            )}
          </Typography>
        </Box>
        <EntitySearchResultsList entities={entities} onSelect={onSelect} />
      </LoaderWrapper>
    </Box>
  );
};

const EntitySearchInput = ({
  onClose,
  onSearch,
  onError,
  onResults,
  onResultSelect,
}: EntitySearchInputProps) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const { name: pollName } = useCurrentPoll();

  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);

  const [search, setSearch] = useState('');
  const [lastSearch, setLastSearch] = useState('');
  const [entities, setEntities] = useState<Array<EntityResult>>([]);

  const closeSearch = () => {
    setSearch('');
    setLastSearch('');
    setEntities([]);
    setError(false);
    setLoading(false);
    onClose && onClose();
  };

  const selectResult = (uid: string) => {
    closeSearch();
    onResultSelect && onResultSelect(uid);
  };

  const searchEntity = async (event: React.FormEvent) => {
    event.preventDefault();
    (document.activeElement as HTMLElement).blur();

    if (!search) {
      return;
    }

    setLoading(true);
    onSearch && onSearch();
    const videoId = extractVideoId(search, { ignoreVideoId: true });

    if (videoId) {
      selectResult(videoId);
      return;
    }

    let entities;
    try {
      entities = await PollsService.pollsRecommendationsList({
        name: pollName,
        search: search,
        unsafe: true,
        limit: 30,
      });
    } catch (err) {
      setError(true);
      setLoading(false);
      setEntities([]);
      setLastSearch(search);
      onError && onError();
      console.error(err);
      return;
    }

    const results = entities.results ?? [];

    setError(false);
    setLoading(false);
    setEntities(results);
    setLastSearch(search);
    onResults && onResults();
  };

  const displayResults = entities.length > 0 || lastSearch !== '';

  return (
    <Box
      pt={2}
      bgcolor="grey.100"
      display="flex"
      flexDirection="column"
      overflow="hidden"
      flexShrink={displayResults ? undefined : 0}
    >
      <form onSubmit={searchEntity} name="entity-selector-search">
        <Box p={1} display="flex">
          <TextField
            size="small"
            color="secondary"
            label={t('entitySearchInput.searchByTextOrPasteUrl')}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            data-testid="entity-search-input"
            sx={{
              flex: 1,
              bgcolor: 'white',
              '& .MuiInputBase-root': {
                borderTopRightRadius: 0,
                borderBottomRightRadius: 0,
              },
            }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label={t('entitySearchInput.closeSearch')}
                    onClick={closeSearch}
                  >
                    <Close />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          <IconButton
            type="submit"
            disabled={loading}
            aria-label={t('entitySearchInput.search')}
            sx={{
              color: theme.palette.text.secondary,
              backgroundColor: theme.palette.primary.main,
              borderRadius: '4px',
              borderTopLeftRadius: 0,
              borderBottomLeftRadius: 0,
              '&:hover': {
                backgroundColor: 'rgb(178, 140, 0)',
              },
            }}
          >
            <Search />
          </IconButton>
        </Box>
      </form>
      {displayResults && (
        <EntitySearchResults
          error={error}
          loading={loading}
          lastSearch={lastSearch}
          entities={entities}
          onSelect={selectResult}
        />
      )}
    </Box>
  );
};

export default EntitySearchInput;
