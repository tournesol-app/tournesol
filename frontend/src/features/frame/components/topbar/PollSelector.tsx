import React from 'react';
import { useHistory } from 'react-router';
import {
  Button,
  Grid,
  Hidden,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Typography,
} from '@mui/material';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { polls } from 'src/utils/constants';

const PollSelector = () => {
  const history = useHistory();
  const { name: currentPoll, setPollName } = useCurrentPoll();

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
    setPollName(event.currentTarget.dataset.pollName || '');
    history.push(event.currentTarget.dataset.pollUrl || '');
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
        {polls
          .sort((a, b) => a.displayOrder - b.displayOrder)
          .map((elem) => (
            <MenuItem
              key={elem.name}
              data-poll-url={elem.path}
              data-poll-name={elem.name}
              onClick={onItemSelect}
              selected={elem.name === currentPoll}
            >
              <ListItemIcon>
                <elem.iconComponent fontSize="small" />
              </ListItemIcon>
              <ListItemText>{elem.displayName}</ListItemText>
            </MenuItem>
          ))}
      </Menu>
    </>
  );
};

export default PollSelector;
