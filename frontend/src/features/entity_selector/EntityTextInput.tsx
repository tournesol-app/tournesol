import React from 'react';

import { Box, InputAdornment, Link, TextField } from '@mui/material';
import { useTranslation } from 'react-i18next';

interface Props {
  entityTextInput: { value: string; onChange: (value: string) => void };
}

const EntityTextInput = ({ entityTextInput }: Props) => {
  const { t } = useTranslation();

  return (
    <Box
      sx={{
        bgcolor: 'grey.100',
      }}
      p={1}
      pt={2}
    >
      <TextField
        label={t('entitySelector.pasteUrlOrVideoId')}
        color="secondary"
        fullWidth
        size="small"
        value={entityTextInput.value}
        onChange={(e) => {
          entityTextInput.onChange(e.target.value);
        }}
        onFocus={(e) => {
          e.target.select();
        }}
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <Link />
            </InputAdornment>
          ),
        }}
        sx={{
          bgcolor: 'white',
        }}
        data-testid="paste-video-url"
      />
    </Box>
  );
};

export default EntityTextInput;
