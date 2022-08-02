import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Grid, TextField, Button } from '@mui/material';
import { extractVideoId } from 'src/utils/video';

interface FormProps {
  addVideo: (id: string) => Promise<boolean>;
}

const RateLaterAddForm = ({ addVideo }: FormProps) => {
  const [formVideo, setFormVideo] = useState('');
  const { t } = useTranslation();

  /**
   * The potential API errors raised by the function `addVideo` are not caught
   * here, and are considered already handled by the function itself.
   */
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const success = await addVideo(extractVideoId(formVideo) || formVideo);
    if (success) {
      setFormVideo('');
    }
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
        <Grid item>
          <TextField
            autoFocus
            required
            fullWidth
            placeholder={t('ratelater.videoIdOrURL')}
            onChange={(e) => setFormVideo(e.target.value)}
            value={formVideo}
            variant="standard"
          />
        </Grid>

        <Grid item>
          <Button
            type="submit"
            size="large"
            variant="contained"
            color="primary"
          >
            {t('ratelater.addToMyRateLaterList')}
          </Button>
        </Grid>
      </Grid>
    </form>
  );
};

export default RateLaterAddForm;
