import { isNavigatorLang } from '../../utils.js';
import { defaultBannerOptions } from './BannerOptions.js';

/**
 * A banner displaying a message and an action button.
 *
 * At the moment this class is specific to the extension research study, but
 * could be refactored to be generic.
 *
 * - the texts could be parameters of the constructor
 * - the action button could be optional
 * - etc.
 */
export class Banner {
  constructor(options = defaultBannerOptions) {
    this.TS_BANNER_DATE_START = options.TS_BANNER_DATE_START;
    this.TS_BANNER_DATE_END = options.TS_BANNER_DATE_END;
    this.TS_BANNER_ACTION_FR_URL = options.TS_BANNER_ACTION_FR_URL;
    this.TS_BANNER_ACTION_EN_URL = options.TS_BANNER_ACTION_EN_URL;
    this.TS_BANNER_PROOF_KW = options.TS_BANNER_PROOF_KW;

    // Create the banner at the initialisation.
    this.element = this.createBanner();
  }

  display() {
    this.element.classList.add('displayed');
  }

  hide() {
    this.element.classList.remove('displayed');
  }

  bannerShouldBeDisplayed() {
    const now = new Date();

    if (this.TS_BANNER_DATE_START <= now && now <= this.TS_BANNER_DATE_END) {
      return true;
    }

    return false;
  }

  createBanner() {
    const banner = document.createElement('div');
    banner.id = 'tournesol_banner';
    banner.className = 'tournesol_banner';

    // Only display the banner if the user didn't explicitly close it.
    chrome.storage.local.get(
      'displayBannerStudy2023',
      ({ displayBannerStudy2023 }) => {
        if ([true, null, undefined].includes(displayBannerStudy2023)) {
          this.display();
        }
      }
    );

    // The first flex item is the campaign icon.
    const bannerIconContainer = document.createElement('div');
    const icon = document.createElement('img');
    icon.id = 'tournesol_banner_icon';
    icon.setAttribute('src', chrome.runtime.getURL('images/campaign.svg'));
    icon.setAttribute('alt', 'Megaphone icon');
    bannerIconContainer.append(icon);

    // The second flex item is the text.
    const bannerTextContainer = document.createElement('div');
    const bannerText = document.createElement('p');
    bannerText.textContent = chrome.i18n.getMessage('study2023BannerText');
    bannerTextContainer.append(bannerText);

    // The third flex item is the action button.
    const actionButtonContainer = document.createElement('div');
    const actionButton = document.createElement('a');
    actionButton.textContent = chrome.i18n.getMessage('study2023ActionButton');
    actionButton.className = 'tournesol_mui_like_button';
    actionButton.setAttribute(
      'href',
      isNavigatorLang('fr')
        ? this.TS_BANNER_ACTION_FR_URL
        : this.TS_BANNER_ACTION_EN_URL
    );
    actionButton.setAttribute('target', '_blank');
    actionButton.setAttribute('rel', 'noopener');

    // The last flex item is the close button.
    const closeButtonContainer = document.createElement('div');
    const closeButton = document.createElement('button');
    closeButton.className = 'tournesol_simple_button';
    const closeButtonImg = document.createElement('img');
    closeButtonImg.id = 'tournesol_banner_close_icon';
    closeButtonImg.setAttribute(
      'src',
      chrome.runtime.getURL('images/close.svg')
    );
    closeButtonImg.setAttribute('alt', 'Close icon');
    closeButton.append(closeButtonImg);
    closeButtonContainer.append(closeButton);

    closeButton.onclick = () => {
      chrome.storage.local.set({ displayBannerStudy2023: false }, () => {
        this.hide();
      });
    };

    // Dynamically get the user proof before opening the URL.
    actionButton.onclick = (event) => {
      event.preventDefault();
      event.stopPropagation();

      new Promise((resolve, reject) => {
        chrome.runtime.sendMessage(
          {
            message: `getProof:${this.TS_BANNER_PROOF_KW}`,
          },
          (response) => {
            if (response.success) {
              resolve(
                isNavigatorLang('fr')
                  ? `${this.TS_BANNER_ACTION_FR_URL}${response.body.signature}`
                  : `${this.TS_BANNER_ACTION_EN_URL}${response.body.signature}`
              );
            } else {
              reject(response);
            }
          }
        );
      })
        .then((url) => {
          actionButton.setAttribute('href', url);
          window.open(url, '_blank', 'noopener');
        })
        .catch((response) => {
          /**
           * Do not block the users in case of API error. The participation
           * proof being optionnal, and the API tested, logging the errors
           * should be enough.
           *
           * Anonymous users are expected to be redirected to the form without
           * participation proof (HTTP 401), no logging is required.
           */
          if (response.status !== 401) {
            console.error(
              `Failed to retrieve user proof with keyword: ${this.TS_BANNER_PROOF_KW}`
            );
            console.error(response.body);
          }

          window.open(
            isNavigatorLang('fr')
              ? this.TS_BANNER_ACTION_FR_URL
              : this.TS_BANNER_ACTION_EN_URL,
            '_blank',
            'noopener'
          );
        });

      return false;
    };

    actionButtonContainer.append(actionButton);

    banner.appendChild(bannerIconContainer);
    banner.appendChild(bannerTextContainer);
    banner.appendChild(actionButtonContainer);
    banner.appendChild(closeButtonContainer);

    return banner;
  }
}
