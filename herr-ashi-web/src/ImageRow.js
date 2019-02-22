import React from 'react'
import {Grid, Image} from "semantic-ui-react";

export default function (props) {
  const {columnCount, items, rowKey} = props;
  const columnComponents = [];
  for (let columnI = 0; columnI < items.length; ++columnI) {
    columnComponents.push((
      <Grid.Column key={columnI}>
        <Image
          src={items[columnI]["s3_image_link"]}
          size='medium'
          as='a'
          href={items[columnI]["source"]}
          target='_blank'
        />
      </Grid.Column>
    ))
  }
  return (
    <Grid relaxed columns={columnCount} key={rowKey}>
      {columnComponents}
    </Grid>
  )
}
