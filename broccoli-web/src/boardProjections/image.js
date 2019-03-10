import React from 'react'

export default function () {
  return function (props) {
    const {document} = props;
    const imageUrl = `${process.env.REACT_APP_S3_HOSTNAME}:${process.env.REACT_APP_S3_PORT}/${process.env.REACT_APP_S3_BUCKET_NAME}/${document["s3_image_id"]}`;
    return (
      <div style={{"width": "200px", "height": "120px"}}>
        <img src={imageUrl} alt={imageUrl} style={{"width": "auto", "height": "100%"}}/>
      </div>
    )
  }
}
