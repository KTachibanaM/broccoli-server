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
  let { text } = data;
  if (text.startsWith('"') && text.endsWith('"')) {
    // double-quotes on both ends are indication that it's a raw string from mongodb, ignore them
    text = text.substring(1, text.length - 1)
  }

  if (isValidUrl(text)) {
    return (
      <a href={text} target="_blank">{text}</a>
    );
  } else {
    return (
      <p>{text}</p>
    );
  }
};

export default Text;
