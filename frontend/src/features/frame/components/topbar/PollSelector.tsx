import React from 'react';
import {
  Button,
  Grid,
  Hidden,
  Menu,
  MenuItem,
  Typography,
} from '@mui/material';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

const PollSelector = () => {
  const { name: pollName } = useCurrentPoll();

  const [menuAnchorEl, setMenuAnchorEl] = React.useState<null | HTMLElement>(
    null
  );

  const displayMenu = (event: React.MouseEvent<HTMLButtonElement>) => {
    setMenuAnchorEl(event.currentTarget);
  };

  const onMenuClose = () => {
    setMenuAnchorEl(null);
  };

  return (
    <>
      <Hidden smDown>
        <Grid container alignItems="center" spacing={1}>
          <Grid item>
            <img src="/svg/LogoSmall.svg" alt="logo" />
          </Grid>
          <Grid item>
            <Button
              onClick={displayMenu}
              variant="text"
              sx={{
                color: 'black',
                fontSize: '1.4em !important',
                lineHeight: 1,
                padding: 0,
                textTransform: 'none',
              }}
            >
              Tournesol
            </Button>
            <Typography variant="subtitle1">{pollName}</Typography>
          </Grid>
        </Grid>
      </Hidden>
      <Hidden smUp>
        <img src="/svg/LogoSmall.svg" alt="logo" />
      </Hidden>
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={onMenuClose}
      >
        <MenuItem>videos</MenuItem>
        <MenuItem>élection 2022</MenuItem>
      </Menu>
    </>
  );
};

export default PollSelector;
