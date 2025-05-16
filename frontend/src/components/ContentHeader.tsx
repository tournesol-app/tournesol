import React from 'react';
import { Box, Grid, Typography } from '@mui/material';

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
  subtitle,
}: {
  title: string;
  subtitle?: React.ReactNode;
}) => {
  return (
    <Box
      sx={{
        px: [2, 4],
        pt: 2,
        color: 'text.secondary',
      }}
    >
      <Grid
        container
        spacing={1}
        sx={{
          justifyContent: 'space-between',
        }}
      >
        <Grid item>
          <Typography
            variant="h4"
            component="h2"
            sx={(theme) => ({
              textDecorationLine: 'underline',
              textDecorationColor: theme.palette.primary.light,
              textDecorationThickness: '0.6em',
              textDecorationSkipInk: 'none',
              textUnderlineOffset: '-0.1em',
            })}
          >
            {title}
          </Typography>
        </Grid>
      </Grid>
      {subtitle && (
        <Typography
          sx={{
            mt: 1,
          }}
        >
          {subtitle}
        </Typography>
      )}
    </Box>
  );
};

export default ContentHeader;
