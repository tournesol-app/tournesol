/* eslint no-unused-vars: ["error", { "argsIgnorePattern": "^_" }] */

import React, { useState } from 'react';

import CircularProgress from '@material-ui/core/CircularProgress';
import { useHistory } from 'react-router-dom';
import { makeStyles } from '@material-ui/core/styles';
import Alert from '@material-ui/lab/Alert';
import Form from '@rjsf/material-ui';
import Button from '@material-ui/core/Button';
import LockOpenIcon from '@material-ui/icons/LockOpen';
import {
  formatError,
  fromOpenAPIToJsonSchema,
  getSchema,
  TournesolAPI,
  undefinedToNullValue,
} from '../api';

const useStyles = makeStyles(() => ({
  root: {
    display: 'flex',
    width: '900px',
    maxWidth: '100%',
    height: '100%',
    overflowY: 'auto',
    overflowX: 'hidden',
    flexDirection: 'column',
    padding: '8px',
  },
}));

const formUISchema = {
  password: {
    'ui:widget': 'password',
  },
};

export default () => {
  const classes = useStyles();
  const history = useHistory();

  const [formData, setFormData] = useState(null);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);
  const [jsonError, setJsonError] = useState(null);
  const [JSONSchema, setJSONSchema] = useState(null);
  const [requested, setRequested] = useState(false);
  const [pending, setPending] = useState(false);

  const saveFormData = (e) => {
    const api = new TournesolAPI.LoginSignupApi();
    const data = e.formData;

    undefinedToNullValue(data);
    setPending(true);

    api.loginSignupLoginPartialUpdate({ patchedLogin: data },
      (err, _data) => {
        setError(err ? formatError(err) : false);
        setSuccess(!err);
        setFormData(data);

        // reload page on success
        if (!err) {
          setFormData(null);
          setRequested(false);
          setJsonError(null);
          window.history.pushState({}, '', '/');
          window.location.reload();
        } else {
          setPending(false);
          setJsonError({ username: { __errors: ['Login failed. Please check your username and the password'] } });
        }
      });
  };

  // load data
  if (!formData && !requested) {
    setRequested(true);
    getSchema().then((apiSchema) => {
      const apiSchemaTransformed = {
        ...apiSchema, // eslint-disable-line no-param-reassign
        ...apiSchema.components.schemas.PatchedLogin,
      };

      const formJSON = fromOpenAPIToJsonSchema(apiSchemaTransformed);
      setJSONSchema(formJSON);
    });

    return <div className={classes.root}>Loading...</div>;
  }

  return (
    <div className={classes.root}>
      {pending ? (
        <p>Logging in...<br />
          <CircularProgress />
        </p>
      ) :
        (JSONSchema && (
        <Form
          schema={JSONSchema}
          formData={formData}
          uiSchema={formUISchema}
          onSubmit={saveFormData}
          extraErrors={jsonError}
          noValidate
        >
          {success && (
          <>
            <Alert severity="success" className="class_success_data_save">Data saved
              <Button onClick={() => window.location.reload()}>
                Refresh
              </Button>
            </Alert>
          </>
          )}
          {error && !success &&
          <Alert severity="error" className="class_error_data_save">Error logging in: {error}</Alert>}

          <Button color="primary" variant="contained" type="submit" id="submit-id-submit">Log in</Button>
              &nbsp;
          <Button
            variant="outlined"
            color="secondary"
            id="id_reset_password"
            onClick={() => history.push('/reset_password')}
          >
            <LockOpenIcon />
            Forgot my password
          </Button>

        </Form>
        ))}

    </div>
  );
};
