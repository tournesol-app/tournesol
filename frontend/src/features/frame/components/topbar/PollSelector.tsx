import React from 'react';
import { useHistory } from 'react-router';
import {
  Button,
  Grid,
  Hidden,
  ListItemIcon,
  Menu,
  MenuItem,
  Typography,
} from '@mui/material';
import { HowToVote, YouTube } from '@mui/icons-material';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

const PollSelector = () => {
  const history = useHistory();
  const { name: currentPoll } = useCurrentPoll();

  const [menuAnchorEl, setMenuAnchorEl] = React.useState<null | HTMLElement>(
    null
  );

  const displayMenu = (event: React.MouseEvent<HTMLButtonElement>) => {
    setMenuAnchorEl(event.currentTarget);
  };

  const onMenuClose = () => {
    setMenuAnchorEl(null);
  };

  const onItemSelect = (event: React.MouseEvent<HTMLElement>) => {
    const poll = event.currentTarget.dataset.pollUrl || '';
    history.push(poll);
    onMenuClose();
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
                fontWeight: 'bold',
                lineHeight: 1,
                padding: 0,
                textTransform: 'none',
              }}
            >
              Tournesol
            </Button>
            <Typography variant="subtitle1">{currentPoll}</Typography>
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
        {[
          {
            name: 'videos',
            label: 'Vidéos',
            url: '/',
            icon: <YouTube fontSize="small" />,
          },
          {
            name: 'presidentielle2022',
            label: 'Élections 2022',
            url: '/presidentielle2022/',
            icon: <HowToVote fontSize="small" />,
          },
        ].map((elem) => (
          <MenuItem
            key={elem.name}
            data-poll-url={elem.url}
            onClick={onItemSelect}
            selected={elem.name === currentPoll}
          >
            <ListItemIcon>{elem.icon}</ListItemIcon>
            {elem.label}
          </MenuItem>
        ))}
      </Menu>
    </>
  );
};

export default PollSelector;
