import React from 'react';
import { Grid } from '@mui/material';
import { makeStyles } from '@mui/styles';
import { entityCardMainSx } from './style';

const useStyles = makeStyles({
  '@keyframes scaling': {
    '0%': {
      opacity: 0.05,
      transform: 'scale(70%)',
    },
    '100%': {
      opacity: 1,
      transform: 'scale(160%)',
    },
  },
  loadingEffect: {
    animation: '1.2s ease-out infinite alternate $scaling',
  },
});

const EmptyEntityCard = ({
  compact,
  loading = false,
}: {
  compact?: boolean;
  loading?: boolean;
}) => {
  const classes = useStyles();

  return (
    <Grid container sx={entityCardMainSx}>
      <Grid
        item
        xs={12}
        sm={compact ? 12 : 4}
        sx={{
          aspectRatio: '16 / 9',
          backgroundColor: '#fafafa',
        }}
        container
        alignItems="center"
        justifyContent="center"
      >
        <img
          src="/svg/LogoSmall.svg"
          alt="logo"
          className={loading ? classes.loadingEffect : undefined}
          style={{ opacity: '0.3' }}
        />
      </Grid>
    </Grid>
  );
};

export default EmptyEntityCard;
