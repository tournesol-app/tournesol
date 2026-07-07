/**
 * Display a banner on YouTube video pages, inviting authenticated users to
 * choose what the extension should do when they watch a video, as long as
 * their `extension__on_video_watched` setting is not set.
 *
 * Choosing any option saves the setting on the user's Tournesol account,
 * which permanently hides the banner. Choosing "do nothing" keeps the
 * default behavior and acts as "don't ask me again".
 *
 * This content script is meant to be run on each YouTube video page.
 */

const BANNER_ID = 'ts-on-video-watched-banner';
// The banner is inserted just before the Tournesol video actions row,
// created by addVideoButtons.js.
const BANNER_BEFORE_REF = 'ts-video-actions-row';

const SETTING_NAME = 'extension__on_video_watched';

// Also defined in detectVideoWatched.js, which listens for this event to
// start tracking the watch progress of the current video without waiting
// for the next navigation.
const SETTING_SAVED_EVENT = 'tournesol:onVideoWatchedSettingSaved';

const SETTING_CHOICES = [
  {
    value: 'MARK_AS_WATCHED',
    labelKey: 'onVideoWatchedMarkAsWatched',
  },
  {
    value: 'MARK_AS_WATCHED_AND_RATE_LATER',
    labelKey: 'onVideoWatchedMarkAsWatchedAndRateLater',
  },
  {
    value: 'DO_NOTHING',
    labelKey: 'onVideoWatchedDoNothing',
    className: 'ts-on-video-watched-choice-do-nothing',
  },
];

let insertBannerTimer = null;

document.addEventListener('yt-navigate-finish', onNavigateFinish);

function onNavigateFinish() {
  if (insertBannerTimer) {
    window.clearInterval(insertBannerTimer);
    insertBannerTimer = null;
  }
  removeBanner();

  // Only enable on youtube.com/watch pages
  if (!location.pathname.startsWith('/watch')) return;

  chrome.storage.local.get(['access_token'], (items) => {
    if (!items.access_token) return;

    chrome.runtime.sendMessage({ message: 'getUserSettings' }, (settings) => {
      // Don't display the banner when the settings can't be retrieved, to
      // avoid proposing the choice based on unknown user preferences.
      if (!settings?.success) return;

      const settingValue = settings.body?.videos?.[SETTING_NAME];
      if (settingValue) return;

      insertBannerWhenActionsRowIsReady();
    });
  });
}

function insertBannerWhenActionsRowIsReady() {
  insertBannerTimer = window.setInterval(() => {
    const actionsRow = document.getElementById(BANNER_BEFORE_REF);
    if (!actionsRow) return;

    window.clearInterval(insertBannerTimer);
    insertBannerTimer = null;

    removeBanner();
    actionsRow.parentNode.insertBefore(createBanner(), actionsRow);
  }, 300);
}

function createBanner() {
  const banner = document.createElement('div');
  banner.id = BANNER_ID;

  const question = document.createElement('span');
  question.className = 'ts-on-video-watched-question';
  question.textContent = chrome.i18n.getMessage('onVideoWatchedQuestion');
  banner.appendChild(question);

  const choices = document.createElement('div');
  choices.className = 'ts-on-video-watched-choices';
  banner.appendChild(choices);

  SETTING_CHOICES.forEach(({ value, labelKey, className }) => {
    const button = document.createElement('button');
    button.className = 'ts-on-video-watched-choice';
    if (className) button.classList.add(className);
    button.textContent = chrome.i18n.getMessage(labelKey);
    button.onclick = () => saveSetting(banner, value);
    choices.appendChild(button);
  });

  return banner;
}

function saveSetting(banner, value) {
  const buttons = banner.querySelectorAll('button');
  buttons.forEach((button) => (button.disabled = true));

  chrome.runtime.sendMessage(
    { message: 'updateSetting', name: SETTING_NAME, value: value },
    (response) => {
      if (response?.success) {
        removeBanner();
        document.dispatchEvent(new CustomEvent(SETTING_SAVED_EVENT));
      } else {
        buttons.forEach((button) => (button.disabled = false));
      }
    }
  );
}

function removeBanner() {
  const banner = document.getElementById(BANNER_ID);
  if (banner) banner.remove();
}
