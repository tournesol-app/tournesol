import React from 'react';

import { Box, Divider, Grid2, Typography } from '@mui/material';

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
    <Grid2 container>
      <Grid2 size={{ xs: 12 }}>
        <Box
          sx={{
            marginBottom: 2,
          }}
        >
          {sectionTitle}
          <Divider />
        </Box>
      </Grid2>
      <Grid2 size={rest}>{children}</Grid2>
    </Grid2>
  );
};

export default SettingsSection;
