/* eslint no-unused-vars: ["error", { "argsIgnorePattern": "^_" }] */

import React, { useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Alert from '@material-ui/lab/Alert';
import Form from '@rjsf/material-ui';
import Button from '@material-ui/core/Button';
import { deleteFrom } from '../utils';
import {
  errorToJsonError,
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

// do not show these fields
const ignoreFields = ['id'];

export default () => {
  const classes = useStyles();

  const [formData, setFormData] = useState({ username: window.username });
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);
  const [jsonError, setJsonError] = useState(null);
  const [JSONSchema, setJSONSchema] = useState(null);
  const [requested, setRequested] = useState(false);

  const saveFormData = (e) => {
    const api = new TournesolAPI.LoginSignupApi();
    const data = e.formData;

    undefinedToNullValue(data);

    api.loginSignupPartialUpdate(window.user_information_id, { patchedOnlyUsernameAndID: data },
      (err, _data) => {
        setError(err ? formatError(err) : false);
        setSuccess(!err);
        setFormData(data);

        // reload page on success
        if (!err) {
          setRequested(false);
          setJsonError(null);
          window.history.pushState({}, '', '/');
          window.location.reload();
        } else {
          setJsonError(errorToJsonError(err));
        }
      });
  };

  // load data
  if (!requested) {
    setRequested(true);
    getSchema().then((apiSchema) => {
      const apiSchemaTransformed = {
        ...apiSchema, // eslint-disable-line no-param-reassign
        ...apiSchema.components.schemas.PatchedOnlyUsernameAndID,
      };

      deleteFrom(apiSchemaTransformed.properties, ignoreFields);
      const formJSON = fromOpenAPIToJsonSchema(apiSchemaTransformed);
      setJSONSchema(formJSON);
    });

    return <div className={classes.root}>Loading...</div>;
  }

  return (
    <div className={classes.root}>
      {JSONSchema && (
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
        <Alert severity="error" className="class_error_data_save">Error changing login name: {error}</Alert>}

        <Button color="primary" variant="contained" type="submit" id="change_login_name">
          Change login name
        </Button>
      </Form>
      )}
    </div>
  );
};
