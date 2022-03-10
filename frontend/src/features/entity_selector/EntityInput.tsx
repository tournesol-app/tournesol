import React, { useEffect, useState } from 'react';
import { Autocomplete, Box, TextField } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import {
  PRESIDENTIELLE_2022_POLL_NAME,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';
import { EntitiesService, TypeEnum, Entity } from 'src/services/openapi';

let CANDIDATES: Promise<Entity[]> | null = null;

const getCandidates = async () => {
  if (CANDIDATES != null) {
    return CANDIDATES;
  }
  CANDIDATES = EntitiesService.entitiesList({
    type: TypeEnum.CANDIDATE_FR_2022,
  }).then((data) => data.results ?? []);
  return CANDIDATES;
};

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

const CandidateInput = ({ onChange }: Props) => {
  const [options, setOptions] = useState<Entity[]>([]);

  useEffect(() => {
    getCandidates().then((candidates) => setOptions(candidates));
  }, []);

  return (
    <Box>
      <Autocomplete
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
    </Box>
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
