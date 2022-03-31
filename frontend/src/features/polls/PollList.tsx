import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Stack, Typography, Button } from '@mui/material';
import { getPollName, polls } from 'src/utils/constants';
import { scrollToTop } from 'src/utils/ui';

const orderedPolls = [...polls].sort((a, b) => a.displayOrder - b.displayOrder);

const PollList = () => {
  const { t } = useTranslation();
  return (
    <Stack direction="row" spacing={2}>
      {orderedPolls.map(({ name, iconComponent: Icon, path }) => {
        return (
          <Button
            component={RouterLink}
            to={path}
            onClick={scrollToTop}
            variant="contained"
            color="inherit"
            key={name}
            sx={{
              color: 'text.secondary',
              p: 2,
              minWidth: 'min(300px, 40vw)',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              backgroundColor: 'grey.100',
            }}
          >
            <Icon color="inherit" sx={{ fontSize: '60px' }} />
            <Typography color="inherit" sx={{ display: 'flex', gap: 1 }}>
              {getPollName(t, name)}
            </Typography>
          </Button>
        );
      })}
    </Stack>
  );
};

export default PollList;
