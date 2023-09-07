import React from 'react';
import { Select, MenuItem, Box } from '@mui/material';
import { CriteriaIcon } from 'src/components';
import { useCurrentPoll } from 'src/hooks';

interface Props {
  criteria: string;
  setCriteria: (c: string) => void;
  extraEmptyOption?: string;
}

const CriteriaSelector = ({
  criteria,
  setCriteria,
  extraEmptyOption = '',
}: Props) => {
  const { criterias } = useCurrentPoll();
  return (
    <Select
      fullWidth
      color="secondary"
      size="small"
      value={criteria}
      onChange={(v) => setCriteria(v.target.value)}
      SelectDisplayProps={{
        style: { whiteSpace: 'normal' },
      }}
    >
      {extraEmptyOption !== '' && (
        <MenuItem value={extraEmptyOption}>------------</MenuItem>
      )}
      {criterias.map((criterion) => (
        <MenuItem key={criterion.name} value={criterion.name}>
          <Box display="flex" alignItems="center">
            <CriteriaIcon
              criteriaName={criterion.name}
              sx={{
                display: 'inline',
                marginRight: '6px',
              }}
            />
            {criterion.label}
          </Box>
        </MenuItem>
      ))}
    </Select>
  );
};

export default CriteriaSelector;
