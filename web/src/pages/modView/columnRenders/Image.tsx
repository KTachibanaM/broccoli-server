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
    <div style={{
      display: "flex",
      flexDirection: "column",
      height: "300px",
      width: "300px",
    }}>
      <img src={url} alt={url} style={{objectFit: "contain"}}/>
    </div>
  );
};

export default Image;
