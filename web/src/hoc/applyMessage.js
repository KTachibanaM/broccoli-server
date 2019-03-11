import React, { Component } from 'react';
import getDisplayName from "./getDisplayName"

export default OriginalComponent => {
  class NewComponent extends Component {
    constructor(props) {
      super(props);
      this.state = {
        "message": "",
        "messageStatus": ""
      };

      this.showOkMessage = this.showOkMessage.bind(this);
      this.showErrorMessage = this.showErrorMessage.bind(this)
    }

    showOkMessage(message) {
      this.setState({
        "message": message,
        "messageStatus": "ok"
      })
    }

    showErrorMessage(message) {
      this.setState({
        "message": message,
        "messageStatus": "error"
      })
    }

    render() {
      return (
        <div>
          <b>{this.props.title}</b>
          <OriginalComponent
            showOkMessage={this.showOkMessage}
            showErrorMessage={this.showErrorMessage}
            {...this.props}
          />
          {this.state.message ?
            (<div style={{
              "color": this.state.messageStatus === "ok" ? "black" : "red"
            }}>{this.state.message}</div>) : null
          }
        </div>
      )
    }
  }
  NewComponent.displayName = `applyMessage(${getDisplayName(OriginalComponent)})`;
  return NewComponent
}

