import React, { useState } from 'react';
import { Grid, TextField, Button } from '@material-ui/core';
import Alert from 'src/components/Alert';
import { ApiError } from 'src/services/openapi/core/ApiError';
import { extractVideoId } from 'src/utils/video';

interface FormProps {
  addVideo: (id: string) => void;
}

const RateLaterAddForm = ({ addVideo }: FormProps) => {
  const [apiError, setApiError] = useState<ApiError | null>(null);
  const [hasSucceeded, setHasSucceeded] = useState(false);
  const [formVideo, setFormVideo] = useState('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setApiError(null);
    setHasSucceeded(false);
    try {
      await addVideo(extractVideoId(formVideo) || '');
      await setFormVideo('');
    } catch (err) {
      console.error('Add to rate later list failed.', `${err}\n`, err.body);
      setApiError(err);
      return;
    }
    setHasSucceeded(true);
  };

  return (
    <form onSubmit={handleSubmit}>
      <Grid
        container
        direction="row"
        justifyContent="center"
        alignItems="center"
        spacing={3}
      >
        <Grid item sm={4}>
          <TextField
            autoFocus
            required
            fullWidth
            placeholder="Video id or URL"
            onChange={(e) => setFormVideo(e.target.value)}
            value={formVideo}
          />
        </Grid>

        <Grid item>
          <Button
            type="submit"
            size="large"
            variant="contained"
            color="primary"
          >
            Add to my rate later list
          </Button>
        </Grid>
      </Grid>

      {hasSucceeded && <Alert>✅ Video added to your Rate Later list!</Alert>}
      {apiError && apiError?.status === 409 && (
        <Alert>⚠️ The video is already in your Rate Later list.</Alert>
      )}
      {apiError && apiError?.status !== 409 && (
        <Alert>❌ An error has occured. {apiError.statusText}</Alert>
      )}
    </form>
  );
};

export default RateLaterAddForm;
