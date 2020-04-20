import React from "react";

export interface TextData {
  text: string;
}

interface Props {
  data: TextData;
}

const isValidUrl = (str: string) => {
  try {
    // tslint:disable-next-line:no-unused-expression
    new URL(str);
  } catch (_) {
    return false;
  }
  return true;
};

const Text: React.FunctionComponent<Props> = (props: Props) => {
  const { data } = props;
  const { text } = data;

  if (isValidUrl(text)) {
    return (
      <a href={text}>{text}</a>
    );
  } else {
    return (
      <p>{text}</p>
    );
  }
};

export default Text;
