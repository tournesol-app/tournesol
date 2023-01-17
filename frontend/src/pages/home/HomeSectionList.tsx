import React from 'react';

import { Grid, useTheme } from '@mui/material';

const SectionGridItem = ({
  child,
  color,
  background,
  padding,
}: {
  child: React.ReactNode;
  color: string;
  background: string;
  padding: string;
}) => {
  const theme = useTheme();

  return (
    <Grid
      item
      xs={12}
      sx={{
        display: 'flex',
        justifyContent: 'center',
        padding: padding,
        [theme.breakpoints.down('md')]: {
          p: padding,
          px: { xs: '16px', md: padding },
        },
        color: color,
        background: background,
      }}
    >
      {child}
    </Grid>
  );
};

const HomeSectionList = ({
  children,
  secondaryColor = 'white',
  secondaryBackground = '#1282B2',
  itemPadding = '48px',
  firstItemPadding = '32px',
}: {
  children: React.ReactNode[];
  secondaryColor?: string;
  secondaryBackground?: string;
  // Used to wrap every item.
  itemPadding?: string;
  // Allow the first item to have a different padding.
  firstItemPadding?: string;
}) => {
  const theme = useTheme();

  const colorAtIndex = (idx: number): string => {
    return idx === 0 ? secondaryColor : theme.palette.text.primary;
  };

  const backgroundColorAtIndex = (idx: number): string => {
    return idx === 0 ? secondaryBackground : theme.palette.background.primary;
  };

  return (
    <Grid container width="100%">
      {children.map((child: React.ReactNode, i: number) => (
        <SectionGridItem
          key={i}
          child={child}
          padding={i == 0 ? firstItemPadding : itemPadding}
          color={colorAtIndex(i)}
          background={backgroundColorAtIndex(i)}
        />
      ))}
    </Grid>
  );
};

export default HomeSectionList;
