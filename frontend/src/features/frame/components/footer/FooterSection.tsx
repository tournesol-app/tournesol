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
import { GridSize } from '@mui/system';

interface Props {
  xs?: GridSize;
  sm?: GridSize;
  lg?: GridSize;
  title: string;
  items: Array<string>;
  trailingDivider?: boolean;
}

/**
 * A section of the footer.
 *
 * This section is displayed as a Grid2 item.
 */
const FooterSection = ({
  xs = 12,
  sm = 6,
  lg = 2,
  title,
  items,
  trailingDivider = true,
}: Props) => {
  return (
    <Grid xs={xs} sm={sm} lg={lg}>
      <Typography variant="h6" fontSize={14}>
        {title}
      </Typography>
      <List dense={true}>
        {items.map((item) => (
          <ListItem key={item}>
            <ListItemText primary={item} />
          </ListItem>
        ))}
      </List>
      {trailingDivider && (
        <Box sx={{ display: { xs: 'block', sm: 'none' } }}>
          <Divider sx={{ backgroundColor: '#fff' }} />
        </Box>
      )}
    </Grid>
  );
};

export default FooterSection;
