import React, { Component } from 'react';
import { Redirect } from "react-router-dom";
import getDisplayName from "./getDisplayName"


export default OriginalComponent => {
  class NewComponent extends Component {
    constructor(props) {
      super(props);
      this.state = {
        "redirectTo": ""
      };

      this.redirectTo = this.redirectTo.bind(this)
    }

    redirectTo(path) {
      this.setState({
        "redirectTo": path
      })
    }

    render() {
      if (this.state.redirectTo) {
        return (<Redirect to={this.state.redirectTo}/>)
      }
      return (<OriginalComponent redirectTo={this.redirectTo} {...this.props} />)
    }
  }

  NewComponent.displayName = `applyRouting(${getDisplayName(OriginalComponent)})`;
  return NewComponent
}
