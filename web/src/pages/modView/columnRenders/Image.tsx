import React from "react";

export interface ImageData {
  url: string;
}

interface Props {
  data: ImageData;
}

const Image: React.FunctionComponent<Props> = (props: Props) => {
  const { data } = props;
  const { url } = data;

  return (
    <img src={url} alt={url} style={{
      objectFit: "scale-down",
      width: "100%",
      height: "100%",
    }}/>
  );
};

export default Image;
