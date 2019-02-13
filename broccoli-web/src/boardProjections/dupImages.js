import React, { Component } from 'react'
import image from "./image"

export default function () {
  return class extends Component {
    constructor(props) {
      super(props);

      this.state = {
        "loading": true,
        "dupImages": []
      }
    }

    componentDidMount() {
      const {document, contentClient} = this.props;
      contentClient.queryNearestHammingNeighbors(
        {"mod": true},
        "image_dhash",
        document["image_dhash"],
        8 // todo: customize max distance
      )
        .then(payload => {
          const dupImages = payload.filter(i => i["s3_image_id"] !== document["s3_image_id"]);
          this.setState({
            "loading": false,
            "dupImages": dupImages
          })
        })
    }

    render() {
      if (this.state.loading) {
        return (<div>Loading...</div>)
      }
      if (this.state.dupImages.length === 0) {
        return (<div>No dup images</div>)
      }
      return (
        <div>
          {this.state.dupImages.map(dupImage => {
            const Image = image();
            return (<Image key={dupImage["_id"]} document={{"s3_image_id": dupImage["s3_image_id"]}} />)
          })}
        </div>
      )
    }
  }
}
