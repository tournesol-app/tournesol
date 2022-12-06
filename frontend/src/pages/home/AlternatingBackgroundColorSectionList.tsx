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

const AlternatingBackgroundColorSectionList = ({
  children,
  secondaryColor = 'white',
  secondaryBackground = '#1282B2',
  itemPadding = '48px',
  firstItemPadding = '32px',
  lastItemIsPrimary,
}: {
  children: React.ReactNode[];
  secondaryColor?: string;
  secondaryBackground?: string;
  // Used to wrap every item.
  itemPadding?: string;
  // Allow the first item to have a different padding.
  firstItemPadding?: string;
  // If true the last item will use the primary color regardless of its
  // position in the list.
  lastItemIsPrimary?: boolean;
}) => {
  const theme = useTheme();

  // children.at(-1) didn't work here...
  const lastItem = children.slice(children.length - 1);

  const colorAtIndex = (idx: number): string => {
    return idx % 2 == 0 ? secondaryColor : theme.palette.text.primary;
  };

  const backgroundColorAtIndex = (idx: number): string => {
    return idx % 2 == 0
      ? secondaryBackground
      : theme.palette.background.primary;
  };

  return (
    <Grid container width="100%">
      {/* display all items except the last one */}
      {children.slice(0, -1).map((child: React.ReactNode, i: number) => (
        <SectionGridItem
          key={i}
          child={child}
          padding={i == 0 ? firstItemPadding : itemPadding}
          color={colorAtIndex(i)}
          background={backgroundColorAtIndex(i)}
        />
      ))}

      {/* display the last item */}
      <SectionGridItem
        child={lastItem}
        padding={itemPadding}
        color={
          lastItemIsPrimary
            ? theme.palette.text.primary
            : colorAtIndex(children.length - 1)
        }
        background={
          lastItemIsPrimary
            ? theme.palette.background.primary
            : backgroundColorAtIndex(children.length - 1)
        }
      />
    </Grid>
  );
};

export default AlternatingBackgroundColorSectionList;
