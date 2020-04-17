import React from "react";

export interface VideoData {
  url: string;
}

interface Props {
  data: VideoData;
}

const Video: React.FunctionComponent<Props> = (props: Props) => {
  const { data } = props;
  const { url } = data;

  return (
    <video controls height={250}>
      <source src={url} type="video/mp4"/>
    </video>
  );
};

export default Video;
