import React from 'react';

import { Grid, useTheme } from '@mui/material';

const SectionGridItem = ({
  child,
  color,
  background,
}: {
  child: React.ReactNode;
  color: string;
  background: string;
}) => {
  const theme = useTheme();

  return (
    <Grid
      item
      xs={12}
      sx={{
        display: 'flex',
        justifyContent: 'center',
        padding: '48px',
        [theme.breakpoints.down('md')]: {
          padding: '48px 16px 48px 16px',
        },
        color: color,
        background: background,
      }}
    >
      {child}
    </Grid>
  );
};

const AlternatingBackgroundColorSectionList = ({
  children,
  secondaryBackground = '#1282B2',
  secondaryColor = 'white',
  lastItemIsPrimary,
}: {
  children: React.ReactNode[];
  secondaryBackground?: string;
  secondaryColor?: string;
  // If true the last item will use the primary color regardless of its
  // position in the list.
  lastItemIsPrimary?: boolean;
}) => {
  const theme = useTheme();

  const isLastItem = (idx: number) => {
    return idx === children.length - 1;
  };

  return (
    <Grid container width="100%">
      {children.map((child: React.ReactNode, i: number) =>
        isLastItem(i) ? (
          <SectionGridItem
            key={i}
            child={child}
            color={
              lastItemIsPrimary
                ? theme.palette.text.primary
                : i % 2 == 0
                ? secondaryColor
                : theme.palette.text.primary
            }
            background={
              lastItemIsPrimary
                ? theme.palette.background.primary
                : i % 2 == 0
                ? secondaryBackground
                : theme.palette.background.primary
            }
          />
        ) : (
          <SectionGridItem
            key={i}
            child={child}
            color={i % 2 == 0 ? secondaryColor : theme.palette.text.primary}
            background={
              i % 2 == 0
                ? secondaryBackground
                : theme.palette.background.primary
            }
          />
        )
      )}
    </Grid>
  );
};

export default AlternatingBackgroundColorSectionList;
