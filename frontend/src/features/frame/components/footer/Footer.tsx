import React from 'react';

import {
  Box,
  Divider,
  List,
  ListItem,
  ListItemText,
  Typography,
} from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2';

const Footer = () => {
  return (
    <Box padding={2} color="#fff" bgcolor="#1282B2">
      <Grid
        container
        spacing={2}
        justifyContent="space-around"
        alignContent="center"
      >
        <Grid xs={12} sm={6} lg={2}>
          <Typography variant="h6" fontSize={14}>
            Get recommendations
          </Typography>
          <List dense={true}>
            <ListItem>
              <ListItemText primary="Single-line item" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Chrome extension" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Firefox extension" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Twitter Bot EN" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Twitter Bot FR" />
            </ListItem>
          </List>
          <Box sx={{ display: { xs: 'block', sm: 'none' } }}>
            <Divider sx={{ backgroundColor: '#fff' }} />
          </Box>
        </Grid>
        <Grid xs={12} sm={6} lg={2}>
          <Typography variant="h6" fontSize={14}>
            Follow Us
          </Typography>
          <List dense={true}>
            <ListItem>
              <ListItemText primary="Discord" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Twitter" />
            </ListItem>
            <ListItem>
              <ListItemText primary="YouTube" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Science4all" />
            </ListItem>
          </List>
          <Box sx={{ display: { xs: 'block', sm: 'none' } }}>
            <Divider sx={{ backgroundColor: '#fff' }} />
          </Box>
        </Grid>
        <Grid xs={12} sm={6} lg={2}>
          <Typography variant="h6" fontSize={14}>
            Support Us
          </Typography>
          <List dense={true}>
            <ListItem>
              <ListItemText primary="Direct Transfer" />
            </ListItem>
            <ListItem>
              <ListItemText primary="uTip" />
            </ListItem>
            <ListItem>
              <ListItemText primary="PayPal" />
            </ListItem>
          </List>
          <Box sx={{ display: { xs: 'block', sm: 'none' } }}>
            <Divider sx={{ backgroundColor: '#fff' }} />
          </Box>
        </Grid>
        <Grid xs={12} sm={6} lg={2}>
          <Typography variant="h6" fontSize={14}>
            Research
          </Typography>
          <List dense={true}>
            <ListItem>
              <ListItemText primary="Paper 1" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Paper 2" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Public Dataset" />
            </ListItem>
          </List>
          <Box sx={{ display: { xs: 'block', sm: 'none' } }}>
            <Divider sx={{ backgroundColor: '#fff' }} />
          </Box>
        </Grid>
        <Grid xs={12} sm={6} lg={2}>
          <Typography variant="h6" fontSize={14}>
            More
          </Typography>
          <List dense={true}>
            <ListItem>
              <ListItemText primary="Privacy Policy" />
            </ListItem>
            <ListItem>
              <ListItemText primary="FAQ" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Wiki" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Source code" />
            </ListItem>
          </List>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Footer;
