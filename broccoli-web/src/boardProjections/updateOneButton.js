import React, { Component } from "react"

export default function (title, filter_q_key, update_set_doc) {
  return class extends Component {
    constructor(props) {
      super(props);

      this.state = {
        "error": ""
      }
    }

    render() {
      if (this.state.error) {
        return (<div>{this.state.error}</div>)
      }
      return (
        <button onClick={() => {
          this.props.contentClient.updateOne(
            {
              [filter_q_key]: this.props.document[filter_q_key]
            },
            {
              "$set": {
                ...update_set_doc
              }
            }
          )
            .then(() => {
              this.props.reload()
            })
            .catch(error => {
              this.setState({
                "error": error.toString()
              })
            })
        }}>{title}</button>
      )
    }
  }
}
