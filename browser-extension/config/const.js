/**
 * A configuration file containing constants that can be used by all content
 * scripts.
 *
 * To make this configuration available to a set of content scripts, it must
 * be the first JavaScript file listed in a `content_scripts` element of the
 * `manifest.json`.
 */

// unique HTML id of the Tournesol iframe
const TOURNESOL_IFRAME_ID = 'x-tournesol-iframe';
// CSS selector identifying the element in which the Tournesol iframe will be added
const TOURNESOL_IFRAME_PARENT_SELECTOR = 'div#info.ytd-watch-flexy';

// the value of the CSS property display used to make the iframe visible
const TOURNESOL_IFRAME_VISIBLE_STATE = 'initial';
