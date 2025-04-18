import React from 'react';

import {
  Box,
  Divider,
  Grid2,
  List,
  ListItemButton,
  ListItemText,
  Typography,
} from '@mui/material';
import { GridSize } from '@mui/system';

interface Props {
  xs?: GridSize;
  sm?: GridSize;
  lg?: GridSize;
  title: string;
  items: Array<{ name: string; to: string }>;
  disableItemsGutters?: boolean;
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
  disableItemsGutters = false,
  trailingDivider = true,
}: Props) => {
  return (
    <Grid2
      size={{
        xs: xs,
        sm: sm,
        lg: lg,
      }}
    >
      <Typography
        variant="h6"
        sx={{
          fontSize: 14,
        }}
      >
        {title}
      </Typography>
      <List dense={true}>
        {items.map((item) => (
          <ListItemButton
            key={item.name}
            href={item.to}
            disableGutters={disableItemsGutters}
          >
            <ListItemText primary={item.name} />
          </ListItemButton>
        ))}
      </List>
      {trailingDivider && (
        <Box sx={{ display: { xs: 'block', sm: 'none' } }}>
          <Divider sx={{ backgroundColor: '#fff' }} />
        </Box>
      )}
    </Grid2>
  );
};

export default FooterSection;
