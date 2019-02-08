import React from 'react'

export default function (props) {
  const {document} = props;
  const imageUrl = `http://localhost:9000/broccoli/${document["s3_image_id"]}`;
  return (
    <div style={{"width": "200px", "height": "120px"}}>
      <img src={imageUrl} alt={imageUrl} style={{"width": "auto", "height": "100%"}}/>
    </div>
  )
}
