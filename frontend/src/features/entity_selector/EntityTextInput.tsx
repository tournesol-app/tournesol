import React, { useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';

import {
  Box,
  InputAdornment,
  IconButton,
  TextField,
  Paper,
  Typography,
  useTheme,
} from '@mui/material';
import { Close, Search } from '@mui/icons-material';

import { RowEntityCard } from 'src/components/entity/EntityCard';
import { useCurrentPoll } from 'src/hooks';
import { PollsService } from 'src/services/openapi';
import { EntityResult } from 'src/utils/types';
import { extractVideoId } from 'src/utils/video';

interface EntitySearchInputProps {
  onClose?: () => void;
  onResults?: () => void;
  onResultSelect?: (uid: string) => void;
}

interface EntitySearchResultsProps {
  error?: boolean;
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
          mt={1}
          mb={2}
          bgcolor="white"
          overflow="auto"
          sx={{
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
                <RowEntityCard key={res.entity.uid} result={res} />
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
  lastSearch,
  entities,
  onSelect,
}: EntitySearchResultsProps) => {
  const theme = useTheme();
  const { t } = useTranslation();
  const nResults = entities.length;
  return (
    <Paper
      elevation={2}
      sx={{
        width: '100%',
        position: 'absolute',
        zIndex: theme.zIndex.entitySelectorSearchResults,
        backgroundColor: 'inherit',
        boxShadow:
          '0px 3px 1px -2px rgba(0,0,0,0.2),0px 2px 2px 0px rgba(0,0,0,0.14),0px 6px 5px 0px rgba(0,0,0,0.12)',
      }}
    >
      <Box p={1}>
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
    </Paper>
  );
};

const EntitySearchInput = ({
  onClose,
  onResults,
  onResultSelect,
}: EntitySearchInputProps) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const { name: pollName } = useCurrentPoll();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

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
    const target = extractVideoId(search, { ignoreVideoId: true });

    if (target) {
      selectResult(target);
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

  const displayResults = () => {
    if (entities.length > 0) {
      return true;
    }

    if (lastSearch !== '') {
      return true;
    }

    return false;
  };

  return (
    <Box pt={2} bgcolor="grey.100">
      <form onSubmit={searchEntity} name="entity-selector-search">
        <Box p={1} display="flex">
          <TextField
            size="small"
            color="secondary"
            label={t('entitySearchInput.search')}
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
      {displayResults() && (
        <EntitySearchResults
          error={error}
          lastSearch={lastSearch}
          entities={entities}
          onSelect={selectResult}
        />
      )}
    </Box>
  );
};

export default EntitySearchInput;
