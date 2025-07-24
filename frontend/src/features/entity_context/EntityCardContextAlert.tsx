import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { Alert, Box, Chip, Grid, Typography } from '@mui/material';

interface EntityCardContextAlertProps {
  uid: string;
}

const EntityCardContextAlert = ({ uid }: EntityCardContextAlertProps) => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/entities/${uid}#entity-context`);
  };

  return (
    <Grid item xs={12}>
      <Alert
        icon={false}
        severity="warning"
        sx={{
          py: '4px',
          borderRadius: 0,
          '& .MuiAlert-message': {
            width: '100%',
            py: '4px',
          },
        }}
      >
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Typography variant="body2">
            {t('entityCardContextAlert.contextHasBeenAddedToThisElement')}
          </Typography>
          <Chip
            variant="outlined"
            size="small"
            label={t('entityCardContextAlert.see')}
            onClick={handleClick}
          />
        </Box>
      </Alert>
    </Grid>
  );
};

export default EntityCardContextAlert;
