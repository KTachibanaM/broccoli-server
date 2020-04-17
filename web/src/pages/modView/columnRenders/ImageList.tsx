import React from "react";
import Image from "./Image";

export interface ImageListData {
  urls: string[];
}

interface Props {
  data: ImageListData;
}

const ImageList: React.FunctionComponent<Props> = (props: Props) => {
  const { data } = props;

  return (
    <div>
      {data.urls.map((url) =>
        <Image data={{url}}/>,
      )}
    </div>
  );
};

export default ImageList;
