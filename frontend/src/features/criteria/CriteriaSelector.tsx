import React from 'react';
import { Select, MenuItem } from '@mui/material';
import { CriteriaIcon } from 'src/components';
import { useCurrentPoll } from 'src/hooks';

interface Props {
  criteria: string;
  setCriteria: (c: string) => void;
}

const CriteriaSelector = ({ criteria, setCriteria }: Props) => {
  const { criterias } = useCurrentPoll();
  return (
    <Select
      fullWidth
      color="secondary"
      size="small"
      value={criteria}
      onChange={(v) => setCriteria(v.target.value)}
    >
      {criterias.map((criterion) => (
        <MenuItem key={criterion.name} value={criterion.name}>
          <CriteriaIcon
            criteriaName={criterion.name}
            sx={{
              marginRight: '6px',
            }}
          />
          {criterion.label}
        </MenuItem>
      ))}
    </Select>
  );
};

export default CriteriaSelector;
