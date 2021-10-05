import React, { useState, useEffect } from 'react';
import { TextField } from '@material-ui/core';
import Lines from './Lines';

interface Props {
  name: string;
  label: string;
  formError: Record<string, string[]>;
  [propName: string]: unknown;
}

const FormTextField = ({ name, label, formError, ...rest }: Props) => {
  const errorMessages = formError?.[name];
  const [showError, setShowError] = useState(false);

  useEffect(() => {
    setShowError(!!errorMessages);
  }, [errorMessages]);

  return (
    <TextField
      required
      fullWidth
      label={label}
      name={name}
      color="secondary"
      size="small"
      variant="outlined"
      error={showError}
      helperText={showError && <Lines messages={errorMessages} />}
      onChange={() => setShowError(false)}
      {...rest}
    />
  );
};

export default FormTextField;
