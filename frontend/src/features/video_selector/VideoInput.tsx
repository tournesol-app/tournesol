import React, { useRef, useState } from 'react';
import {
  Box,
  TextField,
  ClickAwayListener,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { ArrowDropDown } from '@mui/icons-material';
import { VideoRequest, VideoService } from 'src/services/openapi';
import SelectorListBox from './SelectorListbox';
import { VideoCardFromId } from '../videos/VideoCard';
import SelectorPopper from './SelectorPopper';
import { useTranslation } from 'react-i18next';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

const VideoInput = ({ value, onChange }: Props) => {
  const { t } = useTranslation();
  const [inputValue, setInputValue] = useState(value);
  const [suggestionsOpen, setSuggestionsOpen] = useState(false);
  const inputRef = useRef(null);

  const handleNewValue = (value: string) => {
    setInputValue(value);
    onChange(value);
  };

  const handleOptionClick = (video: VideoRequest) => {
    handleNewValue(video.video_id);
    setSuggestionsOpen(false);
  };

  const [options, setOptions] = React.useState<VideoRequest[]>([]);
  const optionsLoading = options.length === 0;

  React.useEffect(() => {
    let active = true;

    if (!optionsLoading) {
      return undefined;
    }

    (async () => {
      const response = await VideoService.videoList({ limit: 10 });

      if (active) {
        setOptions(response.results ?? []);
      }
    })();

    return () => {
      active = false;
    };
  }, [optionsLoading]);

  const toggleSuggestions = () => setSuggestionsOpen(!suggestionsOpen);

  const SuggestionsContainer = SelectorPopper;

  return (
    <ClickAwayListener onClickAway={() => setSuggestionsOpen(false)}>
      <Box>
        <TextField
          fullWidth
          ref={inputRef}
          value={inputValue}
          placeholder={t('videoSelector.pasteUrlOrVideoId')}
          onChange={(e) => handleNewValue(e.target.value)}
          variant="standard"
          onFocus={() => setSuggestionsOpen(true)}
          // onBlur={() => setSuggestionsOpen(false)}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={toggleSuggestions}
                  size="small"
                  sx={{
                    ...(suggestionsOpen && {
                      transform: 'rotate(180deg)',
                    }),
                  }}
                >
                  <ArrowDropDown />
                </IconButton>
              </InputAdornment>
            ),
            sx: (theme) => ({
              [theme.breakpoints.down('sm')]: {
                fontSize: '0.7rem',
              },
            }),
          }}
        />
        <SuggestionsContainer
          open={suggestionsOpen}
          anchorEl={inputRef.current}
        >
          <SelectorListBox>
            {options.map((o) => (
              <li key={o.video_id} onClick={() => handleOptionClick(o)}>
                <VideoCardFromId videoId={o.video_id} variant="row" />
              </li>
            ))}
          </SelectorListBox>
        </SuggestionsContainer>
      </Box>
    </ClickAwayListener>
  );
};

export default VideoInput;
