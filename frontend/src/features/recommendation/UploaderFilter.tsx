import React from 'react';
import { Typography, Chip } from '@mui/material';

interface UploaderProps {
  value: string;
  onDelete: () => void;
}

function UploaderFilter(props: UploaderProps) {
  return (
    <Chip
      label={
        <Typography variant="body2">
          <strong>Uploader: </strong>
          {props.value}
        </Typography>
      }
      color="secondary"
      onDelete={props.onDelete}
    />
  );
}

export default UploaderFilter;
