import React, { useEffect, useState } from 'react';
import { Autocomplete, Box, TextField } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import {
  PRESIDENTIELLE_2022_POLL_NAME,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';
import { Entity } from 'src/services/openapi';
import { getAllCandidates } from 'src/utils/polls/presidentielle2022';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

const VideoInput = ({ value, onChange }: Props) => {
  const { t } = useTranslation();

  return (
    <Box>
      <TextField
        color="secondary"
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
