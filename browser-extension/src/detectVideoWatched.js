/**
 * Auto-detect when a video has been watched on YouTube and mark it as
 * watched on the user's Tournesol contributor rating.
 *
 * A video is considered watched when at least WATCHED_FRACTION of its
 * duration has been played. This matches the frontend's behavior in
 * EntityImagery.tsx.
 *
 * This content script is meant to be run on each YouTube video page.
 */

// Matches the frontend's WATCHED_FRACTION in EntityImagery.tsx
const WATCHED_FRACTION = 0.6;
const PROGRESS_TICK_MS = 1000;

// Holds the cleanup function for the current watch progress tracking,
// so it can be called on SPA navigation before setting up a new one.
let cleanupWatchProgressTracking = null;

document.addEventListener('yt-navigate-finish', onNavigateFinish);

function onNavigateFinish() {
  if (cleanupWatchProgressTracking) {
    cleanupWatchProgressTracking();
    cleanupWatchProgressTracking = null;
  }

  const videoId = new URL(location.href).searchParams.get('v');

  // Only enable on youtube.com/watch?v=* pages
  if (!location.pathname.startsWith('/watch') || !videoId) return;

  chrome.storage.local.get(['access_token'], (items) => {
    if (!items.access_token) return;

    cleanupWatchProgressTracking = startWatchProgressTracking(() => {
      chrome.runtime.sendMessage({
        message: 'updateContributorRatingEntitySeen',
        videoId: videoId,
        entitySeen: true,
      });
    });
  });
}

/**
 * Track how many seconds of the video have been played and call the
 * provided callback when the watched fraction threshold is reached.
 *
 * This accumulates actual playing time (accounting for playback rate),
 * matching the frontend's behavior in EntityImagery.tsx.
 *
 * Returns a cleanup function that removes event listeners and clears
 * the interval. Must be called on SPA navigation before setting up
 * a new tracker.
 */
function startWatchProgressTracking(onWatchThresholdReached) {
  let secondsPlayed = 0;
  let progressInterval = null;

  function onVideoPlaying() {
    if (progressInterval) return;

    progressInterval = window.setInterval(() => {
      const video = document.querySelector('video');
      if (!video || video.paused) {
        stopInterval();
        return;
      }

      // YouTube uses the same <video> element for ads and the actual
      // content. Skip ticks while an ad is playing.
      const isAdPlaying = !!document.querySelector(
        '.html5-video-player.ad-showing'
      );
      if (isAdPlaying) {
        return;
      }

      secondsPlayed += (video.playbackRate * PROGRESS_TICK_MS) / 1000;

      if (
        video.duration > 0 &&
        secondsPlayed > video.duration * WATCHED_FRACTION
      ) {
        cleanup();
        onWatchThresholdReached();
      }
    }, PROGRESS_TICK_MS);
  }

  function stopInterval() {
    if (progressInterval) {
      window.clearInterval(progressInterval);
      progressInterval = null;
    }
  }

  function onVideoPaused() {
    stopInterval();
  }

  const video = document.querySelector('video');
  if (!video) return () => {};

  function cleanup() {
    stopInterval();
    video.removeEventListener('playing', onVideoPlaying);
    video.removeEventListener('pause', onVideoPaused);
  }

  video.addEventListener('playing', onVideoPlaying);
  video.addEventListener('pause', onVideoPaused);

  // If the video is already playing when the tracker starts
  if (!video.paused) {
    onVideoPlaying();
  }

  return cleanup;
}
