import React from "react";

export interface TextData {
  text: string;
}

interface Props {
  data: TextData;
}

const Text: React.FunctionComponent<Props> = (props: Props) => {
  const { data } = props;

  return (
    <div>{data.text}</div>
  );
};

export default Text;
