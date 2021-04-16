import React from 'react';
import YouTube from 'react-youtube';
import ReactPlayer from 'react-player/youtube';
import { youtubeVideoIdRegexSymbol } from './constants';

// variables starting with underscore can be unused
/* eslint no-unused-vars: ["error", { "argsIgnorePattern": "^_" }] */

// Function found on Stackoverflow. At:
// https://stackoverflow.com/questions/42202611/how-to-validate-a-youtube-url-using-js
// eslint-disable-next-line import/prefer-default-export
export const getVideoIdFromURL = (url) => {
  if (typeof url !== 'string') return '';
  const a = document.createElement('A');
  a.href = url;
  const host = a.hostname;
  const srch = a.search;
  const path = a.pathname;

  let returnValue = '';
  const regexpSymbol = youtubeVideoIdRegexSymbol;
  let notRegexpSymbol = '';

  if (regexpSymbol[0] === '[' && regexpSymbol[regexpSymbol.length - 1] === ']') {
    notRegexpSymbol = `[^${regexpSymbol.slice(1, regexpSymbol.length - 1)}]`;
  }

  if (host.search(/youtube\.com|youtu\.be/) === -1) return false;
  if (host.search(/youtu\.be/) !== -1) {
    returnValue = path.slice(1);
  } else if (path.search(/embed/) !== -1) {
    const regexp = new RegExp(`embed/(${regexpSymbol}+)(&|$)`);
    // eslint-disable-next-line prefer-destructuring
    returnValue = regexp.exec(path)[1];
  } else {
    const regexp = new RegExp(`v=(${regexpSymbol}+)(&|$)`);
    const getId = regexp.exec(srch);
    if (host.search(/youtube\.com/) !== -1) {
      returnValue = !getId ? '' : getId[1];
    }
  }
  const regexp1 = new RegExp(notRegexpSymbol, 'g');
  returnValue = returnValue.replace(regexp1, '');
  returnValue = returnValue.substring(0, 20);
  return returnValue;
};

export function deleteFrom(arr, toDelete) {
  // delete elements from a dictionary
  toDelete.forEach((k) => {
    // eslint-disable-next-line no-param-reassign
    delete arr[k];
  });
}

// show the appropriate player
export const YoutubePlayer = ({ videoId, width = 250, light = false,
  height = 142, lightAutoplay = 1 }) => {
  if (window.ENABLE_YOUTUBE_VIDEO_EMBED !== 1) {
    return (
      <span className={`youtube-${videoId}`}>
        YouTube {videoId}
        light={light}
      </span>);
  }

  const opts = {
    height,
    width,
    playerVars: {
    // https://developers.google.com/youtube/player_parameters
      autoplay: 0,
    },
  };

  if (light) {
    return <ReactPlayer
      url={`https://youtube.com/watch?v=${videoId}`}
      controls
      light
      width={opts.width}
      config={{
        youtube: {
          playerVars: { autoplay: lightAutoplay },
        } }}
      height={opts.height}
    />;
  }

  return <YouTube key={videoId} videoId={videoId} opts={opts} />;
};
