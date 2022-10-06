import React from 'react';

import { Grid, useTheme } from '@mui/material';

const AlternatingBackgroundColorSectionList = ({
  children,
  secondaryBackground = '#1282B2',
  secondaryColor = 'white',
}: {
  children: React.ReactNode[];
  secondaryBackground?: string;
  secondaryColor?: string;
}) => {
  const theme = useTheme();

  return (
    <div
      style={{
        width: '100%',
        paddingBottom: 32,
      }}
    >
      <Grid container>
        {children.map((child: React.ReactNode, i: number) => (
          <Grid
            key={i}
            item
            xs={12}
            sx={{
              display: 'flex',
              justifyContent: 'center',
              padding: '32px',
              [theme.breakpoints.down('md')]: {
                padding: '32px 16px 32px 16px',
              },
              background: i % 2 == 0 ? secondaryBackground : '#FAF8F3',
              color: i % 2 == 0 ? secondaryColor : 'black',
            }}
          >
            {child}
          </Grid>
        ))}
      </Grid>
    </div>
  );
};

export default AlternatingBackgroundColorSectionList;
