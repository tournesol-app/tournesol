import React, { useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';

import {
  Box,
  InputAdornment,
  IconButton,
  TextField,
  Paper,
  useTheme,
  Typography,
} from '@mui/material';
import { Close, Search } from '@mui/icons-material';

import { RowEntityCard } from 'src/components/entity/EntityCard';
import { useCurrentPoll } from 'src/hooks';
import { PollsService } from 'src/services/openapi';
import { EntityResult } from 'src/utils/types';

interface EntitySearchInputProps {
  onClear?: () => void;
  onResults?: () => void;
  onResultSelect?: (uid: string) => void;
}

interface EntitySearchResultsProps {
  entities: EntityResult[];
  onSelect?: (uid: string) => void;
}

const EntitySearchResults = ({
  entities,
  onSelect,
}: EntitySearchResultsProps) => {
  return (
    <Box bgcolor="white">
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
  );
};

const EntitySearchInput = ({
  onClear,
  onResults,
  onResultSelect,
}: EntitySearchInputProps) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const { name: pollName } = useCurrentPoll();

  const [loading, setLoading] = useState(false);

  const [search, setSearch] = useState('');
  const [lastSearch, setLastSearch] = useState('');
  const [entities, setEntities] = useState<Array<EntityResult>>([]);
  const nResults = entities.length;

  const clearSearch = () => {
    setSearch('');
    setLastSearch('');
    setEntities([]);
    setLoading(false);
    onClear && onClear();
  };

  const searchEntity = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!search) {
      return;
    }

    setLoading(true);

    let entities;
    try {
      entities = await PollsService.pollsRecommendationsList({
        name: pollName,
        search: search,
        limit: 20,
        // XXX: add control to toggle between true/false
        unsafe: true,
      });
    } catch (err) {
      setLoading(false);
      console.error(err);
      return;
    }

    const results = entities.results ?? [];

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
    <Box
      sx={{
        bgcolor: 'grey.100',
      }}
      pt={2}
    >
      <form onSubmit={searchEntity} name="entity-selector-search">
        <Box p={1} display="flex">
          <TextField
            fullWidth
            size="small"
            color="secondary"
            label={t('entitySelector.search')}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            sx={{
              bgcolor: 'white',
              '& .MuiInputBase-root': {
                borderTopRightRadius: 0,
                borderBottomRightRadius: 0,
              },
            }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton aria-label="clear search" onClick={clearSearch}>
                    <Close />
                  </IconButton>
                </InputAdornment>
              ),
            }}
            // XXX: change the id
            data-testid="paste-video-url"
          />
          <IconButton
            color="primary"
            sx={{
              color: theme.palette.neutral.dark,
              backgroundColor: theme.palette.primary.main,
              borderRadius: '4px',
              borderTopLeftRadius: 0,
              borderBottomLeftRadius: 0,
            }}
            disabled={loading}
            type="submit"
          >
            <Search />
          </IconButton>
        </Box>
      </form>
      {displayResults() && (
        <>
          <Box px={1} my={1}>
            <Typography
              variant="subtitle1"
              textAlign="center"
              sx={{
                '& strong': {
                  color: 'secondary.main',
                  fontSize: '1.4em',
                },
              }}
            >
              <Trans
                t={t}
                i18nKey="entitySelector.searchResults"
                count={nResults}
              >
                <strong>{{ nResults }}</strong> results for {{ lastSearch }}
              </Trans>
            </Typography>
          </Box>
          <Paper
            square
            elevation={2}
            sx={{
              width: '100%',
              position: 'absolute',
              zIndex: theme.zIndex.entitySelectorSearchResults,
              maxHeight: '47vh',
              overflow: 'auto',
              bgcolor: 'grey.100',
              boxShadow:
                '0px 3px 1px -2px rgba(0,0,0,0.2), 0px 2px 2px 0px rgba(0,0,0,0.14), 0px 6px 5px 0px rgba(0,0,0,0.12)',
            }}
          >
            {nResults > 0 && (
              <Box mt={1}>
                <EntitySearchResults
                  entities={entities}
                  onSelect={onResultSelect}
                />
              </Box>
            )}
            <Box p={1} display="flex" justifyContent="flex-end">
              <IconButton onClick={clearSearch}>
                <Close />
              </IconButton>
            </Box>
          </Paper>
        </>
      )}
    </Box>
  );
};

export default EntitySearchInput;
