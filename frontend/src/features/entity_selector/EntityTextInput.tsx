import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, InputAdornment, IconButton, TextField } from '@mui/material';
import { Search } from '@mui/icons-material';

import { useCurrentPoll } from 'src/hooks';
import { PollsService } from 'src/services/openapi';

const EntitySearchInput = () => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const [search, setSearch] = useState('');

  const searchEntity = async () => {
    const entities = await PollsService.pollsRecommendationsList({
      name: pollName,
      search: search,
      // XXX: add control to toggle between true/false
      unsafe: true,
    });
  };

  return (
    <Box
      sx={{
        bgcolor: 'grey.100',
      }}
      p={1}
      pt={2}
    >
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
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton aria-label="search" onClick={searchEntity}>
                <Search />
              </IconButton>
            </InputAdornment>
          ),
        }}
        sx={{
          bgcolor: 'white',
        }}
        // XXX: change the id
        data-testid="paste-video-url"
      />
    </Box>
  );
};

export default EntitySearchInput;
