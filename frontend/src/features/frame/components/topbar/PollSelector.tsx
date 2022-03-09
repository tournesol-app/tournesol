import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router';
import {
  Box,
  Grid,
  Link,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Typography,
} from '@mui/material';
import { ArrowDropDown, ArrowDropUp } from '@mui/icons-material';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { getPollName } from 'src/utils/constants';
import { SelectablePoll } from 'src/utils/types';

const PollSelector = ({ polls }: { polls: Array<SelectablePoll> }) => {
  const history = useHistory();
  const { t } = useTranslation();
  const { name: currentPoll, setPollName } = useCurrentPoll();

  const [menuAnchorEl, setMenuAnchorEl] = React.useState<null | HTMLElement>(
    null
  );

  const displayMenu = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchorEl(event.currentTarget);
  };

  const onMenuClose = () => {
    setMenuAnchorEl(null);
  };

  const onItemSelect = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    setPollName(event.currentTarget.dataset.pollName || '');
    history.push(event.currentTarget.dataset.pollUrl || '');
    onMenuClose();
  };

  return (
    <Box
      padding="8px 4px"
      sx={{
        '&:hover': { backgroundColor: 'rgba(29, 26, 20, 0.08)' },
      }}
    >
      {/* use Link to make the area clickable while preserving its accessibility */}
      <Link
        onClick={displayMenu}
        underline="none"
        sx={{
          cursor: 'pointer',
          color: 'text.primary',
        }}
      >
        <Box sx={{ display: { xs: 'none', sm: 'none', md: 'block' } }}>
          <Grid container alignItems="center" spacing={1}>
            <Grid item>
              <img src="/svg/LogoSmall.svg" alt="Tournesol logo" />
            </Grid>
            <Grid item>
              <Typography
                variant="h3"
                sx={{
                  fontSize: '1.4em !important',
                  fontWeight: 'bold',
                  lineHeight: 1,
                }}
              >
                Tournesol
              </Typography>
              <Box display="flex" flexDirection="row" alignItems="center">
                <Typography variant="subtitle1">
                  {getPollName(t, currentPoll)}
                </Typography>
                {menuAnchorEl ? (
                  <ArrowDropUp sx={{ color: 'rgba(0, 0, 0, 0.32)' }} />
                ) : (
                  <ArrowDropDown sx={{ color: 'rgba(0, 0, 0, 0.32)' }} />
                )}
              </Box>
            </Grid>
          </Grid>
        </Box>
        <Box sx={{ display: { sm: 'block', md: 'none' } }}>
          <img src="/svg/LogoSmall.svg" alt="Tournesol logo" />
        </Box>
      </Link>
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={onMenuClose}
      >
        {polls
          .sort((a, b) => a.displayOrder - b.displayOrder)
          .map((elem: SelectablePoll) => (
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
              <ListItemText>{getPollName(t, elem.name)}</ListItemText>
            </MenuItem>
          ))}
      </Menu>
    </Box>
  );
};

export default PollSelector;
