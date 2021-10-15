export type JSONValue =
  | string
  | number
  | boolean
  | null
  | JSONValue[]
  | { [key: string]: JSONValue };

export interface JSONObject {
  [k: string]: JSONValue;
}

export type ActionList = Array<
  ({ videoId }: { videoId: string }) => JSX.Element
>;

export interface Rating_n {
  contributors: number;
  ratings: number;
}
