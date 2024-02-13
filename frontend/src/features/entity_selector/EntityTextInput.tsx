import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Box,
  InputAdornment,
  IconButton,
  TextField,
  Paper,
  Button,
  useTheme,
} from '@mui/material';
import { Close, Search } from '@mui/icons-material';

import { RowEntityCard } from 'src/components/entity/EntityCard';
import { useCurrentPoll } from 'src/hooks';
import { PollsService } from 'src/services/openapi';
import { EntityResult } from 'src/utils/types';

interface Props {
  onClear?: () => void;
  onResults?: () => void;
  onResultSelect?: (uid: string) => void;
}

const EntitySearchInput = ({ onClear, onResults, onResultSelect }: Props) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const { name: pollName } = useCurrentPoll();

  const [search, setSearch] = useState('');
  const [entities, setEntities] = useState<Array<EntityResult>>([]);

  const clearSearch = () => {
    setSearch('');
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
      // XXX: add control to toggle between true/false
      unsafe: true,
    });

    const results = entities.results ?? [];
    setEntities(results);

    if (results.length > 0) {
      onResults && onResults();
    } else {
      onClear && onClear();
    }
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
      {entities.length > 0 && (
        <Paper
          square
          sx={{
            pb: 2,
            width: '100%',
            position: 'absolute',
            zIndex: theme.zIndex.entitySelectorSearchResults,
            maxHeight: '40vh',
            overflow: 'auto',
            backgroundColor: 'white',
          }}
        >
          <ul>
            {entities.map((res) => (
              <li
                key={res.entity.uid}
                onClick={
                  onResultSelect && (() => onResultSelect(res.entity.uid))
                }
              >
                <RowEntityCard key={res.entity.uid} result={res} />
              </li>
            ))}
          </ul>
        </Paper>
      )}
    </Box>
  );
};

export default EntitySearchInput;
