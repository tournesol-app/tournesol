import React, { useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';

import {
  Box,
  InputAdornment,
  IconButton,
  TextField,
  Paper,
  Button,
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
  const theme = useTheme();

  return (
    <Paper
      square
      sx={{
        pb: 2,
        width: '100%',
        position: 'absolute',
        zIndex: theme.zIndex.entitySelectorSearchResults,
        maxHeight: '47vh',
        overflow: 'auto',
        bgcolor: 'grey.100',
      }}
    >
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
    </Paper>
  );
};

const EntitySearchInput = ({
  onClear,
  onResults,
  onResultSelect,
}: EntitySearchInputProps) => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const [search, setSearch] = useState('');
  const [lastSearch, setLastSearch] = useState('');
  const [entities, setEntities] = useState<Array<EntityResult>>([]);
  const nResults = entities.length;

  const clearSearch = () => {
    setSearch('');
    setLastSearch('');
    setEntities([]);
    onClear && onClear();
  };

  const searchEntity = async () => {
    if (!search) {
      return;
    }

    const entities = await PollsService.pollsRecommendationsList({
      name: pollName,
      search: search,
      limit: 20,
      // XXX: add control to toggle between true/false
      unsafe: true,
    });

    const results = entities.results ?? [];
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
      <Box p={1} display="flex">
        <TextField
          fullWidth
          size="small"
          color="secondary"
          label={t('entitySelector.search')}
          onFocus={(e) => {
            e.target.select();
          }}
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
        <Button
          color="primary"
          variant="contained"
          onClick={searchEntity}
          startIcon={<Search />}
          sx={{ borderTopLeftRadius: 0, borderBottomLeftRadius: 0 }}
          disableElevation
        >
          Search
        </Button>
      </Box>
      {displayResults() && (
        <>
          <Box px={1} mt={1} mb={2}>
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
          {nResults > 0 && (
            <EntitySearchResults
              entities={entities}
              onSelect={onResultSelect}
            />
          )}
        </>
      )}
    </Box>
  );
};

export default EntitySearchInput;
