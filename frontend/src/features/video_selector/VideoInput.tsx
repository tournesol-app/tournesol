import React from 'react';
import { Box, TextField } from '@mui/material';
import { useTranslation } from 'react-i18next';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

const VideoInput = ({ value, onChange }: Props) => {
  const { t } = useTranslation();

  return (
    <Box>
      <TextField
        fullWidth
        value={value}
        placeholder={t('videoSelector.pasteUrlOrVideoId')}
        onChange={(e) => onChange(e.target.value)}
        variant="standard"
        InputProps={{
          sx: (theme) => ({
            [theme.breakpoints.down('sm')]: {
              fontSize: '0.7rem',
            },
          }),
        }}
      />
    </Box>
  );
};

export default VideoInput;
