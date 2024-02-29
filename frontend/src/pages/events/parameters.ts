/**
 * Allow to consider an event as upcoming even if it started two hours ago.
 *
 * The components to still display the invitation link, and latecomers will
 * be able to join.
 *
 * In miliseconds.
 */
export const TOLERANCE_PERIOD = 2 * 3600 * 1000;
