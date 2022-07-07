import React from 'react';
import { Box, Chip, Grid, Typography } from '@mui/material';

/**
 * Display a header.
 *
 * Used to display the main title of nearly every page.
 *
 * If `chipLabel` is provided, display a MUI <Chip> at the end of the
 * header.
 */
const ContentHeader = ({
  title,
  chipIcon,
  chipLabel,
}: {
  title: string;
  chipIcon?: React.ReactElement;
  chipLabel?: string;
}) => {
  return (
    <Box
      px={[2, 4]}
      py={2}
      color="text.secondary"
      bgcolor="background.menu"
      borderBottom="1px solid rgba(0, 0, 0, 0.12)"
    >
      <Grid container spacing={1} justifyContent="space-between">
        <Grid item>
          <Typography variant="h4">{title}</Typography>
        </Grid>
        {/* The <ContentHeader> component could use a list of <Chip> instead
            of only one. */}
        {chipLabel && (
          <>
            <Grid item>
              <Chip
                icon={chipIcon}
                color="secondary"
                label={chipLabel}
                variant="outlined"
              />
            </Grid>
          </>
        )}
      </Grid>
    </Box>
  );
};

export default ContentHeader;
