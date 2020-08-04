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
      objectFit: "contain",
      width: 360,
      height: 480,
    }}/>
  );
};

export default Image;
