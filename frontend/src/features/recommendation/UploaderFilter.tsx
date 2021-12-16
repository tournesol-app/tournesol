import React from 'react';
import { Box, Button } from '@material-ui/core';
import { FilterSection } from 'src/components';

interface Props {
  value: string;
  onChange: () => void;
}

function UploaderFilter(props: Props) {
  return (
    <FilterSection title="Uploader">
      <Box
        display="flex"
        flexDirection="column"
        style={{ textAlign: 'center' }}
      >
        <span style={{ padding: 4 }}>Uploader: {props.value}</span>
        <Button
          type="submit"
          size="large"
          variant="contained"
          color="primary"
          onClick={props.onChange}
        >
          <span>Reset</span>
        </Button>
      </Box>
    </FilterSection>
  );
}

export default UploaderFilter;
