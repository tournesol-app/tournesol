import React from 'react';

import { Box, Divider, Grid, Typography } from '@mui/material';

const SettingsSection = ({
  title,
  children,
  ...rest
}: {
  title: string | React.ReactNode;
  children: React.ReactNode;
  [rest: string]: unknown;
}) => {
  /*
   * A component that displays a children component (often a form)
   * under a title
   */
  const sectionTitle =
    typeof title === 'string' ? (
      <Typography variant="h4" color="secondary">
        {title}
      </Typography>
    ) : (
      title
    );

  return (
    <Grid item container>
      <Grid item xs={12}>
        <Box marginBottom={2}>
          {sectionTitle}
          <Divider />
        </Box>
      </Grid>
      <Grid item {...rest}>
        {children}
      </Grid>
    </Grid>
  );
};

export default SettingsSection;
