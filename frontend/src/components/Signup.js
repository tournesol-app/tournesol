/* eslint no-unused-vars: ["error", { "argsIgnorePattern": "^_" }] */

import React, { useState } from 'react';

import { useHistory } from 'react-router-dom';
import { makeStyles } from '@material-ui/core/styles';
import Alert from '@material-ui/lab/Alert';
import Form from '@rjsf/material-ui';
import Button from '@material-ui/core/Button';
import ReCAPTCHA from 'react-google-recaptcha';
import { DRF_RECAPTCHA_PUBLIC_KEY } from '../constants';
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

const recaptchaRef = React.createRef();

function CaptchaWidget(props) {
  return (
    <ReCAPTCHA
      ref={recaptchaRef}
      sitekey={DRF_RECAPTCHA_PUBLIC_KEY}
      onChange={(e) => props.onChange(e)}
    />
  );
}

const formUISchema = {
  password: {
    'ui:widget': 'password',
  },
  password2: {
    'ui:widget': 'password',
  },
  recaptcha: {
    'ui:widget': CaptchaWidget,
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

  const saveFormData = (e) => {
    const api = new TournesolAPI.LoginSignupApi();
    const data = e.formData;

    undefinedToNullValue(data);

    api.loginSignupRegisterCreate(data,
      (err, _data) => {
        setError(err ? formatError(err) : false);
        setSuccess(!err);
        setFormData(data);

        // reload page on success
        if (!err) {
          setFormData(null);
          setRequested(false);
          setJsonError(null);
          history.push(`/email_show_instructions/${data.email}`);
        } else {
          setJsonError(errorToJsonError(err));
        }

        // reset captcha #354
        recaptchaRef.current.reset();
      });
  };

  // load data
  if (!formData && !requested) {
    setRequested(true);
    getSchema().then((apiSchema) => {
      const apiSchemaTransformed = {
        ...apiSchema, // eslint-disable-line no-param-reassign
        ...apiSchema.components.schemas.Register,
      };

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
          <Alert severity="error" className="class_error_data_save">Error saving data: {error}</Alert>}

          <Button color="primary" variant="contained" type="submit">Register</Button>
          &nbsp;
          <Button color="secondary" variant="contained" onClick={() => history.push('/privacy_policy')}>Privacy policy</Button>
        </Form>
      )}

    </div>
  );
};
