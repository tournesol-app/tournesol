import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Typography, Button } from '@mui/material';
import { getPollName } from 'src/utils/constants';
import { SelectablePoll } from 'src/utils/types';
import { scrollToTop } from 'src/utils/ui';

interface Props {
  poll: SelectablePoll;
}

const PollLargeButton = ({ poll }: Props) => {
  const { t } = useTranslation();
  return (
    <Button
      component={RouterLink}
      to={poll.path}
      onClick={() => scrollToTop()}
      variant="contained"
      color="inherit"
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
      <poll.iconComponent color="inherit" sx={{ fontSize: '60px' }} />
      <Typography color="inherit" sx={{ display: 'flex', gap: 1 }}>
        {getPollName(t, poll.name)}
      </Typography>
    </Button>
  );
};

export default PollLargeButton;
