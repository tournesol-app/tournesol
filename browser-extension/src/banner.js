// TODO: these values are placeholder values that should be updated.
const defaultOptions = {
  TS_BANNER_DATE_START: new Date('2020-01-01T00:00:00Z'),
  TS_BANNER_DATE_END: new Date('2024-01-01T00:00:00Z'),
  TS_BANNER_ACTION_FR_URL:
    'https://docs.google.com/forms/d/e/1FAIpQLScQzlEKBSA3MqxI0kaPazbyIUnZ4PjFcrR8EFiikG1quyAoiw/viewform?usp=pp_url&entry.939413650=',
  TS_BANNER_ACTION_EN_URL:
    'https://docs.google.com/forms/d/e/1FAIpQLSf9PXr-f8o9QqDR-Pi63xRZx4y4nOumNDdwi_jvUWc6LxZRAw/viewform?usp=pp_url&entry.1924714025=',
  TS_BANNER_PROOF_KW: 'browser_extension_study_2023',
}

export class Banner{
  
  TS_BANNER_DATE_START;
  TS_BANNER_DATE_END;
  TS_BANNER_ACTION_FR_URL;
  TS_BANNER_ACTION_EN_URL;
  TS_BANNER_PROOF_KW;
  banner = undefined;

  constructor(options = defaultOptions) {
    this.TS_BANNER_DATE_START = options.TS_BANNER_DATE_START;
    this.TS_BANNER_DATE_END = options.TS_BANNER_DATE_END;
    this.TS_BANNER_ACTION_FR_URL = options.TS_BANNER_ACTION_FR_URL;
    this.TS_BANNER_ACTION_EN_URL = options.TS_BANNER_ACTION_EN_URL;
    this.TS_BANNER_PROOF_KW = options.TS_BANNER_PROOF_KW;
  }

  isNavigatorLang(lang){
    let expected = lang.toLowerCase();
    let found = window.navigator.language.toLocaleLowerCase();

    // `expected` can be the shortest ISO 639 code of a language.
    //  Example: 'fr'.
    if (found === expected) {
      return true;
    }

    // The shortest ISO 639 code can be followed by other "subtags" like the
    // region, or the variant. Example: 'fr-CA'.
    if (found.startsWith(expected + '-')) {
      return true;
    }

    return false;
  }

  displayBanner(){
    this.banner.classList.add('displayed');
  }

  hideBanner(){
    this.banner.classList.remove('displayed');
  }

  createBanner(){

    if(this.banner != undefined) return;

    this.banner = document.createElement('div');
    this.banner.id = 'tournesol_banner';
    this.banner.className = 'tournesol_banner';
  
    // Only display the banner if the user didn't explicitly close it.
    chrome.storage.local.get(
      'displayBannerStudy2023',
      ({ displayBannerStudy2023 }) => {
        if ([true, null, undefined].includes(displayBannerStudy2023)) {
          this.displayBanner();
        }
      }
    );
  
    // The first flex item is the campaign icon.
    const bannerIconContainer = document.createElement('div');
    const icon = document.createElement('img');
    icon.id = 'tournesol_banner_icon';
    icon.setAttribute('src', chrome.extension.getURL('images/campaign.svg'));
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
      this.isNavigatorLang('fr') ? this.TS_BANNER_ACTION_FR_URL : this.TS_BANNER_ACTION_EN_URL
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
      chrome.extension.getURL('images/close.svg')
    );
    closeButtonImg.setAttribute('alt', 'Close icon');
    closeButton.append(closeButtonImg);
    closeButtonContainer.append(closeButton);
  
    closeButton.onclick = () => {
      chrome.storage.local.set({ displayBannerStudy2023: false }, () => {
        this.hideBanner();
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
                this.isNavigatorLang('fr')
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
          // Anonymous users should be redirected to the form without
          // participation proof. Other errors are logged.
          if (response.status === 401) {
            window.open(
              this.isNavigatorLang('fr')
                ? this.TS_BANNER_ACTION_FR_URL
                : this.TS_BANNER_ACTION_EN_URL,
              '_blank',
              'noopener'
            );
          } else {
            console.error(
              `Failed to retrieve user proof with keyword: ${TS_BANNER_PROOF_KW}`
            );
            console.error(response.body);
            alert(chrome.i18n.getMessage('study2023JoinError'));
          }
        });
  
      return false;
    };
  
    actionButtonContainer.append(actionButton);
  
    this.banner.appendChild(bannerIconContainer);
    this.banner.appendChild(bannerTextContainer);
    this.banner.appendChild(actionButtonContainer);
    this.banner.appendChild(closeButtonContainer);
    return this.banner;
  }

  bannerShouldBeDisplayed(){
    const now = new Date();
  
    if (this.TS_BANNER_DATE_START <= now && now <= this.TS_BANNER_DATE_END) {
      return true;
    }
  
    return false;
  }


}

export default Banner;

