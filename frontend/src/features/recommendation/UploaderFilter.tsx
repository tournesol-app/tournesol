import React from 'react';
import { useTranslation } from 'react-i18next';
import { Typography, Chip } from '@mui/material';

interface UploaderProps {
  value: string;
  onDelete: () => void;
}

function UploaderFilter(props: UploaderProps) {
  const { t } = useTranslation();
  return (
    <Chip
      label={
        <Typography variant="body2">
          <strong>
            {t('filter.uploader')}
            {': '}
          </strong>
          {props.value}
        </Typography>
      }
      color="secondary"
      onDelete={props.onDelete}
    />
  );
}

export default UploaderFilter;
